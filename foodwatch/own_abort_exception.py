from werkzeug.exceptions import HTTPException, default_exceptions, Aborter


class Permission_check_fail(HTTPException):
    code = 4011
    description = 'Permission check fail'


class Invalid_header_malformed(HTTPException):
    code = 4012
    description = 'invalid_header - Authorization malformed.'


class Token_expired(HTTPException):
    code = 4013
    description = 'invalid_header'


class Audience_issuer(HTTPException):
    code = 4014
    description = 'Incorrect claims. Please, check the audience and issuer.'


class Authentication_token(HTTPException):
    code = 4015
    description = 'Unable to parse authentication token'


class Unable_appropriate_key(HTTPException):
    code = 4016
    description = 'Unable to find the appropriate key'


class Add_authorization_header(HTTPException):
    code = 4017
    description = 'Add authorization header to the request.'


class Authorization_must_bear(HTTPException):
    code = 4018
    description = 'The authorization header must be bearer'


default_exceptions[4011] = Permission_check_fail
default_exceptions[4012] = Invalid_header_malformed
default_exceptions[4013] = Token_expired
default_exceptions[4014] = Audience_issuer
default_exceptions[4015] = Authentication_token
default_exceptions[4016] = Unable_appropriate_key
default_exceptions[4017] = Add_authorization_header
default_exceptions[4018] = Authorization_must_bear
abort = Aborter()  # don't from flask import abort