#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import subprocess
import logging
import re
from time import sleep
import traceback
import collections
import pprint
from collections import defaultdict

# pyATS imports

from unicon import Connection
from pyats import aetest
from pyats.log.utils import banner
from pyats.datastructures.logic import Not, And, Or
from pyats.easypy import run
from pyats.log.utils import banner
from genie.conf import Genie
from genie.conf import Genie
from genie.libs.conf.vrf.vrf import Vrf
from genie.libs.conf.interface.nxos.interface import SubInterface
from genie.libs.conf.interface.nxos.interface import PortchannelInterface
from genie.libs.conf.vlan.vlan import Vlan
from genie.libs.conf.ospf.ospf import Ospf

# custom imports

import sys
import tgn_spirent
import generic_utils


def device_configuration(
    logger,
    testbed,
    steps,
    template_dir=None,
    device_config_flag=None,
    feature_wise_config_flag=None,
    enable_features=None,
    breakout_config=None,
    interface_config=None,
    ospf_config=None,
    l3_physical_intf_config=None,
    ):
    """ device configurations  """

    fail_flag = 0
    logger.info(banner('###########Device Configuration#############'))
    dev_list = []
    for device in testbed.devices:
        if testbed.devices[device].type == 'nxos':
            dev_list.append(testbed.devices[device])
    if device_config_flag == 1 and feature_wise_config_flag == 1:
        if enable_features is not None:
            logger.info('Enable required feature-sets')
            logger.info(enable_features)
            if enable_feature_set(logger, testbed, enable_features) \
                != 1:
                fail_flag = 1
        if breakout_config is not None:
            logger.info('Breakout Configuration')
            logger.info(breakout_config)
            if config_breakout(logger, testbed, breakout_config) != 1:
                fail_flag = 1
        if interface_config is not None:
            logger.info('Interface Configuration')
            if config_port_channel_intf(logger, testbed,
                    interface_config) != 1:
                fail_flag = 1
        if l3_physical_intf_config is not None:
            logger.info('L3 physical interface Configuration')
            if l3_physical_intf_configuration(logger, testbed,
                    dev_list) != 1:
                fail_flag = 1
        if ospf_config is not None:
            logger.info('OSPF Configuration')
            if config_ospf(logger, testbed, ospf_config) != 1:
                fail_flag = 1
        if fail_flag == 1:
            logger.error('device configuration, FAILED')
            return 0
        else:
            return 1
    elif device_config_flag == 1 and feature_wise_config_flag != 1:
        logger.info(banner('Configure all features at a time,load device jinja files and configure through genie configure_by_jinja2 api'
                    ))
        for device in dev_list:
            test_device = testbed.devices[device]
            template_file = test_device.alias + '_configs.j2'
            logger.info('template file is : %s' % template_file)
            try:
                test_device.api.configure_by_jinja2(templates_dir=template_dir,
                        template_name=template_file)
            except:
                logger.error(traceback.format_exc())
                self.failed('device config not successful')
                fail_flag = 1
        if fail_flag == 1:
            logger.error('device configuration, FAILED')
            return 0
        else:
            return 1
    else:
        logger.info(banner('device already configured and in a proper state, proceed with ISSU/ISSD'
                    ))
        return 1


def enable_feature_set(logger, testbed, enable_features):
    fail_flag = 0
    for (key, value) in enable_features.items():
        try:
            device = testbed.devices[key]
        except KeyError:
            logger.error('device alias to be configured: " %s " is not defined in testbedyaml file'
                          % key)
            return 0
        features = value
        feature_string = \
            generic_utils.render_featuresets_from_jinja(features)
        if generic_utils.config_device(logger, device, feature_string):
            logger.info(banner('Enable feature-sets Passed'))
        else:
            logger.error('Feature sets not enabled, FAILED')
            fail_flag = 1
    if fail_flag == 1:
        return 0
    else:
        return 1


def config_breakout(logger, testbed, breakout_config):
    fail_flag = 0
    for (key, value) in breakout_config.items():
        try:
            device = testbed.devices[key]
        except KeyError:
            logger.error('device alias to be configured: " %s " is not defined in testbedyaml file'
                          % key)
            return 0
        module_port_map = breakout_config[key]['module_port_map']
        logger.info(module_port_map)
        for (key, value1) in module_port_map.items():
            mod = key
            ports = value1
            for port in ports:
                feature_string = \
                    generic_utils.render_breakout_interface_config(mod,
                        port)
                logger.info(feature_string)
                if generic_utils.config_device(logger, device,
                        feature_string):
                    logger.info(banner('Breakout configuration Passed'))
                else:
                    logger.error('Breakout configuration, FAILED')
                    fail_flag = 1
    if fail_flag == 1:
        return 0
    else:
        return 1


