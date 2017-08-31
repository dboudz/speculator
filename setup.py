#!/usr/bin/env python

from setuptools import setup, find_packages
setup(name='speculator',
      version='1.0',
      description='Python Distribution',
      author='dboudz',
      url='https://github.com/dboudz/speculator',
      scripts=[
            'businessLogic.py',
            'exchange_krakken.py',
	    'notifier.py',
            'persistenceHandler.py',
	    'speculator.py'
           ]
      packages=[],
     )
