#!/usr/bin/python
# This is a script that can take an ansible inventory file
# and print the groups of a group
# Extremely poor looking python to json string replacement
# at the bottom.  Feel free to improve :)
## http://docs.ansible.com/ansible/developing_api.html

# Single:
## Return a list of one host in each child group


import argparse
# for parsing the existing inventory
from ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
# for producing json
import json
# checking if inventory_file exists
import os.path
# for exiting with non-zero rc
import sys

###args
parser = argparse.ArgumentParser(description='Different inventory script')
parser.add_argument('--inventory', dest='inventory_file', action='store', default='hosts')
parser.add_argument('--list', dest='list', action='store_true')
parser.add_argument('--host', dest='host', action='store')
parser.add_argument('--group', dest='group', action='store')
parser.add_argument('--json', dest='json', action='store_true')
parser.add_argument('--single', dest='single', action='store_true')

args = parser.parse_args()

inventory_file = args.inventory_file
host = args.host
llist = args.list
chosen_group = args.group
want_json = args.json
single = args.single

dict_hosts = {}
dict_single_hosts = {}
dict_groups = {}
dict_groups2 = {}

def hostfunction(host):
  print host
  print "Host"

def listfunction(llist):
  variable_manager = VariableManager()
  loader = DataLoader()
  if not os.path.isfile(inventory_file):
    print "%s is not a file - halting" % inventory_file
    sys.exit(1)
  else:
    inventory = Inventory(loader=loader, variable_manager=variable_manager,  host_list=inventory_file)

  groups = inventory.groups
  for group in groups:
      dogroup = inventory.get_group(group)
      if dogroup.child_groups:
        list_of_hosts = dogroup.child_groups
        list_of_hosts2 = ','.join("'{0}'".format(x) for x in list_of_hosts)
        list_of_hosts3 = list_of_hosts2.replace('["', '[')
        list_of_hosts4 = list_of_hosts3.replace('"]', ']')
        # the three lists
        dict_groups2[group] = list_of_hosts # used with single
        dict_groups[group] = [ list_of_hosts4 ] # used with list and group
        dict_hosts[group] = inventory.list_hosts(group) # used with single

# make a dict that only has one host per child group
  if chosen_group:
    dict_single_hosts[chosen_group] = []
    for host in dict_hosts[chosen_group]:
      groups_for_host = inventory.groups_for_host(str(host))

      for group in groups_for_host:
        if group in dict_groups2[chosen_group]:
          #this host is in one of the child groups of the chosen_group
          if len(dict_single_hosts[chosen_group]) == 0:
            dict_single_hosts[group] = [ host ]

# here we populate dict_single_hosts so that the chosen_group entry only has a list of 3 hosts that are in three separate child groups
  for group in dict_single_hosts:
    if chosen_group == group:
      continue
    if len(dict_single_hosts[chosen_group]) < ( len(dict_single_hosts) - 1 ):
      for host in dict_single_hosts[group]:
        dict_single_hosts[chosen_group].append(host)

# here we quote them 

  if single:
    list_of_single_hosts = dict_single_hosts[chosen_group]
    list_of_single_hosts2 = ','.join("'{0}'".format(x) for x in list_of_single_hosts)
    dict_single_hosts[chosen_group] = []
    dict_single_hosts[chosen_group] = [ list_of_single_hosts2 ]
##########

#######

  if chosen_group:
    if single:
      return(dict_single_hosts[chosen_group])
    else:
      return(dict_groups[chosen_group])
  else:
    return(dict_groups)

#########
if args.host:
    print hostfunction(args.host)
elif args.list:
    if want_json:
      hostlist = str(listfunction(args.list))
      hostlist2 = hostlist.replace('["', '[')
      hostlist3 = hostlist2.replace('"]', ']')
      hostlist4 = hostlist3.replace('^"', '')
      hostlist5 = hostlist4.replace('"$', '')
      hostlist6 = hostlist5.replace("u'", "'")
      hostlist7 = hostlist6.replace("'", '"')
      print hostlist7
      #print json.dumps(hostlist5)
    else:
      print listfunction(args.list)
elif args.group:
    if want_json:
      hostlist = str(listfunction(args.group))
      hostlist2 = hostlist.replace('["', '[')
      hostlist3 = hostlist2.replace('"]', ']')
      hostlist4 = hostlist3.replace('^"', '')
      hostlist5 = hostlist4.replace('"$', '')
      if not single:
        hostlist6 = hostlist5.replace("u'", "'")
      else:
        hostlist6 = hostlist5
      hostlist7 = hostlist6.replace("'", '"')
      print '{ "%s" : %s }' % (args.group,hostlist7)
      #print json.dumps(hostlist5)
      #print json.dumps(listfunction(args.group))
    else:
      print listfunction(args.group)
