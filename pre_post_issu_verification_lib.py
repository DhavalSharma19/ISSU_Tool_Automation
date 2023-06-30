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


def device_config_verification_pre_post_issu(
    logger,
    testscript,
    testbed,
    pre_issu_verification=None,
    post_issu_verification=None,
    ):
    """ pre/post issu verifications  """

    res = 1

############################ Pre Upgrade Verification ##########################

    if pre_issu_verification is not None:
        
        for devvice in testbed.devices:
            if testscript.parameters["genie_testbed"].devices[devvice].os == "nxos":
                try:
                    device = testbed.devices[devvice]
                except KeyError:
                    logger.error('device alias to be configured: " %s " is not defined in testbedyaml file'
                                % devvice)
                    return 0
                
                verification_lists = ['show_cdp','syslog_check','mts_check','check_core']
                logger.info(verification_lists)
            
                logger.info(banner('Core Check pre upgrade'))
                ret = generic_utils.core_check(device, logger)
                if ret == 0:
                    logger.error('Crash/Core Found pre upgrade!!!!')
                    res = 0
                else:
                    logger.info('NO Crash/Core Found pre upgrade')
            
                logger.info(banner('MTS Status Verification pre upgrade'
                            ))
                ret = generic_utils.mts_leak_verification(logger,
                        device)
                if ret == 0:
                    logger.error('MTS Check Status verification Failed'
                                )
                    res = 0
                else:
                    logger.info('MTS Check Status Verification successful'
                                )
            
                logger.info(banner('Syslog Verification pre upgrade'
                            ))
                ret = generic_utils.verify_syslogs(logger,
                        device)
                if ret == 0:
                    logger.error('Syslog Verification Failed'
                                )
                    res = 0
                else:
                    logger.info('Syslog Verification successful'
                                )
            
                logger.info(banner('Show cdp Verification pre upgrade'
                            ))
                ret = generic_utils.show_cdp(logger,
                        device)
                if ret == 0:
                    logger.error('Show cdp Verification pre upgrade Failed'
                                )
                    res = 0
                else:
                    logger.info('Show cdp Verification successful'
                                )

######################## Post Upgrade Verification #########################################

    if post_issu_verification is not None:
        
        for devvice in testbed.devices:
            if testscript.parameters["genie_testbed"].devices[devvice].os == "nxos":
                try:
                    device = testbed.devices[devvice]
                except KeyError:
                    logger.error('device alias to be configured: " %s " is not defined in testbedyaml file'
                                % devvice)
                    return 0

                verification_lists = ['show_cdp','syslog_check','mts_check','check_core']
                logger.info(verification_lists)

                logger.info(banner('Core Check post upgrade'))
                ret = generic_utils.core_check(device, logger)
                if ret == 0:
                    logger.error('Crash/Core Found post upgrade!!!!')
                    res = 0
                else:
                    logger.info('NO Crash/Core Found post upgrade')

                logger.info(banner('MTS Status Verification post upgrade'
                            ))
                ret = generic_utils.mts_leak_verification(logger,
                        device)
                if ret == 0:
                    logger.error('MTS Check Status verification Failed'
                                )
                    res = 0
                else:
                    logger.info('MTS Check Status Verification successful'
                                )
                
                logger.info(banner('Syslog Verification post upgrade'
                            ))
                ret = generic_utils.verify_syslogs(logger,
                        device)
                if ret == 0:
                    logger.error('Syslog Verification Failed'
                                )
                    res = 0
                else:
                    logger.info('Syslog Verification successful'
                                )
            
                logger.info(banner('Show cdp Verification post upgrade'
                            ))
                ret = generic_utils.show_cdp(logger,
                        device)
                if ret == 0:
                    logger.error('Show cdp Verification post upgrade Failed'
                                )
                    res = 0
                else:
                    logger.info('Show cdp Verification successful'
                                ) 
    return res
