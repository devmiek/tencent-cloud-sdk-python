# integrate is python-3.6 source file

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
This module implements an integrated dispatcher type
    suitable for serverless cloud function integration invoke.
'''

import json
import base64

from tencent.cloud.core import errors

class IntegrateDispatch:
    '''
    Represents a type suitable for serverless cloud function
        integration invoke dispatchers.
    '''

    def __init__(self):
        self.__protocol_version: int = 1
        self.__bind_functions: dict = dict()

    def routine(self,
        bound_function: object
    ) -> object:
        '''
        Bind a Python synchronous function instance to the
            integration invoke dispatcher.
        
        The bound object must be a function, otherwise the
            behavior is undefined.

        Returns:
            Returns the Python decorator handler function.
        '''

        if not bound_function or not callable(bound_function):
            raise ValueError('<bound_function> value invalid')

        if bound_function.__name__ in self.__bind_functions:
            raise errors.ExistedError('bound callable object already exists')

        self.__bind_functions[bound_function.__name__] = bound_function
        return bound_function

    def handler(self,
        event: dict,
        context: dict
    ) -> object:
        '''
        Processing serverless cloud function invoke requests.

        Args:
            event: Serverless cloud function events.
            context: Serverless cloud function execution metadata.
        
        Raises:
            ValueError: Parameter value or integrated invoke protocol
                is not as expected.
            NotFoundError: The calling function indicated by the
                integrated invoke protocol does not exist.
        
        Returns:
            Returns an integrated invoke protocol payload string.
        '''

        if not event or not isinstance(event, dict):
            raise ValueError('<event> value invalid')

        if not context or not isinstance(context, dict):
            raise ValueError('<context> value invalid')

        try:
            protocol_version: int = event['protocol']['version']
            protocol_payload: str = event['protocol']['payload']
        except KeyError as error:
            raise ValueError('<event> missing field: ' + str(error))

        if protocol_version != self.__protocol_version:
            raise ValueError('unsupported protocol version')

        try:
            protocol_context: dict = json.loads(base64.b64decode(protocol_payload))
        except (base64.binascii.Error, json.JSONDecodeError):
            raise ValueError('protocol payload invalid')

        try:
            routine_name: str = protocol_context['routine_name']
            routine_parameter: dict = protocol_context['routine_parameter']
        except KeyError as error:
            raise ValueError('protocol context missing field: ' + str(error))

        try:
            function_instance: object = self.__bind_functions[routine_name]
        except KeyError:
            raise errors.NotFoundError('no such function: ' + str(routine_name))

        return function_instance(**routine_parameter)
