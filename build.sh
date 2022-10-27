#!/bin/sh
#
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

BUILD_DIST_DIR_PATH=./dist
BUILD_PACKAGE_DIR_PATH=./packages
MAIN_PACKAGE_DIR_PATH=./

ensure_installed_build_toolbox() {
    echo "checking build toolbox..."

    if [ -z "$(which python3)" ]
    then
        echo 'error: Python3 must be installed'
        exit 1
    fi

    if [ -z "$(which pip3)" ]
    then
        echo 'error: PIP3 must be installed'
        exit 1
    fi

    pip3 install build -q
    if [ ! $? -eq 0 ]
    then
        echo "error: failed to install build toolbox"
    fi
}

clean_build_packages() {
    if [ -d "${BUILD_DIST_DIR_PATH}" ]
    then
        echo "cleaning build packages..."
        rm -rf "${BUILD_DIST_DIR_PATH}"
    fi
}

get_package_name() {
    if [ $1 = $MAIN_PACKAGE_DIR_PATH ]
    then
        echo 'main'
    else
        basename $1
    fi
}

build_package() {
    package_name=$(get_package_name "${1}")

    echo "building package: ${package_name}"
    python3 -m build "${1}" -o "${BUILD_DIST_DIR_PATH}" > /dev/null

    if [ ! $? -eq 0 ]
    then
        echo "error: failed to build package: ${package_name}"
        exit 1
    fi
}

build_all_packages() {
    echo "building all packages..."
    for package_path in $BUILD_PACKAGE_DIR_PATH/*
    do
        build_package $package_path &
    done

    wait
    build_package $MAIN_PACKAGE_DIR_PATH

    echo 'all packages are build'
}

ensure_installed_build_toolbox
clean_build_packages
build_all_packages
