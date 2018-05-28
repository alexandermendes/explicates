from setuptools import setup, find_packages

requirements = [
    "Flask>=1.0.0, <1.1.0",
    "SQLAlchemy>=1.2.0, <1.3.0",
    "Flask-SQLAlchemy>=2.3.0, <2.4.0",
    "alembic>=0.9.9, <1.0.0",
    "jsonschema>=2.6.0, <3.0.0",
    "flask-cors>=3.0.2, <3.0.3",
    "unidecode>=1.0.22, <2.0.0",
    "zipstream>=1.1.4, <1.2.0",
    "psycopg2>=2.5.2, <3.0",
    "future>=0.16.0, <1.0.0",
    "mkdocs>=0.17.1, <1.0.0",
    "mkdocs-material",
    "pymdown-extensions",
    "markdown_include",
    "factory_boy>=2.4.1, <2.5",
    "nose",
    "mock",
    "rednose",
    "coverage",
    "nose-cov",
    "freezegun",
    "pycodestyle"
]


setup(
    name='explicates',
    version='0.1.0',
    packages=find_packages(),
    install_requires=requirements,
    author='Alexander Mendes',
    author_email='alexanderhmendes@gmail.com',
    description='A PostgreSQL-backed Web Annotation server',
    license='MIT',
    download_url='https://github.com/alexandermendes/explicates'
)
