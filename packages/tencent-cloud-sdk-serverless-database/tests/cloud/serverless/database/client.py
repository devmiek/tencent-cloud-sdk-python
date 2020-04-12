# tests.cloud.serverless.database.client is python-3.6 source file

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

import json

from tencent.cloud.serverless import database

def main():
    client = database.fetch_client()

    instance_info: dict = client.create_instance(
        region_id = 'ap-shanghai',
        zone_id = 'ap-shanghai-2',
        instance_name = 'unit-test',
        instance_configure = {
            'database': {
                'version': '10.4',
                'charset': database.DatabaseCharset.UTF8
            },
            'vpc': {
                'id': 'vpc-f7qfb64q',
                'subnet_id': 'subnet-aieh8myj'
            }
        }
    )

    print('info: instance id = ' + str(instance_info['id']))

    for info in client.list_instances('ap-shanghai'):
        print(json.dumps(info, indent = 2), end = '\n\n')

    client.delete_instance(
        region_id = 'ap-shanghai',
        instance_id = instance_info['id']
    )

if __name__ == '__main__':
    main()
