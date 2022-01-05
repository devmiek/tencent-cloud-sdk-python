# tencent.cloud.core.waitable is python-3.6 source file

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
Implementing waitable abstract types.
'''

import inspect
import asyncio

class WaitableStatus:
    '''
    An enumerator containing waitable operation states.
    '''

    Created: int = 0
    Waiting: int = 1
    Completed: int = 2

class Waitable:
    '''
    Represents a type of waitable operation.

    Args:
        event_loop: An instance of an event loop
            related to a waitable operation.
        
    Raises:
        ValueError: Parameter value or type is not as expected.
    '''

    def __init__(self,
        event_loop: asyncio.AbstractEventLoop
    ):
        if not event_loop or not isinstance(event_loop, asyncio.AbstractEventLoop):
            raise ValueError('<event_loop> value invalid')

        self.__event_loop: asyncio.AbstractEventLoop = event_loop
        self.__wait_status: int = WaitableStatus.Created
        self.__wait_result: object = None

    def _get_event_loop(self) -> asyncio.AbstractEventLoop:
        '''
        Internal method: Get the event loop instance.
        '''

        return self.__event_loop

    def _set_status(self,
        wait_status: int
    ):
        '''
        Internal method: Set wait state.
        '''

        if wait_status == None or not isinstance(wait_status, int):
            raise ValueError('<wait_status> value invalid')

        self.__wait_status = wait_status

    @property
    def status(self) -> int:
        '''
        Indicates waitable operation status.
        '''

        return self.__wait_status
    
    @property
    def result(self) -> object:
        '''
        Indicates the result of the operation.
        '''

        return self.__wait_result

    def set_result(self,
        wait_result: object
    ):
        '''
        Set the operation result of the waitable operation.

        Args:
            wait_result: Operation result instance.
        '''

        self.__wait_result = wait_result

    async def wait_for_done_async(self,
        max_wait_seconds: float = 15
    ) -> object:
        '''
        Wait for the current operation to complete,
            unless it times out.

        Args:
            max_wait_seconds: The maximum number of seconds to
                wait. If set to None, it will wait indefinitely.
        
        Returns:
            Returns an instance containing the result of the operation.
                If no results are available for this operation, None is returned.
        
        Raises:
            ValueError: Parameter value or type is not as expected.
            TimeoutError: Exceeded max waiting time limit.
        '''

        raise NotImplementedError

    def wait_for_done(self,
        max_wait_seconds: float = 15
    ) -> object:
        '''
        Wait for the current operation to complete,
            unless it times out.

        Args:
            max_wait_seconds: The maximum number of seconds to
                wait. If set to None, it will wait indefinitely.
        
        Returns:
            Returns an instance containing the result of the operation.
                If no results are available for this operation, None is returned.
        
        Raises:
            ValueError: Parameter value or type is not as expected.
            TimeoutError: Exceeded max waiting time limit.
        '''

        return self.__event_loop.run_until_complete(self.wait_for_done_async(
            max_wait_seconds))

    def has_done(self) -> bool:
        '''
        Whether the operation has completed.

        Returns:
            Returns True if the operation has completed,
                otherwise returns False.
        '''

        return self.__wait_status == WaitableStatus.Completed

class OperationWaitable(Waitable):
    '''
    Represents a type of waitable operation and
        supports custom wait processing flow.

    Args:
        event_loop: An instance of an event loop
            related to a waitable operation.
        wait_handler: A custom asynchronous function
            instance waiting for processing.
    
    Raises:
        ValueError: Parameter value or type is not as expected.
    '''
    
    def __init__(self,
        event_loop: asyncio.AbstractEventLoop,
        wait_handler: object
    ):
        if not wait_handler or not callable(wait_handler):
            raise ValueError('<wait_handler> value invalid')

        if not inspect.iscoroutinefunction(wait_handler):
            raise ValueError('<wait_handler> not async function')

        self.__wait_handler: object = wait_handler
        super().__init__(event_loop)

    async def wait_for_done_async(self,
        max_wait_seconds: float = 15
    ) -> object:
        '''
        Wait for the current operation to complete,
            unless it times out.

        Args:
            max_wait_seconds: The maximum number of seconds to
                wait. If set to None, it will wait indefinitely.
        
        Returns:
            Returns an instance containing the result of the operation.
                If no results are available for this operation, None is returned.
        
        Raises:
            ValueError: Parameter value or type is not as expected.
            TimeoutError: Exceeded max waiting time limit.
        '''

        if max_wait_seconds and not isinstance(max_wait_seconds, int):
            if not isinstance(max_wait_seconds, float):
                raise ValueError('<max_wait_seconds> value invalid')

        self._set_status(WaitableStatus.Waiting)

        try:
            self.set_result(
                await asyncio.wait_for(self.__wait_handler(),
                    max_wait_seconds, loop = self._get_event_loop())
            )
        except asyncio.TimeoutError:
            self._set_status(WaitableStatus.Created)
            raise TimeoutError('exceeded max waiting time limit')
        except:
            self._set_status(WaitableStatus.Created)
            raise
        
        self._set_status(WaitableStatus.Completed)
        return self.result
