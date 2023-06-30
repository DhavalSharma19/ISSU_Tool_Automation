#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import subprocess
import logging
import re
import pdb
import os
import traceback
import time
import sys
from jinja2 import Environment
from collections import defaultdict
from genie.conf import Genie
from genie.libs.conf.vrf.vrf import Vrf
from genie.libs.conf.interface.nxos.interface import SubInterface
from genie.libs.conf.interface.nxos.interface import PortchannelInterface
from genie.libs.conf.vlan.vlan import Vlan
from genie.libs.conf.ospf.ospf import Ospf
import unicon
import parsergen
import sys
import pdb

# pyATS
from pyats import aetest
from pyats.log.utils import banner
from pyats.datastructures.logic import Not, And, Or
from pyats.easypy import run
from unicon.eal.dialogs import Dialog
from unicon.eal.dialogs import Statement
import collections


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


def core_check(device, logger):
    """ this method checks if any core present in device
        arguments :
            device : device console handle
            logger : logging handle

        Return Values:
          # returns 1   - success
          # returns 0 - Failed case
    """

    res = 1
    cmd = 'show cores'
    try:
        core_output = device.execute(cmd, timeout=120)
    except Exception:
        logger.error(traceback.format_exc())
        logger.error('Error while executing cmd %s on device %s' % cmd)
        res = 0
    if core_output:
        res = re.search("[a-zA-Z]+\s+(\d+)", core_output)
        if res:
            pid = res.group(1)
            logger.error('UUT CRASHED for process %s' % pid)
            res = 0
        else:
            logger.info('Crash not found')
    return res


def verify_syslogs(logger, device):
    """ this method checks syslog errors present in device
        arguments :
            device : device console handle
            logger : logging handle

        Return Values:
          # returns 1   - success
          # returns 0 - Failed case
    """

    res = 1
    cmd = \
        'show logging logfile |include ignore-case fail|warning|critical|error'
    try:
        syslog_output = device.execute(cmd, timeout=2000)
    except Exception:
        logger.error(traceback.format_exc())
        logger.error('Error while executing cmd %s on device %s' % cmd)
        res = 0
    logger.info(banner('Show logging logfile output !!!!!!!!'))
    logger.warning(syslog_output)
    return res


def show_cdp(logger, device):
    """ this method executed show cdp neighbours in device
        arguments :
            device : device console handle
            logger : logging handle

        Return Values:
          # returns 1   - success
          # returns 0 - Failed case
    """

    res = 1
    try:
        showcdp_output = device.api.get_cdp_neighbors_info()
    except Exception:
        logger.error(traceback.format_exc())
        logger.error('Error while executing cmd %s on device %s' % cmd)
        res = 0
    logger.info(banner('Show cdp neighbors output !!!!!!!!'))
    logger.info(showcdp_output)
    return res


#def mts_leak_verification(logger, device):
#    """ this method checks if any MTS leak present in device
#        arguments :
#            device : device console handle
#            logger : logging handle
#
#        Return Values:
#          # returns 1   - success
#          # returns 0 - Failed case
#    """
#
#    res = 1
#    cmd = 'show system internal mts buffers summary'
#    try:
#        mts_output = device.execute(cmd, timeout=120)
#    except Exception:
#        logger.error(traceback.format_exc())
#        logger.error('Error while executing cmd %s on device %s' % cmd)
#        res = 0
#    time.sleep(10)
#    count = 0
#    if mts_output is not None:
#        lines = mts_output.splitlines()
#        for i in lines:
#            if len(i.strip()) != 0:
#                k = i.split()
#                if (k[0] == 'sup' or k[0] == 'lc') and k[1] != '284':
#                    count = count + 1
#    if count > 1:
#        logger.error(banner('MTS Leak found !!!!!!!!'))
#        res = 0
#    else:
#        logger.info(banner('MTS Leak not found'))
#    return res


def get_mts_leak(logger, device):
    """ this method checks if any MTS leak present in device
        arguments :
            device : device console handle
            logger : logging handle

        Return Values:
          # returns 1   - success
          # returns 0 - Failed case
    """

    res = 1
    cmd = 'show system internal mts buffers summary'
    try:
        mts_output = device.execute(cmd, timeout=120)
    except Exception:
        logger.error(traceback.format_exc())
        logger.error('Error while executing cmd %s on device %s' % cmd)
        res = 0
    time.sleep(10)
    count = 0
    if mts_output is not None:
        lines = mts_output.splitlines()
        for i in lines:
            if len(i.strip()) != 0:
                k = i.split()
                if (k[0] == 'sup' or k[0] == 'lc') and k[1] != '284':
                    logger.error("MTS leak found with module:%s sapno:%s,sleep for 10 secs and check again" % (k[0], k[1]))
                    count = count + 1
    logger.info(count)
    if count > 1:
        return count
    else:
        logger.info(banner('MTS Leak not found'))
        return None

def mts_leak_verification(logger,device):
    res = 1
    timeout_sec=300
    interval_sec=10
    counter = interval_sec
    while counter <= timeout_sec:
        logger.info("Check MTS detail for device : %s" % device)
        mts_leak = get_mts_leak(logger,device)
        if mts_leak:
            logger.error("MTS leak found for device:%s" % device )
            time.sleep(interval_sec)
            res=0
        else:
           logger.info("No MTS leak found for device:%s" % device )
           res=1
           break
        counter = counter + interval_sec
    return res

def render_featuresets_from_jinja(features):
    '''returns string:
    feature <features[0]>
    feature <features[1]>
    '''

    cfgfeat = \
        [Environment().from_string(feature_config_template.FEATURE).render(feature=feature)
         for feature in features]
    return ''.join(cfgfeat)


def render_ospf_config_from_jinja(ospf_type, process_id='', router_id=''
                                  ):
    '''returns string:
    '''

    if ospf_type == 'ospf':
        return Environment().from_string(feature_config_template.OSPF).render(process_id=process_id,
                router_id=router_id)
    elif ospf_type == 'ospfv3':
        return Environment().from_string(feature_config_template.OSPF3).render(process_id=process_id,
                router_id=router_id)


