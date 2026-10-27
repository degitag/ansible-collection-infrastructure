"""Compile the portable network API to native backend data."""
from ipaddress import ip_address, ip_interface, ip_network
import re

from ansible.errors import AnsibleFilterError


def compile_network(interfaces, backend):
    """Reject ambiguous input before any host configuration is changed."""
    if backend not in ('netplan', 'interfaces', 'nmcli'):
        raise AnsibleFilterError('Unsupported network backend: ' + str(backend))
    names = set()
    normalized = []
    for entry in interfaces:
        item = dict(entry)
        name = item.get('name', '')
        if not re.fullmatch(r'[A-Za-z0-9_.:-]{1,15}', name) or name in names:
            raise AnsibleFilterError('Interface names must be unique valid Linux interface names: ' + str(name))
        names.add(name)
        kind = item.get('type', 'ethernet')
        if kind not in ('ethernet', 'bridge', 'bond', 'vlan'):
            raise AnsibleFilterError('Unsupported interface type: ' + str(kind))
        item['type'] = kind
        for family in (4, 6):
            addresses = item.setdefault('addresses' + str(family), [])
            for address in addresses:
                if ip_interface(address).version != family:
                    raise AnsibleFilterError('Address family does not match: ' + address)
            gateway = item.get('gateway' + str(family))
            if gateway and ip_address(gateway).version != family:
                raise AnsibleFilterError('Gateway family does not match')
            item['routes' + str(family)] = [dict(route) for route in item.get('routes' + str(family), [])]
            for route in item['routes' + str(family)]:
                if ip_network(route['to'], strict=False).version != family or ip_address(route['via']).version != family:
                    raise AnsibleFilterError('Route address family does not match')
        for server in item.setdefault('dns', []):
            ip_address(server)
        if kind == 'vlan' and (not item.get('parent') or not 1 <= int(item.get('vlan_id', 0)) <= 4094):
            raise AnsibleFilterError('VLANs need a parent and vlan_id in 1..4094')
        if 'mtu' in item and not 68 <= int(item['mtu']) <= 65535:
            raise AnsibleFilterError('MTU must be in 68..65535')
        if item.get('bond_mode', 'active-backup') not in ('active-backup', 'balance-rr', 'balance-xor', 'broadcast', '802.3ad', 'balance-tlb', 'balance-alb'):
            raise AnsibleFilterError('Unsupported bond mode')
        for domain in item.get('search', []):
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,252}', domain):
                raise AnsibleFilterError('Invalid DNS search domain')
        for route in item['routes4'] + item['routes6']:
            if 'metric' in route:
                route['metric'] = int(route['metric'])
                if not 0 <= route['metric'] <= 4294967295:
                    raise AnsibleFilterError('Invalid route metric')
        item.setdefault('members', [])
        if kind not in ('bridge', 'bond') and item['members']:
            raise AnsibleFilterError('Only bridges and bonds may declare members')
        normalized.append(item)
    members = {}
    for item in normalized:
        for member in item['members']:
            if member not in names or member == item['name'] or member in members:
                raise AnsibleFilterError('Each bridge/bond member must be declared and have one master')
            members[member] = item
        if item['type'] == 'vlan' and item['parent'] not in names:
            raise AnsibleFilterError('A VLAN parent must be declared in network_interfaces')
    for item in normalized:
        if item['name'] in members and (item['addresses4'] or item['addresses6'] or item.get('dhcp4') or item.get('dhcp6') or item.get('gateway4') or item.get('gateway6')):
            raise AnsibleFilterError('Addresses and DHCP belong on the bridge/bond, not its members')
    # Detect parent/master cycles rather than producing an unbootable topology.
    edges = {i['name']: ([members[i['name']]['name']] if i['name'] in members else []) + ([i['parent']] if i['type'] == 'vlan' else []) for i in normalized}
    def visit(name, trail):
        if name in trail:
            raise AnsibleFilterError('Network topology contains a cycle')
        for parent in edges[name]:
            visit(parent, trail | {name})
    for name in names:
        visit(name, set())
    if backend == 'interfaces':
        return normalized
    if backend == 'netplan':
        result = {'version': 2, 'renderer': 'networkd'}
        sections = {'ethernet': 'ethernets', 'bridge': 'bridges', 'bond': 'bonds', 'vlan': 'vlans'}
        for item in normalized:
            data = {'dhcp4': item.get('dhcp4', False), 'dhcp6': item.get('dhcp6', False)}
            if item['addresses4'] or item['addresses6']:
                data['addresses'] = item['addresses4'] + item['addresses6']
            if item['dns'] or item.get('search'):
                data['nameservers'] = {'addresses': item['dns'], 'search': item.get('search', [])}
            if 'mtu' in item:
                data['mtu'] = item['mtu']
            routes = item['routes4'] + item['routes6']
            for family in (4, 6):
                if item.get('gateway' + str(family)):
                    routes = routes + [{'to': '0.0.0.0/0' if family == 4 else '::/0', 'via': item['gateway' + str(family)]}]
            if routes:
                data['routes'] = routes
            if item['type'] in ('bridge', 'bond'):
                data['interfaces'] = item['members']
                if item['type'] == 'bond':
                    data['parameters'] = {'mode': item.get('bond_mode', 'active-backup')}
            if item['type'] == 'vlan':
                data.update(id=item['vlan_id'], link=item['parent'])
            result.setdefault(sections[item['type']], {})[item['name']] = data
        return {'network': result}
    connections = []
    for item in normalized:
        data = {'conn_name': 'degit-' + item['name'], 'ifname': item['name'], 'type': item['type'], 'autoconnect': True,
                'method4': 'auto' if item.get('dhcp4') else ('manual' if item['addresses4'] else 'disabled'),
                'method6': 'auto' if item.get('dhcp6') else ('manual' if item['addresses6'] else 'disabled'),
                'ip4': item['addresses4'], 'ip6': item['addresses6'],
                'dns4': [x for x in item['dns'] if ip_address(x).version == 4],
                'dns6': [x for x in item['dns'] if ip_address(x).version == 6]}
        for source, target in [('gateway4', 'gw4'), ('gateway6', 'gw6'), ('mtu', 'mtu')]:
            if source in item:
                data[target] = item[source]
        for family in (4, 6):
            data['routes' + str(family)] = [r['to'] + ' ' + r['via'] + (' ' + str(r['metric']) if 'metric' in r else '') for r in item['routes' + str(family)]]
            data['dns' + str(family) + '_search'] = item.get('search', [])
        if item['type'] == 'vlan':
            data.update(vlanid=item['vlan_id'], vlandev=item['parent'])
        if item['type'] == 'bond':
            data['mode'] = item.get('bond_mode', 'active-backup')
        if item['name'] in members:
            master = members[item['name']]
            data.update(master='degit-' + master['name'], slave_type=master['type'])
            if item['type'] == 'ethernet':
                data['type'] = master['type'] + '-slave'
        connections.append(data)
    return sorted(connections, key=lambda x: ('master' in x, x['type'] == 'vlan'))


