from setuptools import setup, find_packages

requirements = [
    "Flask>=1.0.0, <1.1.0",
    "SQLAlchemy>=1.2.0, <1.3.0",
    "Flask-SQLAlchemy>=2.3.0, <2.4.0",
    "alembic>=0.9.9, <1.0.0",
    "factory_boy>=2.4.1, <2.5",
    "jsonschema>=2.6.0, <3.0.0",
    "rdflib>=4.2.2, <5.0.0",
    "rdflib-jsonld>=0.4.0, <0.5.0",
    "flask_profiler>= 1.6, <1.6.1",
    "nose",
    "mock",
    "rednose",
    "coverage",
    "nose-cov",
    "freezegun",
    "pycodestyle"
]

setup(
    name='pywa',
    version='0.1.0',
    packages=find_packages(),
    install_requires=requirements,
    author='Alexander Mendes',
    author_email='alexanderhmendes@gmail.com',
    description='A PostgreSQL-backed Web Annotation server',
    license='MIT',
    download_url='https://github.com/alexandermendes/pywa'
)
