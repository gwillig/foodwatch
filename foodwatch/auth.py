from __future__ import absolute_import
from flask import Flask
import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import os
import sys
from pathlib import Path
from foodwatch.own_abort_exception import abort


sys.path.append('foodwatch')
import base64

AUTH0_DOMAIN = 'gwillig.eu.auth0.com'
ALGORITHMS = ['RS256']

API_AUDIENCE = 'foodwatchgw'

'#Read secret from file or env'
if "jwt_foodwatch" in os.environ.keys():
    secret = os.environ["jwt_foodwatch"]
else:
    path = Path(__file__).parent / "env.json"
    with open(path,'r') as env_file:
        env_dict = json.load(env_file)
        secret = env_dict["jwt_foodwatch"]

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def get_token_auth_header():
    """Gets the Token from the http authorization header
    """
    headerAuth = request.headers.get('Authorization', None)
    if not headerAuth:
        abort(4017)

    headerAuthList = headerAuth.split()

    if headerAuthList[0].lower() != 'bearer':
        abort(4018)
    token = headerAuthList[1]
    return token

'================================='
def check_permissions(permission, payload):
    if permission in payload["permissions"]:
        return True
    else:
        abort(4011)

'=================================================================='

def verify_decode_jwt(token):
    """Toke implementation of this function from the course """
    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # GET THE DATA IN THE HEADER
    unverified_header = jwt.get_unverified_header(token)

    # CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        abort(4012)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    # Finally, verify!!!
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            abort(4013)

        except jwt.JWTClaimsError:
            abort(4014)
        except Exception:
            abort(4015)
    abort(4016)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator