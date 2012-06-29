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

from setuptools import setup

setup(
    name='cloudkick',
    version='0.2.0-dev',
    description='',
    author='Cloudkick, Inc.',
    author_email='support@cloudkick.ccom',
    packages=[
        'cloudkick_api',
    ],
    package_dir={
        'cloudkick_api': 'cloudkick_api',
    },
    license='Apache License (2.0)',
    url='https://support.cloudkick.com/API',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires='oauth',
)
