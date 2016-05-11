
<h3> Launching H3D on Darwin </h3>

These scripts launch, login, stop and teardown a cluster running H3D on Darwin.
It is customized for Darwin and will not work without modification on other clusters.

<h5> Launch a Cluster </h5>

````
  python launch_cluster.py <template.xml> <machine_img.qcow2> <run_directory> --node <node0> --node <node1> ... --node <noden>
````
  * template.xml: describes the KVM configuration for each node's virtual machine.  The repository provides _./template\_dkrh3d.xml_ for nodes on the galton partition.
  * machine\_img.qcow2: a virtual machine image that contains the source code (research do not distributed) in expected places.  You should use _/projects/groups/vizproject/VMs/dkrh3dubu16.img_ unless you have customized an image.
  * run_directory: temporary directory used to run the cluster.  This needs to be shared among all nodes in the cluster.  It would be desirable to place this on memory or an SSD if/when shared fast storage is available.
  * --node <node1>: add one entry for each node.  Machine name only, not FQDN.
A typical launch process might look like:
````
darwin-fe> salloc -N 2 -p galton
darwin-fe> squeue -u <username>       // say this returns cn180 and cn181
darwin-fe> python launch\_cluster.py ./template\_dkrh3d.xml /projects/groups/vizproject/VMs/dkrh3dubu16.img ./tmp --node cn180 --node cn181

This script will do the following:
 * thin provision virtual machines from the base image--it will not change the given machine image.
 * launch a virtual machine on each node
 * build the H3D docker image on each machine
 * launch docker images waiting to receive requests on all nodes
 * start the code on the master (first) node
 * return an an ssh string to log into the master virtual machine
The code output will appear in the virtual machine in directory /h3dshared/h3drun/data and the log in /h3shared/h3drun/3dhout.log.  This will only work on the __galton__ partition on Darwin.  It requires a second network interface only available on these nodes.

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
