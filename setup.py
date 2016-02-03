
import re
from setuptools import setup

version = re.search(
		    '^__version__\s*=\s*"(.*)"',
			    open('zwitter/zwitter.py').read(),
				    re.M
					    ).group(1)

setup(
		name="zwitter",
		packages=["zwitter"],
		entry_points={
			"console_scripts": ['zwitter = zwitter.zwitter:main']
			},
		version=version,
		author="Zweihander",
		author_email="sd852456@naver.com",
		url="https://twitter.com/panzerbruder",
		description="CUI base Twitter Client",
			)
