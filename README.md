# Explicates

[![Build Status](https://travis-ci.org/alexandermendes/explicates.svg?branch=master)](https://travis-ci.org/alexandermendes/explicates)
[![Coverage Status](https://coveralls.io/repos/github/alexandermendes/explicates/badge.svg?branch=master)](https://coveralls.io/github/alexandermendes/explicates?branch=master)

> A PostgreSQL-backed Web Annotation server.

[**Read the documentation**](https://alexandermendes.github.io/explicates/)

## Setup

A virtual machine setup is provided for local development.

Download and install
[Vagrant](https://www.vagrantup.com/) >= 4.2.10 and
[VirtualBox](https://www.virtualbox.org/) >= 1.2.1,
then run:

```bash
# setup vm
vagrant up

# enter vm
vagrant ssh

# run
python run.py
```

The server should now be available at http://127.0.0.1:3000.

## Configuration

See [settings.py.tmpl](settings.py.tmpl) for all available configuration
settings. To change any settings make a copy of the template:

```bash
cp settings.py.tmpl settings.py
```

## Testing

Explicates is tested against [Python 2.7 and 3.4](https://travis-ci.org/alexandermendes/explicates):

```bash
# python 2
nosetests test/

# python 3
python3 -m "nose"
```
