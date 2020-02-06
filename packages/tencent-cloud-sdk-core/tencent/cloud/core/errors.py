# tencent.cloud.core.errors is python-3.6 source file

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
