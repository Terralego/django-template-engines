#!/usr/bin/env python
from os.path import dirname, join, realpath

from setuptools import setup

HERE = dirname(realpath(__file__))

README = open(join(HERE, 'README.md')).read()
CHANGES = open(join(HERE, 'CHANGES.md')).read()
PACKAGES = ['template_engines']
PACKAGE_DIR = {'template_engines': 'template_engines'}


setup(
    name='django-template-engines',
    version='0.0.1',
    author_email='python@makina-corpus.org',
    description='Additional template engines for Django.',
    long_description=README + '\n\n' + CHANGES,
    packages=PACKAGES,
    package_dir=PACKAGE_DIR,
    include_package_data=True,
    url='https://github.com/Terralego/django-template-engines',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=['Django>=2.2.3', 'Pillow>=6.1.0', 'requests>=2.22.0', 'python-magic>=0.4.15'],
)
