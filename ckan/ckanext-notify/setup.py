from setuptools import setup, find_packages

version = '0.2'

setup(
	name='ckanext-notify',
	version=version,
	description='notify extension for customising CKAN',
	long_description='',
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Federico Oldani',
	author_email='federico.oldani@gmail.com',
	url='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'notifys', 'tests']),
	namespace_packages=['ckanext', 'ckanext.notify'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[],
	entry_points=\
	"""
        [ckan.plugins]
	    notify=ckanext.notify.plugin:notifyPlugin
        notify_datasetform=ckanext.notify.forms:notifyDatasetForm
        notify_groupform=ckanext.notify.forms:notifyGroupForm        

        [ckan.forms]
        notify_form = ckanext.notify.package_form:get_notify_fieldset

        [paste.paster_command]
        notify=ckanext.notify.commands:notifyCommand
	""",
)