def render_ospf_interface_config_from_jinja(
    ospf_type,
    interface,
    process_id='',
    area_id='',
    ):
    '''returns string:
    '''

    if ospf_type == 'ospf':
        return Environment().from_string(feature_config_template.L3_INTERFACE_OSPF_CONFIG).render(interface=interface,
                process_id=process_id, area_id=area_id)
    elif ospf_type == 'ospf3':
        return Environment().from_string(feature_config_template.L3_INTERFACE_OSPF3_CONFIG).render(interface=interface,
                process_id=process_id, area_id=area_id)


def render_l3_interface_config_from_jinja(ip_type, interface, ip_addr):
    '''returns string:
    '''

    if ip_type == 'ipv4':
        return Environment().from_string(feature_config_template.L3_IPV4_INTERFACE_CONFIG).render(interface=interface,
                ipv4=ip_addr)
    elif ip_type == 'ipv6':
        return Environment().from_string(feature_config_template.L3_IPV6_INTERFACE_CONFIG).render(interface=interface,
                ipv6=ip_addr)


def render_breakout_interface_config(module_no, port_no):
    '''returns string:
    '''

    return Environment().from_string(feature_config_template.BREAKOUT_INTERFACE).render(module_no=module_no,
            port_no=port_no)


def config_device(logger, device, feature):
    res = 1
    try:
        device.configure(feature)
    except:
        logger.error(traceback.format_exc())
        res = 0
    return res


def apply_ospf_interface(
    logger,
    device,
    interface,
    ospf_type,
    ospf_pro_id,
    area_id,
    ):

    res = 1
    if ospf_type == 'ospf':
        feature_string = render_ospf_interface_config_from_jinja('ospf'
                , interface.name, process_id=ospf_pro_id,
                area_id=area_id)
        if not config_device(logger, device, feature_string):
            return 0
        else:
            return 1
    elif ospf_type == 'ospfv3':
        feature_string = render_ospf_interface_config_from_jinja('ospf3'
                , interface.name, process_id=ospf_pro_id,
                area_id=area_id)
        if not config_device(logger, device, feature_string):
            return 0
        else:
            return 1


def ospf_verification(
    logger,
    device,
    vrf,
    area_id,
    process_id,
    interface,
    address_family,
    neighbour_router_id,
    ):

    res = 1
    try:
        ospf_out = device.learn('ospf')
    except:
        logger.error(traceback.format_exc())
        res = 0
    logger.info(ospf_out)
    ospf_out = ospf_out.to_dict()
    try:
        if ospf_out['info']['vrf'][vrf]['address_family'
                ][address_family]['instance'][process_id]['areas'
                ][area_id]['interfaces'][interface]['neighbors'
                ][neighbour_router_id]['neighbor_router_id']:
            neighbour_id = ospf_out['info']['vrf'][vrf]['address_family'
                    ][address_family]['instance'][process_id]['areas'
                    ][area_id]['interfaces'][interface]['neighbors'
                    ][neighbour_router_id]['neighbor_router_id']
            logger.info('ospf neighbour details %s', neighbour_id)
            if neighbour_id == neighbour_router_id:
                logger.info('OSPF neighbour learnt succesfully')
            else:
                logger.error('OSPF neighbour not learnt,FAILED')
                res = 0
            state = ospf_out['info']['vrf'][vrf]['address_family'
                    ][address_family]['instance'][process_id]['areas'
                    ][area_id]['interfaces'][interface]['neighbors'
                    ][neighbour_router_id]['state']
            logger.info('ospf state %s', state)
            if state == 'full':
                logger.info('OSPF state is full')
            else:
                logger.error('OSPF state is not FULL,FAILED')
                res = 0
    except:
        res = 0
    return res


def interface_inoutput_rate_compare(logger, device, interface):
    cmd1 = 'show interface ' + interface + ' counters br'
    out = device.execute(cmd1, timeout=120)
    res = 1
    try:
        command = 'show interface ' + interface + ' counters br | json'
        out = device.execute(command, timeout=120)
    except:
        logger.error(traceback.format_exc())
        res = 0
    out_dict = device.api.get_config_dict(out)
    input_rate = out_dict['TABLE_interface']['ROW_interface'
            ]['eth_inrate2']
    output_rate = out_dict['TABLE_interface']['ROW_interface'
            ]['eth_outrate2']
    logger.info('interface traffic input rate %s ' % input_rate)
    logger.info('interface traffic input rate %s ' % output_rate)
    if input_rate != output_rate:
        res = 0
    return res


def interface_reset_status(logger, device):
    cmd = 'show interface'
    res = 1
    try:
        out = device.parse(cmd)
    except:
        logger.error(traceback.format_exc())
        res = 0
    expr = '^Ethernet.*'
    intf_list = []
    for interface in out.keys():
        if re.search(expr, interface):
            intf_list.append(interface)
    for interface in intf_list:
        if out[interface]['interface_reset'] == 0:
            logger.info('interface %s reset status is proper '
                        % interface)
        else:
            logger.error('interface %s reset status is not proper '
                         % interface)
            res = 0
    return res


