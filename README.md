# ISSU_Tool_Automation

## Common Setup section :- <br>
We configure and setup all devices and test equipment in the common setup section.

### initialize_logging :- <br>
Takes 2 arguments : self, testscript <br>
This is the common setup section to initialize logging for script.

### connect_devices :- <br>
Takes 4 arguments : self, logger, testscript, testbed <br>
In this function we loop through all the devices in the testbed and if the device Operating System is of type "nxos" we connect to the device. This will return false if any connection to the device is not possible and the script will stop and throw error. <br>

<pre>
"" NX-OS is a network operating system for the Nexus-series Ethernet switches and MDS-series 
   Fibre Channelstorage area network switches made by Cisco Systems. It evolved from the 
   Cisco operating system SAN-OS, originally developed for its MDS switches. ""
</pre>

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

<pre>
""Spirent helps generate full state application protocol traffic over emulated topology, to conduct
  concurrent Layer 2-3 and Layer 4-7 application traffic generation via single user interface, 
  automation framework."" 
</pre>

#### Connecting to Spirent :- <br>
We call function spirent_connect_interface_traffic_configs from tgn_spirent library file. This function tries to connect to spirent through function sth.connect() in which we pass the ip for spirent and the port_list from the testbed file. <br>
<pre>
Return value: <{offline 0} {port_handle {list_of_ports}} {status 1}> 
</pre>
If connection fails the function return a error and script stops else if device is connected we move forward with interface configuration. <br>

#### Spirent Interface Configuration :- <br>
Now based on the traffic you send if it has vlan or not and whether ip_version is "ipv4" or "ipv6" we use function sth.interface_config and pass arguments provided in tgn_config in datafile which has :-<br>
<pre>
Return value: <{arpnd_status 1} {arpnd_cache none} {arpnd_report none} {status 1} {handles 0}>. 
</pre>
Now if status is '1' means "We have Successfully configured protocol interface" else it will show a error "Failed to configure protocol interface". If interface config is successful we move to traffic configuration <br>

#### Spirent Traffic configuration :- <br>
Now we try to configure traffic with the help of function sth.traffic_config() in which we pass the arguments from the datafile tgn_config parameter. <br>
<pre>
Return value: <{stream_id streamblock1} {status 1}> 
</pre>
If status is 1 we have successfully created traffic else the function throws a error. <br>

#### Starting Traffic :- <br>
Now we create tgn start stop traffic class object with the help of tgnStartStopTraffic() function from traffic_config_lib file. Now we start traffic with the help of tgn_Start_Traffic() function of class tgnStartStopTraffic in traffic_config_lib file which calls function startStopSpirentTraffic() from tgn_spirent file which calls sth.traffic_control() function which takes stream handle, traffic_start_mode and action as arguments. This function has :-<br>
<pre>
Return value: <{status 1}>. 
</pre>
If status is 0 then script will trow error else we have succesfully created traffic. <br>

#### Getting Traffic Stats :- <br>
We create tgn start stop traffic class object from traffic_config_lib file and tgnStartStopTraffic() function. Now we call getTrafficPacketLoss() function on the object which calls getTrafficPacketLoss() function from tgn_spirent file which loops through all devices in the testbed which has type "nxos" and for every interface of the device executes command "show int <intf> | sec RX" and "show int <intf> | sec TX". Now it verifies traffic loss by comparing total rx_packets and pass_packets. If this fails the script throws an error. <br>

## Trigger_issu_verify :- <br>
Takes arguments : self, testbed, testscript, logger, template_dir and variables defined is datafile. <br>
This function loops through all the device details mentioned in ISSU matrix file and starts issu process.<br>

### Pre_issu_verification :- <br>
Takes arguments : logger, testscript, testbed, and variable pre_issu_verification as 1 to make tests permanently<br>
Calls the function device_config_verification_pre_post_issu() from the pre_post_issu_verification_lib file. This function loops for all devices in the testbed of os "nxos" and for all of them performs verifications which are mentioned below in detail :- <br>

#### Core Check :- <br>   

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

#### Mts Leak Verification :- <br> 

