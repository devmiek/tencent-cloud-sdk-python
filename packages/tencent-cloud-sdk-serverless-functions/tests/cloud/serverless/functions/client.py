# tests.cloud.serverless.functions.client is python-3.6 source file

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

def run_unit_tests():
    from tencent.cloud.core import errors
    from tencent.cloud.auth import credentials
    from tencent.cloud.serverless import functions

    function_client: functions.Client = functions.Client(
        credentials_context = credentials.Credentials(
            secret_id = 'AKIDiW4OSFF69wSiiSq9NN7UecLo49zbvCds',
            secret_key = 'BE7mLi0AaVDfrAG8mNm4A6mHlzyg7ML3'
        )
    )

    try:
        function_client.create_namespace(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            namespace_description = 'sdk unit tests'
        )
    except errors.ActionError:
        pass

    try:
        for _ in function_client.list_namespaces('ap-shanghai'):
            pass
    except errors.ActionError:
        pass

    try:
        function_client.create_function(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            function_name = 'hello',
            function_description = 'unit-test function',
            function_code = functions.FunctionCode().use_git_repository(
                git_url = 'https://github.com/tencentyun/scf-demo-repo.git',
                git_directory_name = 'Python3.6-helloworld'
            ),
            function_runtime = functions.FunctionRuntime.Python,
            function_type = functions.FunctionType.Event,
            function_configure = {
                'handler': 'index.main_handler',
                'memory_size': 128,
                'time_out': 3
            }
        )
    except errors.ActionError:
        pass

    try:
        function_client.update_function_code(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            function_name = 'hello',
            function_code = functions.FunctionCode().use_git_repository(
                git_url = 'https://github.com/tencentyun/scf-demo-repo.git',
                git_directory_name = 'Python3.6-helloworld'
            ),
            function_handler = 'index.main_handler'
        )
    except errors.ActionError:
        pass

    try:
        function_client.update_function_configure(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            function_name = 'hello',
            function_configure = {
                'time_out': 5
            }
        )
    except errors.ActionError:
        pass

    try:
        function_client.update_namespace(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            namespace_description = 'update unit-test namespace'
        )
    except errors.ActionError:
        pass

    try:
        for function_info in function_client.list_functions(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest'
        ):
            try:
                function_client.get_function_info(
                    region_id = 'ap-shanghai',
                    namespace_name = 'unittest',
                    function_name = function_info['name']
                )
            except errors.ActionError:
                pass

            try:
                for _ in function_client.list_function_versions(
                    region_id = 'ap-shanghai',
                    namespace_name = 'default',
                    function_name = function_info['name']
                ):
                    pass
            except errors.ActionError:
                pass
    except errors.ActionError:
        pass
    
    try:
        function_client.copy_function(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            function_name = 'hello',
            target_region_id = 'ap-shanghai',
            target_namespace_name = 'unittest',
            target_function_name = 'hello2'
        )
    except errors.ActionError:
        pass

    try:
        function_client.publish_function_version(
            region_id = 'ap-shanghai',
            namespace_name = 'default',
            function_name = 'hello',
            version_description = 'unit-test'
        )
    except errors.ActionError:
        pass

    try:
        function_client.create_trigger(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            function_name = 'hello',
            function_trigger = functions.FunctionTrigger().use_timer(
                timer_name = 'default',
                timer_cron = '0 */1 * * *'
            )
        )
    except errors.ActionError:
        pass

    try:
        function_client.get_function_code_download_url(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            function_name = 'hello'
        )
    except errors.ActionError:
        pass

    try:
        function_client.easy_invoke(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            function_name = 'hello',
            function_event = {
                'value1': 10,
                'value2': 20
            }
        )
    except errors.ActionError:
        pass

    try:
        function_client.easy_invoke(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            function_name = 'hello',
            function_event = {
                'value1': 10,
                'value2': 20
            },
            function_async = True
        )
    except errors.ActionError:
        pass

    hello = function_client.select_function(
        region_id = 'ap-shanghai',
        namespace_name = 'unittest',
        function_name = 'hello'
    )

    try:
        hello(
            value1 = 30,
            value2 = 40
        )
    except errors.ActionError:
        pass

    hello = function_client.select_function(
        region_id = 'ap-shanghai',
        namespace_name = 'unittest',
        function_name = 'hello',
        function_async = True
    )

    try:
        hello(
            value1 = 50,
            value2 = 60
        )
    except errors.ActionError:
        pass

    request_id: str = 'feda8c0e-93d9-470a-a74a-7a3faf7f465e'

    try:
        request_id: str = function_client.invoke(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            function_name = 'hello',
            function_event = {
                'value1': 70,
                'value2': 80
            },
            function_async = True
        )['request_id']
    except errors.ActionError:
        pass

    try:
        function_client.get_function_result_by_request_id(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            function_name = 'hello',
            function_request_id = request_id
        )
    except errors.NotFoundError:
        pass
    except errors.ActionError:
        pass

    try:
        function_client.delete_trigger(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            function_name = 'hello',
            function_trigger = functions.FunctionTrigger().use_timer(
                timer_name = 'default',
                timer_cron = '0 */1 * * *'
            )
        )
    except errors.ActionError:
        pass

    try:
        function_client.delete_function(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            function_name = 'hello2'
        )
    except errors.ActionError:
        pass

    try:
        function_client.delete_function(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest',
            function_name = 'hello'
        )
    except errors.ActionError:
        pass

    try:
        function_client.delete_namespace(
            region_id = 'ap-shanghai',
            namespace_name = 'unittest'
        )
    except errors.ActionError:
        pass

    print('info: <tencent.cloud.serverless.functions.client> test completed')
