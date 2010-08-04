#!/usr/bin/env python

# hackity hack hack mchackersons. I am too lazy to fix my paths in bash-land
import sys, os
sys.path.insert(0, '../')

from optparse import OptionParser
from cloudkick.base import Connection

def create_node_wizard(conn):
  name = raw_input('Name: ')
  ip = raw_input('IP: ')
  print conn.create_node(name=name, ip_address=ip)

def create_check_wizard(conn):
  node_id = raw_input('Node id: ')
  _type = raw_input('Check type: ')
  details = raw_input('Check Details: ')
  print conn.create_check(node_id, _type, details)

def create_address_wizard(conn):
  name = raw_input('Name: ')
  _type = raw_input('Address type: ')
  details = raw_input('Address Details: ')
  print conn.create_address(name, _type, details)

def list_addresses(conn):
  print conn.list_addresses()

def _node_formatter(node):
  return '%s %20s %20s' % (node['id'], node['name'], node['ipaddress'])

def list_nodes(conn):
  print '%s %20s %20s' % ('id', 'name', 'ipaddress')
  for n in c.nodes():
    print _node_formatter(n)
  
if __name__ == "__main__":
  c = Connection()
  parser = OptionParser()
  parser.add_option('--create-node', dest='create_node',
                    action='store_true',
                    help='Create a new node')
  parser.add_option('--create-check', dest='create_check',
                    action='store_true',
                    help='Create a new check')
  parser.add_option('--create-address', dest='create_address',
                    action='store_true',
                    help='Create a new email/sms/pagerduty/webhook alert address')
  parser.add_option('--list-addresses', dest='list_addresses',
                    action='store_true',
                    help='List all alert addresses')
  parser.add_option('--list-nodes', dest='list_nodes',
                    action='store_true',
                    help='Show all your nodes')
  (options, args) = parser.parse_args()
  if options.create_node:
    create_node_wizard(c)
  if options.create_check:
    create_check_wizard(c)
  if options.create_address:
    create_address_wizard(c)
  if options.list_addresses:
    list_addresses(c)
  if options.list_nodes:
    list_nodes(c)
