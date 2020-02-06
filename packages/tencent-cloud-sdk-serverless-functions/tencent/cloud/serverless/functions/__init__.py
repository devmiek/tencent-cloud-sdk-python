# tencent.cloud.serverless.functions.__init__ is python-3.6 source file

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
This package implements the client type of Serverless Cloud Function.

Example:

    from tencent.cloud.serverless import functions
    print(await functions.invoke_async('hello'))
'''

import time
import asyncio
import inspect

from tencent.cloud.serverless.functions import errors
from tencent.cloud.serverless.functions import client
from tencent.cloud.serverless.functions import helper

from tencent.cloud.serverless.functions.client import FunctionCode
from tencent.cloud.serverless.functions.client import FunctionCodeSource
from tencent.cloud.serverless.functions.client import FunctionTrigger
from tencent.cloud.serverless.functions.client import FunctionTriggerKind
from tencent.cloud.serverless.functions.client import FunctionType
from tencent.cloud.serverless.functions.client import FunctionRuntime
from tencent.cloud.serverless.functions.client import FunctionResultType

class FunctionResultFuture(asyncio.Future):
    '''
    A Future type that represents the result of a
        Cloud Function execution.

    Note that this type should not be instantiated
        directly unless necessary.
    '''
    
    def __init__(self,
        function_client: client.AbstractClient,
        function_metadata: dict,
        function_request_id: str,
    ):
        if not function_client or not isinstance(function_client, client.AbstractClient):
            raise ValueError('<function_client> value invalid')

        if not function_metadata or not isinstance(function_metadata, dict):
            raise ValueError('<function_metadata> value invalid')

        if not function_request_id or not isinstance(function_request_id, str):
            raise ValueError('<function_request_id> value invalid')
        
        self.__function_client: client.AbstractClient = function_client
        self.__function_metadata: dict = function_metadata
        self.__function_request_id: str = function_request_id
        
        super().__init__()

    def _complete_callback(self,
        result_future: asyncio.Future = None
    ):
        '''
        Obtaining Cloud Function results is complete.
        
        If the acquisition has not started, a coroutine
            acquisition task is created.
        '''

        if not result_future:
            result_future: asyncio.Future = asyncio.run_coroutine_threadsafe(
                self.__function_client.get_function_result_by_request_id_async(
                    region_id = self.__function_metadata['region_id'],
                    namespace_name = self.__function_metadata['namespace_name'],
                    function_name = self.__function_metadata['function_name'],
                    function_request_id = self.__function_request_id,
                    function_version = self.__function_metadata['function_version']
                ),
                self.__function_client.get_event_loop())

            result_future.add_done_callback(self._complete_callback)
        else:
            if result_future.exception():
                if isinstance(result_future.exception(), errors.errors.NotFoundError):
                    self.__function_client.get_event_loop().call_later(1, self._complete_callback)
                else:
                    self.set_exception(result_future.exception())

                return

            function_result: dict = result_future.result()

            if not function_result['is_successful']:
                self.set_exception(errors.InvokeError(
                    error_message = function_result['return_result'],
                    request_id = self.__function_request_id
                ))
            
            self.set_result(helper.inferred_return_result(
                function_result['return_result']))

            self.done()

    def __await__(self):
        self._complete_callback(None)
        return super().__await__()

class FunctionSchedule:
    '''
    An invoke scheduled task representing a Cloud Function.

    Note that this type should not be instantiated
        directly unless necessary.
    '''
    
    def __init__(self,
        function_client: client.AbstractClient,
        invoke_context: dict,
        invoke_timestamp: int,
        invoked_callback: object = None
    ):
        if not function_client or not isinstance(function_client, client.AbstractClient):
            raise ValueError('<function_client> value invalid')

        if not invoke_context or not isinstance(invoke_context, dict):
            raise ValueError('<invoke_context> value invalid')

        if not invoke_timestamp or not isinstance(invoke_timestamp, int):
            raise ValueError('<invoke_timestamp> value invalid')

        self.__function_client: client.AbstractClient = function_client
        self.__invoke_context: dict = invoke_context
        self.__invoke_timestamp: int = invoke_timestamp
        self.__invoked_callback: object = invoked_callback

        self.__invoke_future: asyncio.Future = None
        self.__invoke_handle: asyncio.TimerHandle = None

        self.__function_client.get_event_loop().call_later(
            delay = invoke_timestamp - int(time.time()),
            callback = self._invoke_callback
        )

    def _invoke_callback(self):
        '''
        Timer callback method.
        
        This method creates and runs the invoke coroutine
            object associated with the Cloud Function.
        '''

        self.__invoke_future = self.__function_client.get_event_loop().create_task(
            self.__function_client.invoke_async(**self.__invoke_context)
        )

        self.__invoke_future.add_done_callback(self._completed_callback)

    def _completed_callback(self,
        invoke_result_future: asyncio.Future
    ):
        '''
        Cloud Function invoke completes the callback method.
        '''

        if invoke_result_future.exception():
            if not self.__invoked_callback:
                raise invoke_result_future.exception()

        if self.__invoked_callback:
            self.__invoked_callback(self)

    def cancel(self):
        '''
        Try canceling a Cloud Function scheduled invoke task.

        Raises:
            StatusError: Invoke task has started
        '''

        if self.__invoke_future:
            raise errors.StatusError('invoke has started')

        self.__invoke_handle.cancel()
    
    @property
    def is_successful(self) -> bool:
        '''
        Whether Invoke was successful
        '''

        if not self.__invoke_future:
            raise errors.StatusError('invoke has not started')

        return self.__invoke_future.exception() == None
    
    @property
    def exception(self) -> errors.errors.Error:
        '''
        An instance of the exception thrown by Invoke.

        Raises:
            StatusError: Invoke task has not started
        '''

        if not self.__invoke_future:
            raise errors.StatusError('invoke has not started')

        return self.__invoke_future.exception()
    
    @property
    def result(self) -> dict:
        '''
        Dictionary object for invoke results

        Raises:
            StatusError: Invoke task has not started
        '''

        if not self.__invoke_future:
            raise errors.StatusError('invoke has not started')

        return self.__invoke_future.result()
    
    @property
    def return_value(self) -> dict:
        '''
        Cloud Function invoke return value.

        Unlike the property result, this property will try to
            infer the result of the Cloud Function's invoke and
            convert it to a Python native data type.

        Raises:
            StatusError: Invoke task has not started
        '''

        return helper.inferred_return_result(self.result['return_result'])

class Client(client.AbstractClient):
    '''
    Abstract client type representing Serverless Cloud Function products.

    Args:
        credentials_context: Credential context instance.
    
    Raises:
        ValueError: Parameter values are not as expected.
    '''

    async def easy_invoke_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_event: dict = None,
        function_version: str = None,
        function_async: bool = False
    ) -> object:
        '''
        Invoke specifies a Cloud Function.

        Args:
            region_id: Unique identifier of the data center campus.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_event: Cloud Function invoke event.
            function_version: Cloud Function version.
            function_async: Make Cloud Function asynchronous invoke.
        
        Returns:
            Returns the automatically inferred Cloud Function return value.
        
        Raises:
            ValueError: Parameter values are not as expected.
            InvokeError: Invoke Cloud Function failed.
            ActionError: Invoke Cloud Function error.
        '''

        if not function_async:
            invoke_result: dict = await self.invoke_async(region_id, namespace_name,
                function_name, function_event, function_version, False)
            
            return helper.inferred_return_result(invoke_result['return_result'])
        else:
            return await FunctionResultFuture(
                function_client = self,
                function_metadata = {
                    'region_id': region_id,
                    'namespace_name': namespace_name,
                    'function_name': function_name,
                    'function_version': function_version
                },
                function_request_id = (await self.invoke_async(region_id, namespace_name,
                    function_name, function_event, function_version, True))['request_id']
            )

    def easy_invoke(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_event: dict = None,
        function_version: str = None,
        function_async: bool = False
    ) -> object:
        '''
        Invoke specifies a Cloud Function.

        Args:
            region_id: Unique identifier of the data center campus.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_event: Cloud Function invoke event.
            function_version: Cloud Function version.
            function_async: Make Cloud Function asynchronous invoke.
        
        Returns:
            Returns the automatically inferred Cloud Function return value.
        
        Raises:
            ValueError: Parameter values are not as expected.
            InvokeError: Invoke Cloud Function failed.
            ActionError: Invoke Cloud Function error.
        '''

        if not function_async:
            return self.get_event_loop().run_until_complete(self.easy_invoke_async(region_id,
                namespace_name, function_name, function_event, function_version, False))
        else:
            return FunctionResultFuture(
                function_client = self,
                function_metadata = {
                    'region_id': region_id,
                    'namespace_name': namespace_name,
                    'function_name': function_name,
                    'function_version': function_version
                },
                function_request_id = (self.get_event_loop().run_until_complete(
                    self.invoke_async(region_id, namespace_name, function_name, function_event,
                    function_version, True))['request_id'])
            )

    async def select_function_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_version: str = None,
        function_async: bool = False
    ):
        '''
        Create Python's native asynchronous abstract
            function for Cloud Function.

        Args:
            region_id: Unique identifier of the data center campus.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_version: Cloud Function version.
            function_async: Make Cloud Function asynchronous invoke.

        Returns:
            Returns a Python native asynchronous function instance.
        '''

        return (lambda **function_event: self.easy_invoke_async(region_id, namespace_name,
            function_name, function_event, function_version, function_async))

    def select_function(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_version: str = None,
        function_async: bool = False
    ):
        '''
        Create Python's native synchronous abstract
            function for Cloud Function.

        Args:
            region_id: Unique identifier of the data center campus.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_version: Cloud Function version.
            function_async: Make Cloud Function asynchronous invoke.

        Returns:
            Returns a Python native synchronous function instance.
        '''

        return (lambda **function_event: self.easy_invoke(region_id,
            namespace_name, function_name, function_event, function_version, function_async))

    def bind_function(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_version: str = None,
        function_async: bool = False,
        include_attributes: list = None
    ) -> object:
        '''
        Create a Python native synchronous or asynchronous function
            binding for a given Cloud Function.
        
        The bound object must be a function, a class method, or a class
            instance method, otherwise the behavior is undefined.

        The parameter type of the bound callable object must be JSON serializable,
            or a JSON serialization related exception will be thrown.
        
        Args:
            region_id: Unique identifier of the data center campus.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_version: Cloud Function version.
            function_async: Make Cloud Function asynchronous invoke.
            include_attributes: Need to include the property name from
                the current instance. These properties will be preferentially
                added to the Cloud Function invoke event. If the bound object
                is not a class method or a class instance method, this parameter is ignored.
        
        Returns:
            Returns the Python decorator handler function.
        '''

        def decorator_handler(
            bound_function: object
        ):
            if not callable(bound_function):
                raise TypeError('invalid binding object type')

            def invoke_handler(*args, **kwargs):
                function_event: dict = dict()
                parameter_names: list = inspect.getfullargspec(bound_function).args

                if len(parameter_names) > 0:
                    if parameter_names[0] == 'self' or parameter_names[0] == 'cls':
                        if include_attributes:
                            for name in include_attributes:
                                function_event[name] = getattr(args[0], name)

                        del parameter_names[0]
                        args = args[1 : ]

                for index in range(len(args)):
                    function_event[parameter_names[index]] = args[index]
                
                for name in kwargs:
                    function_event[name] = kwargs[name]

                return (self.easy_invoke_async if inspect.iscoroutinefunction(bound_function)
                    else self.easy_invoke)(region_id, namespace_name, function_name,
                        function_event, function_version, function_async)

            return invoke_handler

        return decorator_handler

    def schedule_invoke(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_event: dict = None,
        function_version: str = None,
        function_async: bool = False,
        invoke_timestamp: int = None,
        invoked_callback: object = None
    ) -> FunctionSchedule:
        '''
        Schedule a Cloud Function to invoke at a specified time.

        Args:
            region_id: Unique identifier of the data center campus.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_event: Cloud Function invoke event.
            function_version: Cloud Function version.
            function_async: Make Cloud Function asynchronous invoke.
            invoke_timestamp: Specifies the native UNIX timestamp at which invoke begins.
            invoked_callback: Callback function after Invoke is over.
        
        Returns:
            Returns an instance of the FunctionSchedule type representing this schedule.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not invoke_timestamp:
            invoke_timestamp = int(time.time()) + 3
        else:
            if not isinstance(invoke_timestamp, int):
                raise ValueError('<invoke_timestamp> value invalid')
        
        return FunctionSchedule(
            function_client = self,
            invoke_context = {
                'region_id': region_id,
                'namespace_name': namespace_name,
                'function_name': function_name,
                'function_event': function_event,
                'function_version': function_version,
                'function_async': function_async
            },
            invoke_timestamp = invoke_timestamp,
            invoked_callback = invoked_callback
        )

