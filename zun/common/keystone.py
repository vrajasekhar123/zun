# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from keystoneauth1.access import access as ka_access
from keystoneauth1.identity import access as ka_access_plugin
from keystoneauth1.identity import v3 as ka_v3
from keystoneauth1 import loading as ka_loading
from keystoneclient.v3 import client as kc_v3
from oslo_log import log as logging

from zun.common import exception
from zun.common.i18n import _LE
import zun.conf

CONF = zun.conf.CONF
CFG_GROUP = 'keystone_auth'
CFG_LEGACY_GROUP = 'keystone_authtoken'
LOG = logging.getLogger(__name__)

keystone_auth_opts = (ka_loading.get_auth_common_conf_options() +
                      ka_loading.get_auth_plugin_conf_options('password'))

CONF.import_group('keystone_authtoken', 'keystonemiddleware.auth_token')
ka_loading.register_auth_conf_options(CONF, CFG_GROUP)
ka_loading.register_session_conf_options(CONF, CFG_GROUP)
CONF.set_default('auth_type', default='password', group=CFG_GROUP)
CONF.import_opt('auth_uri', 'keystonemiddleware.auth_token',
                group='keystone_authtoken')


class KeystoneClientV3(object):
    """Keystone client wrapper so we can encapsulate logic in one place."""

    def __init__(self, context):
        self.context = context
        self._client = None
        self._session = None

    @property
    def auth_url(self):
        # FIXME(pauloewerton): auth_url should be retrieved from keystone_auth
        # section by default
        return CONF[CFG_LEGACY_GROUP].auth_uri.replace('v2.0', 'v3')

    @property
    def auth_token(self):
        return self.session.get_token()

    @property
    def session(self):
        if self._session:
            return self._session
        auth = self._get_auth()
        session = self._get_session(auth)
        self._session = session
        return session

    def _get_session(self, auth):
        session = ka_loading.load_session_from_conf_options(
            CONF, CFG_GROUP, auth=auth)
        return session

    def _get_auth(self):
        if self.context.is_admin:
            auth = ka_loading.load_auth_from_conf_options(CONF, CFG_GROUP)
        elif self.context.auth_token_info:
            access_info = ka_access.create(body=self.context.auth_token_info,
                                           auth_token=self.context.auth_token)
            auth = ka_access_plugin.AccessInfoPlugin(access_info)
        elif self.context.auth_token:
            auth = ka_v3.Token(auth_url=self.auth_url,
                               token=self.context.auth_token)
        else:
            LOG.error(_LE('Keystone API connection failed: no password '
                          'or token found.'))
            raise exception.AuthorizationFailure()

        return auth

    @property
    def client(self):
        if self._client:
            return self._client
        client = kc_v3.Client(session=self.session)
        self._client = client
        return client
