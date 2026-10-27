from pathlib import Path
import importlib.util
import pytest
from ansible.errors import AnsibleFilterError

ROOT = Path(__file__).resolve().parents[2]


def load_filter(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'plugins/filter' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


compile_network = load_filter('network').compile_network
compile_firewall = load_filter('firewall').compile_firewall


def test_dual_stack_gateways_and_dns_are_preserved_across_backends():
    interfaces = [{'name': 'ens19', 'addresses4': ['192.0.2.10/24'], 'addresses6': ['2001:db8::10/64'], 'gateway4': '192.0.2.1', 'gateway6': '2001:db8::1', 'dns': ['192.0.2.53', '2001:db8::53'], 'routes4': [{'to': '198.51.100.0/24', 'via': '192.0.2.2', 'metric': 20}]}]
    netplan = compile_network(interfaces, 'netplan')['network']['ethernets']['ens19']
    nmcli = compile_network(interfaces, 'nmcli')[0]
    ifupdown = compile_network(interfaces, 'interfaces')[0]
    assert {'to': '::/0', 'via': '2001:db8::1'} in netplan['routes']
    assert nmcli['gw6'] == ifupdown['gateway6'] == '2001:db8::1'
    assert nmcli['routes4'] == ['198.51.100.0/24 192.0.2.2 20']
    assert nmcli['dns6'] == ['2001:db8::53']


def test_bridge_ports_are_unaddressed_slave_profiles():
    profiles = compile_network([{'name': 'ens19'}, {'name': 'br0', 'type': 'bridge', 'members': ['ens19'], 'dhcp4': True}], 'nmcli')
    assert profiles[0]['ifname'] == 'br0'
    assert profiles[1]['slave_type'] == 'bridge'
    assert profiles[1]['master'] == 'degit-br0'


@pytest.mark.parametrize('interfaces', [
    [{'name': 'ens19'}, {'name': 'ens19'}],
    [{'name': 'bad;reboot'}],
    [{'name': 'vlan7', 'type': 'vlan', 'parent': 'missing', 'vlan_id': 7}],
    [{'name': 'ens19', 'dhcp4': True}, {'name': 'br0', 'type': 'bridge', 'members': ['ens19']}],
    [{'name': 'a', 'type': 'bridge', 'members': ['b']}, {'name': 'b', 'type': 'bridge', 'members': ['a']}],
    [{'name': 'ens19', 'addresses4': ['2001:db8::1/64']}],
])
def test_invalid_topologies_are_rejected_before_rendering(interfaces):
    with pytest.raises(AnsibleFilterError):
        compile_network(interfaces, 'nmcli')


@pytest.mark.parametrize('rule', [
    {'port': '0'}, {'port': '65536'}, {'port': '443:80'},
    {'port': '22', 'source': '192.0.2.0/24', 'destination': '2001:db8::/64'},
    {'port': '22', 'interface': 'ens19'}, {'port': '22', 'protocol': 'sctp'},
])
def test_invalid_firewall_rules_are_rejected(rule):
    with pytest.raises(AnsibleFilterError):
        compile_firewall([rule], 'firewalld')


def test_firewall_preserves_ipv6_scoping_and_explicit_removal():
    rule = compile_firewall([{'port': '8000:8100', 'source': '2001:db8::1', 'state': 'absent'}], 'firewalld')[0]
    assert rule['source'] == '2001:db8::1/128'
    assert rule['state'] == 'absent'


def test_networkmanager_adopts_existing_profiles_and_preserves_master_links():
    profiles = compile_network([{'name': 'ens19'}, {'name': 'br0', 'type': 'bridge', 'members': ['ens19']}], 'nmcli')
    adopted = load_filter('network').adopt_nmcli_profiles(profiles, 'br0:Existing bridge\nens19:Existing port\n')
    assert adopted[0]['conn_name'] == 'Existing bridge'
    assert adopted[1]['conn_name'] == 'Existing port'
    assert adopted[1]['master'] == 'Existing bridge'
