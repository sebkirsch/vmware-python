#!/usr/bin/python -W ignore::DeprecationWarning
# -*- coding: utf-8 -*-
###
#
# List the Usage of all vSAN 6.x Datastores
#
# Author: Sebastian Kirsch
# Date:   20.06.2017
#
###
#
import sys
import ssl
import re
import argparse

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim


### CONFIG ###
vcenter = 'VCENTER-NAME.domain.tld'
vcuser = 'administrator@vsphere.local'
vcpass = 'ADMIN-PASSWORD'
### END CONFIG ###


### FUNCTIONS ###
def ConvertSize(size):
    gbsize = (size / 1073741824)
    return gbsize
def GetArgs():
    parser = argparse.ArgumentParser(description='Display information about VSAN usage')
    parser.add_argument('-q', '--quiet', required=False, action='store_true', help='Supress output')
    return parser.parse_args()
### END FUNCTIONS ###


### MAIN ###

# Change to following line to match a substring of your vsan datastore
vsanre = re.compile('^((vsanDS|VxRail)\-)+')

listofvsan = []
vc = None
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_NONE
args = GetArgs()

try:
    # Get datastore infos
    vc = connect.SmartConnect(host=vcenter,user=vcuser,pwd=vcpass,sslContext=context)
    content = vc.RetrieveContent()
    objview = content.viewManager.CreateContainerView(content.rootFolder,[vim.Datastore],True)
    datastores = objview.view
    objview.Destroy()

    # Iterate over all datastores
    for ds in datastores:
        vsan = {}
        summary = ds.summary

        # Get vsan usage data
        if vsanre.match(summary.name):
            vsan['name'] = summary.name
            vsan['capacity'] = summary.capacity
            vsan['free'] = summary.freeSpace
            vsan['used'] = summary.capacity - summary.freeSpace
            vsan['provisioned'] = (summary.capacity - summary.freeSpace) + summary.uncommitted
            listofvsan.append(vsan)

    # Output
    if not args.quiet:
        print "--------------------------------"
        print "          VSAN usage"
        print "--------------------------------"
        for stor in listofvsan:
            print "Name: " + str(stor['name'])
            print "Capacity: " + str(ConvertSize(stor['capacity'])) + " GB"
            print "Free: " + str(ConvertSize(stor['free'])) + " GB"
            print "Used: " + str(ConvertSize(stor['used'])) + " GB"
            print "Provisioned: " + str(ConvertSize(stor['provisioned'])) + " GB"
            print "--------------------------------"
        print ""

    sys.exit(0)

except Exception as error:
    if not args.quiet:
        print "ERROR: " + str(error)
        sys.exit(1)

finally:
    if vc != None:
        connect.Disconnect(vc)

### END MAIN ###

# EOF
