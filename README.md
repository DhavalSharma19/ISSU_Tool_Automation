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
In this section we configure the devices that we connected to in the connect_devices section. We feature bash shell and execute command "copy run start" which overwrite the current startup config file with what is currently in the running configuration file. When device config is successful we save the device configuration.

### get_issu_matrix :- <br>
Takes 5 arguments : self, testbed, testscript, issu_matrix_file, logger <br>
In this section we take the arguments given by the user in the issu_matrix.csv file and store the information. We store switch_alias, to_image(the image we want to upgrade or downgrade the box), to_image_path(the path where the image is located), upgrade_type(upgrade or downgrade), upgrade_subtype(disruptive or nondisruptive). Give lxc_issu as 0 if you dont want that else provide with additional informtion i.e. epld_upgrade, epld_image and module_no in the issu_matrix file.

You can give input as follows :- <br>

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

#### If you don't want to do EPLD Upgrade :- <br>

For the box "ELY_104" you want to do "NonDisruptive Upgrade" to this "nxos64-cs.10.3.3.F.bin" image located at "/tftpboot/fcs/nr3f/" this path and you don't want LXC_ISSU to happen you give input like :- <br>

 <pre>
    ALIAS,TO_IMAGE,TO_IMAGE_PATH,TYPE,SUB_TYPE,LXC_ISSU
    ELY_104,nxos64-cs.10.3.3.F.bin,/tftpboot/fcs/nr3f/,upgrade,nondisruptive,0
 </pre>

For the box "ELY_104" you want to do "NonDisruptive Upgrade" to this "nxos64-cs.10.3.3.F.bin" image located at "/tftpboot/fcs/nr3f/" this path and you want LXC_ISSU to happen you give input like :- <br>

 <pre>
    ALIAS,TO_IMAGE,TO_IMAGE_PATH,TYPE,SUB_TYPE,LXC_ISSU
    ELY_104,nxos64-cs.10.3.3.F.bin,/tftpboot/fcs/nr3f/,upgrade,nondisruptive,1
 </pre>

#### If you want to do EPLD Upgrade :- <br>

For the box "uut2" you want to do "Disruptive Downgrade" to this "nxos.10.1.2.bin" image located at "/tftpboot/" this path and you want LXC_ISSU and EPLD_Upgrade to happen. You want to upgrade to "/auto/ins-bld-tools/branches/jacksonville/nexus/REL_10_1_1_167/build/images/final/n9000-epld.10.1.2.img" EPLD_image and give module_no as all so input matrix file will be like :- <br>

<pre>
   ALIAS,TO_IMAGE,TO_IMAGE_PATH,TYPE,SUB_TYPE,LXC_ISSU,EPLD_UPGRADE,EPLD_IMAGE,MODULE_NO
   uut2,nxos.10.1.2.bin,/tftpboot/,downgrade,disruptive,1,1,/auto/ins-bld-tools/branches/jacksonville/nexus/REL_10_1_1_167/build/images/final/n9000-epld.10.1.2.img,all
</pre>

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

### connect_configure_traffic :- <br>
Takes arguments : self, logger, testscript, traffic_config_flag, tgn_config <br>
If traffic_config_flag set as 1 in the datafile then we make a tgn_config_class_object from the traffic_config_lib file tgnConfig function. <br>

The tgnConfig Class takes care of tgn connect (Spirent or Ixia), configure interface and traffic configuration by using the tgn data provided by user in data yaml file and has function tgn_Connect_Interface_Traffic_Config. In this function we create traffic generator object (spirent/ixia) based on the data provided in the data yaml file. <br>

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
.get_running_config_dict() :- 
   Get show running-config output
        Args:
            device (`obj`): Device object
            option (`str`): option command
        Returns:
            config_dict (`dict`): dict of show run output
</pre>

### trigger_verify_issu :- <br>
We now call the function trigger_verify_issu() from the generic_utils.lib file. This function first checks if all the required parameters are passed correctly in the matrix.csv file. Now we check the current image on the box with the help of .api.get_running_image() function. <br>

