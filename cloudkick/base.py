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

__all__ = ["Connection"]

import os
import urllib
from oauth import oauth

try:
  import json
except:
  import simplejson as json

API_CALLS = {
 '1.0': {
         'nodes': {
           'endpoint': 'query/nodes',
           'arguments': {
              'query': {
                'name': 'query',
                'description': 'Cloudkick query',
                'type': 'query_string',
                'required': True,
                'default_value': 'all',
                'valid_values': []
               }
            },
           'description': 'Return a list of nodes matching a query.',
           'wiki_url': '',
         },

         'checks': {
            'endpoint': 'query/check',
            'arguments': {},
            'description': 'Return a list of checks.',
            'wiki_url': '',
         },

         'live_data': {
            'endpoint': 'query/node/%(node_id)s/check/%(check_name)s',
            'arguments': {
              'node_id': {
                'name': 'node_id',
                'description': 'Node ID',
                'type': 'url',
                'required': True,
                'default_value': None,
                'valid_values': []
              },
              'check_name': {
                'name': 'check_name',
                'description': 'Check name',
                'type': 'url',
                'required': True,
                'default_value': 'cpu',
                'valid_values': [ 'cpu', 'mem', 'disk' ]
                }
            },
            'description': 'Return live data for the specified check.',
            'wiki_url': '',
         },

         'check_data': {
            'endpoint': 'query/check/data',
            'arguments': {
              'check_id': {
                'name': 'metric.0.id',
                'description': 'Metric ID',
                'type': 'query_string',
                'required': True,
                'default_value': None,
                'valid_values': []
              },
              'metric_name': {
                'name': 'metric.0.name',
                'description': 'Metric name',
                'type': 'query_string',
                'required': True,
                'default_value': None,
                'valid_values': []
              },
              'start': {
                'name': 'start',
                'description': 'Start time',
                'type': 'query_string',
                'required': True,
                'default_value': None,
                'valid_values': [],
                'format_function': lambda x: x.strftime('%s')
              },
              'end': {
                'name': 'end',
                'description': 'End time',
                'type': 'query_string',
                'required': True,
                'default_value': '',
                'valid_values': [ ],
                'format_function': lambda x: x.strftime('%s')
              },
              'interval': {
                'name': 'interval',
                'description': 'Interval',
                'type': 'query_string',
                'required': True,
                'default_value': 20,
                'valid_values': []
              }
            },
             'description': 'Return check data.',
             'wiki_url': '',
         },

         'monitor_ips': {
           'endpoint': 'monitor_ips',
           'arguments': {},
           'description': 'Return a list of Cloudkick monitoring IPs.',
           'wiki_url': '',
         },

},

 '2.0': {
        'checks_by_status': {
           'endpoint': 'status/nodes',
           'arguments': {
              'status': {
                'name': 'overall_check_statuses',
                'description': 'Check status',
                'type': 'query_string',
                'required': True,
                'default_value': 'Error',
                'valid_values': [ 'Ok', 'Error', 'Warning' ]
              },
              'include_metrics': {
                'name': 'include_metrics',
                'description': 'Include metrics in the response?',
                'type': 'query_string',
                'required': False,
                'default_value': '',
                'valid_values': [ 'true', 'false' ]
               }
           },
           'description': 'Return a list of checks with a given status.',
           'wiki_url': '',
        },
        'checks_by_id': {
           'endpoint': 'status/nodes',
           'arguments': {
              'check_id': {
                'name': 'check_id',
                'description': 'Check ID',
                'type': 'query_string',
                'required': True,
                'default_value': '',
                'valid_values': []
              },
              'include_metrics': {
                'name': 'include_metrics',
                'description': 'Include metrics in the response?',
                'type': 'query_string',
                'required': False,
                'default_value': '',
                'valid_values': [ 'true', 'false' ]
               }
           },
           'description': 'Return a list of checks filter on check ID.',
           'wiki_url': '',
        },
        'checks_by_monitor_id': {
           'endpoint': 'status/nodes',
           'arguments': {
              'monitor_id': {
                'name': 'monitor_id',
                'description': 'Monitor ID',
                'type': 'query_string',
                'required': True,
                'default_value': '',
                'valid_values': []
               }
           },
           'description': 'Return a list of checks filter on monitor ID.',
           'wiki_url': '',
        },
        'checks_by_query': {
           'endpoint': 'status/nodes',
           'arguments': {
              'query': {
                'name': 'query',
                'description': 'Cloudkick query',
                'type': 'query_string',
                'required': True,
                'default_value': '',
                'valid_values': []
              },
              'include_metrics': {
                'name': 'include_metrics',
                'description': 'Include metrics in the response?',
                'type': 'query_string',
                'required': False,
                'default_value': '',
                'valid_values': [ 'true', 'false' ]
              }
           },
           'description': 'Return a list of checks filter on Cloudkick query.',
           'wiki_url': '',
         }
    }
}