<pre>
command = “show system internal mts buffers summary” 
    this method checks if any MTS leak present in device.
        Takes Arguments:
            device: device console handle
            logger: logging handle
        Return Values:
          # returns 1   - success
          # returns 0 - Failed case
</pre>

#### Verify Syslogs :- <br>

<pre> 
command = “show logging logfile |include ignore-case fail|warning|critical|error” 
    this method checks syslog errors present in device.
        Takes Arguments:
            device: device console handle
            logger: logging handle
        Return Values:
          # returns 1   - success
          # returns 0 - Failed case
</pre>

#### Show Cdp :- <br>
Get details about cdp neighbors from device <br>

<pre>
command = device.api.get_cdp_neighbors_info()
    this method executed show cdp neighbours in device.
        Takes Arguments:<br>
            device: device console handle
            logger: logging handle
        Return Values:
          # returns 1   - success
          # returns 0 - Failed case
</pre>

### Pre Running config snapshot :- <br>
We store this in pre_running_config by calling .get_running_config_dict(). This helps us later in comparing pre and post running config snapshot and whether anything changed or not. <br>

<pre>
.get_running_config_dict() :- Get show running-config output
        Args:
            device (`obj`): Device object
            option (`str`): option command
        Returns:
            config_dict (`dict`): dict of show run output
</pre>

### trigger_verify_issu :- <br>
We now call the function trigger_verify_issu() from the generic_utils.lib file. This function first checks if all the required parameters are passed correctly in the matrix.csv file. Now we check the current image on the box with the help of .api.get_running_image() function. <br>

### Copy Through Kstack :- <br>

<pre>
"" We check if we can use kstack or not as copying files through use-kstack enables faster 
   copy times. This option can be beneficial when copying files from remote servers that are 
   multiple hops from the switch. The use-kstack option work with copying files from, and to, 
   the switch though standard file copy features, such as scp and sftp. ""
</pre>

### Compact Copy :- <br>

<pre>
"" We check if we have to use compact copy or not. Early models of Cisco Nexus 3000, 3100, 
   and 3500 Series switches have 1.4 to 1.6 gigabytes of storage space allocated to the 
   bootflash. Over time, the file size of NX-OS binary image files has steadily increased 
   to be over 1 gigabyte. As a result, it is difficult for Nexus 3000, 3100, and 3500 Series 
   switches to simultaneously store more than one full NX-OS binary image at a time. Therefore, 
   administrators cannot follow the standard NX-OS software upgrade procedure on Nexus 3000, 
   3100, and 3500 Series switches that are used for other Nexus platforms, such as Nexus 5000, 
   6000, 7000, and 9000 Series switches. 

   Starting with NX-OS software release 7.0(3)I3(1), the file size of NX-OS binary image files 
   can be reduced through a Compact Image procedure. This is a non-disruptive procedure that 
   does not affect the switch's control plane or ability to forward data plane traffic. "" 
</pre>

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

### Electronic Programmable Logic Device (EPLD) image :- <br>
<pre>   
""Cisco also provides electronic programmable logic device (EPLD) image upgrades to 
  enhance hardware functionality or to resolve known hardware issues. The EPLD image 
  upgrades are independent from the Cisco NX-OS software upgrades. 
  The advantage of having EPLDs for some module functions is that when you need to 
  upgrade those functions, you just upgrade their software images instead of replacing 
  their hardware.
  
  NOTE: EPLD image upgrades for a line card disrupt the traffic going through the module 
  because the module must power down briefly during the upgrade. The system performs 
  EPLD upgrades on one module at a time, so at any one time the upgrade disrupts only 
  the traffic going through one module.
   
  These EPLD image updates are not mandatory unless otherwise specified. The EPLD image 
  upgrades are independent from the Cisco In Service Software Upgrade (ISSU) process, 
  which upgrades the system image with no impact on the network environment.""
</pre>

### Deciding When to Upgrade EPLDs :- <br>

<pre>
""When new EPLD images are available, the upgrades are always recommended if your 
  network environment allows for a maintenance period in which some level of traffic 
  disruption is acceptable. If such a disruption is not acceptable, then consider 
  postponing the upgrade until a better time.
  
  NOTE: The EPLD upgrade operation is a disruptive operation. Execute this operation 
  only at a programmed maintenance time.
   
  NOTE: Do not perform an EPLD upgrade during an ISSU system upgrade.
