from setuptools import setup, find_packages

exec(open("misophonia_data_analysis/_version.py").read())

setup(
    name="misophonia_data_analysis",
    version=__version__,  # noqa: F821
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "misophonia_data_analysis=misophonia_data_analysis.cli:main",
        ]
    },
    install_requires=[
        "pandas>=1.5.2"
    ],
)