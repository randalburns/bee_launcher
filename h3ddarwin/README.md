
<h3> Launching H3D on Darwin </h3>

Right now this only works for a single node.  More coming.

To launch a single node.
````
python launch_node.py 1 test ./template_dkrh3d.xml /projects/groups/vizproject/VMs/dkrh3dubu16.qcow2 ./tmp
````
Arguments are available through _python launch_node.py_ and are:
  * node identifier
  * virtual machine name
  * VM descriptor file
  * VM base image
  * working directory (place on RAM drive or SSD to be fast)

To terminate a launched code (stop docker), but not stop the virtual machines.
````
python stopdocker.py
````
You will still be able to log into the VMs to examine, visualize, etc. output.

To teardown a cluster (all virtual machines and their images
````
python terminatecluster.py test ./template_dkrh3d.xml ./tmp
````
Arguments are available through _python terminatecluster.py_ and are:
  * node identifier
  * virtual machine name
  * VM descriptor file
  * working directory 


<h3> Randal's Notes--not helpful for you</h3>


Passwordless ssh.

ssh -i darwindkr.rsa docker@.......


Thin provision a new image based on a COW of a base image.

Thin provision two images:

qemu-img create -b /projects/groups/vizproject/VMs/dkrubu16.qcow2 -f qcow2 ./tmp/dkr001.qcow2
qemu-img create -b /projects/groups/vizproject/VMs/dkrubu16.qcow2 -f qcow2 ./tmp/dkr002.qcow2

Create two definition files, changing the name, uuid, mac, and disk

cp template_dkrubu16.xml tmp/dkr001.xml
cp template_dkrubu16.xml tmp/dkr002.xml

sed -i s/NNNNNN/dkr001/ tmp/dkr001.xml
sed -i s/UUUUUU/0001/ tmp/dkr001.xml
sed -i s/MM:MM:MM/00:00:01/ tmp/dkr001.xml
sed -i s#FFFFFF#$PWD/tmp/dkr001.qcow2# tmp/dkr001.xml

sed -i s/NNNNNN/dkr002/ tmp/dkr002.xml
sed -i s/UUUUUU/0002/ tmp/dkr002.xml
sed -i s/MM;MM:MM/00:00:02/ tmp/dkr002.xml
sed -i s#FFFFFF#$PWD/tmp/dkr002.qcow2# tmp/dkr002.xml

launch_cluster.virsh -- is an example script

# got to get the ip addresses



####### Old

For d1
  name -> d1
  uuid last four 7F99 -> 0001
  source file ->   <source file='/home/randalburns/bee/tmp/d1.qcow2'/>
  mac last four 43:18 -> FF:01

For d2
  name -> d2
  uuid last four 7F99 -> 0002
  source file ->   <source file='/home/randalburns/bee/tmp/d2.qcow2'/>
  mac last four 43:18 -> FF:02

Launch VMs by scripting virsh

Here are the interactive commands:
  connect qemu:///system
  define /home/randalburns/bee/tmp/d1.xml
  define /home/randalburns/bee/tmp/d2.xml
  start d1
  start d2
