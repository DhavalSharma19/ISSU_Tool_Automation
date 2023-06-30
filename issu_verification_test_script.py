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
import sys
import pdb


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
import tgn_spirent
import generic_utils
import device_config_lib
import traffic_config_lib
import pre_post_issu_verification_lib



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



###################################################################
#                  COMMON SETUP SECTION                           #
###################################################################

# Configure and setup all devices and test equipment in this section.



class common_setup(aetest.CommonSetup):

    """ Common Setup """
    uid = "common_setup"


    @aetest.subsection
    def initialize_logging(self, testscript):
        """ Common setup section to initialize logging for script"""

        global logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        testscript.parameters["logger"] = logger



    @aetest.subsection
    def connect_devices(
        self,
        logger,
        testscript,
        testbed,
    ):

        """ fetch all required devices, interfaces  """

        global uut1_spirent_1,spirent_uut1_1,uut1_spirent_2,spirent_uut1_2
        
        uut1_spirent_1 = testbed.devices['ELY_104'].interfaces['uut1_spirent_1']
        testscript.parameters['uut1_spirent_1'] = uut1_spirent_1
        testscript.parameters['uut1_spirent_1'].name = testscript.parameters['uut1_spirent_1'].intf

        uut1_spirent_2 = testbed.devices['ELY_104'].interfaces['uut1_spirent_2']
        testscript.parameters['uut1_spirent_2'] = uut1_spirent_2
        testscript.parameters['uut1_spirent_2'].name = testscript.parameters['uut1_spirent_2'].intf

        spirent_uut1_1 = testbed.devices['spirent'].interfaces['spirent_uut1_1']
        testscript.parameters['spirent_uut1_1'] = spirent_uut1_1
        testscript.parameters['spirent_uut1_1'].name = testscript.parameters['spirent_uut1_1'].intf

        spirent_uut1_2 = testbed.devices['spirent'].interfaces['spirent_uut1_2']
        testscript.parameters['spirent_uut1_2'] = spirent_uut1_2
        testscript.parameters['spirent_uut1_2'].name = testscript.parameters['spirent_uut1_2'].intf

        uut1_spirent_1 = uut1_spirent_1.intf
        uut1_spirent_2 = uut1_spirent_2.intf
        spirent_uut1_1 = spirent_uut1_1.intf
        spirent_uut1_2 = spirent_uut1_2.intf

        logger.info(banner("Fetch device object"))
        testscript.parameters["genie_testbed"] = Genie.init(testbed=testbed)
        for device in testbed.devices:
            if testscript.parameters["genie_testbed"].devices[device].os == "nxos":
                try:

                    testscript.parameters["genie_testbed"].devices[device].connect(timeout=600)
                except:
                    testscript.parameters["logger"].error(
                        banner("Device connection is not successful")
                    )
                    self.errored(traceback.format_exc())



    @aetest.subsection
    def common_device_config(
        self,
        logger,
        testscript,
        testbed,
    ):
        """ fetch all required devices, interfaces  """
        res = 1
        logger.info(banner("Fetch device object"))
        testscript.parameters["genie_testbed"] = Genie.init(testbed=testbed)
        for device in testbed.devices:
            if testscript.parameters["genie_testbed"].devices[device].type == "nxos":
                try:
                    testscript.parameters["genie_testbed"].devices[device].configure(
                        "feature bash-shell"
                    )
                except:
                    logger.error(traceback.format_exc())
                    res = 0
        if res == 1:
            logger.info("Common device config is successful")
        else:
            logger.error("Common device config is not successful")
        logger.info(banner("Save device configuration"))
        for device in testscript.parameters["genie_testbed"].devices:
            if testscript.parameters["genie_testbed"].devices[device].type == "nxos":
                testscript.parameters["genie_testbed"].devices[device].execute(
                    "copy run start"
                )



    @aetest.subsection
    def get_issu_matrix(
        self,
        testbed,
        testscript,
        issu_matrix_file,
        logger,
    ):
        
        """ Get ISSU Matrix from user input CSV file path"""
        try:
            with open("%s" % issu_matrix_file) as f:
                issu_data = f.read().splitlines()
                issu_data_header=issu_data[0]
                issu_data = issu_data[1:]
        except:
            self.errored("ISSU Matrix file not defined!")
        # Generate ISSU Matrix
        testscript.parameters['enable_epld_upgrade']=''
        issu_mat = collections.OrderedDict()
        if len(issu_data_header.split(","))>6:
            if issu_data_header.split(",")[6]=='EPLD_UPGRADE':
                testscript.parameters['enable_epld_upgrade']=1
        else:
            testscript.parameters['enable_epld_upgrade']=0
        logger.info(testscript.parameters['enable_epld_upgrade'])
        if testscript.parameters['enable_epld_upgrade']==1:
            for line in issu_data:
                logger.info(line)
                logger.info(len(line.split(",")))
                if len(line.split(",")) < 9:
                    self.errored("FormatError: Please check issu_matrix file format")
                switch_alias = line.split(",")[0]
                to_image = line.split(",")[1]
                to_image_path = line.split(",")[2]
                upgrade_type = line.split(",")[3]
                upgrade_subtype = line.split(",")[4]
                lxc_issu = line.split(",")[5]
                epld_upgrade = line.split(",")[6]
                if int(epld_upgrade)==1:
                    epld_image = line.split(",")[7]
                    module_no = line.split(",")[8]
                if switch_alias not in testbed.devices:
                    self.errored("DeviceNotFound: Please check issu_matrix file")
                switch_name = testbed.devices[switch_alias].name
                if switch_name in issu_mat.keys():
                    issu_mat[switch_name].append(
                        {
                        "to": to_image,
                        "to_path": to_image_path,
                        "upgrade_type": upgrade_type,
                        "upgrade_subtype": upgrade_subtype,
                        "lxc_issu": lxc_issu,
                        "epld_upgrade":epld_upgrade,
                        "epld_image": epld_image,
                        "module_no": module_no
                        }
                    )
                else:
                    issu_mat[switch_name] = []
                    issu_mat[switch_name].append(
                        {
                        "to": to_image,
                        "to_path": to_image_path,
                        "upgrade_type": upgrade_type,
                        "upgrade_subtype": upgrade_subtype,
                        "lxc_issu": lxc_issu,
                        "epld_upgrade":epld_upgrade,
                        "epld_image": epld_image,
                        "module_no": module_no
                        }
                    )
        elif testscript.parameters['enable_epld_upgrade']==0:
            for line in issu_data:
                logger.info(line)
                logger.info(len(line.split(",")))
                if len(line.split(",")) < 6:
                    self.errored("FormatError: Please check issu_matrix file format")
                switch_alias = line.split(",")[0]
                to_image = line.split(",")[1]
                to_image_path = line.split(",")[2]
                upgrade_type = line.split(",")[3]
                upgrade_subtype = line.split(",")[4]
                lxc_issu = line.split(",")[5]
                if switch_alias not in testbed.devices:
                    self.errored("DeviceNotFound: Please check issu_matrix file")
                switch_name = testbed.devices[switch_alias].name
                if switch_name in issu_mat.keys():
                    issu_mat[switch_name].append(
                        {
                        "to": to_image,
                        "to_path": to_image_path,
                        "upgrade_type": upgrade_type,
                        "upgrade_subtype": upgrade_subtype,
                        "lxc_issu": lxc_issu,
                        }
                    )
                else:
                    issu_mat[switch_name] = []
                    issu_mat[switch_name].append(
                        {
                        "to": to_image,
                        "to_path": to_image_path,
                        "upgrade_type": upgrade_type,
                        "upgrade_subtype": upgrade_subtype,
                        "lxc_issu": lxc_issu,
                        }
                     )
        logger.info("ISSU Matrix = ")
        logger.info(issu_mat)
        pprint.pprint(issu_mat)
        testscript.parameters["issu_matrix"] = issu_mat
        testscript.parameters["device_list"] = []
        for device in testscript.parameters["issu_matrix"].keys():
            testscript.parameters["device_list"].append(device)