# Built-in client instances for specific operating environments
__builtin_managed_client: Client = None

def invoke(
    function_name: str,
    function_event: dict = None,
    function_version: str = None,
    function_async: bool = False,
    namespace_name: str = None,
    region_id: str = None
) -> object:
    '''
    Invoke specifies a Cloud Function.

    Note that this is typically used to quickly call another
        Cloud Function within the same Cloud Region and namespace
        as the current Cloud Function.
    
    The current Cloud Function must be configured with a valid execution
        role, otherwise an EnvironmentError exception will be thrown.

    Args:
        function_name: Cloud Function name.
        function_event: Cloud Function invoke event.
        function_version: Cloud Function version.
        function_async: Make Cloud Function asynchronous invoke.
        region_id: Unique identifier of the data center campus.
        namespace_name: Name of the owning namespace.
        
    Returns:
        Returns the automatically inferred Cloud Function return value.
        
    Raises:
        ValueError: Parameter values are not as expected.
        InvokeError: Invoke Cloud Function failed.
        ActionError: Invoke Cloud Function error.
    '''

    global __builtin_managed_client

    if not __builtin_managed_client:
        __builtin_managed_client = Client(None)
    
    return __builtin_managed_client.easy_invoke(region_id, namespace_name, function_name,
        function_event, function_version, function_async)

async def invoke_async(
    function_name: str,
    function_event: dict = None,
    function_version: str = None,
    function_async: bool = False,
    namespace_name: str = None,
    region_id: str = None
) -> object:
    '''
    Invoke specifies a Cloud Function.

    Note that this is typically used to quickly call another
        Cloud Function within the same Cloud Region and namespace
        as the current Cloud Function.
    
    The current Cloud Function must be configured with a valid execution
        role, otherwise an EnvironmentError exception will be thrown.

    Args:
        function_name: Cloud Function name.
        function_event: Cloud Function invoke event.
        function_version: Cloud Function version.
        function_async: Make Cloud Function asynchronous invoke.
        region_id: Unique identifier of the data center campus.
        namespace_name: Name of the owning namespace.
        
    Returns:
        Returns the automatically inferred Cloud Function return value.
        
    Raises:
        ValueError: Parameter values are not as expected.
        InvokeError: Invoke Cloud Function failed.
        ActionError: Invoke Cloud Function error.
    '''

    global __builtin_managed_client

    if not __builtin_managed_client:
        __builtin_managed_client = Client(None)
    
    return await __builtin_managed_client.easy_invoke_async(region_id, namespace_name, function_name,
        function_event, function_version, function_async)