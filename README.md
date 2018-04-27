ORACLE UNIFIED DIRECTORY Audit files retrieval automation script
README file
Execution Instructions:

Normally this script should be called by executing ../../ auto_audit_retrieval.bat. If this is the case, ignore this paragraph and move to edit configuration file on the final page. If for some reason manual execution is needed, follow the instructions bellow:
-	Open Command Prompt ( + R , type cmd on dialog and click OK)
 

-	Navigate to scripts folder using cd command

 
The folder should contain :
./auto.bat  , ./fetchOUD.conf , ./fetchOUD.py , ./prints.txt
You can check if every file exists using dir command.

-	Run the script :type auto.bat on cmd and press enter


fetchOUD.py will be executed according to the given configuration. All needed Audit files will be fetched from the hosts’ remote paths and downloaded to local path. After files are completely fetched, they will transformed to csv and finally will be consolidated to 3 files. Information messages are printed during the procedure. This procedure will be executed for every host.
 
By the time the procedure has finished, the output file name will be printed for every host


Final file name patterns :

merged_audit_<host_name>_OUD_<host_number>OUD_ACCESS.csv
merged_audit_<host_name>_OUD_<host_number>OUD_ERROR.csv
merged_audit_<host_name>_OUD_<host_number>OUD_ADMIN.csv
				

-	Edit configuration file : fetchOUD.conf

Using your desired Text Editor, open fetchOUD.conf and edit the needed parameters :
	The Time Period that Audit files were created
	Number of hosts
	Host Name / Host IP
	Cots type (OUD)
	An existing remote connection User for the selected host
	Correct Password for this User
	Remote Connection Port for Host’s SSH Server (default : 22)
	Remote Path, where OUD Audit files exist (default path: /u01/app/ldap_instance/OUD/logs/ )
	Local Path, were fetched files will be saved


Assume that there 4 OAG instances. Edit the configuration file like :
o	Set Number of Hosts : 4
o	Copy and paste Host Block 4 times 
o	Put the correct parameters for every host

A 4 hosts sample is included on this package.

