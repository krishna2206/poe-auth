from setuptools import setup, find_packages

VERSION = '2.0.0'
DESCRIPTION = 'A reverse-engineered Python library for the Quora\'s Poe authentication API.'
setup(
    name="poe-auth",
    version=VERSION,
    author="Anhy Krishna Fitiavana",
    author_email="fitiavana.krishna@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests', 'beautifulsoup4', 'click'],
    entry_points={
        'console_scripts': [
            'poe-auth=poe_auth.poe_auth:cli',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)
