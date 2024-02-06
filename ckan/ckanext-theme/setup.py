from setuptools import setup, find_packages

version = "0.2"

setup(
    name="ckanext-theme",
    version=version,
    description="theme extension for customising CKAN",
    long_description="",
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords="",
    author="Federico Oldani",
    author_email="federico.oldani@gmail.com",
    url="",
    license="",
    packages=find_packages(exclude=["ez_setup", "themes", "tests"]),
    namespace_packages=["ckanext", "ckanext.theme"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points="""
        [ckan.plugins]
        theme=ckanext.theme.plugin:themePlugin
	""",
)
