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
In this section we take the arguments given by the user in the issu_matrix.csv file and store the information. We store switch_alias, to_image(the image we want to upgrade or downgrade the box), to_image_path(the path where the image is located), upgrade_type(upgrade or downgrade), upgrade_subtype(disruptive or nondisruptive). Give lxc_issu as 0 if you dont want that else provide with additional informtion i.e. epld_upgrade, epld_image and module_no in the issu_matrix file.

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
We call function spirent_connect_interface_traffic_configs from tgn_spirent library file. This function tries to connect to spirent through function sth.connect() in which we pass the ip for spirent and the port_list from the testbed file. <br>
Return value: <{offline 0} {port_handle {list_of_ports}} {status 1}> <br>
If connection fails the function return a error and script stops else if device is connected we move forward with interface configuration. <br>

#### Spirent Interface Configuration :- <br>
Now based on the traffic you send if it has vlan or not and whether ip_version is "ipv4" or "ipv6" we use function sth.interface_config and pass arguments provided in tgn_config in datafile which has :-<br>
Return value: <{arpnd_status 1} {arpnd_cache none} {arpnd_report none} {status 1} {handles 0}>. <br>
Now if status is '1' means "We have Successfully configured protocol interface" else it will show a error "Failed to configure protocol interface". If interface config is successful we move to traffic configuration <br>

#### Spirent Traffic configuration :- <br>
Now we try to configure traffic with the help of function sth.traffic_config() in which we pass the arguments from the datafile tgn_config parameter. <br>
Return value: <{stream_id streamblock1} {status 1}> <br>
If status is 1 we have successfully created traffic else the function throws a error. <br>

#### Starting Traffic :- <br>
Now we create tgn start stop traffic class object with the help of tgnStartStopTraffic() function from traffic_config_lib file. Now we start traffic with the help of tgn_Start_Traffic() function of class tgnStartStopTraffic in traffic_config_lib file which calls function startStopSpirentTraffic() from tgn_spirent file which calls sth.traffic_control() function which takes stream handle, traffic_start_mode and action as arguments. This function has :-<br>
Return value: <{status 1}>. <br>
If status is 0 then script will trow error else we have succesfully created traffic. <br>

#### Getting Traffic Stats :- <br>
We create tgn start stop traffic class object from traffic_config_lib file and tgnStartStopTraffic() function. Now we call getTrafficPacketLoss() function on the object which calls getTrafficPacketLoss() function from tgn_spirent file which loops through all devices in the testbed which has type "nxos" and for every interface of the device executes command "show int <intf> | sec RX" and "show int <intf> | sec TX". Now it verifies traffic loss by comparing total rx_packets and pass_packets. If this fails the script throws an error. <br>

## Trigger_issu_verify :- <br>
Takes arguments : self, testbed, testscript, logger, template_dir and variables defined is datafile. <br>
This function loops through all the device details mentioned in ISSU matrix file and starts issu process.<br>

### Pre_issu_verification :- <br>
Takes arguments : logger, testscript, testbed, and variable pre_issu_verification as 1 to make tests permanently<br>
Calls the function device_config_verification_pre_post_issu() from the pre_post_issu_verification_lib file. This function loops for all devices in the testbed of os "nxos" and for all of them performs verifications which are mentioned below in detail :- <br>

#### core check :- <br>   

<pre>
command = “show cores” <br>
    this method checks if any core present in device. 
        Takes Arguments:
            device: device console handle
            logger: logging handle
        Return Values:
          # returns 1   - success
          # returns 0 - Failed case
</pre>

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
Get details about cdp neighbors from device <br>

command = device.api.get_cdp_neighbors_info()<br>
""" this method executed show cdp neighbours in device.<br>
        Takes Arguments:<br>
            device: device console handle<br>
            logger: logging handle<br>
        Return Values:<br>
          # returns 1   - success<br>
          # returns 0 - Failed case<br>
    """<br>

