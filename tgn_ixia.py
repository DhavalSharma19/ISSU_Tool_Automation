#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TGN IXIA Class
"""
from jinja2 import Template, Environment, FileSystemLoader
import traceback
import pprint
import json
import traceback
from pyats.log.utils import banner
from time import sleep


def ixia_connect_interface_traffic_configs(
    logger,
    testbed,
    device,
    tgn_config,
    int_config=0,
    traf_config=0,
    ):

    ''' this api connect to ixia and configure tgn interfaces'''

    port_list = tgn_config['port_list']
    try:
        tgn_handle = device.connect(port_list=port_list, reset=1)
    except:
        logger.error(traceback.format_exc())
        return None
    if tgn_handle['status'] == 1:
        logger.info(banner('Successfully connected to IxNetwork with ports {0}'.format(port_list)))
    else:
        logger.error(banner('Failed to connect to IxNetwork with ports {0}'.format(port_list)))
        return None
    expr = tgn_handle['port_handle'][tgn_config['ip'].split('.'
            )[0]][tgn_config['ip'].split('.')[1]][tgn_config['ip'
            ].split('.')[2]][tgn_config['ip'].split('.')[3]]
    port_handles_dict = {}
    for i in range(len(port_list)):
        port_handles_dict[port_list[i]] = expr[port_list[i]]
    logger.info('Port handles dict after ixia is connected succesfully is :  {0}'.format(port_handles_dict))
    logger.info('IXIA protocol interface configuration')
    if int_config == 1:
        interface_config_ret = {}
        for i in range(len(tgn_config['interface_config'])):
            j = i + 1
            handle = 'port_handle' + str(j)
            port_handle = \
                device.interfaces[tgn_config['interface_config'
                                  ][handle]['handle']].name
            interface_dict = tgn_config['interface_config'][handle]
            if 'vlan' in interface_dict.keys():
                if interface_dict['ip_version'] == 'ipv4':
                    try:
                        int_config_status = device.interface_config(
                            mode=interface_dict['mode'],
                            port_handle=port_handle,
                            intf_mode=interface_dict['intf_mode'],
                            intf_ip_addr=interface_dict['intf_ip_addr'
                                    ],
                            gateway=interface_dict['gateway'],
                            vlan_id=interface_dict['vlan'],
                            )
                        if int_config_status['status'] == 1:
                            logger.info('Successfully configured protocol interface for {0}'.format(port_handle))
                            interface_config_ret[interface_dict['handle'
                                    ]] = \
                                int_config_status['interface_handle']
                        else:
                            logger.error('Failed to configure protocol interface for {0}'.format(port_handle))
                            return None
                    except:
                        logger.error(traceback.format_exc())
                        return None
                elif interface_dict['ip_version'] == 6:
                    try:
                        int_config_status = device.interface_config(
                            mode=interface_dict['mode'],
                            port_handle=port_handle,
                            intf_mode=interface_dict['intf_mode'],
                            intf_ipv6_addr=interface_dict['intf_ip_addr'
                                    ],
                            gateway_ipv6_addr=interface_dict['gateway'
                                    ],
                            vlan_id=interface_dict['vlan'],
                            )
                        if int_config_status['status'] == 1:
                            logger.info('Successfully configured protocol interface for {0}'.format(port_handle))
                            interface_config_ret[interface_dict['handle'
                                    ]] = \
                                int_config_status['interface_handle']
                        else:
                            logger.error('Failed to configure protocol interface for {0}'.format(port_handle))
                            return None
                    except:
                        logger.error(traceback.format_exc())
                        return None
                else:
                    try:
                        int_config_status = device.interface_config(
                            mode=interface_dict['mode'],
                            vlan=1,
                            static_enable=1,
                            static_mac_dst_mode='increment',
                            static_mac_dst=interface_dict['mac_addr'],
                            static_lan_mac_range_mode='normal',
                            vlan_id=interface_dict['vlan'],
                            )
                        if int_config_status['status'] == 1:
                            logger.info('Successfully configured protocol interface for {0}'.format(port_handle))
                            interface_config_ret[interface_dict['handle'
                                    ]] = \
                                int_config_status['interface_handle']
                        else:
                            logger.error('Failed to configure protocol interface for {0}'.format(port_handle))
                            return None
                    except:
                        logger.error(traceback.format_exc())
                        return None
            else:
                if interface_dict['ip_version'] == 'ipv4':
                    try:
                        int_config_status = \
                            device.interface_config(mode=interface_dict['mode'
                                ], port_handle=port_handle,
                                intf_mode=interface_dict['intf_mode'],
                                intf_ip_addr=interface_dict['intf_ip_addr'
                                ], gateway=interface_dict['gateway'])
                        if int_config_status['status'] == 1:
                            logger.info('Successfully configured protocol interface for {0}'.format(port_handle))
                            interface_config_ret[interface_dict['handle'
                                    ]] = \
                                int_config_status['interface_handle']
                        else:
                            logger.error('Failed to configure protocol interface for {0}'.format(port_handle))
                            return None
                    except:
                        logger.error(traceback.format_exc())
                        return None
                elif interface_dict['ip_version'] == 6:
                    try:
                        int_config_status = \
                            device.interface_config(mode=interface_dict['mode'
                                ], port_handle=port_handle,
                                intf_mode=interface_dict['intf_mode'],
                                intf_ipv6_addr=interface_dict['intf_ip_addr'
                                ],
                                gateway_ipv6_addr=interface_dict['gateway'
                                ])
                        if int_config_status['status'] == 1:
                            logger.info('Successfully configured protocol interface for {0}'.format(port_handle))
                            interface_config_ret[interface_dict['handle'
                                    ]] = \
                                int_config_status['interface_handle']
                        else:
                            logger.error('Failed to configure protocol interface for {0}'.format(port_handle))
                            return None
                    except:
                        logger.error(traceback.format_exc())
                        return None
    sleep(10)
    logger.info('IXIA Traffic configuration')
    if traf_config == 1:
        stream_port_hdl_dict = {}
        for i in range(len(tgn_config['traffic_config'])):
            j = i + 1
            handle = 'port_handle' + str(j)
            logger.info(handle)
            port_handle = device.interfaces[tgn_config['traffic_config'
                    ][handle]['handle']].name
            logger.info(port_handle)
            logger.info(interface_config_ret.keys())
            logger.info(tgn_config['traffic_config'][handle]['handle'])
            if tgn_config['traffic_config'][handle]['handle'] \
                in interface_config_ret.keys():
                traffic_dict = tgn_config['traffic_config'][handle]
                if 'emulation_src_handle' in traffic_dict.keys():
                    emulation_src_handle = \
                        interface_config_ret[traffic_dict['emulation_src_handle'
                            ]]
                if 'emulation_dst_handle' in traffic_dict.keys():
                    emulation_dst_handle = \
                        interface_config_ret[traffic_dict['emulation_dst_handle'
                            ]]
                try:
                    traffic_config_status = device.traffic_config(
                        mode=traffic_dict['mode'],
                        port_handle=port_handle,
                        emulation_src_handle=emulation_src_handle,
                        emulation_dst_handle=emulation_dst_handle,
                        l3_protocol=traffic_dict['l3_protocol'],
                        bidirectional=traffic_dict['bidirectional'],
                        ip_id=traffic_dict['ip_id'],
                        ip_ttl=traffic_dict['ip_ttl'],
                        ip_precedence=traffic_dict['ip_precedence'],
                        ip_hdr_length=traffic_dict['ip_hdr_length'],
                        ip_protocol=traffic_dict['ip_protocol'],
                        track_by=traffic_dict['track_by'],
                        ip_fragment_offset=traffic_dict['ip_fragment_offset'
                                ],
                        name=traffic_dict['name'],
                        frame_size=traffic_dict['frame_size'],
                        length_mode=traffic_dict['length_mode'],
                        pkts_per_burst=traffic_dict['pkts_per_burst'],
                        burst_loop_count=traffic_dict['burst_loop_count'
                                ],
                        transmit_mode=traffic_dict['transmit_mode'],
                        inter_stream_gap=traffic_dict['inter_stream_gap'
                                ],
                        )
                except:
                    logger.error(traceback.format_exc())
                    return None
                if traffic_config_status['status'] == 1:
                    logger.info('Successfully created traffic')
                else:
                    logger.error('Failed to create traffic')
                    return None
                status = traffic_config_status['status']
                stream_id = traffic_config_status['stream_id']
                stream_port_hdl_dict[traffic_dict['handle']] = stream_id
                logger.info(stream_port_hdl_dict)
    logger.info(tgn_handle)
    return (tgn_handle, stream_port_hdl_dict)


def startStopIxNetworkTraffic(
    logger,
    tg_hdl='',
    action='',
    port_handle='',
    handle='',
    ):

    '''
    This function starts and stop IxN traffic which depends on action.
    port_handle is port handle and handle is stream_id.
    To start/stop individual traffic, pass stream_id as handle.
    '''

    ixia_traffic_control = tg_hdl.traffic_control(action=action,
            port_handle=port_handle, handle=handle)
    if ixia_traffic_control['status'] == 1:
        logger.info('Successfully {0} traffic'.format(action))
    else:
        logger.error('Failed to {0} traffic'.format(action))
        return None
    return ixia_traffic_control


def getTrafficPacketLoss(
    logger,
    tg_hdl='',
    port_handle='',
    handle='',
    ):

    ''' api validates traffic stats/traffic loss ,traffic_threshold is set as 10% '''

    logger.info('Fetching Traffic packet loss')
    traffic_stats = tg_hdl.traffic_stats(port_handle=port_handle,
            mode='all')
    if traffic_stats['status'] == 1:
        logger.info('Traffic stats is fetched Successfully {0}'.format(traffic_stats))
    else:
        logger.error('Traffic stats is not fetched Successfully')
        return None
    logger.info(traffic_stats)
    if traffic_stats[port_handle]['stream'][handle].has_key('rx') \
        and traffic_stats[port_handle]['stream'][handle].has_key('tx'):
        logger.info('Traffic stats showing correctly')
    else:
        logger.error('Traffic stats shows zero, please check if device configuration and tgn configuraions are proper'
                     )
        return 0
    total_rx_pkts = int(traffic_stats[port_handle]['stream'
                        ][handle]['rx']['total_pkts'])
    total_tx_pkts = int(traffic_stats[port_handle]['stream'
                        ][handle]['tx']['total_pkts'])
    loss_pkts = int(traffic_stats[port_handle]['stream'][handle]['rx'
                    ]['loss_pkts'])
    logger.info('Total rx packet stats =%r', total_rx_pkts)
    logger.info('Total tx packet stats=%r', total_tx_pkts)
    logger.info('Total rx loss packet stats = %r', loss_pkts)
    logger.info('Verify traffic loss , traffic_threshold is set as 10%')
    pass_pkt = total_tx_pkts * 1 * ((100 - 10) / 100)
    if total_rx_pkts > pass_pkt:
        logger.info('Rx is equal to Tx which is expected,No traffic drop, Test PASSED'
                    )
        return 1
    else:
        logger.error('Rx is not equal to Tx which is not expected.Traffic drop is seen, Test FAILED'
                     )
        return 0	
