

import argparse
import os
import subprocess
import re



def main():

  parser = argparse.ArgumentParser(description='Launch H3D in a VM on this darwin node')
  parser.add_argument('nodeid', type=int, action="store")

  result = parser.parse_args()

  arp_ps= subprocess.Popen(('arp', '-n'), stdout=subprocess.PIPE)
  output = subprocess.check_output(['grep','00:00:{0:02}'.format(result.nodeid)], stdin=arp_ps.stdout)
  m = re.match("(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", output)
  masterip = m.group(1)

  cmd = ["ssh", "-i", "darwindkr.rsa", "docker@{}".format(masterip),  "-x", r'/home/docker/h3ddocker/stopcluster.sh']
  print cmd
  subprocess.call(cmd)


if __name__ == "__main__":
  main()
