from setuptools import setup

setup(
    name='gpmbootstrap',
    version='0.1.0',
    packages=['gpmbootstrap'],
    url='https://gitlab.com/pmbootstrap/gpmbootstrap',
    license='MIT',
    author='Martijn Braam',
    author_email='martijn@brixit.nl',
    description='GTK frontend for pmbootstrap',
    long_description=open("README.rst").read(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX :: Linux',
    ],
    install_requires=[
        'pmbootstrap',
    ],
    zip_safe=True,
    include_package_data=True,
    entry_points={
        'gui_scripts': [
            'gpmbootstrap=gpmbootstrap.__main__:main'
        ]
    }
)