def config_device_through_jinja(
    logger,
    device,
    template_dir,
    template,
    **kwargs
    ):
    """configure device through jinja template"""

    fail_flag = 0
    key_args = {}
    for (key, value) in kwargs.items():
        key_args[key] = value
    if 'TOTAL_VNI_MEMBERS' in key_args.keys():
        TOTAL_MEMBERS = int(key_args['TOTAL_VNI_MEMBERS'])
        logger.info('Total VNI members:%s ' % TOTAL_MEMBERS)

        try:
            out = \
                device.api.configure_by_jinja2(templates_dir=template_dir,
                    template_name=template, TOTAL_MEMBERS=TOTAL_MEMBERS)
        except:
            fail_flag = 1
            logger.error(traceback.format_exc())
    elif 'rp_address' in key_args.keys():

        rp_address = key_args['rp_address']
        group_lst = key_args['group_lst']
        logger.info('rp-address:%s ' % rp_address)
        logger.info('group-list:%s ' % group_lst)

        try:
            out = \
                device.api.configure_by_jinja2(templates_dir=template_dir,
                    template_name=template, rp_address=rp_address,
                    group_lst=group_lst)
        except:
            fail_flag = 1
            logger.error(traceback.format_exc())
    elif 'vlan_range' in key_args.keys():
        vlan_range = key_args['vlan_range']

        logger.info('vlan_range:%s ' % vlan_range)

        try:
            out = \
                device.api.configure_by_jinja2(templates_dir=template_dir,
                    template_name=template, vlan_range=int(vlan_range))
        except:
            fail_flag = 1
            logger.error(traceback.format_exc())
    else:
        try:
            out = \
                device.api.configure_by_jinja2(templates_dir=template_dir,
                    template_name=template)
        except:
            fail_flag = 1
            logger.error(traceback.format_exc())

    if fail_flag:
        return 0
    else:
        return 1


def bfd_state_verify(
    testbed,
    device,
    our_addr,
    neigh_addr,
    vrf_name='default',
    ):

    try:
        parsedOutput = parsergen.oper_fill_tabular(device=device,
                show_command='show bfd neighbors', header_fields=[
            r'OurAddr[\t]*',
            r'NeighAddr[\t]*',
            r'LD\/RD[\t]*',
            r'RH\/RS[\t]*',
            r'Holdown\(mult\)[\t]*',
            r'State[\t]*',
            r'Int[\t]*',
            r'Vrf[\t]*',
            ], index=0)
        status = parsedOutput.entries[our_addr][r'State[\t]*']

    # cmd = "show bfd neighbors vrf %s" % vrf_name
    # output = device.execute(cmd)
    # lines = output.splitlines()
    # pattern = "%s.*%s.*Up.*" % (our_addr, neigh_addr)
    # for line in lines:
    #    bfd_is_up = re.search(pattern, line)
    #    if bfd_is_up:
    #        return 1

        if status:
            return 1
    except:
        return 0
    return 0


def bfd_verification(logger, device):
    res = 1
    try:
        bfd_out = device.execute('show bfd neighbors | json',
                                 timeout=120)
        bfd_out_dict = device.api.get_config_dict(bfd_out)
    except:
        logger.error(traceback.format_exc())
        res = 0

    if bfd_out_dict['TABLE_bfdNeighbor']['ROW_bfdNeighbor'
            ]['local_state'] != 'Up' \
        and bfd_out_dict['TABLE_bfdNeighbor']['ROW_bfdNeighbor'
            ]['remote_state'] != 'Up':
        res = 0
    return res


def generate_port_channel_interface_dict(
    testbed,
    device,
    po,
    int_list,
    ):

    interface_po_dict = defaultdict(list)
    po = po
    int_start_range = int_list.split('-')[0]
    int_end_range = int_list.split('-')[1]
    for i in range(int(int_start_range), int(int_end_range) + 1):
        alias = 'int' + str(i)
        interface = device.interfaces[alias]
        interface_po_dict[po].append(interface)
    return interface_po_dict


def configure_port_channel(
    logger,
    testbed,
    device,
    interface_po_dict,
    ):

    fail_flag = 0
    logger.info('Configure port channel: calling genie apis')
    logger.info(interface_po_dict)
    for (key, value) in interface_po_dict.items():
        po_name = key
        po_int = PortchannelInterface(device=device, name='Port-channel'
                 + str(po_name), force=True)
        for i in range(len(value)):
            int_obj = value[i]
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
        po_int.ipv4 = device.interfaces[po_int_obj].custom['ipv4']
        po_int.ipv6 = device.interfaces[po_int_obj].custom['ipv6']
        try:
            po_int.build_config()
        except:
            logger.error(traceback.format_exc())
            fail_flag = 1
    if fail_flag:
        return 0
    else:
        return 1


def enable_icam(logger, device):
    res = 1
    enable_icam_cmd1 = 'install activate icam'
    enable_icam_cmd2 = 'icam monitor scale'
    out = device.parse('show version')
    if out is not None:
        #system_version=out['platform']['system_version']
        system_version = out['platform']['software']['system_version']

        # match_pattern=r"^(.*)\.(.*)\((.*)\).*"
        match_pattern = \
            r"^([0-1]?[0-9]|2[0-3])\.([0-9]{1})\(([0-9]{1})[a-z]*\).*"

        #match_pattern = \
            #r"^([0-1]?[0-9]|2[0-3])\.([0-9]{1})\(([0-9]{1})\).*"
        match = re.search(match_pattern, system_version)
        # ForkedPdb().set_trace()
        version_part1 = int(match.group(1))
        version_part2 = int(match.group(2))
        version_part3 = int(match.group(3))

        # ForkedPdb().set_trace()

        if version_part1 >= 10 or version_part1 >= 9 and version_part2 \
            >= 3 and version_part3 > 4:
            try:
                out = device.configure(enable_icam_cmd1, timeout=60)
            except:
                logger.error(traceback.format_exc())
                res = 0
            try:
                out = device.configure(enable_icam_cmd2, timeout=60)
            except:
                logger.error(traceback.format_exc())
                res = 0
    else:
        res = 0
    return res


def execute_with_reply(
    device,
    cmd,
    dialog_list,
    resp_list,
    timeout=3000,
    ):

    stmt = []
    for (idx, dialog) in enumerate(dialog_list):
        if resp_list[idx] == 'None':
            s = Statement(pattern=dialog, action=None,
                          loop_continue=True, continue_timer=True)
        else:
            s = Statement(pattern=dialog, action='sendline('
                          + resp_list[idx] + ')', loop_continue=True,
                          continue_timer=True)
        stmt.append(s)
    response = Dialog(stmt)
    result, out = device.reload(cmd, dialog=response, timeout=3000, prompt_recovery=True, return_output=1, reconnect_sleep=500, config_lock_retries=20, config_lock_retry_sleep=10)
    print("========>")
    print(result)
    print(out)
    
    #out = device.execute(cmd, reply=response, timeout=10000)
    return out