def config_ospf(logger, testbed, ospf_config):
    fail_flag = 0
    for key in ospf_config.keys():
        try:
            device = testbed.devices[key]
        except KeyError:
            logger.error('device alias to be configured: " %s " is not defined in testbedyaml file'
                          % key)
            return 0
        ospf_configs = ospf_config[key]
        ospf = Ospf()
        vrf0 = Vrf(ospf_config[key]['vrf'])
        ospf.device_attr[device].enabled = True
        ospf.device_attr[device].vrf_attr[vrf0].instance = \
            ospf_configs['ospf_process_id']
        ospf.device_attr[device].vrf_attr[vrf0].enable = True
        ospf.device_attr[device].vrf_attr[vrf0].router_id = \
            ospf_configs['router_id']
        device.add_feature(ospf)
        for intf in ospf_config[key]['interfaces']:
            ospf.device_attr[device].vrf_attr[vrf0].area_attr['0'
                    ].interface_attr[device.interfaces[intf]].if_admin_control = \
                True
            ospf.device_attr[device].vrf_attr[vrf0].area_attr['0'
                    ].interface_attr[device.interfaces[intf]].if_bfd_enable = \
                True
        try:
            cfgs = ospf.build_config(apply=True)
        except:
            logger.error(traceback.format_exc())
            fail_flag = 1

    if fail_flag:
        logger.error(banner('OSPF configuration Failed'))
        return 0
    else:
        logger.info(banner('OSPF configuration Passed'))
        return 1


def l3_physical_intf_configuration(logger, testbed, dev_list):
    fail_flag = 0
    for dev in dev_list:
        intf_list = dev.interfaces
        for intf in intf_list:
            intf = dev.interfaces[intf]
            if intf.ipv4 != None:
                intf.switchport_enable = False
                intf.ipv4 = intf.ipv4
                intf.ipv6 = intf.ipv6
                intf.shutdown = False
                try:
                    cfgs = intf.build_config(apply=True)
                except:
                    logger.error(traceback.format_exc())
                    fail_flag = 1
    if fail_flag:
        logger.error(banner('L3 interface configuration Failed'))
        return 0
    else:
        logger.info(banner('L3 interface configuration Passed'))
        return 1


def config_port_channel_intf(logger, testbed, interface_config):
    fail_flag = 0
    intf_portch_map = {}
    for key in interface_config.keys():
        try:
            device = testbed.devices[key]
        except KeyError:
            logger.error('device alias to be configured: " %s " is not defined in testbedyaml file'
                          % key)
            return 0
        intf_portch_map[key] = interface_config[key]
    interface_po_dict = defaultdict(list)
    for (key1, value1) in intf_portch_map.items():
        device = key1
        interface_po_dict = value1
        interface_po_dict1 = defaultdict(list)
        for (intf, po_no) in interface_po_dict.items():
            logger.info(intf)
            logger.info(po_no)
            interface_po_dict1[po_no['po_ch_group']].append(intf)
        for (key, value) in interface_po_dict1.items():
            po_name = key
            po_int = \
                PortchannelInterface(device=testbed.devices[device],
                    name='Port-channel' + str(po_name), force=True)
            logger.info(po_int)
            for i in range(len(value)):
                int_obj = testbed.devices[device].interfaces[value[i]]
                int_obj.restore_default()
                int_obj.switchport_enable = False
                po_int.add_member(int_obj)
                int_obj.shutdown = False
                try:
                    int_obj.build_config()
                except:
                    logger.error(traceback.format_exc())
                    fail_flag = 1
            po_int.channel_group_mode = 'on'
            po_int.switchport_enable = False
            po_int_obj = 'po' + str(po_name)
            po_int.ipv4 = \
                testbed.devices[device].interfaces[po_int_obj].ipv4
            po_int.ipv6 = \
                testbed.devices[device].interfaces[po_int_obj].ipv6
            try:
                po_int.build_config()
            except:
                logger.error(traceback.format_exc())
                fail_flag = 1

    if fail_flag:
        logger.error(banner('Port Channel configuration Failed'))
        return 0
    else:
        logger.info(banner('Port Channel configuration Passed'))
        return 1
