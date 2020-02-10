# tencent.cloud.serverless.functions.client is python-3.6 source file

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

'''
Implements the client type of Serverless Cloud Function.
'''

import os
import json

from tencent.cloud.core import client
from tencent.cloud.core import proxies
from tencent.cloud.auth import credentials

from tencent.cloud.serverless.functions import errors
from tencent.cloud.serverless.functions import helper

class FunctionCodeSource:
    '''
    Cloud Function code source enumerator.
    '''

    ObjectStorageBucket: int = 1
    LocalZipFile: int = 2
    GitRepository: int = 3

class FunctionTriggerKind:
    '''
    Cloud Function trigger type enumerator.
    '''

    Timer: str = 'timer'
    ObjectStorageBucket: str = 'cos'
    MessageQueueTopic: str = 'cmq'

class FunctionTrigger:
    '''
    Represents the type of Cloud Function trigger.
    '''

    def __init__(self):
        self.__trigger_kind: str = None
        self.__trigger_context: dict = None

    def get_trigger_kind(self) -> str:
        '''
        Gets the currently configured trigger type.
        '''

        return self.__trigger_kind
    
    def get_trigger_context(self) -> dict:
        '''
        Gets the currently configured trigger context.
        '''

        return self.__trigger_context

    def use_timer(self,
        timer_name: str,
        timer_cron: str
    ):
        '''
        Use timer trigger.

        Args:
            timer_name: Timer name
            timer_cron: Cron expression to trigger the timer
        
        Returns:
            Return to itself.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not timer_name or not isinstance(timer_name, str):
            raise ValueError('<timer_name> value invalid')

        if not timer_cron or not isinstance(timer_cron, str):
            raise ValueError('<timer_cron> value invalid')

        self.__trigger_kind = FunctionTriggerKind.Timer
        self.__trigger_context = {
            'name': timer_name,
            'configure': timer_cron
        }

        return self
    
    def use_object_storage_bucket(self,
        bucket_endpoint: str,
        bucket_requirement_context: dict
    ):
        '''
        Use object storage bucket triggers.

        Args:
            bucket_endpoint: Object storage bucket endpoint host name.
            bucket_requirement_context: Trigger requirement context.
        
        Returns:
            Return to itself.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not bucket_endpoint or not isinstance(bucket_endpoint, str):
            raise ValueError('<bucket_endpoint> value invalid')

        if not bucket_requirement_context or not isinstance(bucket_requirement_context, dict):
            raise ValueError('<bucket_requirement_context> value invalid')

        self.__trigger_kind = FunctionTriggerKind.ObjectStorageBucket

        try:
            trigger_context: dict = {
                'event': bucket_requirement_context['event_id']
            }
        except KeyError as error:
            raise ValueError('<bucket_requirement_context> value missing field: ' + str(error))

        if 'prefix_name' in bucket_requirement_context:
            trigger_context['filter'] = {
                'Prefix': bucket_requirement_context['prefix_name']
            }
                    
        if 'suffix_name' in bucket_requirement_context:
            if 'filter' not in trigger_context:
                trigger_context['filter'] = {
                    'Suffix': bucket_requirement_context['suffix_name']
                }
            else:
                trigger_context['filter']['Suffix'] = bucket_requirement_context['suffix_name']

        self.__trigger_context = {
            'name': bucket_endpoint,
            'configure': json.dumps(trigger_context)
        }

        return self
    
    def use_message_queue_topic(self,
        topic_name: str,
        topic_instance_id: str = None,
        topic_requirement_context = None
    ):
        '''
        Use message queue topic triggers.

        Args:
            topic_name: Topic name.
            topic_instance_id: Topic unique identifier.
            topic_requirement_context: Trigger requirement context.
        
        Returns:
            Return to itself.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not topic_name or not isinstance(topic_name, str):
            raise ValueError('<topic_name> value invalid')

        if topic_instance_id or topic_requirement_context:
            raise NotImplementedError()

        self.__trigger_kind = FunctionTriggerKind.MessageQueueTopic
        self.__trigger_context = {
            'name': topic_name,
            'configure': None
        }

        return self

class FunctionCode:
    '''
    Represents the type of Cloud Function code.
    '''

    def __init__(self):
        self.__code_source: int = None
        self.__code_context: dict = None

    def get_code_source(self) -> int:
        '''
        Get the Cloud Function tag source type.
        '''

        return self.__code_source

    def get_code_context(self) -> dict:
        '''
        Get the Cloud Function code description context.
        '''

        return self.__code_context

    def use_object_storage_bucket(self,
        region_id: str,
        bucket_name: str,
        object_name: str
    ):
        '''
        Use Object storage bucket as source of code.

        Args:
            region_id: Region unique identifier.
            bucket_name: Object storage bucket name.
            object_name: Path to the ZIP archive containing the Cloud Function code.
        
        Returns:
            Return to itself.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not bucket_name or not isinstance(bucket_name, str):
            raise ValueError('<bucket_name> value invalid')

        if not object_name or not isinstance(object_name, str):
            raise ValueError('<object_name> value invalid')

        self.__code_source = FunctionCodeSource.ObjectStorageBucket
        self.__code_context = {
            'region_id': region_id,
            'bucket_name': bucket_name,
            'object_name': object_name
        }

        return self
    
    def use_local_zip_archive(self,
        local_file_path: str
    ):
        '''
        Use a local ZIP archive as the code source.

        Args:
            local_file_path: The full path of the ZIP archive
                containing the source code files.
            
        Raises:
            ValueError: Parameter values are not as expected.
            IOError: The given ZIP archive does not exist or cannot be read.
        '''

        if not local_file_path or not isinstance(local_file_path, str):
            raise ValueError('<local_file_path> value invalid')

        if not os.access(local_file_path, os.R_OK):
            raise IOError('no such file or unreadable')

        self.__code_source = FunctionCodeSource.LocalZipFile
        self.__code_context = {
            'local_file_path': local_file_path
        }

        return self
    
    def use_git_repository(self,
        git_url: str,
        git_branch_name: str = None,
        git_directory_name: str = None,
        git_commit_id: str = None,
        git_username: str = None,
        git_password: str = None
    ):
        '''
        Use a Git repository as a source of code.

        Args:
            git_url: Git repository pull URL.
            git_branch_name: Git repository branch name.
            git_directory_name: The source code is located in the
                directory path of the Git repository.
            git_commit_id: Source code unique Commit ID.
            git_username: The user name who has access to the given
                Git repository.
            git_password: The password of the user who has access to
                the given Git repository.
        
        Raises:
            ValueError: Parameter values are not as expected.
        '''

        if not git_url or not isinstance(git_url, str):
            raise ValueError('<git_url> value invalid')
        
        if git_branch_name and not isinstance(git_branch_name, str):
            raise ValueError('<git_branch_name> value invalid')

        if git_directory_name and not isinstance(git_directory_name, str):
            raise ValueError('<git_directory_name> value invalid')

        if git_commit_id and not isinstance(git_commit_id, str):
            raise ValueError('<git_commit_id> value invalid')

        if git_username and not isinstance(git_username, str):
            raise ValueError('<git_username> value invalid')

        if git_password and not isinstance(git_password, str):
            raise ValueError('<git_password> value invalid')

        self.__code_source = FunctionCodeSource.GitRepository
        self.__code_context = {
            'git_url': git_url,
            'git_branch_name': git_branch_name,
            'git_directory_name': git_directory_name,
            'git_commit_id': git_commit_id,
            'git_username': git_username,
            'git_password': git_password
        }

        return self

