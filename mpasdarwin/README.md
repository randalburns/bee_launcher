
<h3> Launching MPAS on Darwin </h3>

These scripts launch, login, stop and teardown a cluster running MPAS on Darwin.
It is customized for Darwin and will not work without modification on other clusters.

<h5> Checkout the mpasdarwin from github </h5>
Launcher script for mpasdarwin is under the directory of bee_launcher 
````
  darwin-fe> git clone http://github.com/randalburns/bee_launcher
  darwin-fe> cd bee_launcher/mpasdarwin
````
You have to change the access permission to the keys
````
  darwin-fe> chmod 600 darwindkr.pub darwindkr.rsa
````
Then you need to create the run_directory; in this example, we use tmp 
````
  darwin-fe> mkdir tmp
````

<h5> Launch a Cluster </h5>

````
  python launch_cluster.py <template.xml> <machine_img.qcow2> <run_directory> --node <node0> --node <node1> ... --node <noden>
````
  * template.xml: describes the KVM configuration for each node's virtual machine.  The repository provides _./template\_qgmpas.xml_ for nodes on the galton partition. If you want to change the virtual machine configuration, for example, more memory or more cpus, please refer to _https://libvirt.org/formatdomain.html_ for the instruction of modifying a domain configuration file.
  * machine\_img.qcow2: a virtual machine image that contains the source code (research do not distributed) in expected places.  You should use _/projects/groups/vizproject/VMs/qgmpasubu16.img_ unless you have customized an image.
  * run_directory: temporary directory used to run the cluster.  This needs to be shared among all nodes in the cluster.  It would be desirable to place this on memory or an SSD if/when shared fast storage is available.
  * --node <node1>: add one entry for each node.  Machine name only, not FQDN.
  * --verbose: produce verbose output
  * --interactive: launch the cluster but don't start the code.  You will have to log into the master and start manually.

A typical launch process might look like:
````
darwin-fe> salloc -N 2 -p galton
darwin-fe> squeue -u <username>       // say this returns cn180 and cn181
darwin-fe> python launch_cluster.py ./template_qgmpas.xml /projects/groups/vizproject/VMs/qgmpasubu16.qcow2 ./tmp --node cn180 --node cn181
````

This script will do the following:
 * thin provision virtual machines from the base image--it will not change the given machine image.
 * launch a virtual machine on each node
 * build the mpas docker image on each machine
 * launch docker images waiting to receive requests on all nodes
 * start the code on the master (first) node
 * return an ssh string to log into the master virtual machine
#(The code output will appear in the virtual machine in directory /vmshare/mpasrun/ and the log in /vmshare/mpasrun/3dhout.log.  This will only work on the __galton__ partition on Darwin.  It requires a second network interface only available on these nodes.)

<h5> Stop a Cluster </h5>

````
  python stop_cluster.py --node <node0> --node <node1> ... --node <noden>
````

This will stop the docker containers on each virtual machine and leave the virtual machines intact.  Use this to halt a completed code and then login to the master node to view/download output.

<h5> Terminate a Cluster</h5>

This will destroy all the virtual machines and remove all data.  You __MUST__ get your data out before you run this.

````
  python terminate_cluster.py <machine_img.qcow2> <run_directory> --node <node0> --node <node1> ... --node <noden>
````

<h3> Customzing MPAS </h3>

The code launches a preconfigured virtual machine image _/projects/groups/vizprojects/VMs/qgmpasubu16.qcow2_ 
that contains the BEE-atified VPIC code from Darwin in /home/docker/mpasdocker in branch darwin.  The BEE-atified code
is publically available at https://github.com/randalburns/mpasdocker.git.

To customize the code, you can launch the cluster interactively, edit/pull customizations to the 
BEE-atified launch scripts and run manually.  To automate customizations you will need to 
create a customized virtual machine base image.  See https://darwin.lanl.gov/projects/virtualized-environments/wiki/Virtual_Machine_Images_on_Darwin. 

