from setuptools import setup

setup(
    name='JustSnapshot',
    version='0.1',
    packages=['jsnapshot_core'],
    scripts=[
        "scripts/jsnapshot-create",
        "scripts/jsnapshot-delete",
        "scripts/jsnapshot-list",
        "scripts/jsnapshot-setup",
        "scripts/jsnapshot-show",
        "scripts/jsnapshot-restore"
    ],
    url='https://melianmiko.ru/',
    license='BSD',
    author='MelianMiko',
    author_email='melianmiko@gmail.com',
    description='Simple BTRFS backup tool (INDEV)'
)