<pre>
   get_running_image() :-
      Get running image on the device
        Args:
            device (`obj`): Device object
        Returns:
            kickstart (`str`): Kickstart image
            system (`str`): System image
</pre>

We now execute the command "show module" to display module status and information and command "show version" to display the configuration of the system hardware, the software version, the names and sources of configuration files, and the boot images. <br>

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

Now if file does not already exits we use api.copy_to_device() fucntion to Copy file from linux server to the device :- <br>

<pre>
   copy_to_device() :-
      Copy file from linux server to the device
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

If epld_upgrade set as 1 in issu_matrix.csv file then we copy epld_image to the box using api.copy_to_device(). We pass epld_image as argument to the copy_to_device() function. <br>

### Compatibility Check :- <br>
Execute command "show incompatibility-all nxos + <issu_image>" and store the output in variable out. Now if statement "Enable/Disable command : Deactivate iCAM using 'install deactivate icam'" is present in out. The script shows a warning Please remove icam configs from device. So we execute the command 'install deactivate icam' to remove icam configs from device. <br>

Then we execute the command "show boot mode". If this shows an error means LXC ISSU is not supported on current image/device and the function will show a warning and boot mode will be native.<br>

### Top of Rack (ToR) Architecture :- <br>

<pre>
   Top of rack (ToR) which is also known as In-Rack design. In this approach, the network access switch is 
   placed on the top of the server rack; hence, servers are directly connected to the network access switch. 
   This means that 1 or 2 Ethernet switches are directly installed inside the rack, therefore copper cables 
   stay inside the rack. It is cost-effective because it reduces the number of copper cables between racks. 
   The rack is linked to the data center network by an Ethernet switch, often through a fiber cable. This 
   fiber cable is a direct link from the common aggregation area to the rack.

   In the ToR approach, every rack in the data center network is a separate entity that eases its management. 
   Any change, upgrade, or malfunction in the rack usually affects that rack only. Fewer cables mean that one 
   can opt for better quality and higher bandwidth cables in the same budget.
</pre>

### End of Row (EoR) Architecture :- <br>

<pre>
   In EoR network design, there is a direct connection of each server in the rack with the end of row 
   aggregation switch. This eliminates the need to connect servers directly with the in-rack switch.
   
   Racks are normally arranged in such a way that they form a row, a cabinet or rack is positioned at the 
   end of this row. This rack has the row aggregation switch, which provides network connectivity to servers
   mounted in individual racks. This switch, a modular chassis-based platform, sometimes supports hundreds 
   of server connections. A large amount of cabling is required to support this architecture.

   In ToR each rack is an independent unit whereas in EoR the whole row of servers acts as a group within the 
   data center. Any issue with the row aggregation switch impacts the complete row of servers.
</pre>

Note : If an organization aims to save on operational costs then EoR configuration is preferred while ToR is the better choice if fault-tolerance is the ultimate goal. <br>

### Performing Standard ISSU on Top-of-Rack (ToR) Switches with a Single Supervisor :- <br>

<pre>
   The ToR Cisco Nexus 9300 platform switches and Cisco Nexus 3100 Series switches are the NX-OS switches 
   with single supervisors. Performing ISSU on the Cisco Nexus 9000 and 3100 Series switches causes the 
   supervisor CPU to reset and to load the new software version. After the CPU loads the updated version 
   of the Cisco NX-OS software, the system restores the control plane to the previous known configuration 
   and the runtime state and it gets in-sync with the data plane, thereby completing the ISSU process.
   
   The data plane traffic is not disrupted during the ISSU process. In other words, the data plane forwards 
   the packets while the control plane is being upgraded, any servers that are connected to the Cisco Nexus 
   9000 and 3100 Series switches do not see any traffic disruption. The control plane downtime during the 
   ISSU process is approximately less than 120 seconds.
</pre>