def validate_issu(
    logger,
    device,
    img_name,
    upgrade_type,
    upgrade_subtype,
    lxc_issu,
    ):

    issu_upgrade = 1
    res = 1
    logger.info('relogin to the box')
    device.disconnect()
    try:
        device.connect(timeout=2000)
    except:
        logger.error('Device not logging in after ISSU')
        logger.error(traceback.format_exc())
        res = 0
    try:
        device.api.verify_module_status()
    except:
        logger.error('Module status not proper after issu')
        logger.error(traceback.format_exc())
        res = 0
    try:
        out = device.api.get_running_image()
    except:
        logger.error('Show version is not showing correct image after issu'
                     )
        logger.error(traceback.format_exc())
        res = 0

    if out:
        if out[0].split('/')[1] == img_name:
            logger.info('Device loaded with proper image after ISSU')
        else:
            logger.error('Device loaded with incorrect image after ISSU'
                         )
            res = 0
    try:
        out = device.execute('show install all status', timeout=120)
    except:
        res = 0
        logger.error(traceback.format_exc())
    if upgrade_type == 'downgrade':
        if out:
            if not re.search(r'.*Finishing the upgrade, switch will reboot in 10 seconds.*'
                             , out, re.I):
                logger.error('show install all status after ISSU downgrade is not proper'
                             )
                res = 0
    elif upgrade_type == 'upgrade' and upgrade_subtype == 'disruptive':
        if out:
            if not re.search(r'.*Finishing the upgrade, switch will reboot in 10 seconds.*'
                             , out, re.I):
                logger.error('show install all status after ISSU upgrade is not proper'
                             )
                res = 0
    elif upgrade_type == 'upgrade' and upgrade_subtype \
        == 'nondisruptive':
        if out:
            if not re.search(r'.*Install has been successful.*', out,
                             re.I) \
                and re.search(r'.*Finishing the upgrade, switch will reboot in 10 seconds.*'
                              , out, re.I):
                logger.warning('FYI:Disruptive ISSU happened instead of non-disruptive ISSU'
                               )
                issu_upgrade = 0
            elif not re.search(r'.*Install has been successful.*', out,
                               re.I):

                logger.error('show install all status after ISSU upgrade is not proper'
                             )
                res = 0
    try:
        out = device.execute('sh system reset-reason | json',
                             timeout=120)
        out_dict = device.api.get_config_dict(out)
    except:
        res = 0
        logger.error(traceback.format_exc())
    logger.info('Check if device is an EOR, modular chassis setup')
    device_type = ''
    mod_out = device.execute('show mod | inc ha-standby', timeout=120)
    if mod_out != '':
        device_type = 'EOR'
        logger.info('device type is EOR')
    else:
        device_type = 'TOR'
        logger.info('device type is TOR')
    if device_type == 'TOR' and upgrade_type == 'downgrade':
        if out_dict:
            if out_dict['TABLE_reason']['ROW_reason']['TABLE_rr'
                    ]['ROW_rr'][0]['reason'] \
                == 'Reset due to non-disruptive upgrade':
                logger.error('show system reset reason is not proper after ISSU downgrade'
                             )
                res = 0
            else:
                logger.info('show system reset reason is proper after ISSU downgrade'
                            )
    elif device_type == 'TOR' and upgrade_type == 'upgrade':
        if out_dict:
            if upgrade_subtype == 'disruptive' and out_dict['TABLE_reason']['ROW_reason']['TABLE_rr'
                    ]['ROW_rr'][0]['reason'] != 'Reset due to upgrade' :
                logger.error('show system reset reason is not proper after ISSU upgrade disruptive'
                               )
                res=0
            elif upgrade_subtype == 'nondisruptive' and out_dict['TABLE_reason']['ROW_reason']['TABLE_rr'
                    ]['ROW_rr'][0]['reason'] \
                != 'Reset due to non-disruptive upgrade':
                logger.error('show system reset reason is not proper after ISSU upgrade'
                             )
                res = 0
            else:
                logger.info('show system reset reason is proper after ISSU upgrade'
                            )
    elif device_type == 'EOR' and upgrade_type == 'downgrade':
        if out_dict:
            if out_dict['TABLE_reason']['ROW_reason'][0]['TABLE_rr'
                    ]['ROW_rr'][0]['reason'] \
                == 'Reset due to non-disruptive upgrade':
                logger.error('show system reset reason is not proper after ISSU downgrade'
                             )
                res = 0
            else:
                logger.info('show system reset reason is proper after ISSU downgrade'
                            )
    elif device_type == 'EOR' and upgrade_type == 'upgrade':
        if out_dict:
            if upgrade_subtype == 'disruptive' and out_dict['TABLE_reason']['ROW_reason'][0]['TABLE_rr'
                    ]['ROW_rr'][0]['reason'] != 'Reset due to upgrade' :
                logger.error('show system reset reason is not proper after ISSU upgrade disruptive')
                res=0
            elif upgrade_subtype == 'nondisruptive' and out_dict['TABLE_reason']['ROW_reason'][0]['TABLE_rr'
                    ]['ROW_rr'][0]['reason'] \
                != 'Reset due to non-disruptive upgrade':
                logger.error('show system reset reason is not proper after ISSU upgrade'
                             )
                res = 0
            else:
                logger.info('show system reset reason is proper after ISSU upgrade'
                            )
    logger.info(banner('show install all time-stats verfication if upgrade is non-lxc'
                ))
    if upgrade_type == 'upgrade' and upgrade_subtype == 'nondisruptive' and issu_upgrade == 1 and lxc_issu \
        == 0:
        try:
            out = device.execute('sh install all time-stats',
                                 timeout=120)
        except:
            res = 0
            logger.error(traceback.format_exc())
        pattern = \
            re.compile('Total time taken between control plane being down and box online: (.*) seconds'
                       )
        if out:
            if re.search(pattern, out):
                cp_down_time = re.search(pattern, out).group(1)
                if int(cp_down_time) > 120:
                    logger.warning('cp downtime not proper post ISSU')
                    res = 0
                else:
                    logger.info('cp downtime is proper post ISSU')
            else:
                logger.warning('cp downtime info is not available, please check "sh install all time-stats" logs'
                               )
                res = 0
    if lxc_issu == 1:
        logger.info(banner('Check VSUP after LXC Upgrade'))
        try:
            mod_out = device.parse('show module')
        except:
            res = 0
            logger.error(traceback.format_exc())
        if 'upg' in img_name:
            if mod_out['slot']['rp']['28']['Virtual Supervisor Module'
                    ]['slot/world_wide_name'] == 'VSUP':
                logger.info('VSUP Validation after LXC Upgrade is PASSED'
                            )
            else:
                logger.error('VSUP Validation after LXC Upgrade is FAILED'
                             )
                res = 0
        else:
            if mod_out['slot']['rp']['27']['Virtual Supervisor Module'
                    ]['slot/world_wide_name'] == 'VSUP':
                logger.info('VSUP Validation after LXC Upgrade is PASSED'
                            )
            else:
                logger.error('VSUP Validation after LXC Upgrade is FAILED'
                             )
                res = 0
    return res

