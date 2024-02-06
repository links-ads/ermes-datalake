from setuptools import find_packages, setup

version = "0.2"

setup(
    name="ckanext-authcheck",
    version=version,
    description="authcheck extension for customising CKAN",
    long_description="",
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords="",
    author="Federico Oldani",
    author_email="federico.oldani@gmail.com",
    url="",
    license="",
    packages=find_packages(exclude=["ez_setup", "authchecks", "tests"]),
    namespace_packages=["ckanext", "ckanext.authcheck"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points="""
        [ckan.plugins]
        authcheck=ckanext.authcheck.plugin:authcheckPlugin
        authcheck_datasetform=ckanext.authcheck.forms:authcheckDatasetForm
        authcheck_groupform=ckanext.authcheck.forms:authcheckGroupForm        

        [ckan.forms]
        authcheck_form = ckanext.authcheck.package_form:get_authcheck_fieldset

	""",
)