### Performing Enhanced ISSU on Top-of-Rack (ToR) Switches with a Single Supervisor :-

<pre>
   The Cisco NX-OS software normally runs directly on the hardware. However, configuring enhanced or 
   container-based ISSU on single supervisor ToRs is accomplished by creating virtual instances of the 
   supervisor modules and the line cards. With enhanced ISSU, the software runs inside a separate Linux 
   container (LXC) for the supervisors and the line cards. A third container is created as part of the 
   ISSU procedure, and it is brought up as a standby supervisor.

   The virtual instances (or the Linux containers) communicate with each other using an emulated Ethernet
   connection. In the normal state, only two Linux containers are instantiated: vSup1 (a virtual SUP 
   container in an active role) and vLC (a virtual linecard container). Enhanced ISSU requires 16G memory 
   on the switch.

   Note : When you are enabling enhanced ISSU for the first time, you have to reload the switch first.

   During the software upgrade with enhanced ISSU, the supervisor control plane stays up with minimal 
   switchover downtime disruption and the forwarding state of the network is maintained accurately during 
   the upgrade. The supervisor is upgraded first and the line card is upgraded next.

   Note : The data plane traffic is not disrupted during the ISSU process. The control plane downtime is 
   less than 6 seconds.
</pre>

To enable booting in the enhanced ISSU (LXC) mode, use the boot mode lxc command. This command is executed in the config mode. See the following sample configuration for more information: <br>

<pre>
   switch(config)# boot mode lxc
   Using LXC boot mode
   Please save the configuration and reload system to switch into the LXC mode.
   switch(config)# copy r s
   [########################################] 100%
   Copy complete.
</pre>

### LXC_issu variable is set as 1 :- <br>

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

### LXC_issu variable is set as 0 :- <br>

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

### Spanning tree ISSU-Impact :- <br>

If upgrade_type is "upgrade" and upgrade_subtype is "nondisruptive" we first verify show spanning-tree issu-impact by executing the command 'show spanning-tree issu-impact'. <br>

<pre>
ISSU has some requirements:

   1) No Topology change must be active in any STP instance
   2) Bridge assurance(BA) should not be active on any port (except MCT)
   3) There should not be any Non Edge Designated Forwarding port (except MCT)
   4) ISSU criteria must be met on the VPC Peer Switch as well
   
That list is generated when you run:
   "show spanning-tree issu-impact"

That command also runs through each item, and ensure the spanning-tree configuration validates for 
an ISSU.

Number one is fairly easy to validate. This will pass as long as your network isn’t actively going
through a topology change. It is common that a pair of 5Ks are set up in a vPC domain, and everything
is dual-homed off of the vPC domain, so topology changes are extremely rare, if they occur at all.

MCT stands for Multichassis Etherchannel Trunk, or more specifically known in a vPC design, the 
peer-link. Essentially this means that bridge assurance (BA) can’t be configured anywhere except 
the peer-link. Bridge assurance is very similar to Unidirectional Link Detection (UDLD) in that it
listens for the presence of BPDUs on a link. If BPDUs suddenly stop, it could indicate a failure to
maintain a loop-free topology, and will put the link into a spanning tree inconsistent state, blocking
the link and preventing a switching loop.

Spanning tree has a mode called portfast, and in the newer (relatively speaking) spanning tree mode
Rapid STP, they are called “edge ports”. This prevents the ports from cycling through the various
spanning-tree states, and simply begins forwarding traffic immediately.

This checks for the presence of designated ports that have not been configured as edge ports. This 
does not include root or blocked ports, so no edge configuration is needed for interfaces facing 
the spanning-tree root.

When UCS environment is set up in end-host mode, which causes the fabric interconnects to act like 
one big host NIC, so frames are not bridged between the ports on the device, they are forwarded on 
to their destination in a way where loops are not possible. The connectivity to UCS is accomplished
using two vPCs, which is inherently loop-free because of the way spanning-tree works.
</pre>

