# tests.cloud.auth.credentials is python-3.6 source file

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

import time

def run_unit_tests():
    from tencent.cloud.auth import credentials

    credentials_context: credentials.Credentials = credentials.Credentials(
        secret_id = 'AKIDz8krbsJ5yKBZQpn74WFkmLPx3EXAMPLF',
        secret_key = 'Gu5t9xGARNpq86cd98joQYCN3EXAMPLF'
    )

    credentials_context.generate_and_signature(
        request_hostname = 'scf.tencentcloudapi.com',
        request_method = 'POST',
        request_parameters = {
            'Namespace': 'default',
            'FunctionName': 'hello'
        },
        signature_product_id = 'scf',
        signature_timestamp = int(time.time())
    )

    print('info: <tencent.cloud.auth.credentials> test completed')
