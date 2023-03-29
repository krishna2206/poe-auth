from setuptools import setup, find_packages

VERSION = '1.0.1'
DESCRIPTION = 'A Python package for authenticating to Quora\'s poe.'
setup(
    name="poe-auth",
    version=VERSION,
    author="Anhy Krishna Fitiavana",
    author_email="fitiavana.krishna@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests', 'beautifulsoup4', 'click'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)