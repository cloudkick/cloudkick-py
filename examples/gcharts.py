# Licensed to the Cloudkick, Inc under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# libcloud.org licenses this file to You under the Apache License, Version 2.0
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
try:
  import json
except:
  import simplejson as json


from cloudkick.base import Connection
from pprint import pprint
from pygooglechart import SimpleLineChart
from pygooglechart import Axis
from datetime import datetime, timedelta

def gchart(conn, node, check, metric, start=datetime.now()-timedelta(days=1), end=datetime.now()):
  data = conn.data(check['id'], name=metric, start=start, end=end)
  d = []
  ts = []
  for p in  data['metrics'][0]['data']:
    d.append(float(p['avg']))
    ts.append(p['ts'])

  # Chart size of 200x125 pixels and specifying the range for the Y axis
  max_y = int(max(d))
  chart = SimpleLineChart(450, 250, y_range=[0,max_y])
  chart.add_data(d)
  left_axis = range(0, max_y + 1, max_y/5)
  left_axis[0] = ''
  chart.set_axis_labels(Axis.LEFT, left_axis)
  min_dt = datetime.fromtimestamp(min(ts))
  max_dt = datetime.fromtimestamp(max(ts))
  chart.set_axis_labels(Axis.BOTTOM, [ str(min_dt), str(max_dt) ])
  title = '%s.%s.%s' % (node['name'], check['type'], metric)
  chart.set_title(title)
  return chart.get_url()

if __name__ == "__main__":
  c = Connection()
  nodes = c.nodes()
  node = nodes[20]
  print node
  checks = c.checks(node['id'])
  print checks
  check = checks[0][node['id']][0]
  print check
  metric = check['metrics'][1]
  print gchart(c, node=node, check=check, metric=metric)
