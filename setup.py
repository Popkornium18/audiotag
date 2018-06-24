"""Package setup for pytagger."""
from setuptools import setup

setup(
    name='pytagger',
    packages=['pytagger'],
    entry_points={
        'console_scripts': ['pytagger=pytagger.pytagger:main']
    },
    version='0.1.0',
    description='A simple CLI audio tagger.',
    author='Simon Rose',
    author_email='mail@popkornium18.de',
    url='https://gitlab.com/Popkornium18/pytagger',
    keywords=['audio', 'tag', 'taglib', 'mp3', 'flac', 'ogg']
)