If this shows output ISSU cannot proceed then the show spanning-tree issu-impact failed and the function returns an error. <br>

### Compatibility Check :- <br>
Execute command "show incompatibility-all nxos + <issu_image>". If output contains 'The following configurations on active are incompatible with the system image' means show  incompatibility-all nxos failed and the script throws an error. <br>

We now execute the command 'show install all impact nxos ' + issu_image which checks the impact of upgrading the software before actually performing the upgrade. <br>

During the compatibility check, the following ISSU-related messages may appear in the Reason field: <br>

<pre>
       Reason Field Message                          Description
   Incompatible image for ISSU                   The Cisco NX-OS image to which you are attempting to upgrade 
                                                 does not support ISSU.
   
   Default upgrade is not hitless                By default, the software upgrade process is disruptive. You 
                                                 must configure the non-disruptive option to perform an ISSU.
</pre>

If we are doing "disruptive upgrade" with "epld_upgrade" and "upgrade_with_epld" variable set as 1. We assign issu_command variable as 

<pre>
   issu_command = 'install all epld '+epld_image_file+' nxos bootflash:' + issu_image
</pre>

If we are doing "disruptive upgrade" with "epld_upgrade" set as 1 and "upgrade_with_epld" variable set as 0. we assign :- <br> 

<pre>
   issu_command = 'install all nxos bootflash:' + issu_image
   epld_command = 'install epld '+epld_image_file+' module '+module_no
</pre>

For "disruptive upgrade" we assign :- <br>
<pre>
   issu_command = 'install all nxos bootflash:' + issu_image
</pre>

For downgrade write erase reload needed for ISSU Downgrade type so we first save boot variables and execute_change_boot_variable and pass get_running_image() as argument. Then we execute_copy_run_to_start() function and then reload the box at last with the help of execute_reload() function. <br>

<pre>
   execute_change_boot_variable() :-
      Set the boot variables
        Args:
            device ('obj'): Device object
            system ('str'): System image
            kickstart ('str'): Kickstart image
            timeout ('int'): Timeout in seconds
</pre>

<pre>
   get_running_image() :-
      Get running image on the device
        Args:
            device (`obj`): Device object
        Returns:
            kickstart (`str`): Kickstart image
            system (`str`): System image
</pre>
    
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

<pre>
   execute_reload() :-
      Reload device
        Args:
            device ('obj'): Device object
            prompt_recovery ('bool'): Enable/Disable prompt recovery feature. default: True
            reload_creds ('str'): Credential name defined in the testbed yaml file to be used during reload.     
            default: 'default'
            sleep_after_reload ('int'): Time to sleep after reload in seconds, default: 120
            timeout ('int'): reload timeout value, defaults 800 seconds.
            reload_command ('str'): reload command. default: 'reload'
            error_pattern ('list'): List of regex strings to check output for errors.
            devices ('list'): list of device names
            exclude_devices ('list'): excluded device list
        Usage:
            device.api.execute_reload(devices=['ce1', 'ce2', 'pe1'], error_pattern=[], sleep_after_reload=0)
</pre>


### Trigger_ISSU :- <br>

This function takes arguments : logger, device, issu_comand, issu_image and variables issu_nondisruptive_fail and lxc_issu. If ISSU fails this function returns error and script stops. <br>

For the following questions it gives following response :- <br>

<pre>
   dialog = 
   Do you want to continue with the installation - Yes
   Do you want to save the configuration - Yes
   Host kernel is not compatible with target image - None
   Not enough memeory for Swithcover based ISSU - None
   Running-config contains configuration that is incompatible with the new image - None

   dialog_nondisruptive_fail = 
   Do you want to save the configuration - Yes
   Switch will be reloaded for disruptive upgrade do you want to continue with the installation - No
   Do you want to continue with the installation - No
</pre>

Now if variable issu_nondisruptive_fail is set to 1 then with the help of execute_with_reply() function in which we send dialog_nondisruptive_fail and their response as argument else we give dialog and their respnse as arguments. Now if error occurs during this process the function throws a error and we disconnect from the device after giving it sleep time of 5 min. <br>

