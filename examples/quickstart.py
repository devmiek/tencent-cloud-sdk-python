# quickstart is python-3.6 source file

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
Tencent Cloud SDK for Python Quick Start Demo Code.
https://github.com/nobody-night/tencent-cloud-sdk-python
'''

# import module and packages

import sys

from tencent.cloud.core import errors
from tencent.cloud.auth import credentials
from tencent.cloud.serverless import functions

def main():
    # We need to instantiate an access credential so that Tencent Cloud
    # can determine that you have the right to operate.

    access_credentials: credentials.Credentials = credentials.Credentials(
        secret_id = 'AKIDF3sMOAU1pOgkmrKHchX6TZQ1Mo1C5qa7',
        secret_key = 'b4JL8fwxkIgsKMXGi39yYt0ECxZw4wZf'
    )

    # We need to instantiate a product client for Serverless Cloud Function.

    function_client: functions.Client = functions.Client(
        access_credentials = access_credentials
    )

    # We try to Invoke a Cloud Function and get the return value.
    # Suppose we have a Cloud Function hello in the namespace default
    # of the data center ap-shanghai:

    try:
        return_value: str = function_client.easy_invoke(
            region_id = 'ap-shanghai',  # Unique identifier of the data center
            namespace_name = 'default', # Name of the namespace
            function_name = 'hello'     # Name of the Cloud Function
        )

        print('info: ' + return_value)
    except functions.errors.InvokeError as error:
        print('error: ' + str(error), file = sys.stderr)
    except errors.ActionError as error:
        print('error: ' + str(error), file = sys.stderr)

if __name__ == '__main__':
    main()
