from setuptools import setup
from jsnapshot_core.app_info import VERSION

setup(
    name='JustSnapshot',
    version=VERSION,
    packages=['jsnapshot_core', "jsnapshot_cron"],
    scripts=[
        "scripts/jsnapshot-create",
        "scripts/jsnapshot-delete",
        "scripts/jsnapshot-edit",
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