def trigger_epld_upgrade(
    logger,
    device,
    epld_command,
    epld_image
    ):
        dialog = \
           [r"Do you want to continue with the installation \(y\/n\)\?  \[n\]"
            , r"Do you want to save the configuration \(y\/n\)",
            r"Host kernel is not compatible with target image",
            r"Not enough memeory for Swithcover based ISSU",
            r"Running-config contains configuration that is incompatible with the new image",
            r"Do you want to continue \(y\/n\) \?  \[n\]"
            ]
        resp = ['y', 'y', 'None', 'None', 'None','y']

        try:
            output = execute_with_reply(device, epld_command, dialog,
                    resp, timeout=10000)
        except:
            logger.error(traceback.format_exc())
            logger.info('Sleep for 5 min')
            time.sleep(300)
            device.disconnect()
            device.connect()
            logger.error('Error encountered during epld upgrade: \n{}'.format(sys.exc_info()[0]))
            return 0
        logger.info('Verify epld status')
        out=device.execute('show install epld status')
        out_dict = device.api.get_config_dict(out)
        if list(out_dict.keys())[2]=='Status: EPLD Upgrade was Successful':
            logger.info('EPLD verification successfull')
        else:
            logger.error('EPLD verification is failed')
            return 0  

def trigger_issu(
    logger,
    device,
    issu_command,
    issu_image,
    issu_nondisruptive_fail=0,
    lxc_issu=0,
    ):

    dialog = \
        [r"Do you want to continue with the installation \(y\/n\)\?  \[n\]"
         , r"Do you want to save the configuration \(y\/n\)",
         r"Host kernel is not compatible with target image",
         r"Not enough memeory for Swithcover based ISSU",
         r"Running-config contains configuration that is incompatible with the new image"
         ]
    resp = ['y', 'y', 'None', 'None', 'None']
    dialog_nondisruptive_fail = \
        [r"Do you want to save the configuration \(y\/n\)",
         r"Switch will be reloaded for disruptive upgrade\..*\n do you want to continue with the installation \(y\/n\)\?  \[n\]"
         ,
         r"Do you want to continue with the installation \(y\/n\)\?  \[n\]"
         ]
    resp_nondisruptive_fail = ['y', 'n', 'n']
    if issu_nondisruptive_fail == 1:
        try:
            output = execute_with_reply(device, issu_command,
                    dialog_nondisruptive_fail, resp_nondisruptive_fail,
                    timeout=3000)
        except:
            logger.error(traceback.format_exc())
            logger.info('Sleep for 5 min')
            time.sleep(500)
            device.disconnect()
            try:
                device.connect(timeout=600)
            except:
                logger.error('Error encountered during install: \n{}'.format(sys.exc_info()[0]))
                return 0
    else:

        try:
            output = execute_with_reply(device, issu_command, dialog,
                    resp, timeout=3000)
        except:
            logger.error(traceback.format_exc())
            logger.info('Sleep for 5 min')
            time.sleep(500)
            device.disconnect()
            try:
                device.connect(timeout=600)
            except:
                logger.error('Error encountered during install: \n{}'.format(sys.exc_info()[0]))
                return 0
    fallback_issu = 0
    str1 = 'switch will reboot in 10 seconds.'
    str2 = 'Switching over onto standby'
    str3 = 'Install all currently is not supported'
    str4 = 'Switch is not ready for Install all yet'
    str5 = 'Rebooting the switch to proceed with the upgrade'
    str6 = 'Disruptive ISSU will be performed'
    str7 = 'Pre-upgrade check failed'
    str8 = \
        '"Running-config contains configuration that is incompatible with the new image'
    str9 = 'preupgrade check failed - Upgrade needs to be disruptive!'
    str10 = 'Install has been successful'
    str11 = 'Switch will be reloaded for disruptive upgrade.'
    str12 = \
        'Do you want to continue with the installation (y/n)?  [n] n'
    str13 = r"Host kernel is not compatible with target image"
    str14 = r"Not enough memory for Swithcover based ISSU"
    if (str1 in output or str2 in output or str5 in output or str10
        in output) and lxc_issu == 1 and (str13 in output or str14
            in output):
        logger.info('Install all Done and device logged in back,LXC Fallback Upgrade happened'
                    )
        return (1, 1)
    elif str1 in output or str2 in output or str5 in output or str10 \
        in output:
        logger.info('Install all Done and device logged in back')
        return (1, 0)
    elif str3 in output:
        logger.warning('Install all failed as currently not supported')
        return (0, 0)
    elif str4 in output:
        logger.warning('Install all failed as Switch is not ready for install all yet'
                       )
        return (0, 0)
    elif str6 in output:
        logger.warning('Non disruptive ISSU not supported')
        return (0, 0)
    elif (str7 or str8 in output) and str12 in output:
        logger.warning(r"Running-config contains configuration that is incompatible with the new image"
                       )
        logger.warning("Please run 'show incompatibility-all nxos <image>' command to find out which feature needs to be disabled."
                       )
        compatibility_cmd = 'show incompatibility-all nxos ' \
            + issu_image
        try:
            out = device.execute(compatibility_cmd, timeout=120)
        except:
            logger.error(traceback.format_exc())
        return (0, 0)
    elif str7 in output:
        logger.warning('Pre-upgrade check failed')
        return (0, 0)
    elif str11 in output:
        logger.warning('Pre-upgrade check failed, ISSU is supposed to be non-disruptive.Incompatible running configs,blocked disruptive ISSU'
                       )
        return (0, 0)
    elif str12 in output:
        logger.warning('Pre-upgrade check failed, ISSU is supposed to be non-disruptive.Incompatible running configs,blocked disruptive ISSU'
                       )
        return (0, 0)
    elif lxc_issu == 1 and (str13 in output or str14 in output):
        logger.info(banner('Fallback LXC ISSU happened'))
        fallback_issu = 1
        return (1, 1)
    else:
        logger.warning('Install all Command Failed')
        return (0, 0)


