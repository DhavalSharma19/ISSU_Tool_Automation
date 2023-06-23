# ISSU_Tool_Automation

## Common Setup section :- <br>
We configure and setup all devices and test equipment in the common setup section.

### initialize_logging :- <br>
Takes 2 arguments : self, testscript <br>
This is the common setup section to initialize logging for script.

### connect_devices :- <br>
Takes 4 arguments : self, logger, testscript, testbed <br>
In this function we loop through all the devices in the testbed and if the device Operating System is of type "nxos" we connect to the device. This will return false if any connection to the device is not possible and the script will stop and throw error. <br>

"" NX-OS is a network operating system for the Nexus-series Ethernet switches and MDS-series Fibre Channel storage area network switches made by Cisco Systems. It evolved from the Cisco operating system SAN-OS, originally developed for its MDS switches. ""

### common_device_config :- <br>
Takes 4 arguments : self, logger, testscript, testbed <br>
In this section we configure the devices that we connected to in the connect_devices section. We feature bash shell and overwrite the current startup config file with what is currently in the running configuration file. When device config is successful we save the device configuration.

### get_issu_matrix :- <br>
Takes 5 arguments : self, testbed, testscript, issu_matrix_file, logger <br>
In this section we take the arguments given by the user in the issu_matrix.csv file and store the information. We store switch_alias, to_image(the image we want to upgrade or downgrade the box), to_image_path(the path where the image is located), upgrade_type(upgrade or downgrade), upgrade_subtype(disruptive or nondisruptive). Give lxc_issu as 0 if you dont want that else provide with additional informtion i.e. epld_upgrade, epld_image and odule_no in the issu_matrix file.

## Test Section :-
Consists of ISSU_TESTS. <br>

### device_configuration :- <br>
Takes self, logger, testscripts and feature wise arguments. <br>
We call function device_configuration from device_config_lib. Based on device_config_flag and feature_wise_config_flag set as 0 or 1 in the datafile. <br>

If device_config_flag == 1 and feature_wise_config_flag == 1 <br>
Configure the device and also configure all feautures mentioned in the data file. the functions used for feature wise configuration are also mentioned in the device_config_lib file only.<br>

If device_config_flag == 1 and feature_wise_config_flag != 1 <br>
We configure all features at a time, load device jinja files and configure through genie configure_by_jinja2 api from the file in templates_dir. <br>

If device_config_flag != 1 and feature_wise_config_flag == 1 or != 1 <br>
The device is already configured and in a proper state, we proceed with ISSU/ISSD. <br>

If config_result return true then device config was successful else the function throws error and the script stops. We then save the device configuration. We then use the command copy running-config startup-config (copy run start) to overwrite the current startup config file with what is currently in the running configuration file. <br>

connect_configure_traffic :- <br>
Takes arguments : self, logger, testscript, traffic_config_flag, tgn_config <br>
If traffic_config_flag set as 1 in the datafile then we make a tgn_config_class_object from the traffic_config_lib file tgnConfig function. <br>

The tgnConfig Class takes care of tgn connect (Spirent or Ixia), configure interface and traffic configuration by using the tgn data provided by user in data yaml file and has function tgn_Connect_Interface_Traffic_Config. In this function we create trffic generator object (spirent/ixia) based on the data provided in the data yaml file. <br>

### Spirent Specific :- <br>
""Spirent helps generate full state application protocol traffic over emulated topology, to conduct concurrent Layer 2-3 and Layer 4-7 application traffic generation via single user interface, automation framework."" <br>

#### Connecting to Spirent :- <br>
We call function spirent_connect_interface_traffic_configs from tgn_spirent library file. This function tries to connect to spirent through function sth.connect() in which we pass the ip for spirent and the port_list from the testbed file. Return value: <{offline 0} {port_handle {list_of_ports}} {status 1}> If connection fails the function return a error and script stops else if device is connected we move forward with interface configuration. <br>