class Connection(object):
  """
  Cloudkick API Connection Object

  Provides an interface to the Cloudkick API over an HTTPS connection,
  using OAuth to authenticate requests.
  """

  API_SERVER = "api.cloudkick.com"

  def __init__(self, config_path = None, oauth_key = None, oauth_secret = None):
    self.__oauth_key = oauth_key or None
    self.__oauth_secret = oauth_secret or None
    if config_path is None:
      config_path = [os.path.join(os.path.expanduser('~'), ".cloudkick.conf"), "/etc/cloudkick.conf"]
    if not isinstance(config_path, list):
      config_path = [config_path]
    self.config_path = config_path

  def _read_config(self):
    errors = []
    for path in self.config_path:
      try:
        fp = open(path, 'r')
        return self._parse_config(fp)
      except Exception, e:
        errors.append(e)
        continue
    raise IOError("Unable to open configuration files: %s %s" %
                      (", ".join(self.config_path),
                       ", ".join([str(e) for e in errors])))

  def _parse_config(self, fp):
    for line in fp.readlines():
      if len(line) < 1:
        continue
      if line[0] == "#":
        continue
      parts = line.split()
      if len(parts) != 2:
        continue
      key = parts[0].strip()
      value = parts[1].strip()
      if key == "oauth_key":
        self.__oauth_key = value
      if key == "oauth_secret":
        self.__oauth_secret = value

  @property
  def oauth_key(self):
    if not self.__oauth_key:
      self._read_config()
    return self.__oauth_key

  @property
  def oauth_secret(self):
    if not self.__oauth_secret:
      self._read_config()
    return self.__oauth_secret

  def _api_request(self, call, api_version, kwargs):
    if api_version not in API_CALLS.keys():
      raise ValueError('Invalid API version: %s' % (api_version))

    call_dict = API_CALLS[api_version][call]
    required_arguments = [key for key, values in call_dict['arguments'].items() if
                          values['required']]

    query_string_values = {}
    url_values = {}
    post_values = {}
    for key, values in call_dict['arguments'].iteritems():
      kwarg_value = kwargs.get(key, None)
      if values['required'] and values['default_value'] and not \
         key in kwargs:
         kwarg_value = values['default_value']

      if values['required'] and not kwarg_value:
        raise ValueError('Missing required argument: %s' % (key))

      if not values['required'] and not kwarg_value:
        continue

      if values['valid_values'] and kwarg_value not in values['valid_values']:
        raise ValueError('Invalid value %s for argument %s, valid values are: %s' %
                         (kwarg_value, key, ', ' . join(values['valid_values'])))

      argument_type = values['type']
      argument_name = values['name']
      format_function = values.get('format_function', None)

      if format_function:
        kwarg_value = format_function(kwarg_value)

      if argument_type == 'query_string':
        query_string_values[argument_name] = kwarg_value
      elif argument_type == 'url':
        url_values[argument_name] = kwarg_value
      elif argument_type == 'post':
        post_values[argument_name] = kwarg_value

    path = '/%s/%s' % (api_version, call_dict['endpoint'])
    kwarg_dict = self._build_request_kwarg_dict(path,
                                                query_string_values,
                                                url_values, post_values)
    return self._request_json(**kwarg_dict)

  def _build_request_kwarg_dict(self, path, query_string_values, url_values,
                                post_values):

    if url_values:
      path = path % url_values

    parameters = query_string_values or {}
    post_values = post_values or {}

    kwarg_dict = { 'url': path, 'parameters': parameters,
                   'method': 'POST' if post_values else 'GET' }
    return kwarg_dict

  def _request(self, url, parameters, method='GET'):
    signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
    consumer = oauth.OAuthConsumer(self.oauth_key, self.oauth_secret)
    url = 'https://' + self.API_SERVER + url
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer,
                                                                http_url=url,
                                                                parameters=parameters)
    oauth_request.sign_request(signature_method, consumer, None)
    url = oauth_request.to_url()
    f = urllib.urlopen(url)
    s = f.read()
    return s

  def _request_json(self, *args, **kwargs):
    r = self._request(*args, **kwargs)

    try:
      return json.loads(r)
    except ValueError:
      return r

  def nodes(self, **kwargs):
    nodes = self._api_request('nodes', '1.0', kwargs)
    return nodes

  def checks(self, **kwargs):
    checks = self._api_request('checks', '1.0', kwargs)
    return checks

  def live_data(self, **kwargs):
    live_data = self._api_request('live_data', '1.0', kwargs)
    return live_data

  def check_data(self, **kwargs):
    data = self._api_request('check_data', '1.0', kwargs)
    return data

  def monitor_ips(self, **kwargs):
    data = self._api_request('monitor_ips', '1.0', kwargs)
    return data

  def checks_by_status(self, **kwargs):
    data = self._api_request('checks_by_status', '2.0', kwargs)
    return data

  def checks_by_id(self, **kwargs):
    data = self._api_request('checks_by_id', '2.0', kwargs)
    return data

  def checks_by_monitor_id(self, **kwargs):
    data = self._api_request('checks_by_monitor_id', '2.0', kwargs)
    return data

  def checks_by_query(self, **kwargs):
    data = self._api_request('checks_by_query', '2.0', kwargs)
    return data
