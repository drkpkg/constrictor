from setuptools import setup, find_packages

setup(
    name="constrictor-framework",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'Flask',
    ],
    entry_points='''
        [console_scripts]
        constrictor=constrictor.cli:main
    ''',
    long_description="Constrictor microframework",
    long_description_content_type="text/markdown",
)
