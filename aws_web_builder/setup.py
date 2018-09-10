from setuptools import *

setup(
    name='aws_web_builder',
    version='0.1',
    author='Shlubz',
    author_email='jayboy229@gmail.com',
    description='Tool used to deploy static websites to AWS S3.',
    license='GPLv3',
    packages=find_packages(),
    url='https://github.com/shlubz/aws_web_builder',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        aws_web_builder=aws_web_builder.aws_web_builder:cli
    '''
)
