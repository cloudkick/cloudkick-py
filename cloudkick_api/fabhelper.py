# Licensed to Cloudkick, Inc ('Cloudkick') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# Cloudkick licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__all__ = ["hosts", "roledefs", "load"]

import sys
import re
from collections import defaultdict

from cloudkick_api.base import Connection

_CACHED_NODES = None

class RoleDefs:
    def __init__(self, roles):
        self.roles = roles
    
    def __contains__(self, key):
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False
        
    def __getitem__(self, query):
        roles = re.split(r'\s+', query)
        hosts = []
        if len(roles) == 1:
            # If first role is a negative, let's populate the list first with every host
            if roles[0][0] == '-':
                for role in self.roles:
                    for host in self.roles[role]:
                        if not host in hosts:
                            hosts.append(host)
            else:
                # Optimize if there is only one role
                return self.roles[roles[0]]
        
        for role in roles:
            if role[0] in ('-', '+'):
                direction = role[0]
                role = role[1:]
            else:
                direction = '+'
            
            if not role in self.roles:
                # Role doesn't exist, skip it
                continue
            if direction == '+':
                for host in self.roles[role]:
                    if not host in hosts:
                        hosts.append(host)
            elif direction == '-':
                for host in hosts:
                    for to_remove in self.roles[role]:
                        if to_remove in hosts:
                            hosts.remove(to_remove)
        if len(hosts) > 0:
            return hosts
        
        # Throw a KeyError to keep consistent with a dictionary
        raise KeyError(query)
    
    def __str__(self):
        return self.roles.__str__()
    
    def __repr__(self):
        return self.roles.__repr__()

def _get_data():
    global _CACHED_NODES
    if _CACHED_NODES is None:
        c = Connection()
        _CACHED_NODES = c.nodes.read()
    return _CACHED_NODES


def hosts():
    # TODO: need generic DNS (?)
    d = _get_data()
    if d and 'items' in d:
        return [node["ipaddress"] for node in d['items']]
    else:
        print "Problem extracting ipaddresses from (type=%s) %s" % (type(d), d)
        return None

def roledefs():
        rd = defaultdict(list)
        d = _get_data()
        if d and 'items' in d:
            for node in d['items']:
                if node["tags"]:
                    for t in node["tags"]:
                        rd[t["name"]].append(node["ipaddress"])
            return RoleDefs(rd)
        else:
            print "Problem extracting ipaddresses from (type=%s) %s" % (type(d), d)
            return None

def load(x = None):
    from fabric.api import env
    try:
        env.hosts = hosts()
        env.roledefs = roledefs()
    except IOError, e:
        # Don't print a huge stack trace if there's a problem. Most likely cloudkick.conf isn't in the path.
        print e
        sys.exit()
    return x
