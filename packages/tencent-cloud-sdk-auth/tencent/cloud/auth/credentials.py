# tencent.cloud.auth.secret is python-3.6 source file

# MIT License
# 
# Copyright (c) 2020 Tencent Cloud.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
Implement the account access authentication context
    for the Tencent Cloud SDK.

Example:
    from tencent.cloud.auth import credentials

    credentials_context = credentials.Credentials(
        secret_id = 'AKIDylIemfDjwuc5LPRylNqazB9syrXzxLDq',
        secret_key = 'pJbfW9TbU7ZnsjLjtoshHfplVSCiz0nN'
    )
'''

import os

import json
import hmac
import hashlib
import datetime

from tencent.cloud.auth import helper

class Credentials:
    '''
    The authentication context type representing the account access key.

    Args:
        secret_id: ID for access credentials.
        secret_key: Key for access credentials.
        secret_token: Token for access credentials.
    
    Raises:
        ValueError: Parameter values are not as expected.
    '''

    def __init__(self,
        secret_id: str,
        secret_key: str,
        secret_token: str = None
    ):
        self.__secret_id: str = None
        self.__secret_key: str = None
        self.__secret_token: str = None

        self.set_secret_info(secret_id, secret_key, secret_token)

    def get_secret_info(self) -> dict:
        '''
        Get Secret information for current access credentials.

        Returns:
            Returns a dictionary instance containing Secret information.
        '''

        return {
            'id': self.__secret_id,
            'key': self.__secret_key,
            'token': self.__secret_token
        }

    def set_secret_info(self,
        secret_id: str,
        secret_key: str,
        secret_token: str = None
    ):
        '''
        Set secret information for access credentials.

        Args:
            secret_id: ID for access credentials.
            secret_key: Key for access credentials.
            secret_token: Token for access credentials.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not secret_id or not isinstance(secret_id, str):
            raise ValueError('<secret_id> value invalid')

        if not secret_key or not isinstance(secret_key, str):
            raise ValueError('<secret_key> value invalid')

        if secret_token and not isinstance(secret_token, str):
            raise ValueError('<secret_token> value invalid')

        self.__secret_id = secret_id
        self.__secret_key = secret_key
        self.__secret_token = secret_token

    def refresh_secret_info(self):
        '''
        Refresh the access credential information for which the
            current access credential has been set.
        '''

        pass

    def generate_canonical_content(self,
        request_hostname: str,
        request_method: str,
        request_parameters: dict
    ) -> str:
        '''
        Generate a canonical request context string for
            account access signatures.

        Args:
            request_hostname: Cloud API's endpoint host name.
                Example: scf.tencentcloudapi.com

            request_method: Cloud API's HTTP request method.
                Example: POST
            
            request_parameters: Cloud API HTTP request parameters.
        
        Returns:
            Returns the canonical request context string.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not request_hostname or not isinstance(request_hostname, str):
            raise ValueError('<request_hostname> value invalid')

        if not request_method or not isinstance(request_method, str):
            raise ValueError('<request_method> value invalid')

        if request_parameters:
            if not isinstance(request_parameters, dict):
                raise ValueError('<request_parameters> value invalid')
        else:
            request_parameters = dict()

        return (
            '{HTTP_REQUEST_METHOD}\n'
            '/\n'
            '{HTTP_REQUEST_QUERY_STRING}\n'
            'content-type:application/json\n'
            'host:{HTTP_REQUEST_HOSTNAME}\n\n'
            'content-type;host\n'
            '{HTTP_REQUEST_BODY_HASH}'
        ).format(
            HTTP_REQUEST_METHOD = request_method,
            HTTP_REQUEST_QUERY_STRING = (helper.generate_url_query_string(request_parameters)
                if request_method == 'GET' else str()),
            HTTP_REQUEST_HOSTNAME = request_hostname,
            HTTP_REQUEST_BODY_HASH = hashlib.sha256((json.dumps(request_parameters) if request_method != 'GET'
                else str()).encode('utf-8')).hexdigest()
        )

    def generate_signature_content(self,
        signature_product_id: str,
        signature_timestamp: int,
        canonical_content: str
    ) -> str:
        '''
        Generate a signature context string for
            the account access signature.

        Args:
            signature_product_id: Cloud API's unique product identifier.
                Example: scf

            signature_timestamp: Cloud API HTTP request signature UNIX timestamp.
            canonical_content: Canonical request context string.

        Returns:
            Returns the signature context string.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not signature_product_id or not isinstance(signature_product_id, str):
            raise ValueError('<signature_product_id> value invalid')

        if not signature_timestamp or not isinstance(signature_timestamp, int):
            raise ValueError('<signature_timestamp> value invalid')

        if not canonical_content or not isinstance(canonical_content, str):
            raise ValueError('<canonical_content> value invalid')

        return (
            'TC3-HMAC-SHA256\n'
            '{SIGNATURE_UNIX_TIMESTAMP}\n'
            '{SIGNATURE_DATE}/{SIGNATURE_PRODUCT_ID}/tc3_request\n'
            '{CANONICAL_CONTENT_HASH}'
        ).format(
            SIGNATURE_UNIX_TIMESTAMP = signature_timestamp,
            SIGNATURE_DATE = datetime.datetime.utcfromtimestamp(signature_timestamp
                ).strftime('%Y-%m-%d'),
            SIGNATURE_PRODUCT_ID = signature_product_id,
            CANONICAL_CONTENT_HASH = hashlib.sha256(canonical_content.encode('utf-8')).hexdigest()
        )

    def signature(self,
        signature_product_id: str,
        signature_timestamp: int,
        signature_content: str
    ) -> str:
        '''
        Calculates the Cloud API's HTTP request signature
            string based on the specified signature context string.
        
        Args:
            signature_product_id: Cloud API's product unique identifier.
            signature_timestamp: Signature UNIX timestamp.
            signature_content: Signature context string.
        
        Returns:
            Returns the signature calculation result string.

        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not signature_product_id or not isinstance(signature_product_id, str):
            raise ValueError('<signature_product_id> value invalid')

        if not signature_timestamp or not isinstance(signature_timestamp, int):
            raise ValueError('<signature_timestamp> value invalid')

        if not signature_content or not isinstance(signature_content, str):
            raise ValueError('<signature_content> value invalid')

        signature_date: str = datetime.datetime.utcfromtimestamp(signature_timestamp
            ).strftime('%Y-%m-%d')

        secret_date_bytes: bytes = hmac.new(('TC3' + self.__secret_key).encode('utf-8'),
            signature_date.encode('utf-8'), hashlib.sha256).digest()

        secret_service_bytes: bytes = hmac.new(secret_date_bytes, signature_product_id.encode('utf-8'),
            hashlib.sha256).digest()
        
        secret_derived_bytes: bytes = hmac.new(secret_service_bytes, 'tc3_request'.encode('utf-8'),
            hashlib.sha256).digest()

        return hmac.new(secret_derived_bytes, signature_content.encode('utf-8'),
            hashlib.sha256).hexdigest()

    def generate_auth_content(self,
        signature_product_id: str,
        signature_timestamp: int,
        signature_result: str
    ) -> str:
        '''
        Generates a signed authentication context string
            that can be verified by Cloud API.

        Args:
            signature_product_id: Cloud API's product unique identifier.
            signature_timestamp: Signature UNIX timestamp.
            signature_result: Signature calculation result string.
        
        Returns:
            Returns the authentication context string that Cloud API can validate.

        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not signature_product_id or not isinstance(signature_product_id, str):
            raise ValueError('<signature_product_id> value invalid')

        if not signature_timestamp or not isinstance(signature_timestamp, int):
            raise ValueError('<signature_timestamp> value invalid')

        if not signature_result or not isinstance(signature_result, str):
            raise ValueError('<signature_result> value invalid')

        return (
            'TC3-HMAC-SHA256 '
            'Credential={SECRET_ID}/{SIGNATURE_DATE}/{SIGNATURE_PRODUCT_ID}/tc3_request, '
            'SignedHeaders=content-type;host, Signature={SIGNATURE_RESULT}'
        ).format(
            SECRET_ID = self.__secret_id,
            SIGNATURE_DATE = datetime.datetime.utcfromtimestamp(signature_timestamp
                ).strftime('%Y-%m-%d'),
            SIGNATURE_PRODUCT_ID = signature_product_id,
            SIGNATURE_RESULT = signature_result
        )

    def generate_and_signature(self,
        request_hostname: str,
        request_method: str,
        request_parameters: dict,
        signature_product_id: str,
        signature_timestamp: int,
    ) -> tuple:
        '''
        Generates and calculates an authentication context string
            for the TC3-HMAC-SHA256 signature algorithm based on
            Cloud API's HTTP request information.
        
        Args:
            request_hostname: Cloud API's request endpoint host name.
            request_method: Cloud API's HTTP request method.
            request_parameters: Cloud API HTTP request parameters.
            signature_product_id: Cloud API's unique product identifier.
            signature_timestamp: Cloud API's signed UNIX timestamp.
        
        Returns:
            Returns a tuple containing an authentication context
                string and a token string.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        self.refresh_secret_info()

        canonical_content: str = self.generate_canonical_content(
            request_hostname, request_method, request_parameters)

        signature_content: str = self.generate_signature_content(
            signature_product_id, signature_timestamp, canonical_content)

        signature_result: str = self.signature(
            signature_product_id, signature_timestamp, signature_content)

        return (
            self.generate_auth_content(signature_product_id,
                signature_timestamp, signature_result),
            self.__secret_token
        )

class EnvironmentalCredentials(Credentials):
    '''
    Represents an auto-configuration authentication context type
        that is appropriate for a specific operating environment.

    Args:
        variable_name_of_secret_id: Environment variable name with secret-id.
        variable_name_of_secret_key: Environment variable name with secret-key.
        variable_name_of_secret_token: Environment variable name with secret-token.

    Raises:
        EnvironmentError: The current operating environment is not as expected.
        ValueError: The account access key provided by the current operating
            environment is invalid.
    '''

    def __init__(self,
        variable_name_of_secret_id: str = 'TENCENTCLOUD_SECRETID',
        variable_name_of_secret_key: str = 'TENCENTCLOUD_SECRETKEY',
        variable_name_of_secret_token: str = 'TENCENTCLOUD_SESSIONTOKEN'
    ):
        if not variable_name_of_secret_id or not isinstance(variable_name_of_secret_id, str):
            raise ValueError('<variable_name_of_secret_id> value invalid')

        if not variable_name_of_secret_key or not isinstance(variable_name_of_secret_key, str):
            raise ValueError('<variable_name_of_secret_key> value invalid')

        if not variable_name_of_secret_token or not isinstance(variable_name_of_secret_token, str):
            raise ValueError('<variable_name_of_secret_token> value invalid')

        if variable_name_of_secret_id not in os.environ:
            raise EnvironmentError('missing environment variable <{VARIABLE_NAME}>'.format(
                VARIABLE_NAME = variable_name_of_secret_id
            ))
        
        if variable_name_of_secret_key not in os.environ:
            raise EnvironmentError('missing environment variable <{VARIABLE_NAME}>'.format(
                VARIABLE_NAME = variable_name_of_secret_key
            ))
        
        self.__variable_names: dict = {
            'secret_id': variable_name_of_secret_id,
            'secret_key': variable_name_of_secret_key,
            'secret_token': variable_name_of_secret_token
        }

        super().__init__(
            secret_id = os.environ[variable_name_of_secret_id],
            secret_key = os.environ[variable_name_of_secret_key],
            secret_token = os.environ.get(variable_name_of_secret_token, None)
        )

    def refresh_secret_info(self):
        '''
        Refresh the access credential information for which the
            current access credential has been set.

        This method will again look up the access credential
            information from the environment variables of
            the current running environment.
        '''

        self.set_secret_info(
            secret_id = os.environ[self.__variable_names['secret_id']],
            secret_key = os.environ[self.__variable_names['secret_key']],
            secret_token = os.environ.get(self.__variable_names['secret_token'], None)
        )

class FileCredentials(Credentials):
    '''
    Represents the type of access credential using file credentials.

    This access credential type allows you to store and provide the
        access credentials applicable to your account as a JSON serialized
        file. The JSON file that stores access credentials contains at least
        fields named secretId and secretKey.
    
    Args:
        secret_file_name: File path containing access credentials.

    Raises:
        ValueError: Parameter values are not as expected.
        FileNotFoundError: The given access credentials file does not exist
            or cannot be read.
        JSONDecodeError: The content of the given access credential file
            cannot be parsed.
        KeyError: Mandatory field missing for given access credential file content.
    '''
    
    def __init__(self,
        secret_file_name: str
    ):
        if not secret_file_name or not isinstance(secret_file_name, str):
            raise ValueError('<secret_file_name> value invalid')

        if not os.access(secret_file_name, os.R_OK):
            raise FileNotFoundError('no such file or unreadable')
        
        with open(secret_file_name, encoding = 'utf-8') as secret_file_handle:
            secret_context: dict = json.load(secret_file_handle)
        
        try:
            super().__init__(
                secret_id = secret_context['secretId'],
                secret_key = secret_context['secretKey']
            )
        except KeyError as error:
            raise KeyError('secret missing field: ' + str(error))
