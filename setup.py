#!/usr/bin/env python

    from setuptools import setup
    import os

setup(name='amap',
      version='0.1',
      description='Asset Mapping Interface',
      author='CommerceBlock',
      author_email='tom@commerceblock.com',
      url='http://github.com/commerceblock/asset-mapping',
      packages=['amap'],
      scripts=['amaptool'],
      include_package_data=True,
      data_files=[("", ["LICENSE"])],
)
