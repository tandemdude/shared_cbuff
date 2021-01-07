import os
import re
import types

from setuptools import setup, find_namespace_packages


name = "shared_cbuff"


def parse_meta():
    with open(os.path.join(name, "__init__.py")) as fp:
        code = fp.read()

    token_pattern = re.compile(r"^__(?P<key>\w+)?__\s*=\s*(?P<quote>(?:'{3}|\"{3}|'|\"))(?P<value>.*?)(?P=quote)", re.M)

    groups = {}

    for match in token_pattern.finditer(code):
        group = match.groupdict()
        groups[group["key"]] = group["value"]

    return types.SimpleNamespace(**groups)


def long_description():
    with open("README.md") as fp:
        return fp.read()


meta = parse_meta()


setup(
    name="shared_cbuff",
    version=meta.version,
    description="A simple shared circular buffer implementation",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    author="tandemdude",
    author_email="tandemdude1@gmail.com",
    url="https://github.com/tandemdude/Shared-Circular-Buffer",
    packages=find_namespace_packages(include=[name + "*"]),
    python_requires=">=3.8.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
