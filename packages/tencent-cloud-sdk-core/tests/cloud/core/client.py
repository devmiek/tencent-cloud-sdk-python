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

import os
import asyncio

async def run_unit_tests_async():
    from tencent.cloud.auth import credentials
    from tencent.cloud.core import client
    from tencent.cloud.core import errors

    client: client.BaseClient = client.BaseClient(
        credentials_context = credentials.Credentials(
            secret_id = 'AKIDz8krbsJ5yKBZQpn74WFkmLPx3EXAMPLF',
            secret_key = 'Gu5t9xGARNpq86cd98joQYCN3EXAMPLF'
        ),
        request_proxies_context = None,
        request_endpoint = 'scf.tencentcloudapi.com'
    )

    try:
        await client.request_action_async(
            region_id = 'ap-shanghai',
            product_id = 'scf',
            action_id = '__TestFunction',
            action_parameters = {
                'Namespace': 'default',
                'FunctionName': 'hello'
            },
            action_version = '2999-12-31'
        )
    except errors.ActionError:
        pass

    client.get_event_loop()

    await client.download_resource_async(
        resource_url = 'https://libget.com/hello',
        local_file_name = './test.txt'
    )

    os.remove('./test.txt')

    print('info: <tencent.cloud.core.client> test completed')

def run_unit_tests():
    asyncio.get_event_loop().run_until_complete(run_unit_tests_async())
