from setuptools import setup

setup(
    name='iacoll',
    version='0.0.1',
    url='https://github.com/edsu/iacoll',
    author='Ed Summers',
    author_email='ehs@pobox.com',
    py_modules=['iacoll', ],
    description='Collect metadata for Internet Archive collections',
    python_requires='>=3.6',
    install_requires=['internetarchive', 'tqdm', 'plyvel'],
    entry_points={'console_scripts': ['iacoll' = 'iacoll:main']}
)
