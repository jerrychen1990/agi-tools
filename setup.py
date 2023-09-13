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

REQ = [
    "python_snippets",
    "zhipuai",
    "openai",
    "click",
    "pandas",
    "html2text",
    "langchain",
    "tiktoken"
    
]

def get_version(pkg_name):
    try:
        libinfo_py = os.path.join(pkg_name, '__init__.py')
        libinfo_content = open(libinfo_py, 'r', encoding='utf8').readlines()
        version_line = [l.strip() for l in libinfo_content if l.startswith('__version__')][
            0
        ]
        exec(version_line)
        return tuple([int(e) for e in locals()["__version__"].split(".")])

    except FileNotFoundError:
        return None


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) >= 4 and sys.argv[-1].startswith("v"):
        version = sys.argv.pop(-1)
    else:
        version = get_version("snippets")
        version = ".".join([str(e) for e in version])
    print(f"version: {version}")

    setup(
        name='agit',
        version=version,
        install_requires=REQ,
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