class FunctionType:
    '''
    Enumerators for supported function types.
    '''

    Event: str = 'Event'
    HttpService: str = 'HTTP'

class FunctionRuntime:
    '''
    Enumerators for supported function runtimes.
    '''

    Python: str = 'Python3.6'
    Nodejs: str = 'Nodejs8.9'
    Php: str = 'PHP7'
    Golang: str = 'Golang1'
    Java: str = 'Java8'

class FunctionResultType:
    '''
    An enumerator of the supported function run result type.
    '''

    Succeed: str = 'is0'
    Error: str = 'not0'
    TimeLimit: str = 'TimeLimitExceeded'
    ResourceLimit: str = 'ResourceLimitExceeded'
    UserCodeError: str = 'UserCodeException'

class AbstractClient(client.BaseClient):
    '''
    Abstract client type representing Serverless
        Cloud Function products.

    Note that this type should not be instantiated
        manually unless necessary.

    Args:
        credentials_context: Authentication context instance.
        proxies_context: Proxy server context instance.
    '''

    def __init__(self,
        credentials_context: credentials.Credentials = None,
        proxies_context: proxies.Proxies = None
    ):
        self.__product_id: str = 'scf'

        super().__init__(
            credentials_context = credentials_context,
            request_proxies_context = proxies_context,
            request_endpoint = ('scf.tencentcloudapi.com' if not
                helper.is_cloud_function_container() else 'scf.internal.tencentcloudapi.com')
        )
    
    async def invoke_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_event: dict = None,
        function_version: str = None,
        function_async: bool = False
    ) -> dict:
        '''
        Invoke is given a Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Namespace of the given Cloud Function.
            function_name: Requires Cloud Function name for Invoke.
            function_event: Requires Cloud Function event for Invoke.
            function_version: Requires Cloud Function version name for Invoke.
            function_async: Given whether the Cloud Function is Invoke asynchronously.
        
        Returns:
            Returns a dictionary instance containing the Invoke result of
                the Cloud Function.
        
        Raises:
            ValueError: Parameter values are not as expected.
            InvokeError: Invoke given Cloud Function failed.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if region_id:
            if not isinstance(region_id, str):
                raise ValueError('<region_id> value invalid')
        else:
            region_id = helper.get_cloud_function_region_id()

        if namespace_name:
            if not isinstance(namespace_name, str):
                raise ValueError('<namespace_name> value invalid')
        else:
            namespace_name = 'default'

        if not function_name or not isinstance(function_name, str):
            raise ValueError('<function_name> value invalid')

        if function_async != None and not isinstance(function_async, bool):
            raise ValueError('<function_async> value invalid')

        action_parameters: dict = {
            'FunctionName': function_name,
            'InvocationType': 'Event' if function_async else 'RequestResponse',
            'Namespace': namespace_name,
        }

        if function_event:
            if not isinstance(function_event, dict):
                raise ValueError('<function_event> value invalid')
            
            action_parameters['ClientContext'] = json.dumps(function_event)

        if function_version:
            if not isinstance(function_version, str):
                raise ValueError('<function_version> value invalid')

            action_parameters['Qualifier'] = function_version

        action_result: dict = await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'Invoke',
            action_parameters = action_parameters,
            action_version = '2018-04-16'
        )

        try:
            if action_result['Result']['InvokeResult'] != 0:
                raise errors.InvokeError(
                    error_message = action_result['Result']['ErrMsg'],
                    request_id = action_result['Result']['FunctionRequestId']
                )

            return {
                'request_id': action_result['Result']['FunctionRequestId']
            } if function_async else {
                'return_result': action_result['Result']['RetMsg'],
                'request_id': action_result['Result']['FunctionRequestId']
            }
        except KeyError as error:
            raise errors.errors.ActionResultError(
                'action result content missing field: ' + str(error))
  
    def invoke(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_event: dict = None,
        function_version: str = None,
        function_async: bool = False
    ) -> dict:
        '''
        Invoke is given a Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_event: Requires Cloud Function event for Invoke.
            function_version: Cloud Function version name.
            function_async: Given whether the Cloud Function is Invoke asynchronously.
        
        Returns:
            Returns a dictionary instance containing the Invoke result of
                the Cloud Function.
        
        Raises:
            ValueError: Parameter values are not as expected.
            InvokeError: Invoke given Cloud Function failed.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        return self.get_event_loop().run_until_complete(self.invoke_async(region_id,
            namespace_name, function_name, function_event, function_version, function_async))

    async def create_function_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_description: str,
        function_code: FunctionCode,
        function_runtime: str = 'Python3',
        function_type: str = None,
        function_configure: dict = None
    ):
        '''
        Create a new Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_description: Cloud Function description body.
            function_code: Cloud Function default source code.
            function_runtime: Cloud Function runtime name.
            function_type: Cloud Function type (enumerator: FunctionType).
            function_configure: A dictionary instance containing a
                Cloud Function configuration.
            
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        if not function_name or not isinstance(function_name, str):
            raise ValueError('<function_name> value invalid')
        
        if not function_description or not isinstance(function_description, str):
            raise ValueError('<function_description> value invalid')

        if not function_code or not isinstance(function_code, FunctionCode):
            raise ValueError('<function_code> value invalid')

        action_parameters: dict = {
            'Namespace': namespace_name,
            'FunctionName': function_name,
            'Description': function_description
        }

        if 'handler' in function_configure:
            action_parameters['Handler'] = function_configure['handler']
        
        if 'memory_size' in function_configure:
            action_parameters['MemorySize'] = function_configure['memory_size']
        
        if 'time_out' in function_configure:
            action_parameters['Timeout'] = function_configure['time_out']
        
        if 'vpc_configure' in function_configure:
            action_parameters['VpcConfig'] = {
                'VpcId': function_configure['vpc_configure']['vpc_id'],
                'SubnetId': function_configure['vpc_configure']['subnet_id'],
            }
        
        if 'role_id' in function_configure:
            action_parameters['Role'] = function_configure['role_id']
        
        if 'log_configure' in function_configure:
            action_parameters['ClsLogsetId'] = function_configure['log_configure']['logset_id']
            action_parameters['ClsTopicId'] = function_configure['log_configure']['topic_id']
        
        if 'environments' in function_configure:
            action_parameters['Environment'] = {
                'Variables': [{
                    'Key': name,
                    'Value': function_configure['environments'][name]
                } for name in function_configure['environments']]
            }
        
        if function_runtime:
            if not isinstance(function_runtime, str):
                raise ValueError('<function_runtime> value invalid')
            
            action_parameters['Runtime'] = function_runtime
        
        if function_type:
            if not isinstance(function_type, str):
                raise ValueError('<function_type> value invalid')
            
            action_parameters['Type'] = function_type

        function_code_source: int = function_code.get_code_source()
        function_code_context: dict = function_code.get_code_context()

        if function_code_source == FunctionCodeSource.LocalZipFile:
            action_parameters['Code'] = {
                'ZipFile': helper.local_file_to_base64(
                    function_code_context['local_file_path'])
            }

            action_parameters['CodeSource'] = 'ZipFile'
        elif function_code_source == FunctionCodeSource.ObjectStorageBucket:
            action_parameters['Code'] = {
                'CosBucketRegion': function_code_context['region_id'],
                'CosBucketName': function_code_context['bucket_name'],
                'CosObjectName': function_code_context['object_name']
            }

            action_parameters['CodeSource'] = 'Cos'
        elif function_code_source == FunctionCodeSource.GitRepository:
            action_parameters['Code'] = {
                'GitUrl': function_code_context['git_url']
            }

            if function_code_context['git_branch_name']:
                action_parameters['Code']['GitBranch'] = function_code_context['git_branch_name']
            
            if function_code_context['git_directory_name']:
                action_parameters['Code']['GitDirectory'] = function_code_context['git_directory_name']
            
            if function_code_context['git_commit_id']:
                action_parameters['Code']['GitCommitId'] = function_code_context['git_commit_id']
            
            if function_code_context['git_username']:
                action_parameters['Code']['GitUserName'] = function_code_context['git_username']

            if function_code_context['git_password']:
                action_parameters['Code']['GitPassword'] = function_code_context['git_password']

            action_parameters['CodeSource'] = 'Git'
        else:
            raise ValueError('<function_code> value invalid')

        await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'CreateFunction',
            action_parameters = action_parameters,
            action_version = '2018-04-16'
        )

    def create_function(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_description: str,
        function_code: FunctionCode,
        function_runtime: str = 'Python3',
        function_type: str = None,
        function_configure: dict = None
    ):
        '''
        Create a new Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_description: Cloud Function description body.
            function_code: Cloud Function default source code.
            function_runtime: Cloud Function runtime name.
            function_type: Cloud Function type (enumerator: FunctionType).
            function_configure: A dictionary instance containing a
                Cloud Function configuration.
            
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        self.get_event_loop().run_until_complete(self.create_function_async(region_id,
            namespace_name, function_name, function_description, function_code,
            function_runtime, function_type, function_configure))

    async def delete_function_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str
    ):
        '''
        Delete a given Cloud Function that has been created.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        if not function_name or not isinstance(function_name, str):
            raise ValueError('<function_name> value invalid')

        await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'DeleteFunction',
            action_parameters = {
                'Namespace': namespace_name,
                'FunctionName': function_name
            },
            action_version = '2018-04-16'
        )

    def delete_function(self,
        region_id: str,
        namespace_name: str,
        function_name: str
    ):
        '''
        Delete a given Cloud Function that has been created.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        self.get_event_loop().run_until_complete(self.delete_function_async(
            region_id, namespace_name, function_name))

    async def publish_function_version_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        version_description: str = None
    ):
        '''
        Publish a new version of the given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            version_description: New version description text.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        if not function_name or not isinstance(function_name, str):
            raise ValueError('<function_name> value invalid')

        action_parameters: dict = {
            'Namespace': namespace_name,
            'FunctionName': function_name
        }

        if version_description:
            if not isinstance(version_description, str):
                raise ValueError('<version_description> value invalid')
            
            action_parameters['Description'] = version_description
        
        await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'PublishVersion',
            action_parameters = action_parameters,
            action_version = '2018-04-16'
        )

    def publish_function_version(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        version_description: str = None
    ):
        '''
        Publish a new version of the given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            version_description: New version description text.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        self.get_event_loop().run_until_complete(self.publish_function_version_async(
            region_id, namespace_name, function_name, version_description))

    async def copy_function_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        target_region_id: str,
        target_namespace_name: str,
        target_function_name: str,
        allow_override: bool = False,
        copy_configure: bool = True
    ):
        '''
        Creates a copy of the given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            target_region_id: The unique identifier of the target Region.
            target_namespace_name: Target namespace name.
            target_function_name: Cloud Function copy name.
            allow_override: Override if the target Cloud Function already exists.
            copy_configure: The Cloud Function copy has the same configuration
                as the original.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        if not function_name or not isinstance(function_name, str):
            raise ValueError('<function_name> value invalid')

        if not target_region_id or not isinstance(target_region_id, str):
            raise ValueError('<target_region_id> value invalid')

        if not target_namespace_name or not isinstance(target_namespace_name, str):
            raise ValueError('<target_namespace_name> value invalid')

        if not target_function_name or not isinstance(target_function_name, str):
            raise ValueError('<target_function_name> value invalid')

        if allow_override != None and not isinstance(allow_override, bool):
            raise ValueError('<allow_override> value invalid')

        if copy_configure != None and not isinstance(copy_configure, bool):
            raise ValueError('<copy_configure> value invalid')

        await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'CopyFunction',
            action_parameters = {
                'Namespace': namespace_name,
                'FunctionName': function_name,
                'TargetRegion': target_region_id,
                'TargetNamespace': target_namespace_name,
                'NewFunctionName': target_function_name,
                'Override': True if allow_override else False,
                'CopyConfiguration': True if copy_configure else False
            },
            action_version = '2018-04-16'
        )
   
    def copy_function(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        target_region_id: str,
        target_namespace_name: str,
        target_function_name: str,
        allow_override: bool = False,
        copy_configure: bool = True
    ):
        '''
        Creates a copy of the given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            target_region_id: The unique identifier of the target Region.
            target_namespace_name: Target namespace name.
            target_function_name: Cloud Function copy name.
            allow_override: Override if the target Cloud Function already exists.
            copy_configure: The Cloud Function copy has the same configuration
                as the original.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        self.get_event_loop().run_until_complete(self.copy_function_async(
            region_id, namespace_name, function_name, target_region_id,
            target_namespace_name, target_function_name, allow_override,
            copy_configure))

    async def update_function_code_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_code: FunctionCode,
        function_handler: str
    ):
        '''
        Update the source code for a given Cloud Function.
        
        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_code: Cloud Function update source code.
            function_handler: Cloud Function entry point function symbol
                (for example: index.main).
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        if not function_name or not isinstance(function_name, str):
            raise ValueError('<function_name> value invalid')
        
        if not function_code or not isinstance(function_code, FunctionCode):
            raise ValueError('<function_code> value invalid')

        if not function_handler or not isinstance(function_handler, str):
            raise ValueError('<function_handler> value invalid')

        action_parameters: dict = {
            'Namespace': namespace_name,
            'FunctionName': function_name,
            'Handler': function_handler
        }

        function_code_source: int = function_code.get_code_source()
        function_code_context: dict = function_code.get_code_context()

        if function_code_source == FunctionCodeSource.LocalZipFile:
            action_parameters['Code'] = {
                'ZipFile': helper.local_file_to_base64(
                    function_code_context['local_file_path'])
            }

            action_parameters['CodeSource'] = 'ZipFile'
        elif function_code_source == FunctionCodeSource.ObjectStorageBucket:
            action_parameters['Code'] = {
                'CosBucketRegion': function_code_context['region_id'],
                'CosBucketName': function_code_context['bucket_name'],
                'CosObjectName': function_code_context['object_name']
            }

            action_parameters['CodeSource'] = 'Cos'
        elif function_code_source == FunctionCodeSource.GitRepository:
            action_parameters['Code'] = {
                'GitUrl': function_code_context['git_url']
            }

            if function_code_context['git_branch_name']:
                action_parameters['Code']['GitBranch'] = function_code_context['git_branch_name']
            
            if function_code_context['git_directory_name']:
                action_parameters['Code']['GitDirectory'] = function_code_context['git_directory_name']
            
            if function_code_context['git_commit_id']:
                action_parameters['Code']['GitCommitId'] = function_code_context['git_commit_id']
            
            if function_code_context['git_username']:
                action_parameters['Code']['GitUserName'] = function_code_context['git_username']

            if function_code_context['git_password']:
                action_parameters['Code']['GitPassword'] = function_code_context['git_password']

            action_parameters['CodeSource'] = 'Git'
        else:
            raise ValueError('<function_code> value invalid')

        await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'UpdateFunctionCode',
            action_parameters = action_parameters,
            action_version = '2018-04-16'
        )

    def update_function_code(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_code: FunctionCode,
        function_handler: str
    ):
        '''
        Update the source code for a given Cloud Function.
        
        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_code: Cloud Function update source code.
            function_handler: Cloud Function entry point function symbol
                (for example: index.main).
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        self.get_event_loop().run_until_complete(self.update_function_code_async(region_id,
            namespace_name, function_name, function_code, function_handler))

    async def update_function_configure_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_description: str = None,
        function_configure: dict = None
    ):
        '''
        Update the configuration of a given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_description: Cloud Function description body.
            function_configure: A dictionary instance containing a
                Cloud Function configuration.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        if not function_name or not isinstance(function_name, str):
            raise ValueError('<function_name> value invalid')
        
        if not function_configure or not isinstance(function_configure, dict):
            raise ValueError('<function_configure> value invalid')

        action_parameters: dict = {
            'Namespace': namespace_name,
            'FunctionName': function_name
        }
        
        if 'memory_size' in function_configure:
            action_parameters['MemorySize'] = function_configure['memory_size']
        
        if 'time_out' in function_configure:
            action_parameters['Timeout'] = function_configure['time_out']
        
        if 'vpc_configure' in function_configure:
            action_parameters['VpcConfig'] = {
                'VpcId': function_configure['vpc_configure']['vpc_id'],
                'SubnetId': function_configure['vpc_configure']['subnet_id'],
            }
        
        if 'role_id' in function_configure:
            action_parameters['Role'] = function_configure['role_id']
        
        if 'log_configure' in function_configure:
            action_parameters['ClsLogsetId'] = function_configure['log_configure']['logset_id']
            action_parameters['ClsTopicId'] = function_configure['log_configure']['topic_id']
        
        if 'environments' in function_configure:
            action_parameters['Environment'] = {
                'Variables': [{
                    'Key': name,
                    'Value': function_configure['environments'][name]
                } for name in function_configure['environments']]
            }

        if function_description:
            if not isinstance(function_description, str):
                raise ValueError('<function_description> value invalid')
            
            action_parameters['Description'] = function_description
        
        await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'UpdateFunctionConfiguration',
            action_parameters = action_parameters,
            action_version = '2018-04-16'
        )

    def update_function_configure(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_description: str = None,
        function_configure: dict = None
    ):
        '''
        Update the configuration of a given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_description: Cloud Function description body.
            function_configure: A dictionary instance containing a
                Cloud Function configuration.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        self.get_event_loop().run_until_complete(self.update_function_configure_async(region_id,
            namespace_name, function_name, function_description, function_configure))

    async def get_function_result_by_request_id_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_request_id: str,
        function_version: str = None
    ) -> dict:
        '''
        Gets the result of an invoke for a given Cloud Function
            based on the request unique identifier.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_request_id: Request unique identifier.
            function_version: Cloud Function version name.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        if not function_name or not isinstance(function_name, str):
            raise ValueError('<function_name> value invalid')

        if not function_request_id or not isinstance(function_request_id, str):
            raise ValueError('<function_request_id> value invalid')

        action_parameters: dict = {
            'FunctionName': function_name,
            'Namespace': namespace_name,
            'FunctionRequestId': function_request_id
        }

        if function_version:
            if not isinstance(function_version, str):
                raise ValueError('<function_version> value invalid')
            
            action_parameters['Qualifier'] = function_version

        action_result: dict = await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'GetFunctionLogs',
            action_parameters = action_parameters,
            action_version = '2018-04-16'
        )

        try:
            return {
                'function_name': action_result['Data'][0]['FunctionName'],
                'return_result': action_result['Data'][0]['RetMsg'],
                'is_successful': (action_result['Data'][0]['InvokeFinished'] == 1 and
                    action_result['Data'][0]['RetCode'] == 0),
                'start_timestamp': action_result['Data'][0]['StartTime'],
                'run_duration': action_result['Data'][0]['Duration'],
                'bill_duration': action_result['Data'][0]['BillDuration'],
                'usage_memory_size': action_result['Data'][0]['MemUsage'],
                'run_log': action_result['Data'][0]['Log'],
                'log_level': action_result['Data'][0]['Level'],
                'log_source': action_result['Data'][0]['Source']
            }
        except KeyError as error:
            raise errors.errors.ActionResultError(
                'action result content missing field: ' + str(error))
        except IndexError:
            raise errors.errors.NotFoundError('no such function result')

    def get_function_result_by_request_id(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_request_id: str,
        function_version: str = None
    ) -> dict:
        '''
        Gets the result of an invoke for a given Cloud Function
            based on the request unique identifier.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_request_id: Request unique identifier.
            function_version: Cloud Function version name.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        return self.get_event_loop().run_until_complete(
            self.get_function_result_by_request_id_async(region_id, namespace_name,
                function_name, function_request_id, function_version))

    async def get_function_results_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        requirement_context: dict = None,
        function_version: str = None
    ) -> object:
        '''
        Get the qualified running result of a given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            requirement_context: Filter context.
            function_version: Cloud Function version name.
        
        Returns:
            Returns a generator instance used to fetch results one by one.
        
        Yields:
            Generates a dictionary object containing the results of a
                Cloud Function run.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        if not function_name or not isinstance(function_name, str):
            raise ValueError('<function_name> value invalid')

        action_parameters: dict = {
            'FunctionName': function_name,
            'Namespace': namespace_name,
            'Offset': 0,
            'Limit': 100
        }

        if requirement_context:
            try:
                if 'time' in requirement_context:
                    action_parameters['StartTime'] = helper.format_time_by_timestamp(
                        requirement_context['time']['start_timestamp'])
                    
                    action_parameters['EndTime'] = helper.format_time_by_timestamp(
                        requirement_context['time']['end_timestamp'])
                
                if 'type' in requirement_context:
                    action_parameters['Filter'] = {
                        'RetCode': requirement_context['type']
                    }
            except KeyError as error:
                raise ValueError('<requirement_context> value missing field: ' + str(error))
        
        while True:
            action_result: dict = await self.request_action_async(
                region_id = region_id,
                product_id = self.__product_id,
                action_id = 'GetFunctionLogs',
                action_parameters = action_parameters,
                action_version = '2018-04-16'
            )

            if not action_result['Data']:
                break

            try:
                for function_result in action_result['Data']:
                    yield {
                        'return_result': function_result['RetMsg'],
                        'is_successful': (function_result['InvokeFinished'] == 1 and
                            function_result['RetCode'] == 0),
                        'start_time': function_result['StartTime'],
                        'run_duration': function_result['Duration'],
                        'bill_duration': function_result['BillDuration'],
                        'usage_memory_size': function_result['MemUsage'],
                        'run_log': function_result['Log'],
                        'log_level': function_result['Level'],
                        'log_source': function_result['Source'],
                        'request_id': function_result['RequestId']
                    }
            except KeyError as error:
                raise errors.errors.ActionResultError(
                    'action result content missing field: ' + str(error))

            if len(action_result['Data']) < action_parameters['Limit']:
                break

            action_parameters['Offset'] += action_parameters['Limit']

    def get_function_results(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        requirement_context: dict = None,
        function_version: str = None
    ) -> object:
        '''
        Get the qualified running result of a given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            requirement_context: Filter context.
            function_version: Cloud Function version name.
        
        Returns:
            Returns a generator instance used to fetch results one by one.
        
        Yields:
            Generates a dictionary object containing the results of a
                Cloud Function run.

        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        async_generator: object = self.get_function_results_async(region_id,
            namespace_name, function_name, requirement_context, function_version)

        while True:
            function_result: dict = self.get_event_loop().run_until_complete(
                helper.generator_proxy_async(async_generator))

            if not function_result:
                break

            yield function_result

    async def list_functions_async(self,
        region_id: str,
        namespace_name: str,
        requirement_context: dict = None
    ) -> dict:
        '''
        Get an overview of the Cloud Functions you have created.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            requirement_context: Filter context.
        
        Returns:
            Returns a generator instance for traversal.
        
        Yields:
            Generates a dictionary object containing basic
                Cloud Function information.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        action_parameters: dict = {
            'Namespace': namespace_name,
            'Offset': 0,
            'Limit': 20
        }

        if requirement_context:
            if not isinstance(requirement_context, dict):
                raise ValueError('<requirement_context> value invalid')
            
            if 'search' in requirement_context:
                if 'function_name' in requirement_context['search']:
                    action_parameters['SearchKey'] = requirement_context['search']['function_name']
                
                if 'function_description' in requirement_context['search']:
                    action_parameters['Description'] = requirement_context['search']['function_description']

            if 'tags' in requirement_context:
                action_parameters['Filters'] = [{
                    'Name': tag_context['name'],
                    'Values': [value for value in tag_context['values']]
                } for tag_context in requirement_context['tags']]
        
        while True:
            action_result: dict = await self.request_action_async(
                region_id = region_id,
                product_id = self.__product_id,
                action_id = 'ListFunctions',
                action_parameters = action_parameters,
                action_version = '2018-04-16'
            )

            if not action_result['Functions']:
                break

            try:
                for function_info in action_result['Functions']:
                    yield {
                        'namespace_name': function_info['Namespace'],
                        'status': function_info['Status'],
                        'type': function_info['Type'],
                        'id': function_info['FunctionId'],
                        'name': function_info['FunctionName'],
                        'description': function_info['Description'],
                        'runtime': function_info['Runtime'],
                        'tags': {name: function_info['Tags'][name]
                            for name in function_info['Tags']},
                        'last_modified_time': function_info['ModTime'],
                        'create_time': function_info['AddTime']
                    }
            except KeyError as error:
                raise errors.errors.ActionResultError(
                    'action result content missing field: ' + str(error))
            
            if len(action_result['Functions']) < action_parameters['Limit']:
                break
            
            action_parameters['Offset'] += action_parameters['Limit']

    def list_functions(self,
        region_id: str,
        namespace_name: str,
        requirement_context: dict = None
    ) -> dict:
        '''
        Get an overview of the Cloud Functions you have created.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            requirement_context: Filter context.
        
        Returns:
            Returns a generator instance for traversal.
        
        Yields:
            Generates a dictionary object containing basic
                Cloud Function information.

        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        async_generator: object = self.list_functions_async(region_id,
            namespace_name, requirement_context)

        while True:
            function_info: dict = self.get_event_loop().run_until_complete(
                helper.generator_proxy_async(async_generator))
            
            if not function_info:
                break

            yield function_info

    async def list_function_versions_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str
    ) -> dict:
        '''
        Get version information for a given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
        
        Returns:
            Returns a generator instance for traversal.
        
        Yields:
            Generates a dictionary object containing Cloud Function
                version information.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        if not function_name or not isinstance(function_name, str):
            raise ValueError('<function_name> value invalid')
        
        action_result: dict = await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'ListVersionByFunction',
            action_parameters = {
                'Namespace': namespace_name,
                'FunctionName': function_name
            },
            action_version = '2018-04-16'
        )

        for version_info in action_result['Versions']:
            yield {
                'name': version_info['Version'],
                'description': version_info['Description']
            }

    def list_function_versions(self,
        region_id: str,
        namespace_name: str,
        function_name: str
    ) -> object:
        '''
        Get version information for a given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
        
        Returns:
            Returns a generator instance for traversal.
        
        Yields:
            Generates a dictionary object containing Cloud Function
                version information.

        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        async_generator: object = self.list_function_versions_async(region_id,
            namespace_name, function_name)

        while True:
            version_info: dict = self.get_event_loop().run_until_complete(
                helper.generator_proxy_async(async_generator))
            
            if not version_info:
                break

            yield version_info

    async def get_function_info_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_version: str = None
    ) -> dict:
        '''
        Get information for a given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_version: Cloud Function version name.
        
        Returns:
            Returns a dictionary instance containing Cloud Function information.

        Yields:
            Generates a dictionary object containing Cloud Function information.

        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        if not function_name or not isinstance(function_name, str):
            raise ValueError('<function_name> value invalid')

        action_parameters: dict = {
            'Namespace': namespace_name,
            'FunctionName': function_name
        }

        if function_version:
            if not isinstance(function_version, str):
                raise ValueError('<function_version> value invalid')
            
            action_parameters['Qualifier'] = function_version
        
        action_result: dict = await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'GetFunction',
            action_parameters = action_parameters,
            action_version = '2018-04-16'
        )

        return {
            'info': {
                'status': action_result['Status'],
                'type': action_result['Type'],
                'id': action_result['FunctionId'],
                'name': action_result['FunctionName'],
                'description': action_result['Description'],
                'runtime': action_result['Runtime'],
                'tags': {name: action_result['Tags'][name]
                    for name in action_result['Tags']},
                'last_modified_time': action_result['ModTime'],
                'create_time': action_result['AddTime']
            },
            'configure': {
                'handler': action_result['Handler'],
                'memory_size': action_result['MemorySize'],
                'time_out': action_result['Timeout'],
                'vpc_configure': {
                    'vpc_id': action_result['VpcConfig']['VpcId'],
                    'subnet_id': action_result['VpcConfig']['SubnetId']
                },
                'role_id': action_result['Role'],
                'log_configure': {
                    'logset_id': action_result['ClsLogsetId'],
                    'topic_id': action_result['ClsTopicId'],
                },
                'environments': {variable_info['Key']: variable_info['Value']
                    for variable_info in action_result['Environment']['Variables']},
                'eip_configure': {
                    'enabled': action_result['EipConfig']['EipFixed'],
                    'addresses': [address for address in action_result['EipConfig']['Eips']]
                },
                'access_configure': {
                    'hostname': action_result['AccessInfo']['Host'],
                    'ip_address': action_result['AccessInfo']['Vip']
                }
            }
        }

    def get_function_info(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_version: str = None
    ) -> dict:
        '''
        Get information for a given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_version: Cloud Function version name.
        
        Returns:
            Returns a dictionary instance containing Cloud Function information.

        Yields:
            Generates a dictionary object containing Cloud Function information.

        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        return self.get_event_loop().run_until_complete(self.get_function_info_async(
            region_id, namespace_name, function_name, function_version))

    async def _commit_trigger_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_trigger: FunctionTrigger,
        function_version: str,
        is_delete_trigger: bool
    ):
        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        if not function_name or not isinstance(function_name, str):
            raise ValueError('<function_name> value invalid')

        action_parameters: dict = {
            'Namespace': namespace_name,
            'FunctionName': function_name,
        }

        if not is_delete_trigger:
            action_parameters['Enable'] = 'OPEN'

        if function_version:
            if not isinstance(function_version, str):
                raise ValueError('<function_version> value invalid')

            action_parameters['Qualifier'] = function_version
        
        function_trigger_kind: str = function_trigger.get_trigger_kind()
        function_trigger_context: dict = function_trigger.get_trigger_context()

        action_parameters['Type'] = function_trigger_kind
        action_parameters['TriggerName'] = function_trigger_context['name']

        if function_trigger_context['configure']:
            action_parameters['TriggerDesc'] = function_trigger_context['configure']

        await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'CreateTrigger' if not is_delete_trigger else 'DeleteTrigger',
            action_parameters = action_parameters,
            action_version = '2018-04-16'
        )

    async def create_trigger_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_trigger: FunctionTrigger,
        function_version: str = None
    ):
        '''
        Create a trigger for a given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_trigger: Represents an instance of a function
                trigger configuration.
            function_version: Cloud Function version name.

        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        await self._commit_trigger_async(region_id, namespace_name,
            function_name, function_trigger, function_version, False)

    def create_trigger(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_trigger: FunctionTrigger,
        function_version: str = None
    ):
        '''
        Create a trigger for a given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_trigger: Represents an instance of a function
                trigger configuration.
            function_version: Cloud Function version name.

        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        self.get_event_loop().run_until_complete(self._commit_trigger_async(
            region_id, namespace_name, function_name, function_trigger,
            function_version, False))

    async def delete_trigger_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_trigger: FunctionTrigger,
        function_version: str = None
    ):
        '''
        Delete a created trigger for a given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_trigger: Represents an instance of a function
                trigger configuration.
            function_version: Cloud Function version name.

        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        self.get_event_loop().run_until_complete(self._commit_trigger_async(
            region_id, namespace_name, function_name, function_trigger,
            function_version, True))
    
    def delete_trigger(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_trigger: FunctionTrigger,
        function_version: str = None
    ):
        '''
        Delete a created trigger for a given Cloud Function.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_trigger: Represents an instance of a function
                trigger configuration.
            function_version: Cloud Function version name.

        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        self.get_event_loop().run_until_complete(self._commit_trigger_async(
            region_id, namespace_name, function_name, function_trigger,
            function_version, True))

    async def create_namespace_async(self,
        region_id: str,
        namespace_name: str,
        namespace_description: str = None
    ):
        '''
        Create a new namespace.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            namespace_description: Namespace description body.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        action_parameters: dict = {
            'Namespace': namespace_name
        }

        if namespace_description:
            if not isinstance(namespace_description, str):
                raise ValueError('<namespace_description> value invalid')
            
            action_parameters['Description'] = namespace_description
        
        await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'CreateNamespace',
            action_parameters = action_parameters,
            action_version = '2018-04-16'
        )

    def create_namespace(self,
        region_id: str,
        namespace_name: str,
        namespace_description: str = None
    ):
        '''
        Create a new namespace.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            namespace_description: Namespace description body.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        self.get_event_loop().run_until_complete(self.create_namespace_async(
            region_id, namespace_name, namespace_description))

    async def delete_namespace_async(self,
        region_id: str,
        namespace_name: str
    ):
        '''
        Delete a created namespace.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'DeleteNamespace',
            action_parameters = {
                'Namespace': namespace_name
            },
            action_version = '2018-04-16'
        )

    def delete_namespace(self,
        region_id: str,
        namespace_name: str
    ):
        '''
        Delete a created namespace.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        self.get_event_loop().run_until_complete(self.delete_namespace_async(
            region_id, namespace_name))

    async def list_namespaces_async(self,
        region_id: str
    ):
        '''
        Get the created namespace information.

        Args:
            region_id: Region unique identifier.
        
        Returns:
            Returns a generator instance for traversing namespace information.

        Yields:
            Generates a dictionary object containing namespace information.

        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        action_parameters: dict = {
            'Offset': 0,
            'Limit': 20
        }

        while True:
            action_result: dict = await self.request_action_async(
                region_id = region_id,
                product_id = self.__product_id,
                action_id = 'ListNamespaces',
                action_parameters = action_parameters,
                action_version = '2018-04-16'
            )

            try:
                if not action_result['Namespaces']:
                    break

                for namespace_info in action_result['Namespaces']:
                    yield {
                        'name': namespace_info['Name'],
                        'description': namespace_info['Description'],
                        'create_time': namespace_info['AddTime'],
                        'last_modified_time': namespace_info['ModTime'],
                        'type': namespace_info['Type']
                    }
                
                if len(action_result['Namespaces']) < action_parameters['Limit']:
                    break
            except KeyError as error:
                raise errors.errors.ActionResultError(
                    'action result content missing field: ' + str(error))

            action_parameters['Offset'] += action_parameters['Limit']

    def list_namespaces(self,
        region_id: str
    ):
        '''
        Get the created namespace information.

        Args:
            region_id: Region unique identifier.
        
        Returns:
            Returns a generator instance for traversing namespace information.

        Yields:
            Generates a dictionary object containing namespace information.

        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        async_generator: object = self.list_namespaces_async(region_id)

        while True:
            namespace_info: dict = self.get_event_loop().run_until_complete(
                helper.generator_proxy_async(async_generator))
            
            if not namespace_info:
                break

            yield namespace_info

    async def update_namespace_async(self,
        region_id: str,
        namespace_name: str,
        namespace_description: str
    ):
        '''
        Update the created namespace information.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            namespace_description: Namespace description body.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.    
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        if not namespace_description or not isinstance(namespace_description, str):
            raise ValueError('<namespace_description> value invalid')

        await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'UpdateNamespace',
            action_parameters = {
                'Namespace': namespace_name,
                'Description': namespace_description
            },
            action_version = '2018-04-16'
        )

    def update_namespace(self,
        region_id: str,
        namespace_name: str,
        namespace_description: str
    ):
        '''
        Update the created namespace information.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            namespace_description: Namespace description body.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.    
        '''

        self.get_event_loop().run_until_complete(self.update_namespace_async(
            region_id, namespace_name, namespace_description))

    async def get_function_code_download_url_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_version: str = None
    ) -> dict:
        '''
        Get a source code ZIP archive download URL for
            the Cloud Function you created.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_version: Cloud Function version name.
        
        Returns:
            Returns a ZIP archive URL string.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not namespace_name or not isinstance(namespace_name, str):
            raise ValueError('<namespace_name> value invalid')

        if not function_name or not isinstance(function_name, str):
            raise ValueError('<function_name> value invalid')

        action_parameters: dict = {
            'Namespace': namespace_name,
            'FunctionName': function_name
        }

        if function_version:
            if not isinstance(function_version, str):
                raise ValueError('<function_version> value invalid')
            
            action_parameters['Qualifier'] = function_version
        
        action_result: dict = await self.request_action_async(
            region_id = region_id,
            product_id = self.__product_id,
            action_id = 'GetFunctionAddress',
            action_parameters = action_parameters,
            action_version = '2018-04-16'
        )

        try:
            return {
                'url': action_result['Url'],
                'hash': action_result['CodeSha256']
            }
        except KeyError as error:
            raise errors.errors.ActionResultError(
                'action result content missing field: ' + str(error))

    def get_function_code_download_url(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_version: str = None
    ) -> dict:
        '''
        Get a source code ZIP archive download URL for
            the Cloud Function you created.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_version: Cloud Function version name.
        
        Returns:
            Returns a ZIP archive URL string.
        
        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        return self.get_event_loop().run_until_complete(
            self.get_function_code_download_url_async(region_id, namespace_name,
            function_name, function_version))

    async def download_function_code_async(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_version: str = None,
        download_file_name: str = None
    ):
        '''
        Download the source code ZIP archive of a given
            Cloud Function to your local computer.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_version: Cloud Function version name.
            download_file_name: The local file path to store the ZIP archive.

        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        if not download_file_name or not isinstance(download_file_name, str):
            raise ValueError('<download_file_name> value invalid')

        download_info: dict = await self.get_function_code_download_url_async(
            region_id, namespace_name, function_name, function_version)
        
        if not download_file_name:
            download_file_name = './function-code-{FUNCTION_NAME}-{FUNCTION_VERSION}.zip'.format(
                FUNCTION_NAME = function_name,
                FUNCTION_VERSION = function_version
            )

        await self.download_resource_async(
            resource_url = download_info['url'],
            local_file_name = download_file_name
        )

    def download_function_code(self,
        region_id: str,
        namespace_name: str,
        function_name: str,
        function_version: str = None,
        download_file_name: str = None
    ):
        '''
        Download the source code ZIP archive of a given
            Cloud Function to your local computer.

        Args:
            region_id: Region unique identifier.
            namespace_name: Name of the owning namespace.
            function_name: Cloud Function name.
            function_version: Cloud Function version name.
            download_file_name: The local file path to store the ZIP archive.

        Raises:
            ValueError: Parameter values are not as expected.
            ActionError: The related operation corresponding to
                this method encountered an error.
            ActionResultError: The response from the remote server
                was unexpected.
        '''

        self.get_event_loop().run_until_complete(self.download_function_code_async(
            region_id, namespace_name, function_name, function_version, download_file_name))
