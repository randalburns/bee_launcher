

import argparse
import os
import subprocess
import re



def main():

  parser = argparse.ArgumentParser(description='Launch H3D in a VM on this darwin node')
  parser.add_argument('nodeid', type=int, action="store")
  parser.add_argument('nodename', action="store" )
  parser.add_argument('template', action="store" )
  parser.add_argument('qcow2image', action="store" )
  parser.add_argument('tmpdir', action="store" )

  result = parser.parse_args()

  qcow2image = os.path.abspath(result.qcow2image)
  template = os.path.abspath(result.template)

  runname = "dkr_{}".format(result.nodename)
  runimg = "{}/{}.qcow2".format(os.path.abspath(result.tmpdir),runname)
  runxml = "{}/{}.xml".format(os.path.abspath(result.tmpdir),runname) 

  cmd=["qemu-img","create","-b","{}".format(qcow2image),"-f","qcow2","{}".format(runimg)]
  print cmd
  subprocess.call(cmd)

  cmd = ["cp","{}".format(template),"{}".format(runxml)]
  print cmd
  subprocess.call(cmd)


  cmd = ["sed","-i","s/NNNNNN/{}/".format(runname),"{}".format(runxml)]
  print cmd
  subprocess.call(cmd)


  cmd = ["sed","-i","s/UUUUUU/{0:06d}/".format(result.nodeid),"{}".format(runxml)]
  print cmd
  subprocess.call(cmd)


  cmd = ["sed","-i","s/MM:MM:MM/00:00:{0:02d}/".format(result.nodeid),"{}".format(runxml)]
  print cmd
  subprocess.call(cmd)


  cmd = ["sed","-i","s#FFFFFF#{}#".format(runimg),"{}".format(runxml)]
  print cmd
  subprocess.call(cmd)

  cmd = ["virsh",r"connect qemu:///system; define {}; start {}".format(runxml,runname)]
  print cmd
  subprocess.call(cmd)

  print "Waiting 15 seconds for nodes to come up";
  import time; time.sleep(15)

  arp_ps= subprocess.Popen(('arp', '-n'), stdout=subprocess.PIPE)
  output = subprocess.check_output(['grep','00:00:{0:02}'.format(result.nodeid)], stdin=arp_ps.stdout)
  m = re.match("(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", output)
  masterip = m.group(1)


  cmd = ["ssh", "-i", "darwindkr.rsa", "docker@{}".format(masterip),  "-x", r'/home/docker/h3ddocker/build_h3d.sh']
  print cmd
  subprocess.call(cmd)

  cmd = ["ssh", "-i", "darwindkr.rsa", "docker@{}".format(masterip),  "-x", r'/home/docker/h3ddocker/run_h3d.sh']
  print cmd
  subprocess.call(cmd)


if __name__ == "__main__":
  main()
