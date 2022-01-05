# tencent.cloud.core.proxies is python-3.6 source file

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
Implements a proxy server context type.
'''

import os

from tencent.cloud.core import errors

class ProxyType:
    '''
    Proxy server type enumerator
    '''

    Http: str = 'http'
    Https: str = 'https'

class Proxies:
    '''
    Represents the type of proxy server context.

    Args:
        proxy_name: Unique name of the proxy.
        proxy_type: The type of the proxy server,
            including an enumerator: ProxyType.
        proxy_endpoint: Proxy server endpoint.
        proxy_auth: Proxy server authentication context instance.
    
    Raises:
        ValueError: Parameter values are not as expected.
    '''

    def __init__(self,
        proxy_name: str,
        proxy_type: str,
        proxy_endpoint: str,
        proxy_auth: dict = None
    ):
        self.proxy_name: str = None
        self.proxy_type: str = None
        self.proxy_endpoint: str = None
        self.proxy_auth: dict = None

        self.__proxies: dict = dict()

        self.add_proxy_server(proxy_name, proxy_type, proxy_endpoint, proxy_auth)
        self.use_proxy_server(proxy_name)

    def use_proxy_server(self,
        proxy_name: str
    ):
        '''
        Use the given proxy server.

        Args:
            proxy_name: Unique name of the proxy.
        
        Raises:
            NotFoundError: No given proxy server found.
        '''

        try:
            self.proxy_type = self.__proxies[proxy_name]['type']
            self.proxy_endpoint = self.__proxies[proxy_name]['endpoint']
            self.proxy_auth = self.__proxies[proxy_name]['auth']
            self.proxy_name = proxy_name
        except KeyError:
            raise errors.NotFoundError('no such proxy server: ' + proxy_name)

    def add_proxy_server(self,
        proxy_name: str,
        proxy_type: str,
        proxy_endpoint: str,
        proxy_auth: dict = None
    ):
        '''
        Add a new proxy server

        Args:
            proxy_name: Unique name of the proxy.
            proxy_type: The type of the proxy server,
                including an enumerator: ProxyType.
            proxy_endpoint: Proxy server endpoint.
            proxy_auth: Proxy server authentication context instance.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ExistedError: A proxy server with the same name already exists.
        '''

        if not proxy_name or not isinstance(proxy_name, str):
            raise ValueError('<proxy_name> value invalid')

        if not proxy_type or not isinstance(proxy_type, str):
            raise ValueError('<proxy_type> value invalid')

        if not proxy_endpoint or not isinstance(proxy_endpoint, str):
            raise ValueError('<proxy_endpoint> value invalid')

        if proxy_auth:
            if not isinstance(proxy_auth, dict):
                raise ValueError('<proxy_auth> value invalid')
            
            if 'username' not in proxy_auth:
                raise ValueError('<proxy_auth> value missing field: username')

            if 'password' not in proxy_auth:
                raise ValueError('<proxy_auth> value missing field: password')
        
        if proxy_name in self.__proxies:
            raise errors.ExistedError('a proxy server with the same name already exists')

        self.__proxies[proxy_name] = {
            'type': proxy_type,
            'endpoint': proxy_endpoint,
            'auth': proxy_auth
        }

    def remove_proxy_server(self,
        proxy_name: str
    ):
        '''
        Remove the given proxy server.

        Args:
            proxy_name: Unique name of the proxy.
        
        Raises:
            ValueError: Parameter values are not as expected.
            NotFoundError: No given proxy server found.
        '''

        if not proxy_name or not isinstance(proxy_name, str):
            raise ValueError('<proxy_name> value invalid')
        
        if proxy_name == self.proxy_name:
            raise errors.OccupiedError('cannot remove active proxy server')

        try:
            del self.__proxies[proxy_name]
        except KeyError:
            raise errors.NotFoundError('no such proxy server: ' + proxy_name)

class EnvironmentalProxies(Proxies):
    '''
    Represents the type of proxy server that can be automatically
        configured for a specific operating environment.

    Raises:
        EnvironmentError: The current operating environment is not as expected.
        ValueError: The auto-configurable proxy server did not meet expectations.
    '''

    def __init__(self):
        if 'TENCENTCLOUD_PROXY_TYPE' not in os.environ:
            raise EnvironmentError('missing environment variable <TENCENTCLOUD_PROXY_TYPE>')
        
        if 'TENCENTCLOUD_PROXY_ENDPOINT' not in os.environ:
            raise EnvironmentError('missing environment variable <TENCENTCLOUD_PROXY_ENDPOINT>')

        super().__init__(
            proxy_name = 'default',
            proxy_type = os.environ['TENCENTCLOUD_PROXY_TYPE'],
            proxy_endpoint = os.environ['TENCENTCLOUD_PROXY_ENDPOINT'],
            proxy_auth = {
                'username': os.environ['TENCENTCLOUD_PROXY_USERNAME'],
                'password': (os.environ['TENCENTCLOUD_PROXY_PASSWORD'] if
                    'TENCENTCLOUD_PROXY_PASSWORD' in os.environ else None)
            } if 'TENCENTCLOUD_PROXY_USERNAME' in os.environ else None
        )
