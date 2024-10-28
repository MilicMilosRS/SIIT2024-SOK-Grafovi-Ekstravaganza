from setuptools import setup, find_packages

setup(
    name='data_source_json',
    version='0.1',
    packages=find_packages(),
    install_requires=['networkx'],
    description='A JSON data source plugin that parses JSON files and builds graphs.',
)
