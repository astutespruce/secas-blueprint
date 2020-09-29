import os
from setuptools import setup


description = "SECAS Southeast Conservation Blueprint Explorer"

if os.path.exists("README.md"):
    long_description = open("README.md").read()
else:
    long_description = description

setup(
    name="secas-blueprint",
    version="0.1.0",
    url="https://github.com/astutespruce/secas-blueprint",
    license="MIT",
    author="Brendan C. Ward",
    author_email="bcward@astutespruce.com",
    description=description,
    long_description_content_type="text/markdown",
    long_description=long_description,
    install_requires=[],
)
