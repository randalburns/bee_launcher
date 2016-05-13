

import argparse
import os
import subprocess
import re


def main():

  parser = argparse.ArgumentParser(description='Stop docker on nodes, but leave virtual machines up.')
  parser.add_argument('--node', action="append")
  parser.add_argument('--verbose', action="store_true")

  result = parser.parse_args()

  nodeid = 0

  for node in sorted(result.node):

    m = re.match('cn(\d+)',node)
    nodeid = int(m.group(1))

    runname = "h3ddkr_{}".format(node)

    cmd = ["ssh","{}".format(node),"-x",r"/usr/sbin/arp -n | grep 00:00:{0:02x}".format(nodeid)]
    output = subprocess.check_output(cmd)
    m = re.match("(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", output)
    nodeip = m.group(1)

    cmd = ["ssh","{}".format(node),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x /home/docker/h3ddocker/stop_h3d.sh".format(os.path.dirname(os.path.realpath(__file__)),nodeip)]
    if result.verbose:
      print cmd
    subprocess.call(cmd)


if __name__ == "__main__":
  main()