def trigger_verify_ISSU(
    logger,
    testbed,
    device,
    **kwargs
    ):

    res = 1
    try:
        issu_image = kwargs['issu_image']
    except:
        issu_image = ''
    try:
        issu_image_path = kwargs['issu_image_path']
    except:
        issu_image_path = ''
    try:
        issu_upgrade_type = kwargs['issu_upgrade_type']
    except:
        issu_upgrade_type = ''
    try:
        bios_down_grade = kwargs['bios_down_grade']
    except:
        bios_down_grade = ''
    try:
        issu_upgrade_subtype = kwargs['issu_upgrade_subtype']
    except:
        issu_upgrade_subtype = ''
    try:
        lxc_issu = kwargs['lxc_issu']
    except:
        lxc_issu = ''
    try:
        epld_upgrade = kwargs['epld_upgrade']
    except:
        epld_upgrade = ''
    if not issu_image or not issu_image_path or not issu_upgrade_type \
        or not issu_upgrade_subtype or lxc_issu == '' :
        logger.error('Mandatory parameters missing. issu_image,issu_image_path,issu_upgrade_type,issu_upgrade_subtype,lxc_issu info needed to proceed further'
                     )
        return 0
    if epld_upgrade:
        try:
            epld_image = kwargs['epld_image']
        except:
            epld_image = ''
        try:
            module_no = kwargs['module_no']
        except:
            module_no = ''
        if not epld_image or not module_no:
            logger.error('Mandatory parameters epld_image and module_no missing to proceed with epld upgrade.')
            return 0
    out = device.parse('show version')
    if out is not None:
        system_version = out['platform']['software']['system_version']
    match_pattern = \
        r"^([0-1]?[0-9]|2[0-3])\.([0-9]{1})\(([0-9]{1})\).*"
    match_pattern_64 = \
        r"^nxos64\.([0-1]?[0-9]|2[0-3])\.([0-9]{1})\(([0-9]{1})\).*"
    match = re.search(match_pattern, system_version)
    match_64 = re.search(match_pattern_64, system_version)
    if match:
        version_part1 = int(match.group(1))
        version_part2 = int(match.group(2))
        version_part3 = int(match.group(3))
    elif match_64:
        version_part1 = int(match_64.group(1))
        version_part2 = int(match_64.group(2))
        version_part3 = int(match_64.group(3))
    if version_part1 >= 10 and version_part2 \
        >= 1 or version_part3 >=2:
        upgrade_with_epld=1
    else:
        upgrade_with_epld=0
    current_image = device.api.get_running_image()
    logger.info(banner('Current image on device is %s' % current_image))
    compact_copy = 0
    compact_pids = ['N3K-C3132Q-40GX', 'N3K-C3064PQ-10GX',
                    'N3K-C3172PQ-10GE', 'N3K-C3548P-10G',
                    'N3K-C3548P-10GX']
    show_module = device.execute('show module')
    for pid in compact_pids:
        if pid in show_module:
            compact_copy = 1
            break
    use_kstack = 0
    sh_version = device.execute('show version')
    for out in sh_version.splitlines():
        if re.search('CPU.*with (\d+) kB of memory', out, re.I):
            match = re.search('CPU.*with (\d+) kB of memory', out, re.I)
            memory = match.group(1)
            if int(memory) < 5000000:
                use_kstack = 0
            else:
                use_kstack = 1
    logger.info(banner('copy issu_image %s to device' % issu_image))
    issu_image_withpath = issu_image_path + issu_image
    logger.info(issu_image)
    if device.api.verify_file_exists(issu_image) != True:
        if compact_copy == 0 and use_kstack == 0:
            try:
                device.api.copy_to_device(
                    issu_image_withpath,
                    'bootflash:',
                    testbed.servers.tftp['address'],
                    'scp',
                    timeout=2000,
                    vrf='management',
                    )
            except:
                logger.error(traceback.format_exc())
        elif compact_copy == 0 and use_kstack == 1:
            try:
                device.api.copy_to_device(
                    issu_image_withpath,
                    'bootflash:',
                    testbed.servers.tftp['address'],
                    'scp',
                    timeout=2000,
                    vrf='management',
                    use_kstack=True,
                    )
            except:
                logger.error(traceback.format_exc())
        elif compact_copy == 1:
            try:
                device.api.copy_to_device(
                    issu_image_withpath,
                    'bootflash:',
                    testbed.servers.tftp['address'],
                    'scp',
                    timeout=2000,
                    vrf='management',
                    compact=True,
                    )
            except:
                logger.error(traceback.format_exc())
    else:
        logger.info('Skipping copy image as it is already present in the box'
                    )
    if epld_upgrade==1:
        logger.info(banner('copy epld_image %s to device' % epld_image))
        try:
                    device.api.copy_to_device(
                         epld_image,
                        'bootflash:',
                         testbed.servers.tftp['address'],
                        'scp',
                        timeout=2000,
                        vrf='management'
                        )
        except:
                    logger.error(traceback.format_exc())
        epld_image_file=os.path.basename(epld_image)
        if device.api.verify_file_exists(epld_image_file) != True:
             logger.error('EPLD Image copy fails . Please check logs')
             return 0
    if device.api.verify_file_exists(issu_image) != True:
        logger.error('ISSU Image copy fails . Please check logs')

        return 0

        # res = 0

    logger.info(issu_upgrade_subtype)
    logger.info(banner('Start ISSU based on upgrade type : %s upgrade subtype : %s'
                 % (issu_upgrade_type, issu_upgrade_subtype)))
    logger.info(banner("Please run 'show incompatibility-all nxos <image>' command and fix if ICAM related configs issues available"
                ))
    compatibility_cmd = 'show incompatibility-all nxos ' + issu_image
    try:
        out = device.execute(compatibility_cmd, timeout=120)
    except:
        logger.error(traceback.format_exc())
    if re.search(r"Enable/Disable command : Deactivate iCAM using 'install deactivate icam' "
                 , out, re.I):
        logger.warning('Please remove icam configs from device')
        cmd = 'install deactivate icam'
        try:
            out = device.execute(cmd, timeout=60)
        except:
            logger.error(traceback.format_exc())
    boot_mode = ''
    logger.info('Check boot mode selected in device')
    try:
        boot = device.execute('show boot mode')
    except unicon.core.errors.SubCommandFailure as e:
        logger.warning(banner('LXC ISSU is not supported on current image/device'))
        logger.warning(traceback.format_exc())
        boot = 'Current mode is native'
    if 'Current mode is LXC' in boot:
        boot_mode = 'LXC'
    elif 'Current mode is native' in boot:

        # logger.info ('boot mode is already seleceted lxc in device, proceed with ISSU')

        boot_mode = 'native'
    if lxc_issu == 1:
        logger.info(banner('LXC ISSU selected by user'))
        if boot_mode == 'LXC':
            logger.info('boot mode set by user is lxc. Current Boot mode is already set lxc in device, proceed with ISSU'
                        )
        elif boot_mode == 'native':
            logger.info('boot mode set by user is lxc. Current Boot mode set in device is native , please change boot mode to lxc'
                        )
            lxc_boot_cmd = 'boot mode lxc'
            try:
                out = device.configure(lxc_boot_cmd, timeout=60)
            except:
                logger.error(traceback.format_exc())
            logger.info('save boot variables')
            try:
                device.api.execute_change_boot_variable(device.api.get_running_image()[0])
            except:
                logger.error(traceback.format_exc())
            device.execute('copy run start')
            device.api.execute_copy_run_to_start()
            credentials=device.tacacs['username']+' '+device.passwords['tacacs']
            device.api.execute_reload(prompt_recovery='true',
                    reload_creds=credentials, timeout=2000)
            boot = device.execute('sh boot mode')
            if 'Current mode is LXC' in boot:
                logger.info('Boot mode to LXC changed successfully')
            else:
                logger.error('Boot mode to LXC not successful, Test failed'
                             )
                return 0
    elif lxc_issu == 0:
        logger.info(banner('Native mode ISSU selected by user, disable lxc mode if enabled in device'
                    ))
        if boot_mode == 'native':
            logger.info('boot mode set by user is native. Native boot mode is already set in device, proceed with ISSU'
                        )
        elif boot_mode == 'LXC':
            logger.info('boot mode set by user is native. Current Boot mode set in device is lxc, please change boot mode to native'
                        )
            lxc_boot_cmd = 'no boot mode lxc'
            try:
                out = device.configure(lxc_boot_cmd, timeout=60)
            except:
                logger.error(traceback.format_exc())
            logger.info('save boot variables')
            try:
                device.api.execute_change_boot_variable(device.api.get_running_image()[0])
            except:
                logger.error(traceback.format_exc())
            device.execute('copy run start')
            device.api.execute_copy_run_to_start()
            credentials=device.tacacs['username']+' '+device.passwords['tacacs']
            device.api.execute_reload(prompt_recovery='true',
                    reload_creds=credentials, timeout=2000)
            boot = device.execute('sh boot mode')
            if 'Current mode is native' in boot:
                logger.info('Boot mode to native changed successfully')
            else:
                logger.error('Boot mode to native not successful, Test failed'
                             )
                return 0
    issu_nondisruptive_fail = 0
    if issu_upgrade_type == 'upgrade' and issu_upgrade_subtype \
        == 'nondisruptive':
        issu_command = 'install all nxos bootflash:' + issu_image \
            + ' non-disruptive'
        logger.info('ISSU command is %s' % issu_command)
        logger.info(banner('Verify show spanning-tree issu-impact'))
        cmd = 'show spanning-tree issu-impact'
        try:
            out = device.execute(cmd, timeout=2000)
        except:
            logger.error(traceback.format_exc())
            res = 0
        if re.search(r'ISSU Cannot Proceed', out, re.I):
            logger.error(banner('show spanning-tree issu-impact failed'
                         ))
            issu_nondisruptive_fail = 1
        logger.info(banner('Verify show incompatibility issu image'))
        cmd = 'show incompatibility-all nxos ' + issu_image
        try:
            out = device.execute(cmd, timeout=2000)
        except:
            logger.error(traceback.format_exc())
            res = 0
        if re.search(r'The following configurations on active are incompatible with the system image'
                     , out, re.I):
            logger.error(banner('show  incompatibility-all nxos failed'
                         ))
            issu_nondisruptive_fail = 1
        impact_cmd = 'show install all impact nxos ' + issu_image + ' non-disruptive'
        try:
            impact_out = device.execute(impact_cmd, timeout=2000)
        except:
            logger.error(traceback.format_exc())
            res = 0
        match_pattern='.*([0-9]?[0-9]|2[0-3]).*disruptive.*'
        if 'non-disruptive' not in re.search(match_pattern, impact_out, re.I).group():
            logger.error(banner('show  incompatibility-all nxos failed'
                         ))
            issu_nondisruptive_fail = 1
        time.sleep(60)
    elif issu_upgrade_type == 'upgrade' and issu_upgrade_subtype \
        == 'disruptive' and epld_upgrade==1 and upgrade_with_epld==1:
        issu_command = 'install all epld '+epld_image_file+' nxos bootflash:' + issu_image
    elif issu_upgrade_type == 'upgrade' and issu_upgrade_subtype \
        == 'disruptive' and epld_upgrade==1 and upgrade_with_epld==0:
        issu_command = 'install all nxos bootflash:' + issu_image
        epld_command = 'install epld '+epld_image_file+' module '+module_no
    elif issu_upgrade_type == 'upgrade' and issu_upgrade_subtype \
        == 'disruptive':
        issu_command = 'install all nxos bootflash:' + issu_image
            # + ' disruptive'
        logger.info('ISSU command is %s' % issu_command)
        logger.info(banner('Verify show incompatibility issu image'))
        cmd = 'show incompatibility-all nxos ' + issu_image
        try:
            out = device.execute(cmd, timeout=120)
        except:
            logger.error(traceback.format_exc())
            res = 0
    elif issu_upgrade_type == 'downgrade' and bios_down_grade == 1:
        issu_command = 'install all nxos bootflash:' + issu_image \
            + ' bios-force'
        logger.info('ISSU command is %s' % issu_command)
        logger.info(banner('Write erase reload needed for ISSU Downgrade type'
                    ))
        logger.info('save boot variables')
        device.api.execute_change_boot_variable(device.api.get_running_image()[0])
        device.api.execute_copy_run_to_start()
        credentials=device.tacacs['username']+' '+device.passwords['tacacs']
        device.api.execute_reload(prompt_recovery='true',
                                  reload_creds=credentials,
                                  timeout=600)
    else:
        if epld_upgrade==1 and upgrade_with_epld==1:
            issu_command = 'install all epld '+epld_image_file+' nxos bootflash:' + issu_image
        elif epld_upgrade==1 and upgrade_with_epld==0:
            issu_command = 'install all nxos bootflash:' + issu_image
            epld_command = 'install epld '+epld_image_file+' module '+module_no
        else:
            issu_command = 'install all nxos bootflash:' + issu_image
        logger.info('ISSU command is %s' % issu_command)
        logger.info(banner('Verify show incompatibility issu image'))
        cmd = 'show incompatibility-all nxos ' + issu_image
        try:
            out = device.execute(cmd, timeout=120)
        except:
            logger.error(traceback.format_exc())
            res = 0
