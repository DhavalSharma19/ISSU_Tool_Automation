# ISSU_Tool_Automation

## Common Setup section :- <br>
We configure and setup all devices and test equipment in the common setup section.

initialize_logging :- <br>
Takes 2 arguments : self, testscript <br>
This is the common setup section to initialize logging for script.

connect_devices :- <br>
Takes 4 arguments : self, logger, testscript, testbed <br>
In this function we loop through all the devices in the testbed and if the device Operating System is of type "nxos" we connect to the device. This will return false if any connection to the device is not possible and the script will stop and throw error. <br>

"" NX-OS is a network operating system for the Nexus-series Ethernet switches and MDS-series Fibre Channel storage area network switches made by Cisco Systems. It evolved from the Cisco operating system SAN-OS, originally developed for its MDS switches. ""

common_device_config :- <br>
Takes 4 arguments : self, logger, testscript, testbed <br>
In this section we configure the devices that we connected to in the connect_devices section. We feature bash shell and overwrite the current startup config file with what is currently in the running configuration file. When device config is successful we save the device configuration.

get_issu_matrix :- <br>
Takes 5 arguments : self, testbed, testscript, issu_matrix_file, logger <br>
In this section we take the arguments given by the user in the issu_matrix.csv file and store the information. We store switch_alias, to_image(the image we want to upgrade or downgrade the box), to_image_path(the path where the image is located), upgrade_type(upgrade or downgrade), upgrade_subtype(disruptive or nondisruptive). Give lxc_issu as 0 if you dont want that else provide with additional informtion i.e. epld_upgrade, epld_image and odule_no in the issu_matrix file.

## Test Section :-
Consists of ISSU_TESTS. <br>

device_configuration :- <br>
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

## Spirent Specific :- <br>
""Spirent helps generate full state application protocol traffic over emulated topology, to conduct concurrent Layer 2-3 and Layer 4-7 application traffic generation via single user interface, automation framework."" <br>

We call function spirent_connect_interface_traffic_configs from tgn_spirent library file. This function tries to connect to spirent through function sth.connect() in which we pass the ip for spirent and the port_list from the testbed file. Now that device is connected we do interface configuration. <br>

Now based on the traffic you send if it has vlan or not and whether ip_version is "ipv4" or "ipv6" we use function sth.interface_config and pass arguments provided in tgn_config in datafile which Return value: <{arpnd_status 1} {arpnd_cache none} {arpnd_report none} {status 1} {handles 0}>. Now if status is '1' means "We have Successfully configured protocol interface" else it will show a error "Failed to configure protocol interface". <br>
