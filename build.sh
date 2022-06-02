#!/bin/sh

pip3 install build
rm -rf ./dist

build_package() {
    python3 -m build ./packages/$1 -o ./dist
}

build_package tencent-cloud-sdk-auth
build_package tencent-cloud-sdk-common
build_package tencent-cloud-sdk-core
build_package tencent-cloud-sdk-serverless-database
build_package tencent-cloud-sdk-serverless-functions
build_package ..
