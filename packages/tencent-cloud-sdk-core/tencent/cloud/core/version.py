# tencent.cloud.core.version is python-3.6 source file

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
Defines the core version information of the Tencent Cloud SDK.
'''

class VersionInfo:
    '''
    Static type indicating the core version information of
        the current Tencent Cloud SDK.

    Attributes:
        MAJOR: Major version number
        MINOR: Minor version number
        REVISION: Revision version number
    '''

    MAJOR: int = 0
    MINOR: int = 1
    REVISION: int = 5

def get_version_text() -> str:
    '''
    Get the core version number string of the Tencent Cloud SDK.
    '''

    return '{MAJOR}.{MINOR}.{REVISION}'.format(
        MAJOR = VersionInfo.MAJOR,
        MINOR = VersionInfo.MINOR,
        REVISION = VersionInfo.REVISION
    )
