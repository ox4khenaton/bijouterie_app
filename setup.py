from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in bijouterie_app/__init__.py
from bijouterie_app import __version__ as version 
setup(
	name="bijouterie_app",
	version=version,
	description="Application personnalisée pour bijouterie algérienne spécialisée dans l'or 18 carats",
	author="Manus",
	author_email="support@manus.ai",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
