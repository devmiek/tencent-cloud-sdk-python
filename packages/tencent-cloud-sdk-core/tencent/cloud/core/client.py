# tencent.cloud.core.client is python-3.6 source file

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
The basic client type that implements the Tencent Cloud SDK.

Example:

    from tencent.cloud.core import client

    base_client: client.BaseClient = client.BaseClient(
        request_endpoint = 'scf.tencentcloudapi.com'
    )

    base_client.request_action(
        region_id = 'ap-shanghai',
        product_id = 'scf',
        action_id = 'Invoke',
        action_parameters = {
            'Namespace': 'default',
            'FunctionName': 'get_user_name'
        },
        action_version = '2018-04-16'
    )

Example2:

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

import json
import time
import random
import asyncio

try:
    import aiohttp
except ImportError:
    from tencent.cloud.common import aiohttp

from tencent.cloud.core import errors
from tencent.cloud.core import version
from tencent.cloud.core import proxies
from tencent.cloud.auth import credentials

class BaseClient:
    '''
    Tencent Cloud SDK base client type.

    Any established product client will inherit from this type, and the
        underlying client will provide direct access to the Cloud API.

    Args:
        credentials_context: Authentication context type instance
        request_endpoint: Cloud API's HTTP request endpoint host name
    
    Raises:
        ValueError: Parameter values are not as expected.
    '''

    def __init__(self,
        credentials_context: credentials.Credentials,
        request_proxies_context: proxies.Proxies,
        request_endpoint: str
    ):
        self.__initialized: bool = False

        if credentials_context:
            if not isinstance(credentials_context, credentials.Credentials):
                raise ValueError('<credentials_context> value invalid')

            self.__credentials_context: credentials.Credentials = credentials_context
        else:
            try:
                self.__credentials_context: credentials.Credentials = (
                    credentials.FileCredentials('secret.json'))
            except FileNotFoundError:
                self.__credentials_context: credentials.Credentials = (
                    credentials.EnvironmentalCredentials())

        if request_proxies_context:
            if not isinstance(request_proxies_context, proxies.Proxies):
                raise ValueError('<request_proxies_context> value invalid')

            self.__request_proxies_context = request_proxies_context
        else:
            self.__request_proxies_context = None

        if not request_endpoint or not isinstance(request_endpoint, str):
            raise ValueError('<request_endpoint> value invalid')

        self.__request_endpoint: str = request_endpoint
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

        if self.get_event_loop().is_closed():
            raise RuntimeError('destroy the client before the event loop closes')

        if not self.get_event_loop().is_running():
            self.get_event_loop().run_until_complete(self.__request_client.close())
        else:
            self.get_event_loop().create_task(self.__request_client.close())

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

        return self.__credentials_context

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

    def get_event_loop(self) -> asyncio.AbstractEventLoop:
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

    def set_request_endpoint(self,
        request_endpoint: str
    ):
        '''
        Set a new Cloud API HTTP request endpoint host name.

        Args:
            request_endpoint: HTTP request endpoint host name.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not request_endpoint or not isinstance(request_endpoint, str):
            raise ValueError('<request_endpoint> value invalid')

        self.__request_endpoint = request_endpoint

    async def try_request_action_async(self,
        region_id: str,
        product_id: str,
        action_id: str,
        action_parameters: dict,
        action_version: str,
        action_endpoint: str = None
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

        if action_endpoint and not isinstance(action_endpoint, str):
            raise ValueError('<action_endpoint> value invalid')

        signature_timestamp: int = int(time.time())

        auth_content: str = self.__credentials_context.generate_and_signature(
            request_hostname = self.__request_endpoint if not action_endpoint else action_endpoint,
            request_method = 'POST',
            request_parameters = action_parameters,
            signature_product_id = product_id,
            signature_timestamp = signature_timestamp
        )

        try:
            response_context: aiohttp.ClientResponse = await self.__request_client.post(
                url = 'https://{REQUEST_ENDPOINT}/'.format(
                    REQUEST_ENDPOINT = self.__request_endpoint if not action_endpoint else action_endpoint
                ),
                json = action_parameters if action_parameters else dict(),
                headers = {
                    'X-TC-Action': action_id,
                    'X-TC-Region': region_id if region_id else str(),
                    'X-TC-Timestamp': str(signature_timestamp),
                    'X-TC-Version': action_version,
                    'Authorization': auth_content
                },
                proxy = '{PROXY_TYPE}://{PROXY_ENDPOINT}'.format(
                    PROXY_TYPE = self.__request_proxies_context.proxy_type,
                    PROXY_ENDPOINT = self.__request_proxies_context.proxy_endpoint
                ) if self.__request_proxies_context else None,
                proxy_auth = (aiohttp.BasicAuth(
                    self.__request_proxies_context.proxy_auth['username'],
                    self.__request_proxies_context.proxy_auth['password']
                ) if self.__request_proxies_context and
                    self.__request_proxies_context.proxy_auth else None)
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

    async def request_action_async(self,
        region_id: str,
        product_id: str,
        action_id: str,
        action_parameters: dict,
        action_version: str,
        action_endpoint: str = None
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
            action_version: Cloud API version name
        
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
                return await self.try_request_action_async(region_id, product_id,
                    action_id, action_parameters, action_version, action_endpoint)
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

    async def download_resource_async(self,
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
        credentials_context: Authentication context instance.
    
    Raises:
        ValueError: Parameter values are not as expected.
    '''
    
    def __init__(self,
        product_id: str,
        credentials_context: credentials.Credentials = None,
        proiexs_context: proxies.Proxies = None
    ):
        if not product_id or not isinstance(product_id, str):
            raise ValueError('<product_id> value invalid')
        
        self.__product_id: str = product_id

        super().__init__(credentials_context, proiexs_context,
            product_id + '.tencentcloudapi.com')

    async def action_async(self,
        region_id: str,
        action_id: str,
        action_parameters: dict,
        action_version: str
    ) -> dict:
        '''
        Request a given Cloud API

        Args:
            region_id: Region unique identifier.
            action_id: Cloud API unique identifier.
            action_parameters: Parameters passed to the Cloud API.
            action_version: Cloud API version name.

        Returns:
            Returns a dictionary object containing Cloud API responses.
        
        Raises:
            ValueError: Parameter values are not as expected.
            RequestError: Cloud API HTTP request failed.
            ResponseError: Cloud API's HTTP response content is not as expected.
            ActionError: Cloud API's HTTP request succeeded, but the operation failed.
        '''

        return await self.request_action_async(region_id, self.__product_id,
            action_id, action_parameters, action_version)

    def action(self,
        region_id: str,
        action_id: str,
        action_parameters: dict,
        action_version: str
    ) -> dict:
        '''
        Request a given Cloud API

        Args:
            region_id: Region unique identifier.
            action_id: Cloud API unique identifier.
            action_parameters: Parameters passed to the Cloud API.
            action_version: Cloud API version name.

        Returns:
            Returns a dictionary object containing Cloud API responses.
        
        Raises:
            ValueError: Parameter values are not as expected.
            RequestError: Cloud API HTTP request failed.
            ResponseError: Cloud API's HTTP response content is not as expected.
            ActionError: Cloud API's HTTP request succeeded, but the operation failed.
        '''

        return self.get_event_loop().run_until_complete(self.request_action_async(
            region_id, self.__product_id, action_id, action_parameters, action_version))

    async def action_for_mixed_async(self,
        product_id: str,
        region_id: str,
        action_id: str,
        action_parameters: dict,
        action_version: str,
        action_endpoint: str = None
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

        Returns:
            Returns a dictionary object containing Cloud API responses.
        
        Raises:
            ValueError: Parameter values are not as expected.
            RequestError: Cloud API HTTP request failed.
            ResponseError: Cloud API's HTTP response content is not as expected.
            ActionError: Cloud API's HTTP request succeeded, but the operation failed.
        '''

        if not action_endpoint:
            action_endpoint = product_id + '.tencentcloudapi.com'

        return await self.request_action_async(region_id, product_id, action_id,
            action_parameters, action_version, action_endpoint)

    def action_for_mixed(self,
        product_id: str,
        region_id: str,
        action_id: str,
        action_parameters: dict,
        action_version: str,
        action_endpoint: str = None
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

        Returns:
            Returns a dictionary object containing Cloud API responses.
        
        Raises:
            ValueError: Parameter values are not as expected.
            RequestError: Cloud API HTTP request failed.
            ResponseError: Cloud API's HTTP response content is not as expected.
            ActionError: Cloud API's HTTP request succeeded, but the operation failed.
        '''

        return self.get_event_loop().run_until_complete(self.request_action_async(
            region_id, product_id, action_id, action_parameters,
            action_version, action_endpoint
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

        self.set_request_endpoint(product_id + '.tencentcloudapi.com')
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
