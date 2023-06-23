# ISSU_Tool_Automation

Common Setup section :- <br>
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
In this section we configure the devices that we connected to in the connect_devices section. We feature bash shell and copy the running config to startup config. When device config is successful we save the device configuration.

get_issu_matrix :- <br>
Takes 5 arguments : self, testbed, testscript, issu_matrix_file, logger <br>
In this section we take the arguments given by the user in the issu_matrix.csv file and store the information. We store switch_alias, to_image(the image we want to upgrade or downgrade the box), to_image_path(the path where the image is located), upgrade_type(upgrade or downgrade), upgrade_subtype(disruptive or nondisruptive). Give lxc_issu as 0 if you dont want that else provide with additional informtion i.e. epld_upgrade, epld_image and odule_no in the issu_matrix file.

