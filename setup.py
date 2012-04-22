from setuptools import setup, find_packages

version = "0.4.0"

setup(name="sauna.reload",
      version=version,
      description="Instant code reloading for Plone using a fork loop",
      long_description=open("README.rst").read() + "\n" +
                       open("HISTORY.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords="plone reload zope2 restart developer",
      author="Asko Soukka",
      author_email="asko.soukka@iki.fi",
      url="http://github.com/collective/sauna.reload",
      license="ZPL",
      packages=find_packages(exclude=["ez_setup"]),
      namespace_packages=["sauna"],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "setuptools",
          "z3c.autoinclude",
          # -*- Extra requirements: -*-
          "watchdog>=0.6.0",
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
