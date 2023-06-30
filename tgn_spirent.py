#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TGN Spirent Class
"""
from jinja2 import Template, Environment, FileSystemLoader
import traceback
import pprint
import json
import traceback
from pyats.log.utils import banner
from time import sleep
import sth
import sys
import pdb
import re


class ForkedPdb(pdb.Pdb):
    '''A Pdb subclass that may be used
    from a forked multiprocessing child1
    '''
    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin


def spirent_connect_interface_traffic_configs(
    logger,
    testbed,
    device,
    tgn_config,
    int_config=0,
    traf_config=0,
    ):

    ''' this api connect to spirent and configure tgn interfaces'''

    try:
        tgn_handle = sth.connect(device = str(testbed.devices['spirent'].connections.hltapi.ip),port_list = testbed.devices['spirent'].connections.hltapi.port_list,break_locks = 1)
    except: 
        logger.error(traceback.format_exc())
        return None
    
    logger.info('Spirent protocol interface configuration')
    if int_config == 1:
        interface_config_ret = {}
        for i in range(len(tgn_config['interface_config'])):
            j = i + 1
            handle = 'port_handle' + str(j)
            port_handle=handle
            interface_dict = tgn_config['interface_config'][handle]
            if 'vlan' in interface_dict.keys():
                if interface_dict['ip_version'] == 'ipv4':
                    try:
                        int_config_status = sth.interface_config(
                            mode=interface_dict['mode'],
                            port_handle=interface_dict['handle'],
                            intf_mode=interface_dict['intf_mode'],
                            vlan_id=interface_dict['vlan'],
                            scheduling_mode=interface_dict['scheduling_mode'],
                            enable_ping_response=interface_dict['enable_ping_response'],
                            create_host=interface_dict['create_host'],
                            phy_mode=interface_dict['phy_mode'],
                            port_loadunit=interface_dict['port_loadunit'],
                            port_load=interface_dict['port_load'],
                            control_plane_mtu=interface_dict['control_plane_mtu'],
                            flow_control=interface_dict['flow_control'],
                            data_path_mode=interface_dict['data_path_mode'],
                            autonegotiation=interface_dict['autonegotiation'],
                            duplex=interface_dict['duplex']
                            )
                        if int_config_status['status'] == '1':
                            logger.info('Successfully configured protocol interface for {0}'.format(port_handle))
                            interface_config_ret[interface_dict['handle'
                                    ]] = \
                                int_config_status['handles']
                        else:
                            logger.error('Failed to configure protocol interface for {0}'.format(port_handle))
                            return None
                    except:
                        logger.error(traceback.format_exc())
                        return None
                elif interface_dict['ip_version'] == 'ipv6':
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
                        int_config_status = sth.interface_config(
                            mode=interface_dict['mode'],
                            port_handle=interface_dict['handle'],
                            intf_mode=interface_dict['intf_mode'],
                            scheduling_mode=interface_dict['scheduling_mode'],
                            enable_ping_response=interface_dict['enable_ping_response'],
                            create_host=interface_dict['create_host'],
                            phy_mode=interface_dict['phy_mode'],
                            port_loadunit=interface_dict['port_loadunit'],
                            port_load=interface_dict['port_load'],
                            control_plane_mtu=interface_dict['control_plane_mtu'],
                            flow_control=interface_dict['flow_control'],
                            data_path_mode=interface_dict['data_path_mode'],
                            autonegotiation=interface_dict['autonegotiation'],
                            duplex=interface_dict['duplex']
                            )
                        logger.info(int_config_status['handles'])
                        if int_config_status['status'] == '1':
                            logger.info('Successfully configured protocol interface for {0}'.format(port_handle))
                            interface_config_ret[interface_dict['handle'
                                    ]] = \
                                int_config_status['handles']
                        else:
                            logger.error('Failed to configure protocol interface for {0}'.format(port_handle))
                            return None
                    except:
                        logger.error(traceback.format_exc())
                        return None
                elif interface_dict['ip_version'] == 'ipv6':
                    try:
                        int_config_status = sth.interface_config(
                            mode=interface_dict['mode'],
                            port_handle=interface_dict['handle'],
                            intf_mode=interface_dict['intf_mode'],
                            scheduling_mode=interface_dict['scheduling_mode'],
                            enable_ping_response=interface_dict['enable_ping_response'],
                            create_host=interface_dict['create_host'],
                            phy_mode=interface_dict['phy_mode'],
                            port_loadunit=interface_dict['port_loadunit'],
                            port_load=interface_dict['port_load'],
                            control_plane_mtu=interface_dict['control_plane_mtu'],
                            flow_control=interface_dict['flow_control'],
                            data_path_mode=interface_dict['data_path_mode'],
                            autonegotiation=interface_dict['autonegotiation'],
                            duplex=interface_dict['duplex']
                            )
                        logger.info(int_config_status['handles'])
                        if int_config_status['status'] == '1':
                            logger.info('Successfully configured protocol interface for {0}'.format(port_handle))
                            interface_config_ret[interface_dict['handle'
                                    ]] = \
                                int_config_status['handles']
                        else:
                            logger.error('Failed to configure protocol interface for {0}'.format(port_handle))
                            return None
                    except:
                        logger.error(traceback.format_exc())
                        return None
    
    sleep(10)
    logger.info('Spirent Traffic configuration')
    if traf_config == 1:
        stream_port_hdl_dict = {}
        for i in range(len(tgn_config['traffic_config'])):
            j = i + 1
            handle = 'port_handle' + str(j)
            logger.info(handle)
            port_handle=handle
            logger.info(port_handle)
            logger.info(interface_config_ret.keys())
            logger.info(tgn_config['traffic_config'][handle]['handle'])
            if tgn_config['traffic_config'][handle]['handle'] \
                in interface_config_ret.keys():
                traffic_dict = tgn_config['traffic_config'][handle]
                if 'emulation_src_handle' in traffic_dict.keys():
                    emulation_src_handle = traffic_dict['emulation_src_handle']
                if 'emulation_dst_handle' in traffic_dict.keys():
                    emulation_dst_handle = traffic_dict['emulation_dst_handle'] 
                try:
                    traffic_config_status = sth.traffic_config (
                        mode = traffic_dict['mode'],
                        port_handle=traffic_dict['handle'],
                        stream_id = str(j),
                        l2_encap = traffic_dict['l2_encap'],
                        l3_protocol = traffic_dict['l3_protocol'],
                        ip_id = traffic_dict['ip_id'],
                        ip_ttl = traffic_dict['ip_ttl'],
                        ip_hdr_length = traffic_dict['ip_hdr_length'],
                        ip_protocol = traffic_dict['ip_protocol'],
                        ip_src_addr = traffic_dict['ip_src_addr'],
                        ip_dst_addr = traffic_dict['ip_dst_addr'],
                        ip_fragment_offset = traffic_dict['ip_fragment_offset'],
                        mf_bit = traffic_dict['mf_bit'],
                        reserved = traffic_dict['reserved'],
                        ip_fragment = traffic_dict['ip_fragment'],
                        ip_tos_field = traffic_dict['ip_tos_field'],
                        ip_mbz = traffic_dict['ip_mbz'],
                        ip_precedence = traffic_dict['ip_precedence'],
                        mac_src = traffic_dict['mac_src'],
                        mac_dst = traffic_dict['mac_dst'],
                        enable_control_plane = traffic_dict['enable_control_plane'],
                        name = traffic_dict['namme'],
                        length_mode = traffic_dict['length_mode'],
                        endpoint_map = traffic_dict['endpoint_map'],
                        traffic_pattern = traffic_dict['traffic_pattern'],
                        l3_length = traffic_dict['l3_length'],
                        fill_type = traffic_dict['fill_type'],
                        fill_value = traffic_dict['fill_value'],
                        frame_size = traffic_dict['frame_size'],
                        enable_stream_only_gen = traffic_dict['enable_stream_only_gen'],
                        traffic_state = traffic_dict['traffic_state'],
                        high_speed_result_analysis = traffic_dict['high_speed_result_analysis'],
                        disable_signature = traffic_dict['disable_signature'],
                        fcs_error = traffic_dict['fcs_error'],
                        tx_port_sending_traffic_to_self_en = traffic_dict['tx_port_sending_traffic_to_self_en'],
                        inter_stream_gap = traffic_dict['inter_stream_gap'],
                        inter_stream_gap_unit = traffic_dict['inter_stream_gap_unit'],
                        pkts_per_burst = traffic_dict['pkts_per_burst'],
                        burst_loop_count = traffic_dict['burst_loop_count'],
                        transmit_mode = traffic_dict['transmit_mode'],
                        rate_percent = traffic_dict['rate_percent'],
                        mac_discovery_gw = traffic_dict['mac_discovery_gw'])
                except:
                    logger.error(traceback.format_exc())
                    return None
                if traffic_config_status['status'] == '1':
                    logger.info('Successfully created traffic')
                else:
                    logger.error('Failed to create traffic')
                    return None
                logger.info(traffic_config_status)
                status = traffic_config_status['status']
                stream_id = traffic_config_status['stream_id']
                stream_port_hdl_dict[traffic_dict['handle']] = stream_id
                logger.info(stream_port_hdl_dict)
    tgn_handle=device
    logger.info(tgn_handle)
    return (tgn_handle, stream_port_hdl_dict)


def startStopSpirentTraffic(
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

    spirent_traffic_control = sth.traffic_control (
            stream_handle                                    =  handle,
            traffic_start_mode                               = 'async',
            action                                           = action)

    if spirent_traffic_control['status'] == '1':
        logger.info('Successfully {0} traffic'.format(action))
    else:
        logger.error('Failed to {0} traffic'.format(action))
        return None
    return spirent_traffic_control


def getTrafficPacketLoss(
    logger,
    testscript,
    testbed,
    tg_hdl='',
    port_handle='',
    handle=''
    ):

    ''' api validates traffic stats/traffic loss ,traffic_threshold is set as 10% '''

    logger.info('Fetching Traffic packet loss')
    for devvice in testbed.devices:
        if testscript.parameters["genie_testbed"].devices[devvice].os == "nxos":
            try:
                device = testbed.devices[devvice]
            except KeyError:
                logger.error('device alias to be configured: " %s " is not defined in testbedyaml file'
                            % devvice)
                return 0

            for interfacess in device.interfaces:

                res_rx = device.execute("show int %s | sec RX" % testbed.devices[devvice].interfaces[interfacess].intf)
                match=re.search('([0-9]+) input packets.*',res_rx)
                if match:
                    rx_pkt = match.group(1)
                else:
                    self.failed('CLI format didnt match')

                res_tx = device.execute("show int %s | sec TX" % testbed.devices[devvice].interfaces[interfacess].intf)
                matchh=re.search('([0-9]+) output packets.*',res_tx)
                if matchh:
                    tx_pkt = matchh.group(1)
                else:
                    self.failed('CLI format didnt match')

                logger.info('Verify traffic loss , traffic_threshold is set as 10%')
                pass_pkt = tx_pkt * 1 * (int)((100 - 10) / 100)
                if rx_pkt > pass_pkt:
                    logger.info('Rx is equal to Tx which is expected,No traffic drop, Test PASSED'
                                )
                else:
                    logger.error('Rx is not equal to Tx which is not expected.Traffic drop is seen, Test FAILED'
                                )
                    return 0

    return 1
