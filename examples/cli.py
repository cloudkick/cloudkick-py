#!/usr/bin/env python
from optparse import OptionParser

from cloudkick.base import Connection

def create_node_wizard(conn):
  name = raw_input('Name: ') 
  ip = raw_input('IP: ')
  print conn.create_node(name=name, ip_address=ip)

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
  parser.add_option('--list-nodes', dest='list_nodes',
                    action='store_true',
                    help='Show all your nodes')
  (options, args) = parser.parse_args()
  if options.create_node:
    create_node_wizard(c)
  if options.list_nodes:
    list_nodes(c)

