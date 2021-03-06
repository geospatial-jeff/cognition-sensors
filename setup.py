from setuptools import setup, find_packages

with open("./requirements.txt") as reqs:
    requirements = [line.rstrip() for line in reqs if "git" not in line]

setup(
    name="sensors",
    version="0.1",
    description="Sensor configurations and patterns for automatic ingest",
    author="Jeff Albrecht",
    author_email="geospatialjeff@gmail.com",
    packages=find_packages(),
    install_requires=requirements
)