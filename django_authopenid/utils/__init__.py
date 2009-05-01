# -*- coding: utf-8 -*-
# Copyright 2007, 2008,2009 by Benoît Chesneau <benoitc@e-engura.org>
# 
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
#
import time
import urllib

from django.conf import settings
from django.http import str_to_unicode, get_host
from django.utils.html import escape

from openid.consumer.discover import discover
from openid.extensions import sreg, ax
try: # needed for some linux distributions like debian
    from openid.yadis import xri
except ImportError:
    from yadis import xri


class OpenID(object):
    def __init__(self, openid_, issued, attrs=None, sreg_=None, ax_=None):
        self.openid = openid_
        self.issued = issued
        self.attrs = attrs or {}
        self.sreg = sreg_ or {}
        self.ax = ax_
        self.is_iname = (xri.identifierScheme(openid_) == 'XRI')
    
    def __repr__(self):
        return '<OpenID: %s>' % self.openid
    
    def __str__(self):
        return self.openid
    
SUPPORTED_EXTENSIONS = {
    "http://openid.net/srv/ax/1.0": ax,
    'http://openid.net/sreg/1.0': sreg,
    'http://openid.net/extensions/sreg/1.1': sreg
}   

def discover_extensions(openid_url):
    service = discover(openid_url)
    found = []
    for endpoint in service[1]:
        found = filter(endpoint.usesExtension, SUPPORTED_EXTENSIONS.keys())
    return found

DEFAULT_NEXT = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')
def clean_next(next):
    if next is None:
        return DEFAULT_NEXT
    next = str_to_unicode(urllib.unquote(next), 'utf-8')
    next = next.strip()
    if next.startswith('/'):
        return next
    return DEFAULT_NEXT


def from_openid_response(openid_response):
    """ return openid object from response """
    issued = int(time.time())
    sreg_resp = sreg.SRegResponse.fromSuccessResponse(openid_response) \
            or []
    
    return OpenID(
        openid_response.identity_url, issued, openid_response.signed_fields, 
         dict(sreg_resp)
    )
    
def get_url_host(request):
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    host = escape(get_host(request))
    return '%s://%s' % (protocol, host)

def get_full_url(request):
    return get_url_host(request) + request.get_full_path()
    
