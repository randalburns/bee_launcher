import argparse
import os
import subprocess
import re
import tempfile

def main():

  parser = argparse.ArgumentParser(description='Launch H3D in a VM on this darwin node')
  parser.add_argument('--node', action="append")
  parser.add_argument('template', action="store" )
  parser.add_argument('qcow2image', action="store" )
  parser.add_argument('tmpdir', action="store" )

  result = parser.parse_args()

  qcow2image = os.path.abspath(result.qcow2image)
  template = os.path.abspath(result.template)

  for node in sorted(result.node):

    m = re.match('cn(\d+)',node)
    nodeid = int(m.group(1))

    runname = "h3ddkr_{}".format(node)
    runimg = "{}/{}.qcow2".format(os.path.abspath(result.tmpdir),runname)
    runxml = "{}/{}.xml".format(os.path.abspath(result.tmpdir),runname) 

    cmd=["qemu-img","create","-b","{}".format(qcow2image),"-f","qcow2","{}".format(runimg)]
    print cmd
    subprocess.call(cmd)

    cmd = ["cp","{}".format(template),"{}".format(runxml)]
    print cmd
    subprocess.call(cmd)

    # Rewrite the template
    cmd = ["sed","-i","s/NNNNNN/{}/".format(runname),"{}".format(runxml)]
    subprocess.call(cmd)
    cmd = ["sed","-i","s/UUUUUU/{0:06d}/".format(nodeid),"{}".format(runxml)]
    subprocess.call(cmd)
    cmd = ["sed","-i","s/MM:MM:MM/00:00:{0:02x}/".format(nodeid),"{}".format(runxml)]
    subprocess.call(cmd)
    cmd = ["sed","-i","s#FFFFFF#{}#".format(runimg),"{}".format(runxml)]
    subprocess.call(cmd)

    cmd = ["ssh","{}".format(node),"-x",r"virsh 'connect qemu:///system; define {}; start {}'".format(runxml,runname)]
    print cmd
    subprocess.call(cmd)

  print "Waiting 10 seconds for nodes to come up";
  import time; time.sleep(10)

  mpiaddrs = []

  masternode = sorted(result.node)[0]

  # launch the ssh daemons and build the hostfile and machinefile
  for node in sorted(result.node):

    m = re.match('cn(\d+)',node)
    nodeid = int(m.group(1))

    cmd = ["ssh","{}".format(node),"-x",r"/usr/sbin/arp -n | grep 00:00:{0:02x}".format(nodeid)]
    output = subprocess.check_output(cmd)
    m = re.match("(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", output)
    nodeip = m.group(1)

    mpiaddrs.append('10.0.0.{}'.format(nodeid))

    # activate the second interface on the darwin node
    cmd = ["ssh", "{}".format(node),"-x", r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x 'sudo /sbin/ifconfig ens8 10.0.0.{} netmask 255.255.255.0'".format(os.path.dirname(os.path.realpath(__file__)),nodeip,nodeid)]
    print cmd
    subprocess.call(cmd)

    if node == masternode:

      masterip = nodeip
      master_prv_ip = '10.0.0.{}'.format(nodeid)

      #start the NFS server on the master node.
      cmd = ["ssh","{}".format(node),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x sudo /etc/init.d/nfs-kernel-server start".format(os.path.dirname(os.path.realpath(__file__)),nodeip)]
      print cmd
      subprocess.call(cmd)


    # build container and run sshd on all slave VMs
    else:

      cmd = ["ssh","{}".format(node),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x /home/docker/h3ddocker/build_h3d.sh".format(os.path.dirname(os.path.realpath(__file__)),nodeip)]
      print cmd
      subprocess.call(cmd)

      cmd = ["ssh","{}".format(node),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x sudo mount {}:/h3dshare /h3dshare".format(os.path.dirname(os.path.realpath(__file__)),nodeip,master_prv_ip)]
      print cmd
      subprocess.call(cmd)

      cmd = ["ssh","{}".format(node),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x 'nohup /home/docker/h3ddocker/run_sshd.sh > /home/docker/h3ddocker/h3derrlog.out 2>&1 &'".format(os.path.dirname(os.path.realpath(__file__)),nodeip)]
      print cmd
      subprocess.call(cmd)

  # build the machinefile
  mfilestr = ""
  for mpiaddr in mpiaddrs:
    mfilestr += "{}:16\n".format(mpiaddr)

  # build a machinefile
  cmd = ["ssh","{}".format(masternode),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x 'cat > /home/docker/h3ddocker/machinefile'".format(os.path.dirname(os.path.realpath(__file__)),masterip)]
  p = subprocess.Popen ( cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
  output = p.communicate(input=mfilestr)

  # now build the master container -- must have machinefile first
  cmd = ["ssh","{}".format(masternode),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x /home/docker/h3ddocker/build_h3d.sh".format(os.path.dirname(os.path.realpath(__file__)),masterip)]
  print cmd
  subprocess.call(cmd)

  # start the code on the master
  cmd = ["ssh","{}".format(masternode),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x 'nohup /home/docker/h3ddocker/run_h3d.sh > /home/docker/h3ddocker/h3drunlog.out 2>&1 &'".format(os.path.dirname(os.path.realpath(__file__)),masterip)]
  print cmd
  subprocess.call(cmd)

  # Give the user information.
  print "Launched H3D on a Darwin cluster with masterr node."
  print 'Node {} VM IP {}.'.format(masternode,masterip)
  print r"ssh -t {} 'ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{}'".format(masternode,os.path.dirname(os.path.realpath(__file__)),masterip)
 


if __name__ == "__main__":
  main()
