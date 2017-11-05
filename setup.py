try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import pyupnp_async

with open("README.rst") as readme_file:
    readme_string = readme_file.read()

setup(
    name="pyupnp-async",
    version=pyupnp_async.__version__,
    description="Python Library for UPnP operations using asyncio",
    author="Xin Huang",
    author_email="xinhuang.abc@gmail.com",
    url="https://github.com/xinhuang/pyupnp-async",
    packages=['pyupnp_async', 'tests'],
    license="License :: OSI Approved :: MIT License",
    long_description=readme_string,
    install_requres=[
        'aiohttp',
        'async-timeout',
        'xmltodict',
    ],
)