### Pre Running config snapshot :- <br>
We store this in pre_running_config by calling .get_running_config_dict(). This helps us later in comparing pre and post running config snapshot and whether anything changed or not. <br>

.get_running_config_dict() :- Get show running-config output<br>
        Args: <br>
            device (`obj`): Device object<br>
            option (`str`): option command<br>
        Returns:<br>
            config_dict (`dict`): dict of show run output<br>

### trigger_verify_issu :- <br>
We now call the function trigger_verify_issu() from the generic_utils.lib file. This function first checks if all the required parameters are passed correctly in the matrix.csv file. Now we check the current image on the box with the help of .api.get_running_image() function. <br>

### Copy Through Kstack :- <br>
""We check if we can use kstack or not as copying files through use-kstack enables faster copy times. This option can be beneficial when copying files from remote servers that are multiple hops from the switch. The use-kstack option work with copying files from, and to, the switch though standard file copy features, such as scp and sftp.""<br>

### Compact Copy :- <br>
""We check if we have to use compact copy or not. Early models of Cisco Nexus 3000, 3100, and 3500 Series switches have 1.4 to 1.6 gigabytes of storage space allocated to the bootflash. Over time, the file size of NX-OS binary image files has steadily increased to be over 1 gigabyte. As a result, it is difficult for Nexus 3000, 3100, and 3500 Series switches to simultaneously store more than one full NX-OS binary image at a time. Therefore, administrators cannot follow the standard NX-OS software upgrade procedure on Nexus 3000, 3100, and 3500 Series switches that are used for other Nexus platforms, such as Nexus 5000, 6000, 7000, and 9000 Series switches. <br>

Starting with NX-OS software release 7.0(3)I3(1), the file size of NX-OS binary image files can be reduced through a Compact Image procedure. This is a non-disruptive procedure that does not affect the switch's control plane or ability to forward data plane traffic. <br>

### Copying Image :- <br>

Now we check if file already exists in the box or not. If it already exits then we skip the copy image section as it is already present in the box. <br>

Now if file does does already exits we use api.copy_to_device() fucntion to Copy file from linux server to the device :- <br>

<pre>
Args: 
        device (Device): Device object
        remote_path (str): remote file path on the server
        local_path (str): local file to copy to on the device (default: None)
        server (str): hostname or address of the server (default: None)
        protocol(str): file transfer protocol to be used (default: scp)
        vrf (str): vrf to use (optional)
        timeout(int): timeout value in seconds, default 300
        compact(bool): compress image option for n9k, defaults False
        fu(obj): FileUtils object to use instead of creating one. Defaults to None.
        use_kstack(bool): Use faster version of copy, defaults False
        Not supported with a file transfer protocol
        prompting for a username and password
        http_auth (bool): Use http authentication (default: True)

Returns:
        None
</pre>

If the server is not specified, a HTTP server will be spawned on the local system and serve the directory of the file specified via remote_path and the copy operation will use http.<br>

If the device is connected via CLI proxy (unix jump host) and the proxy has 'socat' installed, the transfer will be done via the proxy automatically.<br>








Incompatibility Check :- <br>
Execute command "show show incompatibility-all nxos + <issu_image>"




### Validate_ISSU :- <br>
Takes arguments : logger, device, img_name, upgrade_type, upgrade_subtype, lxc_issu. <br>

In this function we first relogin to the box. So we first do device.disconnect() and then try device.connect() to make sure device is logging in after ISSU. <br>

Now we check the module status and if it is proper after ISSU using api.verify_module_status()<br>

api.verify_module_status()<br>
Check status of slot using 'show module'  <br>
        Args: <br>
            device ('obj'): Device object  <br>
            timeout ('int'): Max timeout to re-check module status  <br>
            interval ('int'): Max interval to re-check module status  <br>
            ignore_modules ('list'): Modules to ignore the status check  <br>

