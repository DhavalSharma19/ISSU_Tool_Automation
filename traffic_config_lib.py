#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import traceback
import tgn_spirent
import tgn_ixia
from pyats.log.utils import banner


class tgnConfig(object):

    '''this class takes care of tgn connect, configure interface and traffic configuration
    by using the tgn data provided by user in data yaml file'''

    def __init__(
        self,
        logger,
        testbed,
        tgn_config,
        int_config=0,
        traf_config=0,
        ):

        self.logger = logger
        self.testbed = testbed
        self.tgn_config = tgn_config
        self.int_config = int_config
        self.traf_config = traf_config

    def tgn_Connect_Interface_Traffic_Config(self):

        ''' This api takes care of tgn connect, configure interface and traffic configuration
            by using the tgn data provided by user in data yaml file'''

        self.tgn_list = []
        self.int_config = 1
        self.traf_config = 1
        for device in self.testbed.devices:
            if self.testbed.devices[device].type != 'nxos':
                self.tgn_list.append(device)
        for device in self.tgn_list:
            test_device = self.testbed.devices[device]
            self.logger.info('Create tgn object')
            if test_device.type == 'spirent':
                self.logger.info('Connect to Spirent')
                try:
                    (tgn_obj, self.stream_port_hdl_dict) = \
                        tgn_spirent.spirent_connect_interface_traffic_configs(
                        self.logger,
                        self.testbed,
                        test_device,
                        self.tgn_config,
                        int_config=self.int_config,
                        traf_config=self.traf_config,
                        )  
                except:
                    self.logger.error(traceback.format_exc())

                if not self.stream_port_hdl_dict:
                    self.logger.error('Spirent Traffic Configuration FAILED'
                            )
                    return None
                else:
                    return (tgn_obj, self.stream_port_hdl_dict)
            elif test_device.type == 'ixia':
                if self.tgn_config['mode'] == 'native':
                    self.logger.info(banner('Ixia native mode selected by user'
                            ))
                    self.logger.info('Connect to Ixia, tgn interface and traffic configuration'
                            )
                    try:
                        (tgn_obj, self.stream_port_hdl_dict) = \
                            tgn_ixia.ixia_connect_interface_traffic_configs(
                            self.logger,
                            self.testbed,
                            test_device,
                            self.tgn_config,
                            int_config=self.int_config,
                            traf_config=self.traf_config,
                            )
                    except:
                        self.logger.error(traceback.format_exc())

                if not self.stream_port_hdl_dict:
                    self.logger.error('Ixia Traffic Configuration FAILED'
                            )
                    return None
                else:
                    return (tgn_obj, self.stream_port_hdl_dict)


class tgnStartStopTraffic(object):

    '''this class takes care of tgn start/stop traffic'''

    def __init__(
        self,
        logger,
        testscript,
        testbed,
        tgn_config,
        tgn_hdl,
        tgn_port_hdl,
        tgn_stream_hdl,
        int_config=0,
        traf_config=0,
        ):

        self.logger = logger
        self.testscript = testscript
        self.testbed = testbed
        self.tgn_config = tgn_config
        self.tgn_hdl = tgn_hdl
        self.tgn_port_hdl = tgn_port_hdl
        self.tgn_stream_hdl = tgn_stream_hdl
        self.int_config = int_config
        self.traf_config = traf_config

    def tgn_Start_Traffic(self):

        ''' api will start tgn traffic'''

        self.tgn_list = []
        for device in self.testbed.devices:
            if self.testbed.devices[device].type != 'nxos':
                self.tgn_list.append(device)
        for device in self.tgn_list:
            test_device = self.testbed.devices[device]
            if test_device.type == 'spirent':
                try:
                    self.traffic_control = \
                        tgn_spirent.startStopSpirentTraffic(self.logger,
                            tg_hdl=test_device, action='run',
                            port_handle=self.tgn_port_hdl,
                            handle=self.tgn_stream_hdl)
                except:
                    self.logger.error(traceback.format_exc())
                if not self.traffic_control:
                    self.logger.error('Spirent Start Traffic FAILED')
                    return None
                else:
                    return self.traffic_control
            elif test_device.type == 'ixia':
                try:
                    self.traffic_control = \
                        tgn_ixia.startStopIxNetworkTraffic(self.logger,
                            tg_hdl=test_device, action='run',
                            port_handle=self.tgn_port_hdl,
                            handle=self.tgn_stream_hdl)
                except:
                    self.logger.error(traceback.format_exc())
                if not self.traffic_control:
                    self.logger.error('Ixia Start Traffic FAILED')
                    return None
                else:
                    return self.traffic_control

    def tgn_Stop_Traffic(self):

        ''' api will stop tgn traffic'''

        self.tgn_list = []
        for device in self.testbed.devices:
            if self.testbed.devices[device].type != 'nxos':
                self.tgn_list.append(device)
        for device in self.tgn_list:
            test_device = self.testbed.devices[device]
            if test_device.type == 'spirent':
                try:
                    self.traffic_control = \
                        tgn_spirent.startStopSpirentTraffic(self.logger,
                            tg_hdl=test_device, action='stop',
                            port_handle=self.tgn_port_hdl,
                            handle=self.tgn_stream_hdl)
                except:
                    self.logger.error(traceback.format_exc())
                if not self.traffic_control:
                    self.logger.error('Spirent Stop Traffic FAILED')
                    return None
                else:
                    return self.traffic_control
            elif test_device.type == 'ixia':
                try:
                    self.traffic_control = \
                        tgn_ixia.startStopIxNetworkTraffic(self.logger,
                            tg_hdl=test_device, action='stop',
                            port_handle=self.tgn_port_hdl,
                            handle=self.tgn_stream_hdl)
                except:
                    self.logger.error(traceback.format_exc())
                if not self.traffic_control:
                    self.logger.error('Ixia Stop Traffic FAILED')
                    return None
                else:
                    return self.traffic_control

    def getTrafficPacketLoss(self):

        ''' api will verify tgn traffic stats'''

        self.tgn_list = []
        for device in self.testbed.devices:
            if self.testbed.devices[device].type != 'nxos':
                self.tgn_list.append(device)
        for device in self.tgn_list:
            test_device = self.testbed.devices[device]
            if test_device.type == 'spirent':
                try:
                    self.traffic_pkt_loss = \
                        tgn_spirent.getTrafficPacketLoss(self.logger,
                            self.testscript,
                            self.testbed,
                            tg_hdl=test_device,
                            port_handle=self.tgn_port_hdl,
                            handle=self.tgn_stream_hdl)
                except:
                    self.logger.error(traceback.format_exc())
                    return None
                if not self.traffic_pkt_loss:
                    self.logger.error('Spirent Traffic stats validation FAILED'
                            )
                    return None
                else:
                    return self.traffic_pkt_loss               
            elif test_device.type == 'ixia':
                try:
                    self.traffic_pkt_loss = \
                        tgn_ixia.getTrafficPacketLoss(self.logger,
                            tg_hdl=test_device,
                            port_handle=self.tgn_port_hdl,
                            handle=self.tgn_stream_hdl)
                except:
                    self.logger.error(traceback.format_exc())
                    return None
                if not self.traffic_pkt_loss:
                    self.logger.error('Ixia Traffic stats validation FAILED'
                            )
                    return None
                else:
                    return self.traffic_pkt_loss