def network_needs_apply(interfaces, runtime):
    current = {item['ifname']: item for item in runtime}
    for interface in interfaces:
        state = current.get(interface['name'], {})
        addresses = {str(ip_interface(str(a['local']) + '/' + str(a['prefixlen']))) for a in state.get('addr_info', [])}
        expected = {str(ip_interface(address)) for family in (4, 6) for address in interface.get('addresses' + str(family), [])}
        if not expected.issubset(addresses) or 'UP' not in state.get('flags', []):
            return True
        for family in (4, 6):
            if interface.get('dhcp' + str(family)) and not any(ip_interface(address).version == family for address in addresses):
                return True
        if 'mtu' in interface and state.get('mtu') != interface['mtu']:
            return True
    return False


def adopt_nmcli_profiles(profiles, active_connections):
    active = dict(line.split(':', 1) for line in active_connections.splitlines() if ':' in line)
    names = {profile['conn_name']: active.get(profile['ifname'], profile['conn_name']) for profile in profiles}
    result = []
    for profile in profiles:
        item = dict(profile)
        item['conn_name'] = names[item['conn_name']]
        if 'master' in item:
            item['master'] = names.get(item['master'], item['master'])
        result.append(item)
    return result


class FilterModule:
    def filters(self):
        return {'network_compile': compile_network, 'network_needs_apply': network_needs_apply, 'network_nmcli_profiles': adopt_nmcli_profiles}
