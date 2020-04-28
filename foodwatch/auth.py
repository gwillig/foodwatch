from __future__ import absolute_import
import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import os
import sys
from pathlib import Path

sys.path.append('foodwatch')
import base64

AUTH0_DOMAIN = 'gwillig.eu.auth0.com'
ALGORITHMS = ['RS256']

API_AUDIENCE = 'foodwatchgw'

'#Read secret from file or env'
if "jwt_foodwatch" in os.environ.keys():
    secret = os.environ["jwt_foodwatch"]
elif "JWT_FOODWATCH"in os.environ.keys():
    secret = os.environ["JWT_FOODWATCH"]
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
        raise AuthError({
            'code':'authorization is missing',
            'description':'Add authorization header to the request'
        }, 401)

    headerAuthList = headerAuth.split()
    if headerAuthList[0].lower() != 'bearer':
        raise AuthError({
            'code': 'Invalid header',
            'description':'The authorization header must be bearer'
        }, 401)
    token = headerAuthList[1]
    return token


'================================='
def check_permissions(permission, payload):
    if permission in payload["permissions"]:
        return True
    else:
        raise AuthError({
            'code': 'Permission check fail',
            'description':'The person doenst has the required permission'
        }, 401)

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
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

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
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)


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