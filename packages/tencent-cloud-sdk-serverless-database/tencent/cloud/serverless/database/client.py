# tencent.cloud.serverless.database.client is python-3.6 source file

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
Object-oriented client types that implement Tencent Cloud's
    serverless database products. With client-side instances,
    you can quickly interact with serverless database products
    in an object-oriented programming manner.
'''

from tencent.cloud.core import client

from tencent.cloud.serverless.database import errors
from tencent.cloud.serverless.database import helper

class DatabaseCharset:
    '''
    A character set type enumerator supported by
        serverless databases.
    '''

    UTF8: str = 'UTF8'
    LATIN1: str = 'LATIN1'

class Client(client.UniversalClient):
    '''
    An object-oriented client type representing a serverless
        database product.
    
    Args:
        access_credentials: Access credentials configuration.
        access_proiexs: Access proxy configuration.
    
    Raises:
        ValueError: The parameters did not meet expectations.
    '''
    
    def __init__(self,
        access_credentials = None,
        access_proiexs = None
    ):
        super().__init__(
            product_id = 'postgres',
            access_credentials = access_credentials,
            access_proiexs = access_proiexs
        )

    async def create_instance_async(self,
        region_id: str,
        zone_id: str,
        instance_name: str,
        instance_configure: dict = None
    ) -> dict:
        '''
        Create a new serverless database instance.

        Args:
            region_id: Data center unique identifier.
            zone_id: Zone Unique Identifier.
            instance_name: Database instance name.
            instance_configure: Database instance configuration.
        
        Returns:
            Returns the dictionary instance containing the metadata
                of the newly created database instance.
        
        Raises:
            ValueError: The parameters did not meet expectations.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not zone_id or not isinstance(zone_id, str):
            raise ValueError('<zone_id> value invalid')

        if not instance_name or not isinstance(instance_name, str):
            raise ValueError('<instance_name> value invalid')
        
        if instance_configure:
            if not isinstance(instance_configure, dict):
                raise ValueError('<instance_configure> value invalid')
        else:
            instance_configure = {
                'database': {
                    'version': '10.4',
                    'charset': DatabaseCharset.UTF8
                }
            }
        
        action_parameters: dict = {
            'Zone': zone_id,
            'DBInstanceName': instance_name
        }

        try:
            if 'project_id' in instance_configure:
                action_parameters['ProjectId'] = instance_configure['project_id']

            if 'database' in instance_configure:
                if 'version' in instance_configure['database']:
                    action_parameters['DBVersion'] = (
                        instance_configure['database']['version']
                    )
                
                if 'charset' in instance_configure['database']:
                    action_parameters['DBCharset'] = (
                        instance_configure['database']['charset']
                    )
            else:
                raise ValueError('<instance_configure> missing field: database')

            if 'vpc' in instance_configure:
                action_parameters['VpcId'] = instance_configure['vpc']['id']
                action_parameters['SubnetId'] = instance_configure['vpc']['subnet_id']
        except KeyError as error:
            raise ValueError('<instance_configure> missing field: ' + str(error))
            
        action_result: dict = await self.action_async(
            region_id = region_id,
            action_id = 'CreateServerlessDBInstance',
            action_parameters = action_parameters,
            action_version = '2017-03-12'
        )

        try:
            return {
                'id': action_result['DBInstanceId']
            }
        except KeyError as error:
            raise errors.errors.ActionResultError('missing field: ' + str(error))

    def create_instance(self,
        region_id: str,
        zone_id: str,
        instance_name: str,
        instance_configure: dict = None
    ) -> dict:
        '''
        Create a new serverless database instance.

        Args:
            region_id: Data center unique identifier.
            zone_id: Zone Unique Identifier.
            instance_name: Database instance name.
            instance_configure: Database instance configuration.
        
        Returns:
            Returns the dictionary instance containing the metadata
                of the newly created database instance.
        
        Raises:
            ValueError: The parameters did not meet expectations.
        '''

        return self._get_event_loop().run_until_complete(
            self.create_instance_async(
                region_id, zone_id, instance_name, instance_configure
            )
        )

    async def delete_instance_async(self,
        region_id: str,
        instance_id: str
    ):
        '''
        Delete a serverless database instance that has
            been created ready.
        
        Args:
            region_id: Data center unique identifier.
            instance_id: Database instance unique identifier.
        
        Raises:
            ValueError: The parameters did not meet expectations.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not instance_id or not isinstance(instance_id, str):
            raise ValueError('<instance_id> value invalid')
        
        await self.action_async(
            region_id = region_id,
            action_id = 'DeleteServerlessDBInstance',
            action_parameters = {
                'DBInstanceId': instance_id
            },
            action_version = '2017-03-12'
        )

    def delete_instance(self,
        region_id: str,
        instance_id: str
    ):
        '''
        Delete a serverless database instance that has
            been created ready.
        
        Args:
            region_id: Data center unique identifier.
            instance_id: Database instance unique identifier.
        
        Raises:
            ValueError: The parameters did not meet expectations.
        '''

        self._get_event_loop().run_until_complete(
            self.delete_instance_async(
                region_id, instance_id
            )
        )

    async def list_instances_async(self,
        region_id: str
    ):
        '''
        List information about the serverless database
            instances that have been created.
        
        Args:
            region_id: Data center unique identifier.
        
        Yields:
            Generate dictionary instances that contain
                information on serverless database instances.
        
        Raises:
            ValueError: The parameters did not meet expectations.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')
        
        action_parameters: dict = {
            'Limit': 20,
            'Offset': 0
        }

        while True:
            action_result: dict = await self.action_async(
                region_id = region_id,
                action_id = 'DescribeServerlessDBInstances',
                action_parameters = action_parameters,
                action_version = '2017-03-12'
            )

            if not action_result['DBInstanceSet']:
                break
            
            if len(action_result['DBInstanceSet']) == 0:
                break
            
            try:
                for info in action_result['DBInstanceSet']:
                    yield {
                        'id': info['DBInstanceId'],
                        'name': info['DBInstanceName'],
                        'status': info['DBInstanceStatus'],
                        'region_id': info['Region'],
                        'zone_id': info['Zone'],
                        'project_id': info['ProjectId'],
                        'vpc': {
                            'id': info['VpcId'],
                            'subnet_id': info['SubnetId']
                        },
                        'database': {
                            'version': info['DBVersion'],
                            'charset': info['DBCharset'],
                            'names': [
                                name for name in info['DBDatabaseList']
                            ] if info['DBDatabaseList'] else list()
                        },
                        'create_time': info['CreateTime'],
                        'networks': [
                            {
                                'type': network_info['NetType'],
                                'status': network_info['Status'],
                                'address': {
                                    'ip': network_info['Ip'],
                                    'port': network_info['Port'],
                                }
                            } for network_info in info['DBInstanceNetInfo']
                        ] if info['DBInstanceNetInfo'] else list(),
                        'users': [
                            {
                                'name': user_info['DBUser'],
                                'password': user_info['DBPassword']
                            } for user_info in info['DBAccountSet']
                        ] if info['DBAccountSet'] else list()
                    }
            except KeyError as error:
                raise errors.errors.ActionResultError('missing field: ' + str(error))
            
            if len(action_result['DBInstanceSet']) < action_parameters['Limit']:
                break

    def list_instances(self,
        region_id: str
    ):
        '''
        List information about the serverless database
            instances that have been created.
        
        Args:
            region_id: Data center unique identifier.
        
        Yields:
            Generate dictionary instances that contain
                information on serverless database instances.
        
        Raises:
            ValueError: The parameters did not meet expectations.
        '''

        async_generator: object = self.list_instances_async(region_id)

        while True:
            instance_info: dict = self._get_event_loop().run_until_complete(
                helper.generator_proxy_async(async_generator))
            
            if not instance_info:
                break

            yield instance_info

    async def set_instance_extranet_async(self,
        region_id: str,
        instance_id: str,
        instance_extranet: bool = True
    ):
        '''
        Set whether serverless database instances
            are allowed to be accessed via the extranet.
        
        Args:
            region_id: Data center unique identifier.
            instance_id: Database instance unique identifier.
            instance_extranet: Whether access is allowed via the extranet.
        
        Raises:
            ValueError: The parameters did not meet expectations.
        '''

        if not region_id or not isinstance(region_id, str):
            raise ValueError('<region_id> value invalid')

        if not instance_id or not isinstance(instance_id, str):
            raise ValueError('<instance_id> value invalid')
        
        if instance_extranet == None or not isinstance(instance_extranet, bool):
            raise ValueError('<instance_extranet> value invalid')

        await self.action_async(
            region_id = region_id,
            action_id = ('OpenServerlessDBExtranetAccess'
                if instance_extranet else 'CloseServerlessDBExtranetAccess'),
            action_parameters = {
                'DBInstanceId': instance_id
            },
            action_version = '2017-03-12'
        )

    def set_instance_extranet(self,
        region_id: str,
        instance_id: str,
        instance_extranet: bool = True
    ):
        '''
        Set whether serverless database instances
            are allowed to be accessed via the extranet.
        
        Args:
            region_id: Data center unique identifier.
            instance_id: Database instance unique identifier.
            instance_extranet: Whether access is allowed via the extranet.
        
        Raises:
            ValueError: The parameters did not meet expectations.
        '''

        self._get_event_loop().run_until_complete(
            self.set_instance_extranet_async(
                region_id, instance_id, instance_extranet
            )
        )
