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

'''
Tencent Cloud SDK for Python Sub-Package installer
https://github.com/nobody-night/tencent-cloud-sdk-python
'''

import setuptools

def read_readme_content() -> str:
    with open('README.md', encoding = 'utf-8') as readme_file_handle:
        return readme_file_handle.read()

setuptools.setup(
    name = 'tencent-cloud-sdk-auth',
    version = '0.2.2',
    packages = [
        'tencent.cloud.auth'
    ],
    keywords = 'tencent-cloud sdk-python',
    license = 'MIT License',
    author = 'MIEK',
    author_email = 'king@xiaoyy.org',
    description = (
        'Tencent Cloud SDK for Python components. '
        'This package implements the access credential '
        'type and signature calculation related functions '
        'for the Tencent Cloud SDK.'
    ),
    long_description = read_readme_content(),
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/nobody-night/tencent-cloud-sdk-python',
    python_requires = '>=3.6',
    zip_safe = False,
    classifiers = [
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable'
        # 'Development Status :: 4 - Beta'
    ]
)
