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

import sys

from tencent.cloud.core import errors
from tencent.cloud.core import helper
from tencent.cloud.serverless import functions

async def main():
    '''
    Call the cloud function named testing in ap-shanghai and print the
    function return value.
    '''

    try:
        print(await functions.invoke_async('testing', 'ap-shanghai'))
    except functions.errors.InvokeError as error:
        print('error: ' + str(error), file = sys.stderr)
    except errors.ActionError as error:
        print('error: ' + str(error), file = sys.stderr)

if __name__ == '__main__':
    '''
    For historical Python reasons, we can't use asyncio.run to run entry
    functions for maximum SDK compatibility.

    asyncio will manage the lifecycle of the event loop internally. When
    asyncio closes the internal event loop, there are still objects that
    are using the associated event loop.
    
    Therefore, we must keep the event loop open. run_with_asyncio will
    create a new event loop and run the given entry function. Unlike
    asyncio, it never closes the created event loop until the process
    terminates.

    In general, the caller should only call it at the entry point.
    '''

    helper.run_with_asyncio(main())