Now we see if the device is showing the image that we wanted to install or not. If not then the device is loaded with incorrect image and so the function throws an error. We use api.get_running_image() function to get this information. <br> 

device.execute('show install all status') <br>
Now we Enter the show install all status command to verify the status of the installation. It Displays a high-level log of the installation. <br>

If upgrade_Type was "downgrade" and "show install all status" does not has statement "Finishing the upgrade, switch will reboot in 10 seconds" Then script throws error as show install all status after ISSU downgrade is not proper. <br>

Now if upgrade_Type was "upgrade" and sub_type was "disruptive" and "show install all status" does not has statement "Finishing the upgrade, switch will reboot in 10 seconds" Then script throws error as show install all status after ISSU upgrade is not proper.

If for "upgrade" but "nondisruptive" if "show install all status" does not has "Install has been successful" statement and has statement "Finishing the upgrade, switch will reboot in 10 seconds" then function throws a warning as Disruptive ISSU happened instead of non-disruptive ISSU.<br>

For "nondisruptive" "upgrade" if "show install all status" does not has "Install has been successful" statement then show install all status after ISSU upgrade is not proper and script throws an error. <br>






### Validate Traffic post ISSU :- <br>
If "verify_traffic_post_upgrade" flag set to 1 in the datafile. We first create tgn start stop traffic class object using the function tgnStartStopTraffic() from the traffic_config_lib file. Now with the help of getTrafficPacketLoss() from tgn_spirent file which loops through all devices in the testbed which has type "nxos" and for every interface of the device executes command "show int <intf> | sec RX" and "show int <intf> | sec TX". Now it verifies traffic loss by comparing total rx_packets and pass_packets. If this fails the script throws an error. <br>

Now if issu upgrade subtype is "disruptive" and traffic loss is seen it returns true which is to be expected as upgrade was disruptive and if subtype is "nondisruptive" and traffic loss is seen then test fails and throws error.<br>

### Running traffic post upgrade :- <br>
If start_traffic_post_upgrade set as 1 in data file and upgrade_subtype is "disruptive" this function takes place. We create tgn start stop traffic class object and then start traffic using function tgn_start_traffic of class tgnStartStopTraffic in traffic_config_lib file which calls function startStopSpirentTraffic() from tgn_spirent file which calls sth.traffic_control() function which takes stream handle, traffic_start_mode and action as arguments. This function Return value: <{status 1}>. If status is 0 then script will trow error else we have succesfully created traffic. <br>

### Post_issu_verification :- <br>
Takes arguments : logger, testscript, testbed, and variable post_issu_verification as 1 to make tests permanently<br>
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
Get details about cdp neighbors from device <br>

command = device.api.get_cdp_neighbors_info()<br>
""" this method executed show cdp neighbours in device.<br>
        Takes Arguments:<br>
            device: device console handle<br>
            logger: logging handle<br>
        Return Values:<br>
          # returns 1   - success<br>
          # returns 0 - Failed case<br>
    """<br>

### Post Running config snapshot :- <br>
We store this in post_running_config by calling .get_running_config_dict(). <br>

.get_running_config_dict() :- Get show running-config output<br>
        Takes Args: <br>
            device (`obj`): Device object<br>
            option (`str`): option command<br>
        Returns:<br>
            config_dict (`dict`): dict of show run output<br>

### Comparing Pre_Post Running Config Snapshot :- <br>
After ISSU in this function we compare two configuration dicts and return the differences with the help of the function. We pass pre and post running configs that we stored earlier here as arguments. <br> 

api.compare_config_dicts(). <br>
        Takes Args: <br>
            a (`dict`): Configuration dict <br>
            b (`dict`): Configuration dict <br>
            exclude (`list`): List of item to ignore. Supports Regex. <br>
                              Regex must begins with ( ) <br>
        Returns: <br>
            out (`str`): differences <br>

If Pre and Post Running config snapshot are not matching after ISSU , Test fails and throws error. <br>

If no errors are encountered till now the script passes. <br>

