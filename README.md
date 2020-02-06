# Tencent Cloud SDK for Python

> **Tips:** This project is currently under development and this document is for reference only.

Tencent Cloud SDK for Python, which provides an easier-to-use abstract client and advanced features.

By integrating and using the Tencent Cloud SDK for Python, you can achieve fast and secure access to the Tencent Cloud API in an object-oriented programming manner, without having to pay attention to implementation details.

**Features:** Tencent Cloud SDK for Python supports full asynchronous programming.

## Navigation
- [Homepage](https://github.com/nobody-night/tencent-cloud-sdk-python)
- Documentation
  - English (Writing...)
  - 简体中文 (Writing...)
- [Release Notes](https://github.com/nobody-night/tencent-cloud-sdk-python/releases)
- [License](LICENSE)
- [Author Homepage](https://cloud.tencent.com/)

## Installation
With the Python package manager, you can quickly install the Tencent Cloud SDK for Python.

```bash
pip install tencent-cloud-sdk
```

If you want to integrate only the products you need, you can take a subcontracted installation of the Tencent Cloud SDK for Python. First we need to install the base package:

```bash
pip install tencent-cloud-sdk-auth
pip install tencent-cloud-sdk-core
```

Then install the packages for the required products, such as Serverless Cloud Function:

```bash
pip install tencent-cloud-sdk-serverless-functions
```

**Tips:** Please note that your uninstallation method should be the same as the installation method, otherwise some packages may not be removed.

## Getting Started
With the Tencent Cloud SDK for Python, you can use Tencent Cloud products with Python's object-oriented programming.

Currently Tencent Cloud SDK for Python supports programmatic use in synchronous and asynchronous ways. Asynchronous way can write applications with better performance. Below we will show you how to use the Tencent Cloud SDK for Python in multiple consecutive code snippets using synchronous programming.

### Serverless Cloud Function
For example, Invoke has created a Serverless Cloud Function:

#### Import Package
First, we need to import the packages we use:

```python
from tencent.cloud.core import errors
from tencent.cloud.auth import credentials
from tencent.cloud.serverless import functions
```

#### Access Credentials
Next, we need to instantiate an access credential so that Tencent Cloud can determine that you have the right to operate.

```python
access_credentials = credentials.Credentials(
    secret_id = 'AKIDF3sMOAU1pOgkmrKHchX6TZQ1Mo1C5qa7',
    secret_key = 'b4JL8fwxkIgsKMXGi39yYt0ECxZw4wZf'
)
```

The `secret_id` and `secret_key` given in the sample code above are demo credentials. You need to go to the [Tencent Cloud Console](https://console.cloud.tencent.com/cam/capi) to obtain credentials for your account.

#### Product Client
Then, we need to instantiate a product client for Serverless Cloud Function:

```python
function_client: functions.Client = functions.Client(
    credentials_context = access_credentials
)
```

The parameter `credentials_context` is optional. If you use the Tencent Cloud SDK for Python in a Serverless Cloud Function container, this parameter can be ignored or set to `None`.

#### Invoke Cloud Function
Finally, we try to Invoke a Cloud Function and get the return value. Suppose we have a Cloud Function `hello` in the namespace `default` of the data center `ap-shanghai`:

```python
return_value: str = function_client.easy_invoke(
    region_id = 'ap-shanghai',  # Unique identifier of the data center
    namespace_name = 'default', # Name of the namespace
    function_name = 'hello'     # Name of the Cloud Function
)
```

The local variable `return_value` now has the actual return value of the Cloud Function.

The method `easy_invoke` will attempt to infer the return value in the given Cloud Function result and return the return value as a Python native data type.

**Tips:** If an error occurs for a given Cloud Function runtime, an `InvokeError` exception is thrown. The above exceptions are defined in the `tencent.cloud.serverless.functions.errors` module.

See the [Quick-Start](quickstart.py) source code for the complete demo code.

### Other Tencent Cloud Products
For Tencent Cloud products that do not yet provide a product client in the Tencent Cloud SDK, a universal client can be used.

#### Import Packages
As with the Serverless Cloud Function product, we need to import the packages we use:

```python
from tencent.cloud.core import errors
from tencent.cloud.core import client
from tencent.cloud.auth import credentials
```

#### Access Credentials
As with the Serverless Cloud Function product, we need to instantiate an access credential. For this paragraph, please refer to the Serverless Cloud Function product getting started demo.

#### Product Client
Since the Tencent Cloud product we need to use does not provide a product client, we need to instantiate a universal client.

Below we take Cloud Virtual Machine (CVM) products as an example:

```python
virtual_machine_client: client.UniversalClient = client.UniversalClient(
    product_id = 'cvm',     # Unique identifier of the product
    credentials_context = access_credentials    # Access credentials
)
```

#### Use Tencent Cloud API
Finally, we try to retrieve Zone information operated by a given data center campus, which will use the Tencent Cloud API called [DescribeZones](https://cloud.tencent.com/document/api/213/15707):

```python
action_result: dict = virtual_machine_client.action(
    region_id = 'ap-shanghai',      # Unique identifier of the data center
    action_id = 'DescribeZones',    # Unique identifier of the Tencent Cloud API
    action_version = '2017-03-12'   # Version name of the Tencent Cloud API
)
```

**Tips:** If a given Tencent Cloud API encounters an error, an `ActionError` exception is thrown; if the given Tencent Cloud API response is not as expected, an `ActionResultError` exception is thrown. The above exceptions are defined in the `tencent.cloud.core.errors` module.

Print unique identifiers for all zones:

```python
for zone_info in action_result['ZoneSet']:
    print(zone_info['Zone'])
```

For more ways to use Tencent Cloud SDK for Python, see our online documentation. Thank you!

## Other
If you encounter any problems during use, you are welcome to navigate to the [Issues](https://github.com/nobody-night/tencent-cloud-sdk-python/issues) page to submit and we will be happy to assist you with the problem.