</pre>

If epld_upgrade set as 1 in issu_matrix.csv file then we copy epld_image to the box using api.copy_to_device() <br>

### Incompatibility Check :- <br>
Execute command "show show incompatibility-all nxos + <issu_image>"

First we execute the command "show boot mode". If this shows an error means LXC ISSU is not supported on current image/device and the function will show a warning and boot mode will be native.<br>

#### LXC_issu variable is set as 1 :- <br>

Now if boot mode is "LXC" and lxc_issu variable is set as 1 in the data file. So as boot mode set by user is lxc. Current Boot mode is already set lxc in device, so we can proceed with ISSU. <br>

Else if boot mode is "native" we have to change boot mode to lxc. So we execute the command device.configure("boot mode lxc"). Then we execute the command .api.execute_change_boot_variable() and give device.api.get_running_image() as the argument in this function. <br>

<pre>  
execute_change_boot_variable() :-  
Set the boot variables
        Args:
            device ('obj'): Device object
            system ('str'): System image
            kickstart ('str'): Kickstart image
            timeout ('int'): Timeout in seconds
</pre>    

Then we execute the command "copy run start" and execute_copy_run_to_start()<br>

<pre>
execute_copy_run_to_start() :- 
Execute copy running-config to startup-config
        Args:
            device ('obj'): Device object
            command_timeout ('int'): Timeout value in sec, Default Value is 300 sec
            max_time ('int'): Maximum time in seconds, Default Value is 300 sec
            check_interval ('int'): Check interval in seconds, Default Value is 20 sec
            copy_vdc_all ('boolean'): Copy on all VDCs or not, Default Value is False
</pre>

Now we reload the box and check if boot mode is changed to LXC or not if not then the function returns an error. For reloading we execute command api.execute_reload().

<pre>
execute_reload() :-
Reload device
        Args:
            device ('obj'): Device object
            prompt_recovery ('bool'): Enable/Disable prompt recovery feature. default: True
            reload_creds ('str'): Credential name defined in the testbed yaml file to be used during reload. default: 'default'
            sleep_after_reload ('int'): Time to sleep after reload in seconds, default: 120
            timeout ('int'): reload timeout value, defaults 800 seconds.
            reload_command ('str'): reload command. default: 'reload'
            error_pattern ('list'): List of regex strings to check output for errors.
            devices ('list'): list of device names
            exclude_devices ('list'): excluded device list
        Usage:
            device.api.execute_reload(devices=['ce1', 'ce2', 'pe1'], error_pattern=[], sleep_after_reload=0)
</pre>

#### LXC_issu variable is set as 0 :- <br>

We check if boot mode is native. We disable lxc mode if enabled in device so if boot mode is "LXC" we execute command device.configure("no boot mode lxc"). <br>

Then we execute the command .api.execute_change_boot_variable() and give device.api.get_running_image() as the argument in this function. <br> 

<pre>  
execute_change_boot_variable() :-  
Set the boot variables
        Args:
            device ('obj'): Device object
            system ('str'): System image
            kickstart ('str'): Kickstart image
            timeout ('int'): Timeout in seconds
</pre>    

Then we execute the command "copy run start" and execute_copy_run_to_start()<br>

<pre>
execute_copy_run_to_start() :- 
Execute copy running-config to startup-config
        Args:
            device ('obj'): Device object
            command_timeout ('int'): Timeout value in sec, Default Value is 300 sec
            max_time ('int'): Maximum time in seconds, Default Value is 300 sec
            check_interval ('int'): Check interval in seconds, Default Value is 20 sec
            copy_vdc_all ('boolean'): Copy on all VDCs or not, Default Value is False
</pre>

Now we reload the box and check if boot mode is changed to native or not if not then the function returns an error. For reloading we execute command api.execute_reload().

