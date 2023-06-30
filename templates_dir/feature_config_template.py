FEATURE = '''
feature {{ feature }}
'''

L3_IPV4_INTERFACE_CONFIG='''
interface {{ interface }}
no switchport
ip address {{ ipv4 }}
'''

L3_IPV6_INTERFACE_CONFIG='''
interface {{ interface }}
no switchport
ipv6 address {{ ipv6 }}
'''

OSPF = '''
router ospf {{ process_id }}
router-id {{ router_id }}
bfd
'''

OSPF3 = '''
router ospfv3 {{ process_id }}
router-id {{ router_id }}
bfd
'''

L3_INTERFACE_OSPF_CONFIG='''
interface {{ interface }}
no switchport
ip router ospf {{ process_id }} area {{ area_id }}
'''

L3_INTERFACE_OSPF3_CONFIG='''
interface {{ interface }}
no switchport
ipv6 router ospfv3 {{ process_id }} area {{ area_id }}
'''

BREAKOUT_INTERFACE='''
interface breakout module {{ module_no }} port {{ port_no }} map 10g-4x
'''
