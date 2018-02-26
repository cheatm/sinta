from setuptools import setup, find_packages


REQUIRES = open("requirements.txt").readlines()


setup(
    name="sinta",
    version="0.0.1",
    packages=find_packages(),
    install_requires=REQUIRES,
    entry_points={"console_scripts": ["sinta = sinta.entry_point:group"]}
)