<pre>
execute_reload() :-
Reload device
        Args:
            device ('obj'): Device object
            prompt_recovery ('bool'): Enable/Disable prompt recovery feature. default: True
            reload_creds ('str'): Credential name defined in the testbed yaml file to be used during reload. default: 'default'
            sleep_after_reload ('int'): Time to sleep after reload in seconds, default: 120
            timeout ('int'): reload timeout value, defaults 800 seconds.
            reload_command ('str'): reload command. default: 'reload'
            error_pattern ('list'): List of regex strings to check output for errors.
            devices ('list'): list of device names
            exclude_devices ('list'): excluded device list
        Usage:
            device.api.execute_reload(devices=['ce1', 'ce2', 'pe1'], error_pattern=[], sleep_after_reload=0)
</pre>






### Validate_ISSU :- <br>
Takes arguments : logger, device, img_name, upgrade_type, upgrade_subtype, lxc_issu. <br>

In this function we first relogin to the box. So we first do device.disconnect() and then try device.connect() to make sure device is logging in after ISSU. <br>

Now we check the module status and if it is proper after ISSU using api.verify_module_status()<br>

<pre>
api.verify_module_status()
Check status of slot using 'show module' 
        Args: 
            device ('obj'): Device object  
            timeout ('int'): Max timeout to re-check module status  
            interval ('int'): Max interval to re-check module status  
            ignore_modules ('list'): Modules to ignore the status check  
</pre>
    
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
If start_traffic_post_upgrade set as 1 in data file and upgrade_subtype is "disruptive" this function takes place. We create tgn start stop traffic class object and then start traffic using function tgn_start_traffic of class tgnStartStopTraffic in traffic_config_lib file which calls function startStopSpirentTraffic() from tgn_spirent file which calls sth.traffic_control() function which takes stream handle, traffic_start_mode and action as arguments. This function :- <br>
<pre>
Return value: <{status 1}>. 
</pre>
If status is 0 then script will trow error else we have succesfully created traffic. <br>

### Post_issu_verification :- <br>
Takes arguments : logger, testscript, testbed, and variable post_issu_verification as 1 to make tests permanently<br>
Calls the function device_config_verification_pre_post_issu() from the pre_post_issu_verification_lib file. This function loops for all devices in the testbed of os "nxos" and for all of them performs verifications which are mentioned below in detail :- <br>

#### Core Check :- <br>   

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

#### Mts Leak Verification :- <br> 

<pre>
command = “show system internal mts buffers summary” 
    this method checks if any MTS leak present in device.
        Takes Arguments:
            device: device console handle
            logger: logging handle
        Return Values:
          # returns 1   - success
          # returns 0 - Failed case
</pre>

#### Verify Syslogs :- <br>

<pre> 
command = “show logging logfile |include ignore-case fail|warning|critical|error” 
    this method checks syslog errors present in device.
        Takes Arguments:
            device: device console handle
            logger: logging handle
        Return Values:
          # returns 1   - success
          # returns 0 - Failed case
</pre>

#### Show Cdp :- <br>
Get details about cdp neighbors from device <br>

<pre>
command = device.api.get_cdp_neighbors_info()
    this method executed show cdp neighbours in device.
        Takes Arguments:<br>
            device: device console handle
            logger: logging handle
        Return Values:
          # returns 1   - success
          # returns 0 - Failed case
</pre>

### Post Running config snapshot :- <br>
We store this in post_running_config by calling .get_running_config_dict(). <br>

<pre>
.get_running_config_dict() :- Get show running-config output
        Takes Args: 
            device (`obj`): Device object
            option (`str`): option command
        Returns:
            config_dict (`dict`): dict of show run output
</pre>
    
### Comparing Pre_Post Running Config Snapshot :- <br>
After ISSU in this function we compare two configuration dicts and return the differences with the help of the function. We pass pre and post running configs that we stored earlier here as arguments. <br> 

<pre> 
api.compare_config_dicts(). 
        Takes Args: 
            a (`dict`): Configuration dict 
            b (`dict`): Configuration dict 
            exclude (`list`): List of item to ignore. Supports Regex. 
                              Regex must begins with ( ) 
        Returns: 
            out (`str`): differences 
</pre>

If Pre and Post Running config snapshot are not matching after ISSU , Test fails and throws error. <br>

If no errors are encountered till now the script passes. <br>

