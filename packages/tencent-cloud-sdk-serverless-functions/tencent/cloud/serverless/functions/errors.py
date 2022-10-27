# Copyright (c) 2022 MIEK
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
Defines the types of exceptions that the Serverless Cloud Function
    product client may actively throw.
'''

from tencent.cloud.core import errors

class InvokeError(errors.ClientError):
    '''
    This exception indicates that Invoke has an error with a given Cloud Function,
        which is usually caused by a given Cloud Function failing to run.
    '''
    
    def __init__(self,
        error_message: str,
        request_id: str
    ):
        if not error_message or not isinstance(error_message, str):
            raise ValueError('<error_message> value invalid')

        if not request_id or not isinstance(request_id, str):
            raise ValueError('<request_id> value invalid')

        self.error_message: str = error_message
        self.request_id: str = request_id

        super().__init__(
            'invoke function error: error-message: {ERROR_MESSAGE}; request-id: {REQUEST_ID}'.format(
                ERROR_MESSAGE = error_message,
                REQUEST_ID = request_id
            )
        )

class StatusError(errors.ClientError):
    '''
    This exception indicates that the current state
        of the operated object is not as expected.
    '''
