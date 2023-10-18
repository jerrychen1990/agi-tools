# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     setup
   Description :
   Author :       chenhao
   date：          2021/4/6
-------------------------------------------------
   Change Activity:
                   2021/4/6:
-------------------------------------------------
"""
import os
import sys

from setuptools import find_packages, setup
from snippets import get_latest_version, get_next_version, read2list


def get_install_req():
    req = read2list("requirements.txt")
    return req


if __name__ == "__main__":
    # print(sys.argv)
    name = "agit"

    if len(sys.argv) >= 4 and sys.argv[-1].startswith("v"):
        version = sys.argv.pop(-1)
    else:
        latest_version = get_latest_version(name)
        version = get_next_version(latest_version)

    install_req = get_install_req()
    print(f"version: {version}")
    print(f"install_req:{install_req}")

    setup(
        name=name,
        version=version,
        install_requires=install_req,
        packages=find_packages(exclude=['tests*']),
        package_dir={"": "."},
        package_data={},
        url='https://github.com/jerrychen1990/agi-tools.git',
        license='MIT',
        author='Chen Hao',
        author_email='jerrychen1990@gmail.com',
        zip_safe=True,
        description='tools for agi',
        long_description="tools for agi"
    )