#### Spirent Interface Configuration :- <br>
Now based on the traffic you send if it has vlan or not and whether ip_version is "ipv4" or "ipv6" we use function sth.interface_config and pass arguments provided in tgn_config in datafile which has Return value: <{arpnd_status 1} {arpnd_cache none} {arpnd_report none} {status 1} {handles 0}>. Now if status is '1' means "We have Successfully configured protocol interface" else it will show a error "Failed to configure protocol interface". If interface config is successful we move to traffic configuration <br>

#### Spirent Traffic configuration :- <br>
Now we try to configure traffic with the help of function sth.traffic_config() in which we pass the arguments from the datafile tgn_config parameter. Return value: <{stream_id streamblock1} {status 1}> If status is 1 we have successfully created traffic else the function throws a error. <br>

#### Starting Traffic :- <br>
Now we create tgn start stop traffic class object with the help of tgnStartStopTraffic() function from traffic_config_lib file. Now we start traffic with the help of tgn_Start_Traffic() function of class tgnStartStopTraffic in traffic_config_lib file which calls function startStopSpirentTraffic() from tgn_spirent file which calls sth.traffic_control() function which takes stream handle, traffic_start_mode and action as arguments. This function Return value: <{status 1}>. If status is 0 then script will trow error else we have succesfully created traffic. <br>

#### Getting Traffic Stats :- <br>
We create tgn start stop traffic class object from traffic_config_lib file and tgnStartStopTraffic() function. Now we call getTrafficPacketLoss() function on the object which calls getTrafficPacketLoss() function from tgn_spirent file which loops through all devices in the testbed which has type "nxos" and for every interface of the device executes command "show int <intf> | sec RX" and "show int <intf> | sec TX". Now it verifies traffic loss by comparing total rx_packets and pass_packets. If this fails the script throws an error. <br>

## Trigger_issu_verify :- <br>
Takes arguments : self, testbed, testscript, logger, template_dir and variables defined is datafile. <br>
This function loops through all the device details mentioned in ISSU matrix file and starts issu process.<br>

### Pre_issu_verification :- <br>
Takes arguments : logger, testscript, testbed, and variable pre_issu_verification as 1 to make tests permanently<br>
Calls the function device_config_verification_pre_post_issu() from the pre_post_issu_verification_lib file. This function loops for all devices in the testbed of os "nxos" and for all of them performs verifications which are mentioned below in detail :- <br>

#### core check :- <br>   
command = “show cores” <br>
""" this method checks if any core present in device. <br>
        Takes Arguments:<br>
            device: device console handle<br>
            logger: logging handle<br>
        Return Values:<br>
          # returns 1   - success<br>
          # returns 0 - Failed case<br>
    """<br>

#### mts leak verification :- <br> 
command = “show system internal mts buffers summary” <br>
""" this method checks if any MTS leak present in device.<br>
        Takes Arguments:<br>
            device: device console handle<br>
            logger: logging handle<br>
        Return Values:<br>
          # returns 1   - success<br>
          # returns 0 - Failed case<br>
    """<br>

#### verify syslogs :- <br>
command = “show logging logfile |include ignore-case fail|warning|critical|error” <br>
""" this method checks syslog errors present in device.<br>
        Takes Arguments:<br>
            device: device console handle<br>
            logger: logging handle<br>
        Return Values:<br>
          # returns 1   - success<br>
          # returns 0 - Failed case<br>
    """<br>

#### show cdp :- <br>
command = device.api.get_cdp_neighbors_info()<br>
""" this method executed show cdp neighbours in device.<br>
        Takes Arguments:<br>
            device: device console handle<br>
            logger: logging handle<br>
        Return Values:<br>
          # returns 1   - success<br>
          # returns 0 - Failed case<br>
    """<br>

### Pre Running config snpshot :- <br>
We store this in pre_running_config by calling .get_running_config_dict(). This helps us later in comparing pre and post running config snapshot and whether anything changed or not. <br>

