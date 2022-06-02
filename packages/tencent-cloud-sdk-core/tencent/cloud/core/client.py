# tencent.cloud.core.client is python-3.6 source file

# MIT License
# 
# Copyright (c) 2021 Handle.
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
The basic client type that implements the Tencent Cloud SDK.

Example:

    from tencent.cloud.core import client

    function_client: client.UniversalClient = client.UniversalClient(
        product_id = 'scf'
    )

    function_client.action(
        region_id = 'ap-shanghai',
        action_id = 'Invoke',
        action_parameters = {
            'Namespace': 'default',
            'FunctionName': 'get_user_name'
        },
        action_version = '2018-04-16'
    )
'''

import os
import ssl
import json
import time
import random
import asyncio

from tencent.cloud.common import aiohttp
from tencent.cloud.common import certifi

from tencent.cloud.core import errors
from tencent.cloud.core import version
from tencent.cloud.core import proxies
from tencent.cloud.auth import credentials

_common_ssl_context: ssl.SSLContext = None

def get_common_ssl_context() -> ssl.SSLContext:
    '''
    Get common SSL contexts. If the common SSL context does not
    exist, a new one is created.
    
    The returned SSL context uses the internal CA root certificate.
    For more information, see https://github.com/certifi/python-certifi
    '''

    global _common_ssl_context

    if not _common_ssl_context:
        _common_ssl_context = ssl.create_default_context(
            cafile = certifi.where()
        )
    
    return _common_ssl_context

def set_common_ssl_context(
    ssl_context: ssl.SSLContext
):
    '''
    Set a common SSL context.
    '''

    if not ssl_context or not isinstance(ssl_context, ssl.SSLContext):
        raise ValueError('ssl context is invalid')

    global _common_ssl_context
    _common_ssl_context = ssl_context

def has_common_ssl_context() -> bool:
    '''
    Whether the common SSL context already exists.
    '''

    return _common_ssl_context != None

def need_common_ssl_context() -> bool:
    '''
    Evaluate the need to use common SSL context instead of global
    default SSL context.

    This checks if the SSL global CA root certificate file exists
    and is readable.    
    '''

    default_verify_paths: ssl.DefaultVerifyPaths = ssl.get_default_verify_paths()
    return not default_verify_paths.cafile or not os.access(default_verify_paths.cafile, os.R_OK)

class BaseClient:
    '''
    Tencent Cloud SDK base client type.

    Any established product client will inherit from this type, and the
        underlying client will provide direct access to the Cloud API.

    Args:
        access_credentials: Authentication context type instance
        access_endpoint: Cloud API's HTTP request endpoint host name
    
    Raises:
        ValueError: Parameter values are not as expected.
    '''

    def __init__(self,
        access_credentials: credentials.Credentials,
        access_proxies: proxies.Proxies,
        access_endpoint: str
    ):
        self.__initialized: bool = False

        if access_credentials:
            if not isinstance(access_credentials, credentials.Credentials):
                raise ValueError('<access_credentials> value invalid')

            self.__access_credentials: credentials.Credentials = access_credentials
        else:
            try:
                self.__access_credentials: credentials.Credentials = (
                    credentials.EnvironmentalCredentials())
            except EnvironmentError:
                self.__access_credentials: credentials.Credentials = (
                    credentials.FileCredentials())

        if access_proxies:
            if not isinstance(access_proxies, proxies.Proxies):
                raise ValueError('<access_proxies> value invalid')

            self.__access_proxies = access_proxies
        else:
            self.__access_proxies = None

        if not access_endpoint or not isinstance(access_endpoint, str):
            raise ValueError('<access_endpoint> value invalid')

        self.__access_endpoint: str = access_endpoint
        self.__event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        
        self.__request_client: aiohttp.ClientSession = aiohttp.ClientSession(
            loop = self.__event_loop,
            headers = {
                'User-Agent': 'tencent-cloud-sdk/' + version.get_version_text(),
                'Content-Type': 'application/json'
            },
            conn_timeout = 5,
            read_timeout = 5
        )

        self.__ssl_context: ssl.SSLContext = None
        if need_common_ssl_context():
            self.__ssl_context = get_common_ssl_context()

        self.__last_response_metadata: dict = None

        self.__error_manager: errors.ErrorManager = errors.ErrorManager(
            error_handlers = [
                self._error_handler_callback
            ]
        )

        self.__action_retry_error_ids: list = [
            'AuthFailure.SignatureExpire',
            'InternalError',
            'LimitExceeded',
            'RequestLimitExceeded',
            'ResourceInsufficient'
        ]

        self.__initialized = True

    def __del__(self):
        if not self.__initialized:  # Base client instance construction error
            return

        # The event loop instance running in the hyperthreaded context
        # of the underlying client should not be closed.

        if self._get_event_loop().is_closed():
            raise RuntimeError('destroy the client before the event loop closes')

        if not self._get_event_loop().is_running():
            self._get_event_loop().run_until_complete(self.__request_client.close())
        else:
            self._get_event_loop().create_task(self.__request_client.close())

    @property
    def error_manager(self) -> errors.ErrorManager:
        '''
        Error manager instance.
        '''

        return self.__error_manager

    @property
    def credentials(self) -> credentials.Credentials:
        '''
        Binding access credentials instance.
        '''

        return self.__access_credentials
    
    @property
    def enable_builtin_error_handler(self) -> bool:
        '''
        Enable the built-in error handler.
        '''

        return self.__error_manager.has_handler(self._error_handler_callback)

    @enable_builtin_error_handler.setter
    def enable_builtin_error_handler(self, value: bool):
        '''
        Enable the built-in error handler.
        '''

        if value == None or not isinstance(value, bool):
            raise ValueError('<enable_builtin_error_handler> value invalid')

        if self.enable_builtin_error_handler:
            if not value:
                self.__error_manager.remove_handler(self._error_handler_callback)
        elif value:
            self.__error_manager.add_handler(self._error_handler_callback)

    def _error_handler_callback(self,
        error_manager: errors.ErrorManager,
        error_source: object,
        error_instance: errors.ClientError,
        error_retry_count: int
    ) -> int:
        '''
        Built-in error handler callback function.
        '''

        if isinstance(error_instance, errors.RequestError):
            return errors.ErrorHandlerResult.Backoff
        elif isinstance(error_instance, errors.ResponseError):
            if error_instance.status_code >= 500:
                return errors.ErrorHandlerResult.Backoff
        elif isinstance(error_instance, errors.ActionError):
            if error_instance.error_id in self.__action_retry_error_ids:
                return errors.ErrorHandlerResult.Backoff

        return errors.ErrorHandlerResult.Ignore

    def _get_event_loop(self) -> asyncio.AbstractEventLoop:
        '''
        Gets the event loop instance to which the current client belongs.

        Returns:
            Return event loop instance.
        '''

        return self.__event_loop
    
    def get_last_response_metadata(self) -> dict:
        '''
        Get the last Cloud API response metadata

        Returns:
            Returns a dictionary object containing metadata.
                If not, it returns None.
        '''

        return self.__last_response_metadata

    def set_access_endpoint(self,
        access_endpoint: str
    ):
        '''
        Set the Tencent Cloud API endpoint host name.

        Note that this will immediately override the default Tencent Cloud
            API endpoint hostname for the current client instance.

        Args:
            access_endpoint: Endpoint hostname.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not access_endpoint or not isinstance(access_endpoint, str):
            raise ValueError('<access_endpoint> value invalid')

        self.__access_endpoint = access_endpoint

    def set_access_proxies(self,
        access_proxies: proxies.Proxies
    ):
        '''
        Set the proxy server configuration to use when accessing
            the Tencent Cloud API.
        
        Args:
            access_proxies: Access proxy server configuration.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if access_proxies and not isinstance(access_proxies, proxies.Proxies):
            raise ValueError('<access_proxies> value invalid')
        
        self.__access_proxies = access_proxies

    def set_ssl_context(
        self,
        ssl_context: ssl.SSLContext
    ):
        '''
        Set the SSL context to replace the global SSL context
        or the common SSL context.
        '''

        if not ssl_context or not isinstance(ssl_context, ssl.SSLContext):
            raise ValueError('ssl context is invalid')

        self.__ssl_context = ssl_context

    @property
    def proxies(self) -> proxies.Proxies:
        '''
        Binding proxy server configuration instance.
        '''

        return self.__access_proxies

    @property
    def ssl_context(self) -> ssl.SSLContext:
        '''
        The client's SSL context. If the global SSL context is
        being used, the value is None.
        '''

        return self.__ssl_context

    async def _try_request_action_async(self,
        region_id: str,
        product_id: str,
        action_id: str,
        action_parameters: dict,
        action_version: str,
        access_endpoint: str = None
    ) -> dict:
        '''
        Attempt to make an HTTP request to the Cloud API.

        Note that this method still throws an exception when
            it encounters an unexpected error.

        Args:
            region_id: Data center physical region unique identifier.
            product_id: Product unique identifier.
            action_id: Cloud API unique identifier.
            action_parameters: Cloud API request parameters.
            action_version: Cloud API version name
            access_endpoint: Tencent Cloud API endpoint host name.
        
        Returns:
            Returns a dictionary object containing Cloud API responses.
        
        Raises:
            ValueError: Parameter values are not as expected.
            RequestError: Cloud API HTTP request failed.
            ResponseError: Cloud API's HTTP response content is not as expected.
            ActionError: Cloud API's HTTP request succeeded, but the operation failed.
        '''

        if region_id and not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not product_id or not isinstance(product_id, str):
            raise ValueError('<product_id> value invalid')

        if not action_id or not isinstance(action_id, str):
            raise ValueError('<action_id> value invalid')

        if action_parameters and not isinstance(action_parameters, dict):
            raise ValueError('<action_parameters> value invalid')

        if not action_version or not isinstance(action_version, str):
            raise ValueError('<action_version> value invalid')

        if access_endpoint and not isinstance(access_endpoint, str):
            raise ValueError('<access_endpoint> value invalid')

        signature_timestamp: int = int(time.time())

        auth_content, auth_token = self.__access_credentials.generate_and_signature(
            request_hostname = self.__access_endpoint if not access_endpoint else access_endpoint,
            request_method = 'POST',
            request_parameters = action_parameters,
            signature_product_id = product_id,
            signature_timestamp = signature_timestamp
        )

        try:
            response_context: aiohttp.ClientResponse = await self.__request_client.post(
                url = 'https://{access_endpoint}/'.format(
                    access_endpoint = self.__access_endpoint if not access_endpoint else access_endpoint
                ),
                json = action_parameters if action_parameters else dict(),
                headers = {
                    'X-TC-Action': action_id,
                    'X-TC-Region': region_id if region_id else str(),
                    'X-TC-Timestamp': str(signature_timestamp),
                    'X-TC-Version': action_version,
                    'X-TC-Token': auth_token if auth_token else str(),
                    'Authorization': auth_content
                },
                proxy = '{PROXY_TYPE}://{PROXY_ENDPOINT}'.format(
                    PROXY_TYPE = self.__access_proxies.proxy_type,
                    PROXY_ENDPOINT = self.__access_proxies.proxy_endpoint
                ) if self.__access_proxies else None,
                proxy_auth = (aiohttp.BasicAuth(
                    self.__access_proxies.proxy_auth['username'],
                    self.__access_proxies.proxy_auth['password']
                ) if self.__access_proxies and
                    self.__access_proxies.proxy_auth else None),
                ssl_context = self.__ssl_context
            )

            response_context.raise_for_status()
        except aiohttp.ClientError as error:
            raise errors.RequestError(str(error))
        
        if response_context.status != 200:
            raise errors.ResponseError(
                status_code = response_context.status,
                error_message = await response_context.text()
            )
        
        try:
            response_result: dict = json.loads(await response_context.text())
        except json.JSONDecodeError:
            raise errors.ResponseError(
                status_code = response_context.status,
                error_message = 'action response content invalid'
            )
        
        try:
            if 'Error' in response_result['Response']:
                raise errors.ActionError(
                    action_id = action_id,
                    error_id = response_result['Response']['Error']['Code'],
                    error_message = response_result['Response']['Error']['Message'],
                    request_id = response_result['Response']['RequestId']
                )
            
            self.__last_response_metadata = {
                'request_id': response_result['Response']['RequestId']
            }
        except KeyError as error:
            raise errors.ResponseError(
                status_code = response_context.status_code,
                error_message = 'action response content missing field: ' + str(error)
            )

        return response_result['Response']

    async def _request_action_async(self,
        region_id: str,
        product_id: str,
        action_id: str,
        action_parameters: dict,
        action_version: str,
        access_endpoint: str = None
    ) -> dict:
        '''
        Make an HTTP request to the Cloud API.

        Unlike the try_request_action_async method, this method
            will retry the RequestError exception.

        Args:
            region_id: Data center physical region unique identifier.
            product_id: Product unique identifier.
            action_id: Cloud API unique identifier.
            action_parameters: Cloud API request parameters.
            action_version: Cloud API version name.
            access_endpoint: Tencent Cloud API endpoint host name.
        
        Returns:
            Returns a dictionary object containing Cloud API responses.
        
        Raises:
            ValueError: Parameter values are not as expected.
            RequestError: Cloud API HTTP request failed.
            ResponseError: Cloud API's HTTP response content is not as expected.
            ActionError: Cloud API's HTTP request succeeded, but the operation failed.
        '''

        error_retry_count: int = 0

        while True:
            try:
                return await self._try_request_action_async(region_id, product_id,
                    action_id, action_parameters, action_version, access_endpoint)
            except (errors.RequestError, errors.ResponseError, errors.ActionError) as error:
                if error_retry_count == self.__error_manager.max_number_of_retries:
                    raise

                error_handler_result: int = self.__error_manager.handler(self, error,
                    error_retry_count)

                if error_handler_result == errors.ErrorHandlerResult.Backoff:
                    backoff_interval: float = (2 ** error_retry_count) + (
                        random.randint(1, 1000) / 1000)

                    await asyncio.sleep(min(backoff_interval,
                        self.__error_manager.max_backoff_interval))
                elif error_handler_result == errors.ErrorHandlerResult.Retry:
                    continue
                elif error_handler_result == errors.ErrorHandlerResult.Throw:
                    raise
            finally:
                error_retry_count += 1

    async def _download_resource_async(self,
        resource_url: str,
        local_file_name: str
    ):
        '''
        Download the specified resource data to the local.

        Args:
            resource_url: Resource full URL.
            local_file_name: Full local file name for storing resources.
        
        Raises:
            ValueError: Parameter values are not as expected.
            RequestError: An HTTP request failed.
            IOError: Failed to download resource block or write resource block
        '''

        if not resource_url or not isinstance(resource_url, str):
            raise ValueError('<resource_url> value invalid')

        if not local_file_name or not isinstance(local_file_name, str):
            raise ValueError('<local_file_name> value invalid')

        try:
            with open(local_file_name, mode = 'wb+') as file_context:
                file_context.truncate()

                async with self.__request_client.get(resource_url) as response_context:
                    response_context.raise_for_status()
                    
                    while True:
                        download_buffer: bytes = await response_context.content.read(65535)

                        if not download_buffer:
                            break

                        file_context.write(download_buffer)
        except aiohttp.ClientError as error:
            raise errors.RequestError(str(error))

class UniversalClient(BaseClient):
    '''
    Represents a universal client type that applies to all products.

    Args:
        product_id: Unique identifier of the product.
        access_credentials: Access credentials configuration.
        access_proiexs: Access proxy server configuration.
    
    Raises:
        ValueError: Parameter values are not as expected.
    '''
    
    def __init__(self,
        product_id: str,
        access_credentials: credentials.Credentials = None,
        access_proiexs: proxies.Proxies = None
    ):
        if not product_id or not isinstance(product_id, str):
            raise ValueError('<product_id> value invalid')
        
        self.__product_id: str = product_id

        super().__init__(access_credentials, access_proiexs,
            product_id + '.tencentcloudapi.com')

    async def action_async(self,
        region_id: str,
        action_id: str,
        action_parameters: dict,
        action_version: str
    ) -> dict:
        '''
        Call the specified Tencent Cloud API of the Tencent Cloud
            product bound to the current client and get the result.

        Args:
            region_id: Data center unique identifier.
            action_id: Tencent Cloud API unique identifier.
            action_parameters: Dictionary instance with Tencent Cloud API parameters.
            action_version: Tencent Cloud API version name.

        Returns:
            Returns a dictionary instance containing the results of a
                Tencent Cloud API call.
        
        Raises:
            ValueError: Parameter values are not as expected.
            RequestError: Cloud API HTTP request failed.
            ResponseError: Cloud API's HTTP response content is not as expected.
            ActionError: Cloud API's HTTP request succeeded, but the operation failed.
        '''

        return await self._request_action_async(region_id, self.__product_id,
            action_id, action_parameters, action_version)

    def action(self,
        region_id: str,
        action_id: str,
        action_parameters: dict,
        action_version: str
    ) -> dict:
        '''
        Call the specified Tencent Cloud API of the Tencent Cloud
            product bound to the current client and get the result.

        Args:
            region_id: Data center unique identifier.
            action_id: Tencent Cloud API unique identifier.
            action_parameters: Dictionary instance with Tencent Cloud API parameters.
            action_version: Tencent Cloud API version name.

        Returns:
            Returns a dictionary instance containing the results of a
                Tencent Cloud API call.
        
        Raises:
            ValueError: Parameter values are not as expected.
            RequestError: Cloud API HTTP request failed.
            ResponseError: Cloud API's HTTP response content is not as expected.
            ActionError: Cloud API's HTTP request succeeded, but the operation failed.
        '''

        return self._get_event_loop().run_until_complete(self._request_action_async(
            region_id, self.__product_id, action_id, action_parameters, action_version))

    async def action_for_product_async(self,
        product_id: str,
        region_id: str,
        action_id: str,
        action_parameters: dict,
        action_version: str,
        access_endpoint: str = None
    ) -> dict:
        '''
        Request a given Tencent Cloud API for a given Tencent Cloud product.

        This method is different from the action or action_async method.
            This method will allow you to make a Tencent Cloud API request
            for a specific Tencent Cloud product, and is not limited to the
            Tencent Cloud API product and API request endpoint bound to the
            current client.

        Args:
            product_id: Unique identifier of the product.
            region_id: Region unique identifier.
            action_id: Cloud API unique identifier.
            action_parameters: Parameters passed to the Cloud API.
            action_version: Cloud API version name.
            access_endpoint: Tencent Cloud API endpoint host name.

        Returns:
            Returns a dictionary object containing Cloud API responses.
        
        Raises:
            ValueError: Parameter values are not as expected.
            RequestError: Cloud API HTTP request failed.
            ResponseError: Cloud API's HTTP response content is not as expected.
            ActionError: Cloud API's HTTP request succeeded, but the operation failed.
        '''

        if not access_endpoint:
            access_endpoint = product_id + '.tencentcloudapi.com'

        return await self._request_action_async(region_id, product_id, action_id,
            action_parameters, action_version, access_endpoint)

    def action_for_product(self,
        product_id: str,
        region_id: str,
        action_id: str,
        action_parameters: dict,
        action_version: str,
        access_endpoint: str = None
    ) -> dict:
        '''
        Request a given Tencent Cloud API for a given Tencent Cloud product.

        This method is different from the action or action_async method.
            This method will allow you to make a Tencent Cloud API request
            for a specific Tencent Cloud product, and is not limited to the
            Tencent Cloud API product and API request endpoint bound to the
            current client.

        Args:
            product_id: Unique identifier of the product.
            region_id: Region unique identifier.
            action_id: Cloud API unique identifier.
            action_parameters: Parameters passed to the Cloud API.
            action_version: Cloud API version name.
            access_endpoint: Tencent Cloud API endpoint host name.

        Returns:
            Returns a dictionary object containing Cloud API responses.
        
        Raises:
            ValueError: Parameter values are not as expected.
            RequestError: Cloud API HTTP request failed.
            ResponseError: Cloud API's HTTP response content is not as expected.
            ActionError: Cloud API's HTTP request succeeded, but the operation failed.
        '''

        return self._get_event_loop().run_until_complete(self._request_action_async(
            region_id, product_id, action_id, action_parameters,
            action_version, access_endpoint
        ))

    def set_product_id(self,
        product_id: str
    ):
        '''
        Set the product ID corresponding to the current
            client to the given product ID.

        Args:
            product_id: Product unique identifier.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not product_id or not isinstance(product_id, str):
            raise ValueError('<product_id> value invalid')

        self.set_access_endpoint(product_id + '.tencentcloudapi.com')
        self.__product_id = product_id

    def get_product_id(self) -> str:
        '''
        Get the product ID corresponding to the current client.

        Returns:
            Returns a string corresponding to the product ID.
        '''

        return self.__product_id

    async def select_action_async(self,
        action_id: str,
        action_version: str
    ):
        '''
        Create a Python native asynchronous function for a
            given Cloud API.

        Args:
            action_id: Cloud API unique identifier.
            action_version: Cloud API version name.

        Returns:
            Returns a Python function instance.
        '''

        return (lambda region_id = None, action_parameters = None:
            self.action_async(region_id, action_id, action_parameters,
            action_version))

    def select_action(self,
        action_id: str,
        action_version: str
    ):
        '''
        Create a Python native synchronous function for a
            given Cloud API.

        Args:
            action_id: Cloud API unique identifier.
            action_version: Cloud API version name.

        Returns:
            Returns a Python function instance.
        '''

        return (lambda region_id = None, action_parameters = None:
            self.action(region_id, action_id, action_parameters,
            action_version))
