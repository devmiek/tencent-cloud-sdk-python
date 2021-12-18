# Tencent Cloud SDK for Python - Common
A subpackage of the Tencent Cloud SDK for Python. This sub-package integrates external packages that Tencent Cloud SDK for Python depends on, avoiding the need to deploy additional external dependencies of Tencent Cloud SDK for Python when deploying on a serverless platform.

**Tips:** Note that if the required external dependencies are already installed in the Tencent Cloud SDK for Python, dependencies are not looked up from this package by default.

## Installation
With the Python package manager, you can quickly install the Tencent Cloud SDK for Python - Common.

```bash
pip install tencent-cloud-sdk-common
```

You can also try to build and install locally:

```bash
python setup.py install
```

## License
This package includes the third-party packages that the Tencent Cloud SDK for Python relies on. We do not modify the source code of these dependent packages unless necessary. If the source code of these dependent packages is modified, we will explain the details of the modification.

To facilitate the deployment and migration of the Tencent Cloud SDK for Python, we have encapsulated the dependent packages in a package called `tencent-cloud-sdk-common`, which are:

- https://pypi.org/project/aiohttp/
- https://pypi.org/project/async-timeout/
- https://github.com/python-attrs/attrs
- https://pypi.org/project/charset-normalizer/
- https://pypi.org/project/multidict/
- https://pypi.org/project/yarl/
- https://pypi.org/project/idna/

It is worth noting that our use of these dependent packages is subject to their open source licenses.

## Other
If you encounter any problems during use, you are welcome to navigate to the [Issues](https://github.com/nobody-night/tencent-cloud-sdk-python/issues) page to submit and we will be happy to assist you with the problem.
