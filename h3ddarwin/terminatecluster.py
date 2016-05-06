import argparse
import os
import subprocess
import re


def main():

  parser = argparse.ArgumentParser(description='Launch H3D in a VM on this darwin node')
  parser.add_argument('nodeid', type=int, action="store")
  parser.add_argument('nodename', action="store" )
  parser.add_argument('template', action="store" )
  parser.add_argument('tmpdir', action="store" )

  result = parser.parse_args()

  template = os.path.abspath(result.template)

  runname = "dkr_{}".format(result.nodename)
  runimg = "{}/{}.qcow2".format(os.path.abspath(result.tmpdir),runname)
  runxml = "{}/{}.xml".format(os.path.abspath(result.tmpdir),runname) 

  cmd = ["virsh",r"connect qemu:///system; destroy {}".format(runname)]
  print cmd
  subprocess.call(cmd)

  cmd=["rm", "{}".format(runimg)]
  print cmd
  subprocess.call(cmd)

  cmd=["rm", "{}".format(runxml)]
  print cmd
  subprocess.call(cmd)

if __name__ == "__main__":
  main()
