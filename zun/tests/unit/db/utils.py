#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""Zun test utilities."""

import json
import mock

from oslo_config import cfg

from zun.common import name_generator
from zun.db import api as db_api

CONF = cfg.CONF


def get_test_container(**kw):
    return {
        'id': kw.get('id', 42),
        'uuid': kw.get('uuid', 'ea8e2a25-2901-438d-8157-de7ffd68d051'),
        'container_id': kw.get('container_id', 'ddcb39a3fcec'),
        'name': kw.get('name', 'container1'),
        'project_id': kw.get('project_id', 'fake_project'),
        'user_id': kw.get('user_id', 'fake_user'),
        'image': kw.get('image', 'ubuntu'),
        'created_at': kw.get('created_at'),
        'updated_at': kw.get('updated_at'),
        'command': kw.get('command', 'fake_command'),
        'status': kw.get('status', 'Running'),
        'status_reason': kw.get('status_reason', 'Created Successfully'),
        'task_state': kw.get('task_state', 'container_creating'),
        'environment': kw.get('environment', {'key1': 'val1', 'key2': 'val2'}),
        'cpu': kw.get('cpu', 1.0),
        'memory': kw.get('memory', '512m'),
        'workdir': kw.get('workdir', '/home/ubuntu'),
        'ports': kw.get('ports', [80, 443]),
        'hostname': kw.get('hostname', 'testhost'),
        'labels': kw.get('labels', {'key1': 'val1', 'key2': 'val2'}),
        'meta': kw.get('meta', {'key1': 'val1', 'key2': 'val2'}),
        'addresses': kw.get('addresses', {
            'private': [
                {
                    'OS-EXT-IPS-MAC:mac_addr': 'fa:16:3e:04:da:76',
                    'version': 4,
                    'addr': '10.0.0.12',
                    'OS-EXT-IPS:type': 'fixed'
                },
            ],
        }),
        'image_pull_policy': kw.get('image_pull_policy', 'always'),
        'host': kw.get('host', 'localhost'),
        'restart_policy': kw.get('restart_policy',
                                 {'Name': 'no', 'MaximumRetryCount': '0'}),
        'status_detail': kw.get('status_detail', 'up from 5 hours'),
        'tty': kw.get('tty', True),
        'stdin_open': kw.get('stdin_open', True),
    }


def create_test_container(**kw):
    """Create test container entry in DB and return Container DB object.

    Function to be used to create test Container objects in the database.
    :param kw: kwargs with overriding values for container's attributes.
    :returns: Test Container DB object.
    """
    container = get_test_container(**kw)
    # Let DB generate ID if it isn't specified explicitly
    if CONF.db_type == 'sql' and 'id' not in kw:
        del container['id']
    dbapi = db_api._get_dbdriver_instance()
    return dbapi.create_container(kw['context'], container)


def get_test_image(**kw):
    return {
        'id': kw.get('id', 42),
        'uuid': kw.get('uuid', 'ea8e2a25-2901-438d-8157-de7ffd68d051'),
        'repo': kw.get('repo', 'image1'),
        'tag': kw.get('tag', 'latest'),
        'image_id': kw.get('image_id', 'sha256:c54a2cc56cbb2f0400'),
        'size': kw.get('size', '1848'),
        'project_id': kw.get('project_id', 'fake_project'),
        'user_id': kw.get('user_id', 'fake_user'),
        'created_at': kw.get('created_at'),
        'updated_at': kw.get('updated_at'),
    }


def create_test_image(**kw):
    """Create test image entry in DB and return Image DB object.

    Function to be used to create test Image objects in the database.
    :param kw: kwargs with overriding values for image's attributes.
    :returns: Test Image DB object.
    """
    image = get_test_image(**kw)
    # Let DB generate ID if it isn't specified explicitly
    if 'id' not in kw:
        del image['id']
    if 'repo' not in kw:
        image['repo'] = _generate_repo_for_image()
    dbapi = db_api._get_dbdriver_instance()
    return dbapi.pull_image(kw['context'], image)


def _generate_repo_for_image():
    '''Generate a random name like: zeta-22-image.'''
    name_gen = name_generator.NameGenerator()
    name = name_gen.generate()
    return name + '-image'


def get_test_zun_service(**kw):
    return {
        'id': kw.get('id', 23),
        'uuid': kw.get('uuid', '2e8e2a25-2901-438d-8157-de7ffd68d066'),
        'host': kw.get('host', 'fakehost'),
        'binary': kw.get('binary', 'fake-bin'),
        'disabled': kw.get('disabled', False),
        'disabled_reason': kw.get('disabled_reason', 'fake-reason'),
        'last_seen_up': kw.get('last_seen_up'),
        'forced_down': kw.get('forced_down', False),
        'report_count': kw.get('report_count', 13),
        'created_at': kw.get('created_at'),
        'updated_at': kw.get('updated_at'),
    }


def create_test_zun_service(**kw):
    zun_service = get_test_zun_service(**kw)
    # Let DB generate ID if it isn't specifiled explicitly
    if CONF.db_type == 'sql' and 'id' not in kw:
        del zun_service['id']
    dbapi = db_api._get_dbdriver_instance()
    return dbapi.create_zun_service(zun_service)


class FakeEtcdMultipleResult(object):

    def __init__(self, value):
        self.children = []
        for v in value:
            res = mock.MagicMock()
            res.value = json.dumps(v)
            self.children.append(res)


class FakeEtcdResult(object):

    def __init__(self, value):
        self.value = json.dumps(value)
