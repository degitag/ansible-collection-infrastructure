"""Validate portable firewall rules before passing them to native backends."""
from ipaddress import ip_network
from ansible.errors import AnsibleFilterError
import re


def compile_firewall(rules, backend, zone='public'):
    if backend not in ('ufw', 'firewalld'):
        raise AnsibleFilterError('Unsupported firewall backend')
    output = []
    for source in rules:
        item = dict(source)
        port = str(item.get('port', ''))
        if not re.fullmatch(r'[0-9]+([:-][0-9]+)?', port):
            raise AnsibleFilterError('A numeric port or port range is required')
        bounds = [int(x) for x in re.split('[:-]', port)]
        if any(x < 1 or x > 65535 for x in bounds) or bounds != sorted(bounds):
            raise AnsibleFilterError('Port range must be ascending and within 1..65535')
        item.update(port=port, protocol=item.get('protocol', 'tcp'), action=item.get('action', 'allow'), state=item.get('state', 'present'), zone=item.get('zone', zone))
        if item['protocol'] not in ('tcp', 'udp') or item['action'] not in ('allow', 'deny', 'reject') or item['state'] not in ('present', 'absent'):
            raise AnsibleFilterError('Unsupported protocol, action or state')
        if item.get('direction', 'in') != 'in':
            raise AnsibleFilterError('The portable firewall API only supports inbound rules')
        if backend == 'firewalld' and 'interface' in item:
            raise AnsibleFilterError('An interface match cannot be translated to a firewalld zone')
        versions = set()
        for key in ('source', 'destination'):
            if item.get(key, 'any') != 'any':
                network = ip_network(item[key], strict=False)
                item[key] = str(network)
                versions.add(network.version)
        if len(versions) > 1:
            raise AnsibleFilterError('Source and destination address families must match')
        if 'interface' in item and not re.fullmatch(r'[A-Za-z0-9_.:-]{1,15}', item['interface']):
            raise AnsibleFilterError('Invalid interface name')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', item['zone']):
            raise AnsibleFilterError('Invalid firewalld zone')
        output.append(item)
    return output


class FilterModule:
    def filters(self):
        return {'firewall_compile': compile_firewall, 'firewall_networks': lambda sources: [str(ip_network(source, strict=False)) for source in sources]}
