# tencent.cloud.core.errors is python-3.6 source file

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
Defines the exception type for the Tencent Cloud SDK.
'''

class Error(Exception):
    '''
    Tencent Cloud SDK exception base class, any exceptions
        actively raised by Tencent Cloud SDK are based on this type.
    '''

class NotFoundError(Error):
    '''
    This exception indicates that the related operation did not
        find the specified project or resource.
    '''

class ExistedError(Error):
    '''
    This exception indicates that a given project or resource
        already exists for the relevant operation.
    '''

class OccupiedError(Error):
    '''
    This exception indicates that a given project or resource
        is in use for the relevant operation.
    '''

class ClientError(Error):
    '''
    Tencent Cloud SDK client exception base class.
        Any Tencent Cloud SDK client self-raised exception 
        is based on this type.
    '''

class RequestError(ClientError):
    '''
    This exception indicates that the Cloud API HTTP request failed.
    '''

class ResponseError(ClientError):
    '''
    This exception indicates that the Cloud API HTTP response was unexpected,
        which means that the server may have encountered some errors.
    '''

    def __init__(self,
        status_code: int,
        error_message: str = None
    ):
        if not status_code or not isinstance(status_code, int):
            raise ValueError('<status_code> value invalid')

        if error_message and not isinstance(error_message, str):
            raise ValueError('<error_message> value invalid')

        self.status_code: int = status_code
        self.error_message: str = error_message

        super().__init__(error_message)

class ActionError(ClientError):
    '''
    The exception indicates that the Cloud API's HTTP request was successful
        and the response was as expected, but the Cloud API returned an error.
    '''

    def __init__(self,
        action_id: str,
        error_id: str,
        error_message: str,
        request_id: str
    ):
        if not action_id or not isinstance(action_id, str):
            raise ValueError('<action_id> value invalid')

        if not error_id or not isinstance(error_id, str):
            raise ValueError('<error_id> value invalid')

        if not error_message or not isinstance(error_message, str):
            raise ValueError('<error_message> value invalid')

        if not request_id or not isinstance(request_id, str):
            raise ValueError('<request_id> value invalid')

        self.action_id: str = action_id
        self.error_id: str = error_id
        self.error_message: str = error_message
        self.request_id: str = request_id

        super().__init__(
            (
                'action <{ACTION_ID}> error: error-id: {ERROR_ID}; '
                'error-message: {ERROR_MESSAGE}; request-id: {REQUEST_ID}'
            ).format(
                ACTION_ID = action_id,
                ERROR_ID = error_id,
                ERROR_MESSAGE = error_message,
                REQUEST_ID = request_id
            )
        )

class ActionResultError(ClientError):
    '''
    The exception indicates that the HTTP request for Cloud API was successful,
        but the response did not meet expectations.
    '''

class ErrorHandlerResult:
    '''
    Error handler result enumerator.

    Members:
        Ignore: Ignore the error and pass to the next error handler (if any).
        Throw: Handle and throw the exception instance corresponding to the error.
        Retry: Retry the operation that caused the error immediately.
        Backoff: Backoff retry the operation that caused the error.
    '''

    Ignore: int = 0
    Throw: int = 1
    Retry: int = 2
    Backoff: int = 3

class ErrorManager:
    '''
    Represents the type of one or more error handlers and configurations.

    Args:
        error_handlers: Contains a list instance of the error handler functions.
    
    Raises:
        ValueError: Parameter values are not as expected.
    '''

    def __init__(self,
        error_handlers: list = None
    ):
        self.__error_handlers: list = list()

        if error_handlers:
            if not isinstance(error_handlers, list):
                raise ValueError('<error_handlers> value invalid')

            for handler in error_handlers:
                self.add_handler(handler)
        
        self.__max_number_of_retries: int = 10
        self.__max_backoff_interval: int = 64
        self.__enabled: bool = True

    @property
    def max_number_of_retries(self) -> int:
        '''
        Maximum number of retries for errors, value must be greater than 0.
        '''

        return self.__max_number_of_retries

    @max_number_of_retries.setter
    def max_number_of_retries(self, value: int):
        '''
        Maximum number of retries for errors, value must be greater than 0.
        '''

        if not value or not isinstance(value, int):
            raise ValueError('<max_number_of_retries> value invalid')

        self.__max_number_of_retries = value

    @max_number_of_retries.deleter
    def max_number_of_retries(self):
        '''
        Maximum number of retries for errors, value must be greater than 0.
        '''

        raise OccupiedError('<max_number_of_retries> not allowed to delete')

    @property
    def max_backoff_interval(self) -> int:
        '''
        The length (in seconds) of each error backoff retry,
            this value must be greater than 0.
        '''

        return self.__max_backoff_interval

    @max_backoff_interval.setter
    def max_backoff_interval(self, value: int):
        '''
        The length (in seconds) of each error backoff retry,
            this value must be greater than 0.
        '''

        if not value or not isinstance(value, int):
            raise ValueError('<max_backoff_interval> value invalid')

    @max_backoff_interval.deleter
    def max_backoff_interval(self):
        '''
        The length (in seconds) of each error backoff retry,
            this value must be greater than 0.
        '''

        raise OccupiedError('<max_backoff_interval> not allowed to delete')

    @property
    def enabled(self) -> bool:
        '''
        Whether the error manager is enabled.
        '''

        return self.__enabled
    
    @enabled.setter
    def enabled(self, value: bool):
        '''
        Whether the error manager is enabled.
        '''

        if value == None or not isinstance(value, bool):
            raise ValueError('<enabled> value invalid')
        
        self.__enabled = value

    @enabled.deleter
    def enabled(self):
        '''
        Whether the error manager is enabled.
        '''

        raise OccupiedError('<enabled> not allowed to delete')

    def handler(self,
        error_source: object,
        error_instance: Error,
        error_retry_count: int
    ) -> int:
        '''
        Handle an error and get the result of the error handler on the error.

        Args:
            error_source: The instance that caused the error.
            error_instance: The exception instance corresponding to the error.
            error_retry_count: Number of times the error has been retried.
        
        Returns:
            Returns error handler results.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not error_instance or not isinstance(error_instance, Error):
            raise ValueError('<error_instance> value invalid')

        if not self.__enabled:
            return ErrorHandlerResult.Throw

        for error_handler in self.__error_handlers:
            handler_result: int = error_handler(self, error_source, error_instance,
                error_retry_count)

            if handler_result == None or not isinstance(handler_result, int):
                raise ValueError('<handler_result> value invalid')

            if handler_result != ErrorHandlerResult.Ignore:
                return handler_result
        
        return ErrorHandlerResult.Throw

    def add_handler(self,
        error_handler: object
    ):
        '''
        Add an error handler.

        Args:
            error_handler: Function instance of the error handler.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ExistedError: The given error handler callback function already exists.
        '''

        if not error_handler and callable(error_handler):
            raise ValueError('<error_handler> value invalid')

        if error_handler in self.__error_handlers:
            raise ExistedError('error handler already exists')

        self.__error_handlers.append(error_handler)
    
    def remove_handler(self,
        error_handler: object
    ):
        '''
        Remove an added error handler.

        Args:
            error_handler: Function instance of the error handler.
        
        Raises:
            ValueError: Parameter values are not as expected.
            NotFoundError: The function instance for the given error
                handler was not found.
        '''
    
        if not error_handler and callable(error_handler):
            raise ValueError('<error_handler> value invalid')

        try:
            del self.__error_handlers[
                self.__error_handlers.index(error_handler)]
        except ValueError:
            raise NotFoundError('no such error handler')

    def has_handler(self,
        error_handler: object
    ):
        '''
        Check if the given error handler has been added.

        Args:
            error_handler: Function instance of the error handler.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not error_handler and callable(error_handler):
            raise ValueError('<error_handler> value invalid')

        return error_handler in self.__error_handlers

    def clear_all_handler(self):
        '''
        Remove all error handlers.
        '''

        self.__error_handlers.clear()
