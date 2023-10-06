from setuptools import setup, find_packages

setup(
    name="constrictor",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'Flask',
        # Add other dependencies if needed
    ],
    entry_points='''
        [console_scripts]
        constrictor=constrictor.cli:main
    '''
)
