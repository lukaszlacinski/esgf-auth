from social_core.backends.oauth import BaseOAuth2
from six.moves.urllib_parse import urlencode, unquote

from jwt import DecodeError, ExpiredSignature, decode as jwt_decode

import os
from base64 import b64encode
from OpenSSL import crypto
from urlparse import urlparse

from openid.yadis.services import getServiceEndpoints

class ESGFOAuth2(BaseOAuth2):
    name = 'esgf'
    AUTHORIZATION_URL = 'https://slcs.ceda.ac.uk/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://slcs.ceda.ac.uk/oauth/access_token'
    CERTIFICATE_URL = 'https://slcs.ceda.ac.uk/oauth/certificate/'
    DEFAULT_SCOPE = ['https://slcs.ceda.ac.uk/oauth/certificate/']
#    REDIRECT_STATE = False
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('access_token', 'access_token', True),
        ('expires_in', 'expires_in', True),
        ('refresh_token', 'refresh_token', True),
        ('private_key', 'private_key', True),
        ('certificate', 'certificate', True),
        ('openid', 'openid', True)
    ]


    # PSA does not encode redirect_uri if REDIRECT_STATE=False
    def auth_url(self):
        openid = self.strategy.session_get('openid', None)
#        self.set_urls(openid)
        """Return redirect url"""
        state = self.get_or_create_state()
        params = self.auth_params(state)
        params.update(self.get_scope_argument())
        params.update(self.auth_extra_arguments())
        params = urlencode(params)
        return '{0}?{1}'.format(self.authorization_url(), params)


    def set_urls(self, openid):
        uri, endpoints = getServiceEndpoints(openid)
        endpoints = applyFilter(openid, r)
        for e in endpoints:
            if e.matchTypes(['urn:esg:security:oauth:endpoint:authorize']):
                self.AUTHORIZATION_UR = e.uri
            elif e.matchTypes(['urn:esg:security:oauth:endpoint:access']):
                self.ACCESS_TOKEN_UR = e.uri
            elif e.matchTypes(['urn:esg:security:oauth:endpoint:resource']):
                self.CERTIFICATE_UR = e.uri
                self.DEFAULT_SCOP = [e.url]


    def get_certificate(self, access_token):
        """ Generate a new key pair """
        key_pair = crypto.PKey()
        key_pair.generate_key(crypto.TYPE_RSA, 2048)
        self.private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key_pair).decode('utf-8')

        """ Generate a certificate request """
        cert_request = crypto.X509Req()
        cert_request.set_pubkey(key_pair)
        cert_request.sign(key_pair, 'md5')
        cert_request = crypto.dump_certificate_request(crypto.FILETYPE_ASN1, cert_request)

        headers = {'Authorization': 'Bearer {}'.format(access_token)}
        url = self.CERTIFICATE_URL

        request_args = {'headers': headers,
                        'data': {'certificate_request': b64encode(cert_request)}
        }
        response = self.request(url, method='POST', **request_args)
        self.cert = response.text
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, response.text)
        self.subject = cert.get_subject()
        return (self.private_key, self.cert, self.subject.commonName)


    # extract user info from an X.509 user certificate
    def user_data(self, access_token, *args, **kwargs):
        print 'user_data'
        pkey, cert, openid = self.get_certificate(access_token)
        username = os.path.basename(urlparse(openid).path)
        return {'uid': openid,
                'username': username
                }


    def get_user_details(self, response):
        print 'get_user_details'
        print response
        access_token = response.get('access_token')
        pkey, cert, openid = self.get_certificate(access_token)
        username = os.path.basename(urlparse(openid).path)
        return {'private_key': pkey,
                'certificate': cert,
                'openid': openid,
                'username': username}


    def get_user_id(self, details, response):
        print 'get_user_id'
        print details['openid']
        return details['openid']
