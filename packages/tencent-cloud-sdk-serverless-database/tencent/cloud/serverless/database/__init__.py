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
This package provides object-oriented programming support
    for Tencent Cloud's serverless databases.
'''

import threading

from tencent.cloud.serverless.database.client import Client
from tencent.cloud.serverless.database.client import DatabaseCharset

__thread_local_attributes: threading.local = threading.local()

def fetch_client() -> Client:
    '''
    Get the built-in serverless database product client
        instance for the current hyperthreading. If the built-in
        serverless database product client instance has never
        been created in the current hyper-threading, a new one
        is created by default.

    Returns:
        Returns a serverless database product client instance.
    '''

    global __thread_local_attributes

    if not hasattr(__thread_local_attributes, 'builtin_client'):
        __thread_local_attributes.builtin_client = Client()

    return __thread_local_attributes.builtin_client
