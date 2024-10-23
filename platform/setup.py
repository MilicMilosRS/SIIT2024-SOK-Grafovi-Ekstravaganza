from setuptools import setup, find_packages

setup(
    name='platform',
    version='0.1.0',
    packages=find_packages(),
    description='The platform library handles all graph manipulation logic and communicates with plug-ins that implement the API library',
    #NOT WORKING 
    install_requires=[
        'api @ file://../api'
    ],
)