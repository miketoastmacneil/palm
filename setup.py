from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="palm",
    version="0.0.0",
    description="Palm backtesting simulation engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mike MacNeil",
    license="Apache 2.0",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "matplotlib==3.0.3",
        "numpy==1.18.4",
        "pandas==1.0.3",
        "seaborn==0.10.1"
    ]
)
