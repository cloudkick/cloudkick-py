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
"""
Interactive Cloudkick Shell for testing the API.
"""

import re
import cmd
import sys
import readline
import os.path
from pprint import pprint
from os.path import join

from cloudkick.base import Connection, API_CALLS

IGNORED_CMDS = [ 'login' ]

def get_available_cmds():
  functions = Connection.__dict__
  functions = [ func for func in functions if
               not func.startswith('_') and
               callable(getattr(Connection, func))]

  return functions

def ignore_exception(fn):
  def wrapped(*args, **kwargs):
    try:
      return fn(*args, **kwargs)
    except CmdError, e:
      print 'Error: %s' % (e.message)
    except IOError, e:
      error = repr(e).lower()
      if error.find('unauthorized') != -1:
        shell_instance = args[0]
        print 'Error: You have provided invalid credentials, please ' + \
              'login again.'
        setattr(shell_instance, '_connection', None)
    except Exception, e:
      print repr(e)
  return wrapped

def authentication_required(fn):
  def wrapped(*args, **kwargs):
    connection = args[0]._connection

    if not connection:
      raise CmdError('You need to be authenticated to use this command.')

    return fn(*args, **kwargs)
  return wrapped

class CmdError(Exception):
  def __init__(self, message):
    self._message = message

  def _get_message(self):
      return self._message

  def _set_message(self, message):
      self._message = message

  message = property(_get_message, _set_message)

class CloudkickShell(cmd.Cmd):

  prompt = '> '
  use_raw_input = True
  
  def __init__(self, *args, **kwargs):
    self._connection = self._build_connection_instance()

    self._save_history = True
    self._history_file = join(os.path.expanduser('~'), '.cloudkick_history')

    self._read_history()
    readline.parse_and_bind('tab: complete')

    cmd.Cmd.__init__(self, *args, **kwargs)

  def do_status(self, line):
    if not self._connection:
      login_status = 'not authenticated'
    else:
      login_status = 'authenticated using the following key: %s.' % \
                     (self._connection.oauth_key)
    print 'History save to a file status: %s' % ('enabled' if self._save_history else
                                                'disabled')
    print 'Login status: %s' % (login_status)

  def do_history(self, line):
    if line.find('on') != -1 or line.find('enable') != -1:
      if self._save_history:
        print 'History save is already enabled.'
      else:
        self._save_history = True
        print 'Done.'
    elif line.find('off') != -1 or line.find('disable') != -1:
      if not self._save_history:
        print 'History save is already disabled.'
      else:
        self._save_history = False
        print 'Done.'
    else:
      if not line:
        print 'Missing argument.'
      else:
        print 'Invalid argument: %s' % (line)

  def help_history(self):
    print 'Enable or disable saving of history to a file.\n'
    print 'Usage: history on|off'

  @ignore_exception
  def do_login(self, line):
    if self._connection:
      print 'You are already authentication.\n' + \
            'If you want to change the account first type logout and then login.'
      return

    kwargs = self._parse_arguments(line, ['key', 'secret'])
    connection = self._build_connection_instance(kwargs['key'], kwargs['secret'])

    self._connection = connection
    print 'Done.'

  def help_login(self):
    print 'Description: Logs you in using the provided credentials.'
    print 'Arguments:\n\nkey - oauth key\nsecret - oauth secret'

  def do_logout(self, line):
    if not self._connection:
      print 'You are not authenticated.'
      return

    self._connection = None
    print 'Done.'

  def help_logout(self):
    print 'Logs you out.'

  def do_commands(self, line):
    self.do_help(line)

  def do_quit(self, line):
    self._write_history()
    sys.exit()

  def do_q(self, line):
    self.do_quit(line)

  def help_quit(self):
    print 'Quits the application'

  def help_q(self):
    self.help_quit()

  def _parse_arguments(self, line, expected_arguments=None,
                       argument_order=None):
    argument_order = argument_order or []
    expected_arguments = expected_arguments or {}
    argument_matches = re.findall(r'(\w+)=(\w+|".*?")', line)

    argument_dict = {}
    if argument_matches:
      for key, value in argument_matches:
        argument_dict[key] = value.replace('"', '')

    if not set(expected_arguments).issubset(argument_dict.keys()):
      missing_args = set(expected_arguments) - set(argument_dict.keys())
      raise CmdError('Missing required argument(s): %s' %
                     (', ' . join(missing_args)))

    return argument_dict

  def _read_history(self):
    if self._save_history:
      readline.read_history_file(self._history_file)

  def _write_history(self):
    if self._save_history:
      history_len = readline.get_current_history_length()

      to_remove_indexes = []
      for index in range(0, history_len):
        line = readline.get_history_item(index)

        # Don't save API credentials
        for cmd in IGNORED_CMDS:
          if line.find(cmd) != -1:
            to_remove_indexes.append(index)

      removed_count = 0
      for index in to_remove_indexes:
        readline.remove_history_item(index - removed_count)
        removed_count += 1
      readline.write_history_file(self._history_file)

  def _build_connection_instance(self, oauth_key=None, oauth_secret=None):
    connection = Connection(oauth_key=oauth_key, oauth_secret=oauth_secret)

    try:
      connection.oauth_key
    except Exception, e:
      # cloudkick.conf could not be found, user must provide key and secret
      # manually
      return None

    return connection

def get_cmd_dict(cmd):
  api_versions = API_CALLS.keys()

  cmd_dict = {}
  cmd_list = []
  for api_version in api_versions:
    for key in API_CALLS[api_version].keys():
      cmd_dict[key] = api_version

  api_version = cmd_dict[cmd]
  return API_CALLS[api_version][cmd]

def build_handler(cmd):
  @ignore_exception
  @authentication_required
  def handler(shell_instance, line):
    cmd_dict = get_cmd_dict(cmd)
    cmd_args = [key for key, values in cmd_dict['arguments'].items() if
                values['required'] and not values['default_value']]
    kwargs = shell_instance._parse_arguments(line, cmd_args)

    result = getattr(shell_instance._connection, cmd)(**kwargs)
    pprint(result)
  return handler

def build_help(cmd):
  def help(shell_instance):
    cmd_dict = get_cmd_dict(cmd)
    description = cmd_dict['description']
    arguments = cmd_dict['arguments']

    help_text = 'Description: %s\n' % (description)

    arguments_list = []
    if len(arguments) > 0:
      for key, values in arguments.iteritems():
        valid_values = values['valid_values']
        if valid_values:
          valid_values_string = '(valid values: %s)' % (', ' . join(valid_values))
        else:
          valid_values_string = ''
        arguments_list.append('%s - %s %s' % (key, values['description'],
                                              valid_values_string))
      help_text += 'Arguments: \n\n%s' % \
                    ('\n' . join(arguments_list))
    else:
      help_text += 'Arguments: none'
    print help_text
  return help

def build_shell():
  shell = CloudkickShell

  functions = get_available_cmds()
  for func in functions:
    setattr(shell, 'do_%s' % (func), build_handler(func))
    setattr(shell, 'help_%s' % (func), build_help(func))

  shell = shell()
  return shell

def start():
  banner = 'Welcome to the Cloudkick API shell!\n\n' + \
           'Type "commands" for a list all the available commands ' + \
           'and "help <command>" to see help for the specified command'

  shell = build_shell()

  try:
    shell.cmdloop(banner)
  except KeyboardInterrupt:
    sys.exit(0)

if __name__ == '__main__':
  start()
