from setuptools import setup, find_packages

requirements = [
  "Flask>=1.0.0, <1.1.0",
  "SQLAlchemy>=1.2.0, <1.3.0"
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
