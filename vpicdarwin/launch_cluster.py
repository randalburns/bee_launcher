import argparse
import os
import subprocess
import re
import tempfile

def main():

  parser = argparse.ArgumentParser(description='Launch H3D in a VM on this darwin node')
  parser.add_argument('--verbose', action="store_true")
  parser.add_argument('--interactive', action="store_true")
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

    runname = "vpicdkr_{}".format(node)
    runimg = "{}/{}.qcow2".format(os.path.abspath(result.tmpdir),runname)
    runxml = "{}/{}.xml".format(os.path.abspath(result.tmpdir),runname) 

    cmd=["qemu-img","create","-b","{}".format(qcow2image),"-f","qcow2","{}".format(runimg)]
    if result.verbose:
      print cmd
    subprocess.call(cmd)

    cmd = ["cp","{}".format(template),"{}".format(runxml)]
    if result.verbose:
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
    if result.verbose:
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
    if result.verbose:
      print cmd
    subprocess.call(cmd)

    cmd = ["ssh","{}".format(node),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x 'git clone https://github.com/randalburns/vpicdocker.git'".format(os.path.dirname(os.path.realpath(__file__)),nodeip)]
    if result.verbose:
      print cmd
    subprocess.call(cmd)

    cmd = ["ssh","{}".format(node),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x 'cd /home/docker/vpicdocker; git checkout darwin'".format(os.path.dirname(os.path.realpath(__file__)),nodeip)]
    if result.verbose:
      print cmd
    subprocess.call(cmd)


    if node == masternode:

      masterip = nodeip
      master_prv_ip = '10.0.0.{}'.format(nodeid)

      #start the NFS server on the master node.
      cmd = ["ssh","{}".format(node),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x sudo /etc/init.d/nfs-kernel-server start".format(os.path.dirname(os.path.realpath(__file__)),nodeip)]
      if result.verbose:
        print cmd
      subprocess.call(cmd)


    # build container and run sshd on all slave VMs
    else:
      cmd = ["ssh","{}".format(node),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x /home/docker/vpicdocker/build_vpic.sh".format(os.path.dirname(os.path.realpath(__file__)),nodeip)]
      if result.verbose:
        print cmd
      subprocess.call(cmd)

      cmd = ["ssh","{}".format(node),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x sudo mount {}:/vmshare /vmshare".format(os.path.dirname(os.path.realpath(__file__)),nodeip,master_prv_ip)]
      if result.verbose:
        print cmd
      subprocess.call(cmd)

      cmd = ["ssh","{}".format(node),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x 'nohup /home/docker/vpicdocker/run_sshd.sh > /home/docker/vpicdocker/vpicerrlog.out 2>&1 &'".format(os.path.dirname(os.path.realpath(__file__)),nodeip)]
      if result.verbose:
        print cmd
      subprocess.call(cmd)

  # build the machinefile
  mfilestr = ""
  for mpiaddr in mpiaddrs:
    # VPIC only tolerates certain decompositions
    if len(result.node) == 2:
      mfilestr += "{}:4\n".format(mpiaddr)
    elif len(result.node) == 4:
      mfilestr += "{}:2\n".format(mpiaddr)
    else:
      print "Bad VPIC domain decomposition.  Talk to Randal or David."

  # build a machinefile
  cmd = ["ssh","{}".format(masternode),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x 'cat > /home/docker/vpicdocker/machinefile'".format(os.path.dirname(os.path.realpath(__file__)),masterip)]
  p = subprocess.Popen ( cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
  output = p.communicate(input=mfilestr)

  # now build the master container -- must have machinefile first
  cmd = ["ssh","{}".format(masternode),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x /home/docker/vpicdocker/build_vpic.sh".format(os.path.dirname(os.path.realpath(__file__)),masterip)]
  if result.verbose:
    print cmd
  subprocess.call(cmd)

  if not result.interactive:
    # start the code on the master
    cmd = ["ssh","{}".format(masternode),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x 'nohup /home/docker/vpicdocker/run_vpic.sh > /home/docker/vpicdocker/vpicrunlog.out 2>&1 &'".format(os.path.dirname(os.path.realpath(__file__)),masterip)]
    if result.verbose:
      print cmd
    subprocess.call(cmd)
  else:
    print "Launching in interactive mode.  Login to master to start simulation."

  # Give the user information.
  if result.verbose:
    print cmd
  print 'Master node {} VM IP {}.'.format(masternode,masterip)
  print r"ssh -t {} 'ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{}'".format(masternode,os.path.dirname(os.path.realpath(__file__)),masterip)
 


if __name__ == "__main__":
  main()
