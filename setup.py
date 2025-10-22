from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Constrictor microframework"

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['click>=8.1.7', 'Flask>=3.0.3']

setup(
    name="constrictor-framework",
    version="1.0.0",
    author="Daniel",
    author_email="daniel@example.com",
    description="A microframework based on Flask for creating modular applications",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/daniel/constrictor",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=8.3.3',
            'pytest-flask>=1.3.0',
            'python-dotenv>=1.0.1',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
            'myst-parser>=0.18.0',
            'sphinx-autodoc-typehints>=1.19.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'constrictor=constrictor.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Framework :: Flask',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    python_requires='>=3.8',
    keywords='flask microframework modular web framework',
    project_urls={
        'Bug Reports': 'https://github.com/daniel/constrictor/issues',
        'Source': 'https://github.com/daniel/constrictor',
        'Documentation': 'https://github.com/daniel/constrictor#readme',
    },
)
