#!/usr/bin/python -W ignore::DeprecationWarning
# -*- coding: utf-8 -*-
###
#
# List the amount of managed machines by vRA for each tenant
#
# Author: Sebastian Kirsch
# Date: 03.05.2017
#
###
#

import sys
import json
import re
import requests
import argparse


### CONFIG ###
vracenter = 'VRA-HOST.domain.tld'
vrauser = 'VRA-ADMIN-USER'
vrapass = 'ADMIN-PASSWORD'
tenants = ['TENANT-1', 'TENANT-2']
### END CONFIG ###


### FUNCTIONS ###
def GetArgs():
	parser = argparse.ArgumentParser(description='Display information about virtual machines managed by vRA')
	parser.add_argument('-q', '--quiet', required=False, action='store_true', help='Supress output')
	return parser.parse_args()
def GetToken(tenant):
	tokenurl = 'https://' + vracenter + '/identity/api/tokens'
	headers = {"Content-type" : "application/json", "Accept" : "application/json"}
	data = '{"username":"' + vrauser + '","password":"' + vrapass + '","tenant":"' + tenant + '"}'
	response = requests.post(tokenurl, data=data, headers=headers)
	tokenval = 'Bearer ' + response.json()['id']
	return tokenval
### END FUNCTIONS ###


### MAIN ###
vmtotal = 0
listofvm = []

requests.packages.urllib3.disable_warnings()
args = GetArgs()
params = {'page' :  '1', 'limit' : '500', 'orderby' : 'name'}

for tenant in tenants:
	vmlist = []
	tenantvms = {}

	# Get security token for tenant
	token = GetToken(tenant)

	# Set http headers
  	headers = {'Content-type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}

  	# Get managed machines in tenant
  	vmurl = 'https://' + vracenter + '/catalog-service/api/consumer/resources/types/Infrastructure.Machine/'
  	response = requests.get(vmurl, params=params, headers=headers)
  	vmdata = response.json()
  	for vm in vmdata['content']:
		vmlist.append(str(vm['name']))

	# Write infos to list
	vmtotal = vmtotal + len(vmlist)
	tenantvms['tenantname'] = tenant
	tenantvms['vmcount'] = len(vmlist)
	listofvm.append(tenantvms)

# Output
if not args.quiet:
	print "--------------------------------"
	print "    Managed Virtual Machines    "
	print "--------------------------------"
	for vms in listofvm:
		print "Tenant '" + vms['tenantname'] + "' :  " + str(vms['vmcount'])
	print ""
	print "Managed VMs Total: " + str(vmtotal)
	print ""

sys.exit(0)

### END MAIN ###
# EOF
