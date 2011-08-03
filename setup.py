from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='sauna.reload',
      version=version,
      description="",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone reload zope2 restart auto',
      author='Esa-Matti Suuronen',
      author_email='esa-matti@suuronen.org',
      url='http://github.com/epeli/sauna.reload',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sauna'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.autoinclude',
          # -*- Extra requirements: -*-
          'watchdog',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