#        logger.info(banner('Write erase reload needed for ISSU Downgrade type'
#                    ))
#
#        logger.info('save boot variables')
#        try:
#            device.api.execute_change_boot_variable(device.api.get_running_image()[0])
#        except:
#            result = 0
#            logger.error(traceback.format_exc())
#        try:
#            device.api.execute_copy_run_to_start()
#        except:
#            logger.error(traceback.format_exc())
#            result = 0
#        try:
#            device.api.write_erase_reload_device_without_reconfig('a' ,reload_timeout=180)
#        except:
#            logger.error(traceback.format_exc())
#            result=0

    result = 1
    logger.info('trigger ISSU')
    (trigger_issu_result, fallback_lxc) = trigger_issu(
        logger,
        device,
        issu_command,
        issu_image,
        issu_nondisruptive_fail=issu_nondisruptive_fail,
        lxc_issu=lxc_issu,
        )
    if not trigger_issu_result:
        logger.error('ISSU not successful on device %s', device.name)
        return trigger_issu_result
    logger.info('sleep for 10 mins waiting for Active Sup up')
    time.sleep(720)
    validate_issu_result = validate_issu(
        logger,
        device,
        issu_image,
        issu_upgrade_type,
        issu_upgrade_subtype,
        lxc_issu,
        )
    if epld_upgrade==1 and upgrade_with_epld==0:
        logger.info(banner('Trigger epld'))
        epld_res=trigger_epld_upgrade(logger,device,epld_command,epld_image_file)
        if epld_res==0:
            logger.error('epld upgrade is not successfull')
            result=0
        else:
            logger.info(banner('epld upgrade is successfull'))
    if trigger_issu_result == 1 and lxc_issu == 1 and fallback_lxc == 1 \
        and validate_issu_result == 1:
        logger.info(banner('Please collect control plane downtime stats after completing the fallback LXC ISSU'
                    ))
        match_pattern = \
            r"^nxos\.([0-1]?[0-9]|2[0-3])\.([0-9]{1})\.([0-9]{1}).*"
        match_pattern_64 = \
            r"^nxos64\.([0-1]?[0-9]|2[0-3])\.([0-9]{1})\.([0-9]{1}).*"
        match = re.search(match_pattern, issu_image)
        match_64 = re.search(match_pattern_64, issu_image)
        if match:
            version_part1 = int(match.group(1))
        elif match_64:
            version_part1 = int(match_64.group(1))
        else:
            logger.error (banner('ISSU image pattern not matching standard format, cp downtime info not available'))
            
        if version_part1 < 10:
            with device.bash_console() as bash:
                try:
                    output1 = \
                        bash.execute('/isan/bin/python /isan/python/scripts/issu_stats.py'
                            )
                    logger.warning(output1)
                except:
                    result = 0
                    logger.error(traceback.format_exc())
        elif version_part1 >= 10:
            with device.bash_console() as bash:
                try:
                    output1 = \
                        bash.execute('/isan/bin/python3 /isan/python3/scripts/issu_stats.py'
                            )
                    logger.warning(output1)
                except:
                    result = 0
                    logger.error(traceback.format_exc())
#    else:
#        logger.info(banner('ISSU/ISSU Validation not successfull, control plane downtime stats after completing the fallback LXC ISSU will not be collected'
#                    ))
    if validate_issu_result == 0:
        result = 0
        logger.error('ISSU Validation not successful on device %s',
                     device.name)
    else:
        logger.info('ISSU Validation successful on device %s',
                    device.name)
    return result
