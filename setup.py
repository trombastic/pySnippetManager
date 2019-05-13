# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
import pysnippetmanager


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: POSIX',
    'Operating System :: MacOS :: MacOS X',
    'Programming Language :: Python',
]
setup(
    author=pysnippetmanager.__author__,
    author_email="m.schroeder@tu-berlin.de",
    name='pySnippetManager',
    version=pysnippetmanager.__version__,
    description='A Snippet Manager written in Python',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='http://www.github.com/trombastic/pySnippetManager',
    license='GPL version 3',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'pygments'
    ],
    packages=find_packages(exclude=["project", "project.*"]),
    include_package_data=True,
    test_suite='runtests.main',
    scripts=['scripts/pysnippetmanager']
)
