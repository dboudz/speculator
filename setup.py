#!/usr/bin/env python

from setuptools import setup, find_packages
setup(name='speculator',
      version='1.0',
      description='Python Distribution',
      author='dboudz',
      url='https://github.com/dboudz/speculator',
      scripts=[
            'bin/businessLogic.py',
            'bin/exchange_krakken.py',
	    'bin/notifier.py',
            'bin/persistenceHandler.py',
	    'bin/speculator.py'
           ],
     install_requires=[
            'krakenex',
            'pushbullet.py',
            'simplejson',
            'pandas',
            'psycopg2',
            'SQLAlchemy' 
     ],
     )
