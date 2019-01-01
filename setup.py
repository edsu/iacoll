from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name='iacoll',
    version='0.0.1',
    url='https://github.com/edsu/iacoll',
    author='Ed Summers',
    author_email='ehs@pobox.com',
    py_modules=['iacoll', ],
    description='Collect metadata for Internet Archive collections',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    install_requires=['internetarchive', 'tqdm', 'plyvel'],
    entry_points={'console_scripts': ['iacoll' = 'iacoll:main']}
)
