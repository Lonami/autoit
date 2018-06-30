#!/usr/bin/env python3
import re
from codecs import open
from sys import argv

from setuptools import find_packages, setup


def main():
    if len(argv) >= 2 and argv[1] == 'pypi':
        from subprocess import run
        from shutil import rmtree

        for x in ('build', 'dist', 'autoit.egg-info'):
            rmtree(x, ignore_errors=True)
        run('python3 setup.py sdist', shell=True)
        run('python3 setup.py bdist_wheel', shell=True)
        run('twine upload dist/*', shell=True)
        for x in ('build', 'dist', 'autoit.egg-info'):
            rmtree(x, ignore_errors=True)

    else:
        # Get the long description from the README file
        with open('README.rst', 'r', encoding='utf-8') as f:
            long_description = f.read()

        with open('ait/version.py', 'r', encoding='utf-8') as f:
            version = re.search(r"^__version__\s*=\s*'(.*)'.*$",
                                f.read(), flags=re.MULTILINE).group(1)
        setup(
            name='autoit',
            version=version,
            description="Automate it with Python",
            long_description=long_description,

            url='https://github.com/Lonami/autoit',
            download_url='https://github.com/Lonami/autoit/releases',

            author='Lonami Exo',
            author_email='totufals@hotmail.com',

            license='MIT',

            # See https://stackoverflow.com/a/40300957/4759433
            # -> https://www.python.org/dev/peps/pep-0345/#requires-python
            # -> http://setuptools.readthedocs.io/en/latest/setuptools.html
            python_requires='>=3.5',

            # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
            classifiers=[
                #   3 - Alpha
                #   4 - Beta
                #   5 - Production/Stable
                'Development Status :: 3 - Alpha',

                'Intended Audience :: Developers',
                'Topic :: Communications :: Chat',

                'License :: OSI Approved :: MIT License',

                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.5',
                'Programming Language :: Python :: 3.6'
            ],
            keywords='gui mouse keyboard automation automate',
            packages=find_packages(),
            install_requires=[]
        )


if __name__ == '__main__':
    main()
