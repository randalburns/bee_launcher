

import argparse
import os
import subprocess
import re



def main():

  parser = argparse.ArgumentParser(description='Launch H3D in a VM on this darwin node')
  parser.add_argument('--node', action="append")

  result = parser.parse_args()

  nodeid = 0

  for node in sorted(result.node):

    nodeid = nodeid+1

    runname = "dkr_{}".format(node)

    cmd = ["ssh","{}".format(node),"-x",r"/usr/sbin/arp -n | grep 00:00:{0:02}".format(nodeid)]
    output = subprocess.check_output(cmd)
    m = re.match("(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", output)
    masterip = m.group(1)

    cmd = ["ssh","{}".format(node),"-x",r"ssh -o StrictHostKeyChecking=no -i {}/darwindkr.rsa docker@{} -x /home/docker/h3ddocker/stopcluster.sh".format(os.path.dirname(os.path.realpath(__file__)),masterip)]
    print cmd
    subprocess.call(cmd)


if __name__ == "__main__":
  main()
