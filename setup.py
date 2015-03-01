from os import path
from setuptools import setup, find_packages
from codecs import open

setup(
    name='dumblr',
    version='1.0',
    url="https://github.com/devty1023/dumblr",
    description='tumblr for devs',

    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'pyyaml',
        'pytumblr',
        'requests',
        'requests_oauthlib',
        'unidecode'
    ],
    entry_points='''
        [console_scripts]
        dumblr=dumblr.cli:cli
    ''',

    author="Daniel Y Lee",
    author_email="devty1023@gmail.com",
    license='MIT',
)
