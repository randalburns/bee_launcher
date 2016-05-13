import argparse
import os
import subprocess
import re


def main():

  parser = argparse.ArgumentParser(description='Terminate all VMs on darwin.')
  parser.add_argument('--verbose', action="store_true")
  parser.add_argument('--node', action="append")
  parser.add_argument('template', action="store" )
  parser.add_argument('tmpdir', action="store" )

  result = parser.parse_args()

  template = os.path.abspath(result.template)

  for node in sorted(result.node):

    m = re.match('cn(\d+)',node)
    nodeid = int(m.group(1))

    runname = "vpicdkr_{}".format(node)
    runimg = "{}/{}.qcow2".format(os.path.abspath(result.tmpdir),runname)
    runxml = "{}/{}.xml".format(os.path.abspath(result.tmpdir),runname) 

    cmd = ["ssh","{}".format(node),"-x",r"virsh 'connect qemu:///system; destroy {}; undefine {}'".format(runname,runname)]
    if result.verbose:
      print cmd
    subprocess.call(cmd)

    cmd=["rm", "-f", "{}".format(runimg)]
    if result.verbose:
      print cmd
    subprocess.call(cmd)

    cmd=["rm", "{}".format(runxml)]
    if result.verbose:
      print cmd
    subprocess.call(cmd)

if __name__ == "__main__":
  main()
