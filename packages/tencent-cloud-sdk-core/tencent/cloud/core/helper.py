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
Implemented the Tencent Cloud SDK helper functions.
'''

import asyncio

def run_with_asyncio(
    coroutine: asyncio.Future
):
    '''
    Create a new event loop and call the given coroutine. The caller will be
    blocked until the coroutine completes.

    In general, run_with_asyncio is used instead of asyncio.run to avoid
    compatibility issues. The caller should only call at the entry point.

    The event loop created will be set as the global default event loop and
    will not be closed until the process terminates.

    Args:
        coroutine: Coroutine that need to be called on the event loop.

    Raises:
        ValueError: The given coroutine is invalid.
    '''

    if not asyncio.iscoroutine(coroutine):
        raise ValueError('future is not coroutine')

    event_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_until_complete(coroutine)
