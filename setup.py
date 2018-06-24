import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='pytagger',
    version='0.0.1',
    entry_points={
        'console_scripts': ['pytagger=pytagger.pytagger:main']
    },
    author='Simon Rose',
    author_email='mail@popkornium18.de',
    description='A simple CLI audio tagger.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/Popkornium18/pytagger',
    packages=setuptools.find_packages(),
    keywords=['audio', 'tag', 'taglib', 'mp3', 'flac', 'ogg'],
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
)