###################################################################
##                  Test  SECTION                                 #
###################################################################
#



class ISSU_TEST(aetest.Testcase):

    uid = "issu_test"


    @aetest.setup
    def device_configuration(
        self,
        logger,
        testscript,
        steps,
        device_config_flag=None,
        feature_wise_config_flag=None,
        template_dir=None,
        enable_features=None,
        breakout_config=None,
        interface_config=None,
        ospf_config=None,
        l3_physical_intf_config=None,
    ):
        """ device configurations  """

        logger.info(device_config_flag)
        fail_flag = 0
        logger.info(banner("Configure devices"))
        dev_list = []
        for device in testscript.parameters["genie_testbed"].devices:
            if testscript.parameters["genie_testbed"].devices[device].type == "nxos":
                dev_list.append(testscript.parameters["genie_testbed"].devices[device])
        config_result = device_config_lib.device_configuration(
            logger,
            testscript.parameters["genie_testbed"],
            steps,
            template_dir,
            device_config_flag,
            feature_wise_config_flag,
            enable_features,
            breakout_config,
            interface_config,
            ospf_config,
            l3_physical_intf_config,
        )
        if config_result:
            logger.info(banner("device Configuration successful"))
        else:
            logger.error(banner("device Configuration failed"))
            self.failed()
        logger.info(banner("Save device configuration"))
        for device in testscript.parameters["genie_testbed"].devices:
            if testscript.parameters["genie_testbed"].devices[device].type == "nxos":
                testscript.parameters["genie_testbed"].devices[device].execute(
                    "copy run start"
                )



    @aetest.test
    def connect_configure_traffic(
        self,
        logger,
        testscript,
        traffic_config_flag=None,
        tgn_config=None,
    ):
        """ traffic configurations  """

        fail_flag = 0
        logger.info(
            banner(
                "Create tgn class object passing all tgn details available in data file"
            )
        )
        testscript.parameters['tgn_config_flag']=1
        testscript.parameters['tgn_run_flag']=1
        if traffic_config_flag == 1:
            tgn_config_obj = traffic_config_lib.tgnConfig(
                logger,
                testscript.parameters["genie_testbed"],
                tgn_config,
                int_config=1,
                traf_config=1,
            )
            logger.info(banner("tgn_config_class_object is : %s " % (tgn_config_obj)))

            logger.info(
            banner(
                "Connect and Configure traffic, script will connect ixia,configure tgn interface, configure traffic "
                )
            ) 
            (
                testscript.parameters["tgn_obj"],
                testscript.parameters["tgn_streams_list"],
            ) = tgn_config_obj.tgn_Connect_Interface_Traffic_Config()
            logger.info(
                banner(
                    "tgn port handle and respective traffic stream dict returned is : %s "
                    % (testscript.parameters["tgn_streams_list"])
                )
            )
            logger.info(
                banner("tgn object handle is : %s " % (testscript.parameters["tgn_obj"]))
            )
            if (
                testscript.parameters["tgn_obj"] is not None
                and testscript.parameters["tgn_streams_list"] is not None
            ):
                logger.info(banner("TGN traffic configuration passed"))
            else:
                logger.error(banner("TGN traffic configuration failed"))
                testscript.parameters['tgn_config_flag']=0
                testscript.parameters['tgn_run_flag']=0
                self.failed()

            logger.info(banner("Start Traffic"))
            ## input to run traffic:-- porthandle_stream dictionary,should be in this format.{'ixia-intf-1': 'TI0-Streamblock1'}
            if tgn_config['type']== 'ixia':
                for tgn_intf_hdl in testscript.parameters["tgn_streams_list"].keys():
                    logger.info("tgn interface handle is : %s " % (tgn_intf_hdl))
                    tgn_port_hdl = (
                        testscript.parameters["genie_testbed"]
                        .devices[tgn_config["tgn"]]
                        .interfaces[tgn_intf_hdl]
                        .name
                    )
                    logger.info(
                        "tgn port handle fetched from testbed yaml is : %s " % (tgn_port_hdl)
                    )
                    logger.info(banner("Create tgn start stop traffic class object"))
                    testscript.parameters[
                        "tgn_start_stop_traffic_obj"
                    ] = traffic_config_lib.tgnStartStopTraffic(
                        logger,
                        testscript.parameters["genie_testbed"],
                        tgn_config,
                        testscript.parameters["tgn_obj"],
                        tgn_port_hdl,
                        testscript.parameters["tgn_streams_list"][tgn_intf_hdl],
                        int_config=0,
                        traf_config=0,
                    )
                    logger.info(
                        banner(
                            "tgn_start_stop_traffic_obj is : %s "
                            % (testscript.parameters["tgn_start_stop_traffic_obj"])
                        )
                    )
                    tgn_traffic_control = testscript.parameters[
                        "tgn_start_stop_traffic_obj"
                    ].tgn_Start_Traffic()
                    sleep(30)
                    if tgn_traffic_control is not None:
                        logger.info(banner("TGN start traffic passed"))
                    else:
                        logger.error(banner("TGN start traffic failed"))
                        testscript.parameters['tgn_config_flag']=0
                        testscript.parameters['tgn_run_flag']=0
                        self.failed()
                    logger.info("Run traffic status is : %s" % (tgn_traffic_control))
            elif tgn_config['type']== 'spirent':
                for tgn_intf_hdl in testscript.parameters["tgn_streams_list"].keys():
                    logger.info("tgn interface handle is : %s " % (tgn_intf_hdl))
                    tgn_port_hdl=tgn_intf_hdl
                    logger.info(
                        "tgn port handle fetched from testbed yaml is : %s " % (tgn_port_hdl)
                    )
                    logger.info(banner("Create tgn start stop traffic class object"))
                    
                    testscript.parameters[
                        "tgn_start_stop_traffic_obj"
                    ] = traffic_config_lib.tgnStartStopTraffic(
                        logger,
                        testscript,
                        testscript.parameters["genie_testbed"],
                        tgn_config,
                        testscript.parameters["tgn_obj"],
                        tgn_port_hdl,
                        testscript.parameters["tgn_streams_list"][tgn_intf_hdl],
                        int_config=0,
                        traf_config=0,
                    )

                    logger.info(
                        banner(
                            "tgn_start_stop_traffic_obj is : %s "
                            % (testscript.parameters["tgn_start_stop_traffic_obj"])
                        )
                    )

                    tgn_traffic_control = testscript.parameters[
                        "tgn_start_stop_traffic_obj"
                    ].tgn_Start_Traffic()
                    sleep(30)
                    if tgn_traffic_control is not None:
                        logger.info(banner("TGN start traffic passed"))
                    else:
                        logger.error(banner("TGN start traffic failed"))
                        testscript.parameters['tgn_config_flag']=0
                        testscript.parameters['tgn_run_flag']=0
                        self.failed()

            logger.info(banner("Get Traffic stats/ Verify traffic loss"))
            ## input to check traffic stats:-- porthandle_stream dictionary,should be in this format.{'ixia-intf-1': 'TI0-Streamblock1'}
            if tgn_config['type']== 'ixia':
                for tgn_intf_hdl in testscript.parameters["tgn_streams_list"].keys():
                    logger.info("tgn interface handle is : %s " % (tgn_intf_hdl))
                    tgn_port_hdl = (
                        testscript.parameters["genie_testbed"]
                        .devices[tgn_config["tgn"]]
                        .interfaces[tgn_intf_hdl]
                        .name
                    )
                    logger.info(
                        "tgn port handle fetched from testbed yaml is : %s " % (tgn_port_hdl)
                    )
                    logger.info(banner("Create tgn start stop traffic class object"))
                    testscript.parameters[
                        "tgn_start_stop_traffic_obj"
                    ] = traffic_config_lib.tgnStartStopTraffic(
                        logger,
                        testscript.parameters["genie_testbed"],
                        tgn_config,
                        testscript.parameters["tgn_obj"],
                        tgn_port_hdl,
                        testscript.parameters["tgn_streams_list"][tgn_intf_hdl],
                        int_config=0,
                        traf_config=0,
                    )
                    logger.info(
                        banner(
                            "tgn_start_stop_traffic_obj is : %s "
                            % (testscript.parameters["tgn_start_stop_traffic_obj"])
                        )
                    )
                    tgn_traffic_loss = testscript.parameters[
                        "tgn_start_stop_traffic_obj"
                    ].getTrafficPacketLoss()
                    if tgn_traffic_loss is not None:
                        logger.info(banner("TGN stats verification passed"))
                    else:
                        logger.error(banner("TGN stats verification failed"))
                        testscript.parameters['tgn_config_flag']=0
                        testscript.parameters['tgn_run_flag']=0
                        self.failed()
            elif tgn_config['type']== 'spirent':
                for tgn_intf_hdl in testscript.parameters["tgn_streams_list"].keys():
                    logger.info("tgn interface handle is : %s " % (tgn_intf_hdl))
                    tgn_port_hdl=tgn_intf_hdl
                    logger.info(
                        "tgn port handle fetched from testbed yaml is : %s " % (tgn_port_hdl)
                    )
                    logger.info(banner("Create tgn start stop traffic class object"))
                    testscript.parameters[
                        "tgn_start_stop_traffic_obj"
                    ] = traffic_config_lib.tgnStartStopTraffic(
                        logger,
                        testscript,
                        testscript.parameters["genie_testbed"],
                        tgn_config,
                        testscript.parameters["tgn_obj"],
                        tgn_port_hdl,
                        testscript.parameters["tgn_streams_list"][tgn_intf_hdl],
                        int_config=0,
                        traf_config=0,
                    )
                    logger.info(
                        banner(
                            "tgn_start_stop_traffic_obj is : %s "
                            % (testscript.parameters["tgn_start_stop_traffic_obj"])
                        )
                    )
                    tgn_traffic_loss = testscript.parameters[
                        "tgn_start_stop_traffic_obj"
                    ].getTrafficPacketLoss()
                    if tgn_traffic_loss is not None:
                        logger.info(banner("TGN stats verification passed"))
                    else:
                        logger.error(banner("TGN stats verification failed"))
                        testscript.parameters['tgn_config_flag']=0
                        testscript.parameters['tgn_run_flag']=0
                        self.failed()

        else:
            logger.info(banner('traffic is already configured,up and running, proceed with ISSU/ISSD'
                        ))

    @aetest.test
    def trigger_issu_verify(
        self,
        testbed,
        testscript,
        logger,
        template_dir,
        device_config_flag,
        steps,
        feature_wise_config_flag,
        verify_traffic_post_upgrade,
        start_traffic_post_upgrade,
        pre_issu_verification=None,
        post_issu_verification=None,
    ):

        logger.info(
            "loop through device details mentioned in ISSU matrix and start ISSU process"
        )
        fail_flag = 0
        is_looping = True
        for device in testscript.parameters["issu_matrix"].keys():
            for value in range(len(testscript.parameters["issu_matrix"][device])):
                logger.info(value)
                issu_image = testscript.parameters["issu_matrix"][device][value]["to"]
                issu_image_path = testscript.parameters["issu_matrix"][device][value][
                    "to_path"
                ]
                issu_upgrade_type = testscript.parameters["issu_matrix"][device][value][
                    "upgrade_type"
                ]
                issu_upgrade_subtype = testscript.parameters["issu_matrix"][device][
                    value
                ]["upgrade_subtype"]
                lxc_issu = testscript.parameters["issu_matrix"][device][value][
                    "lxc_issu"
                ]
                if testscript.parameters['enable_epld_upgrade']==1:
                    epld_upgrade = testscript.parameters["issu_matrix"][device][value]["epld_upgrade"] 
                    epld_image = testscript.parameters["issu_matrix"][device][value][
                        "epld_image"
                    ]
                    module_no = testscript.parameters["issu_matrix"][device][value][
                    "module_no"
                    ]
                logger.info("Make sure icam is enabled for 9.3(5) above releases")
                res = generic_utils.enable_icam(
                    logger, testscript.parameters["genie_testbed"].devices[device]
                )
                if res != 1:
                    logger.error("Activate icam is not successful")
                    fail_flag = 0
                else:
                    logger.info("Activate icam is successful")
                logger.info(
                    "ISSU test for device: %s , image: %s, image_path: %s, upgrade_type: %s,upgrade_subtype: %s ,lxc_issu: %s"
                    % (
                        device,
                        issu_image,
                        issu_image_path,
                        issu_upgrade_type,
                        issu_upgrade_subtype,
                        lxc_issu
                    )
                )
                
                if pre_post_issu_verification_lib.device_config_verification_pre_post_issu(
                    logger,
                    testscript,
                    testscript.parameters["genie_testbed"],
                    pre_issu_verification = 1,
                ):
                    logger.info(
                        "Pre ISSU verification succesfull for image: %s on device: %s"
                        % (issu_image, device)
                    )
                else:
                    logger.error(
                        "Pre ISSU verification is not succesfull for image: %s on device: %s"
                        % (issu_image, device)
                    )

                    fail_flag = 1

                logger.info("Pre Running config snapshot")
                pre_running_config = (
                    testscript.parameters["genie_testbed"]
                    .devices[device]
                    .api.get_running_config_dict()
                )
                if testscript.parameters['enable_epld_upgrade']==1:
                    issu_res = generic_utils.trigger_verify_ISSU(
                    logger,
                    testscript.parameters["genie_testbed"],
                    testscript.parameters["genie_testbed"].devices[device],
                    issu_image=issu_image,
                    issu_image_path=issu_image_path,
                    issu_upgrade_type=issu_upgrade_type,
                    issu_upgrade_subtype=issu_upgrade_subtype,
                    lxc_issu=int(lxc_issu),
                    epld_upgrade=int(epld_upgrade),
                    epld_image=epld_image,
                    module_no=module_no,

                )
                elif testscript.parameters['enable_epld_upgrade']==0:
                    issu_res = generic_utils.trigger_verify_ISSU(
                        logger,
                        testscript.parameters["genie_testbed"],
                        testscript.parameters["genie_testbed"].devices[device],
                        issu_image=issu_image,
                        issu_image_path=issu_image_path,
                        issu_upgrade_type=issu_upgrade_type,
                        issu_upgrade_subtype=issu_upgrade_subtype,
                        lxc_issu=int(lxc_issu),
                        epld_upgrade=0,
                    )
                if issu_res == 0:
                    logger.error(
                        banner(
                            "ISSU Failed for image: %s on device: %s. Can't proceed further"
                            % (issu_image, device)
                        )
                    )
                    fail_flag = 1
                    is_looping = False
                    break
                else:
                    logger.info(
                        banner(
                            "ISSU Successfull for image: %s on device: %s"
                            % (issu_image, device)
                        )
                    )
                    logger.info(
                        banner(
                            'Validate traffic post ISSU/ISSD if "verify_traffic_post_upgrade" flag set to 1 in data file'
                        )
                    )

                    ## input to check traffic stats:-- porthandle_stream dictionary,should be in this format.{'ixia-intf-1': 'TI0-Streamblock1'}
                    
                    if verify_traffic_post_upgrade == 1 and testscript.parameters['tgn_config_flag']==1 and testscript.parameters['tgn_run_flag']==1:
                        if testscript.parameters['tgn_config']['type']== 'ixia':
                            for tgn_intf_hdl in testscript.parameters["tgn_streams_list"].keys():
                                logger.info(
                                    "tgn interface handle is : %s " % (tgn_intf_hdl)
                                )
                                tgn_port_hdl = (
                                    testscript.parameters["genie_testbed"]
                                    .devices[tgn_config["tgn"]]
                                    .interfaces[tgn_intf_hdl]
                                    .name
                                )
                                logger.info(
                                    "tgn port handle fetched from testbed yaml is : %s "
                                    % (tgn_port_hdl)
                                )
                                logger.info(
                                    banner("Create tgn start stop traffic class object")
                                )
                                testscript.parameters[
                                    "tgn_start_stop_traffic_obj"
                                ] = traffic_config_lib.tgnStartStopTraffic(
                                    logger,
                                    testscript.parameters["genie_testbed"],
                                    tgn_config,
                                    testscript.parameters["tgn_obj"],
                                    tgn_port_hdl,
                                    testscript.parameters["tgn_streams_list"][tgn_intf_hdl],
                                    int_config=0,
                                    traf_config=0,
                                )
                                logger.info(
                                    banner(
                                        "tgn_start_stop_traffic_obj is : %s "
                                        % (
                                            testscript.parameters[
                                                "tgn_start_stop_traffic_obj"
                                            ]
                                        )
                                    )
                                )
                                tgn_traffic_loss = testscript.parameters[
                                    "tgn_start_stop_traffic_obj"
                                ].getTrafficPacketLoss()
                        elif testscript.parameters['tgn_config']['type']== 'spirent':
                            for tgn_intf_hdl in testscript.parameters["tgn_streams_list"].keys():
                                logger.info(
                                    "tgn interface handle is : %s " % (tgn_intf_hdl)
                                )
                                tgn_port_hdl=tgn_intf_hdl
                                logger.info(
                                    "tgn port handle fetched from testbed yaml is : %s "
                                    % (tgn_port_hdl)
                                )
                                logger.info(
                                    banner("Create tgn start stop traffic class object")
                                )
                                testscript.parameters[
                                    "tgn_start_stop_traffic_obj"
                                ] = traffic_config_lib.tgnStartStopTraffic(
                                    logger,
                                    testscript,
                                    testscript.parameters["genie_testbed"],
                                    testscript.parameters['tgn_config'],
                                    testscript.parameters["tgn_obj"],
                                    tgn_port_hdl,
                                    testscript.parameters["tgn_streams_list"][tgn_intf_hdl],
                                    int_config=0,
                                    traf_config=0,
                                )
                                logger.info(
                                    banner(
                                        "tgn_start_stop_traffic_obj is : %s "
                                        % (
                                            testscript.parameters[
                                                "tgn_start_stop_traffic_obj"
                                            ]
                                        )
                                    )
                                )
                                tgn_traffic_loss = testscript.parameters[
                                    "tgn_start_stop_traffic_obj"
                                ].getTrafficPacketLoss()

                        if issu_upgrade_subtype == "disruptive":
                            if tgn_traffic_loss is None:
                                logger.info(
                                    banner(
                                        "Traffic loss seen , expected as upgrade was disruptive"
                                    )
                                )
                        elif issu_upgrade_subtype == "nondisruptive":
                            if tgn_traffic_loss is not None:
                                logger.info(banner("TGN stats verification passed"))
                            else:
                                logger.error(
                                    banner("Traffic loss seen , Test Failed")
                                )
                                fail_flag = 1

                    logger.info(
                        'Run traffic post upgrade if upgrade is disruptive upgrade if "start_traffic_post_upgrade" flag set to 1 in data file'
                    )
                    
                    ## input to run traffic:-- porthandle_stream dictionary,should be in this format.{'ixia-intf-1': 'TI0-Streamblock1'}
                    
                    if start_traffic_post_upgrade == 1 and testscript.parameters['tgn_config_flag']==1 and testscript.parameters['tgn_run_flag']==1:
                        if issu_upgrade_subtype == "disruptive":
                            if testscript.parameters['tgn_config']['type']== 'ixia':
                                for tgn_intf_hdl in testscript.parameters["tgn_streams_list"].keys():
                                    logger.info(
                                        "tgn interface handle is : %s " % (tgn_intf_hdl)
                                    )
                                    tgn_port_hdl = (
                                        testscript.parameters["genie_testbed"]
                                        .devices[tgn_config["tgn"]]
                                        .interfaces[tgn_intf_hdl]
                                        .name
                                    )
                                    logger.info(
                                        "tgn port handle fetched from testbed yaml is : %s "
                                        % (tgn_port_hdl)
                                    )
                                    logger.info(
                                        banner("Create tgn start stop traffic class object")
                                    )
                                    testscript.parameters[
                                        "tgn_start_stop_traffic_obj"
                                    ] = traffic_config_lib.tgnStartStopTraffic(
                                        logger,
                                        testscript.parameters["genie_testbed"],
                                        tgn_config,
                                        testscript.parameters["tgn_obj"],
                                        tgn_port_hdl,
                                        testscript.parameters["tgn_streams_list"][
                                            tgn_intf_hdl
                                        ],
                                        int_config=0,
                                        traf_config=0,
                                    )
                                    logger.info(
                                        banner(
                                            "tgn_start_stop_traffic_obj is : %s "
                                            % (
                                                testscript.parameters[
                                                    "tgn_start_stop_traffic_obj"
                                                ]
                                            )
                                        )
                                    )
                                    tgn_traffic_control = testscript.parameters[
                                        "tgn_start_stop_traffic_obj"
                                    ].tgn_Start_Traffic()
                                    sleep(30)
                            elif testscript.parameters['tgn_config']['type']== 'spirent':
                                for tgn_intf_hdl in testscript.parameters["tgn_streams_list"].keys(): 
                                    logger.info(
                                        "tgn interface handle is : %s " % (tgn_intf_hdl)
                                    )
                                    tgn_port_hdl=tgn_intf_hdl
                                    logger.info(
                                        "tgn port handle fetched from testbed yaml is : %s "
                                        % (tgn_port_hdl)
                                    )
                                    logger.info(
                                        banner("Create tgn start stop traffic class object")
                                    )
                                    testscript.parameters[
                                        "tgn_start_stop_traffic_obj"
                                    ] = traffic_config_lib.tgnStartStopTraffic(
                                        logger,
                                        testscript,
                                        testscript.parameters["genie_testbed"],
                                        testscript.parameters['tgn_config'],
                                        testscript.parameters["tgn_obj"],
                                        tgn_port_hdl,
                                        testscript.parameters["tgn_streams_list"][
                                            tgn_intf_hdl
                                        ],
                                        int_config=0,
                                        traf_config=0,
                                    )
                                    logger.info(
                                        banner(
                                            "tgn_start_stop_traffic_obj is : %s "
                                            % (
                                                testscript.parameters[
                                                    "tgn_start_stop_traffic_obj"
                                                ]
                                            )
                                        )
                                    )
                                    tgn_traffic_control = testscript.parameters[
                                        "tgn_start_stop_traffic_obj"
                                    ].tgn_Start_Traffic()
                                    sleep(30)
                            if tgn_traffic_control is not None:
                                logger.info(banner("TGN start traffic passed"))
                            else:
                                logger.error(banner("TGN start traffic failed"))
                                fail_flag = 1
                                logger.info(
                                    "Run traffic status is : %s" % (tgn_traffic_control)
                                )

                    
                    if pre_post_issu_verification_lib.device_config_verification_pre_post_issu(
                        logger,
                        testscript,
                        testscript.parameters["genie_testbed"],
                        post_issu_verification=1,
                    ):
                        logger.info(
                            "Post ISSU verification succesfull for image: %s on device: %s"
                            % (issu_image, device)
                        )
                    else:
                        logger.error(
                            "Post ISSU verification is not succesfull for image: %s on device: %s"
                            % (issu_image, device)
                        )
                        fail_flag = 1
                        
                    logger.info("Post Running config snapshot")
                    post_running_config = (
                        testscript.parameters["genie_testbed"]
                        .devices[device]
                        .api.get_running_config_dict()
                    )
                    logger.info(
                        "Compare Pre and Post Running config snapshot after ISSU"
                    )
                    # excludes = [r"(^boot nxos)"]
                    excludes = [r"(^boot nxos|version.*Bios:version.* )"]
                    compare_dict = (
                        testscript.parameters["genie_testbed"]
                        .devices[device]
                        .api.compare_config_dicts(
                            pre_running_config, post_running_config, excludes
                        )
                    )

                    if compare_dict != "":
                        logger.error(
                            "Pre and Post Running config snapshot are not matching after ISSU , Test FAILED"
                        )
                        logger.error(compare_dict)
                        fail_flag = 1
                    else:
                        logger.info(
                            "Pre and Post Running config snapshot are matching after ISSU , Test PASSED"
                        )

        if fail_flag == 1:
            self.failed("ISSU Validation FAILED on device: %s" % device)
        else:
            logger.info(banner("ISSU PASSED on device: %s" % device))
          
