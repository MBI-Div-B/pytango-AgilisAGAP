from setuptools import setup, find_packages

setup(
    name="tangods_agilisagap",
    version="0.0.1",
    description="Tango device server for a Newport Conex Agilis AGAP piezo mirror with controller.",
    author="Daniel Schick",
    author_email="dschick@mbi-berlin.de",
    python_requires=">=3.6",
    entry_points={"console_scripts": ["AgilisAGAP = tangods_agilisagap:main"]},
    license="MIT",
    packages=["tangods_agilisagap"],
    install_requires=[
        "pytango",
    ],
    url="https://github.com/MBI-Div-b/pytango-AgilisAGAP",
    keywords=[
        "tango device",
        "tango",
        "pytango",
        "agilisagap",
    ],
)
