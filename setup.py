import os

from setuptools import setup

import versioneer

_here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(_here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="incense",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Interactively retrieve data from sacred experiments.",
    long_description=long_description,
    author="Rüdiger Busche",
    author_email="rbusche@uos.de",
    url="https://github.com/JarnoRFB/incense",
    license="MIT",
    packages=["incense"],
    python_requires=">=3.5",
    install_requires=[
        "sacred",
        "matplotlib>=3",
        "pandas>=0.23",
        "jupyterlab>=0.35",
        "pymongo>=3.7",
        "easydict>=1.9",
        "future-fstrings==1.0.0",
    ],
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
