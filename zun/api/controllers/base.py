# All Rights Reserved.
#
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


class APIBase(object):

    def __init__(self, **kwargs):
        for field in self.fields:
            if field in kwargs:
                value = kwargs[field]
                setattr(self, field, value)

    def __setattr__(self, field, value):
        super(APIBase, self).__setattr__(field, value)

    def as_dict(self):
        """Render this object as a dict of its fields."""
        return {f: getattr(self, f)
                for f in self.fields
                if hasattr(self, f)}

    def __json__(self):
        return self.as_dict()

    def unset_fields_except(self, except_list=None):
        """Unset fields so they don't appear in the message body.

        :param except_list: A list of fields that won't be touched.

        """
        if except_list is None:
            except_list = []

        for k in self.as_dict():
            if k not in except_list:
                setattr(self, k, None)
