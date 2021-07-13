from setuptools import setup

setup(
    name='JustSnapshot',
    version='0.1',
    packages=['jsnapshot_cli', 'jsnapshot_core'],
    scripts=["bin/jsnapshot"],
    url='https://melianmiko.ru/',
    license='BSD',
    author='MelianMiko',
    author_email='melianmiko@gmail.com',
    description='Simple BTRFS backup tool (INDEV)'
)
