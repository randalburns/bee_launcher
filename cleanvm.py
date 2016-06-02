#!/usr/bin/env python
#
# ---------------------
# Destroy and undefine all active and inactive VMs on this node
# No input

from __future__ import print_function
import sys
import libvirt

# Connect to hypervisor
conn = libvirt.open('qemu:///system')
if conn == None:
    print('Failed to open connection to qemu:///system', file=sys.stderr)
    exit(1)

# All active domains
print("Clean all active domain names:")
activeIDs = conn.listDomainsID()
if len(activeIDs) != 0:
    for ID in activeIDs:
	try:
	    domain = conn.lookupByID(ID)
	    name = domain.name()
	    domain.destroy()
	    domain.undefine()
  	    print('  '+name)
	except libvirt.libvirtError, e:
	    print >> sys.stderr, 'Domain ={1} : {2}'.format(name, e)
	    continue
else:
    print('  None')

# All inactive domains
print("Clean all inactive domain names:")
activeDomains = conn.listDefinedDomains()
if len(activeDomains) != 0:
    for domain in activeDomains:
	try:
	    name = domain.name()
            print('  '+name)
	    domain.destroy()
	    domain.undefine()
	except libvirt.libvirtError, e:
	    print >> sys.stderr, 'Domain ={1} : {2}'.format(name, e)
else:
    print('  None')



conn.close()
exit(0)
