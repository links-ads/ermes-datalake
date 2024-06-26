from setuptools import setup, find_packages
import sys, os

version = "0.0"

setup(
    name="ckanext-datatype",
    version=version,
    description="",
    long_description="""\
	""",
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords="",
    author="",
    author_email="",
    url="",
    license="",
    packages=find_packages(exclude=["ez_setup", "themes", "tests"]),
    namespace_packages=["ckanext", "ckanext.datatype"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points="""
        [ckan.plugins]
	# Add plugins here, eg
	# myplugin=ckanext.datatype:PluginClass
    datatype=ckanext.datatype.plugin:DatatypePlugin
	""",
)
