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
from collections import defaultdict

from cloudkick_api.base import Connection

_CACHED_NODES = None

class RoleDefs:
    _cache = {}

    def __init__(self, roles):
        self.roles = roles

    def _get_data(self, query):
        if not query in self._cache:
            c = Connection()
            self._cache[query] = c.nodes.read(query=query)

        return self._cache[query]

    def __contains__(self, key):
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def __getitem__(self, query):
        if query in self.roles:
            return self.roles[query]

        d = self._get_data(query)

        if d and 'items' in d and len(d['items']) > 0:
                return [node['ipaddress'] for node in d['items']]

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