<pre>
    str1 = 'switch will reboot in 10 seconds.'
    str2 = 'Switching over onto standby'
    str3 = 'Install all currently is not supported'
    str4 = 'Switch is not ready for Install all yet'
    str5 = 'Rebooting the switch to proceed with the upgrade'
    str6 = 'Disruptive ISSU will be performed'
    str7 = 'Pre-upgrade check failed'
    str8 = 'Running-config contains configuration that is incompatible with the new image'
    str9 = 'preupgrade check failed - Upgrade needs to be disruptive!'
    str10 = 'Install has been successful'
    str11 = 'Switch will be reloaded for disruptive upgrade.'
    str12 = 'Do you want to continue with the installation (y/n)?  [n] n'
    str13 = 'Host kernel is not compatible with target image'
    str14 = 'Not enough memory for Swithcover based ISSU'
    
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
</pre>

What this function returns is stored in variables trigger_issu_result and fallback_lxc. If trigger_issu_result is set to 0 means ISSU not successful on device and the function throws an error. Else we give sleep time of 10 mins and wait for Active Sup up. <br>

### Enhanced ISSU fallback option (KEXEC LXC ISSU) :- <br>
<pre>
   Kexec is a system call that enables you to load and boot into another kernel from the currently 
   running kernel. This is useful for kernel developers or other people who need to reboot very 
   quickly without waiting for the whole BIOS boot process to finish.
   
   Due to recent PSIRT bug fixes in Linux Kernel change, Enhanced ISSU requires the kernel to 
   be upgraded as well.
   
   In order to support this, KEXEC based kernel upgrade is needed similar to Native mode ND 
   ISSU during LXC ISSU. Contol plane downtime will be longer as similar to traditional ISSU. 
   This feature will be supported from "I" release onwards. All the current test coverage for 
   LXC mode needs to be extended to eISSU fallback scenario.

   Verify ISSU fallback  with below message
               "Host kernel is not compatible with target image.
                 Full ISSU will be performed and control plane will be impacted."

   Currently, Fallback KEXEC LXC issue is triggered for two reasons:
      Target Image kernel version is not same as the current running kernel image
      Low available memory before LXC ISSU
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

If variable lxc_issu has been set as 1 then we Check VSUP after LXC Upgrade. So we execute device.parse("show module") and see if VSUP Validation after LXC Upgrade passed or failed. We use the show module command to display module status and information.<br> 



### EPLD Upgrade :- <br>

If epld_upgrade is set as 1 and upgrade_with_epld is set as 0 then we trigger epld and store it in variable epld_res. For this we use the function trigger_epld_upgrade() which takes logger, device, epld_command and epld_image_file as arguments. <br>

#### Trigger_epld_upgrade :- <br>

<pre>
   dialog = 
   Do you want to continue with the installation - Yes
   Do you want to save the configuration - Yes
   Host kernel is not compatible with target image - None 
   Not enough memeory for Swithcover based ISSU - None
   Running-config contains configuration that is incompatible with the new image - None
   Do you want to continue - Yes
</pre>

We execute this with the function execute_with_reply() and if this gives an error then we give sleep time of 5 min and disconnect from the device. <br>

Now we verify epld status for this we execute command "show install epld status" and sent this as an argument to .get_config_dict() function. If that contains statement "Status: EPLD Upgrade was Successful" then EPLD verification was successfull else function returns error.<br>

<pre>
.get_config_dict() :-
    Cast config to Configuration dict

        Args:
            config ('str'): config string
        Returns:
            Configuration dict
    
</pre>

If trigger_issu_result == 1 and lxc_issu == 1 and fallback_lxc == 1 and validate_issu_result == 1 then we collect control plane downtime stats after completing the fallback LXC ISSU. <br>

Now if validate_issu_result is set as 1 that means no errors occured in the above processes and ISSU Validation successful on device. <br>


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

