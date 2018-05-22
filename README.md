# Explicates

[![Build Status](https://travis-ci.org/alexandermendes/explicates.svg?branch=master)](https://travis-ci.org/alexandermendes/explicates)
[![Coverage Status](https://coveralls.io/repos/github/alexandermendes/explicates/badge.svg?branch=master)](https://coveralls.io/github/alexandermendes/explicates?branch=master)

> A PostgreSQL-backed Web Annotation server.

## Setup

### Development

A virtual machine setup is provided for easily getting a development server up
and running.

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

By default the server will now be available at http://127.0.0.1:3000.

### Production

The requirements for production servers are:

- Ubuntu 18.04 LTS
- Python 2.7 or >= 3.4
- PostgreSQL >= 10

## Configuration

See [settings.py.tmpl](settings.py.tmpl) for all available configuration
settings. To change any settings make a copy of the template:

```bash
cp settings.py.tmpl settings.py
```

## Usage

Proper documentation to follow.

### Web Annotations

The Web Annotation endpoints are served from `/annotations/`.

### Search

A search service for Annotations is implemented at `/search/`. Results are
returned as an AnnotationCollection.

The following parameters are provided:

- `contains`: Search for objects that contain some nested value
(e.g. `contains={"motivation":"commenting"}`)
- `fts`: Full text search (e.g. `fts=body::foo`)

### Export

The following endpoint is provided to export the data for the purposes of
migration or offline analysis, where the `collection_id` is the IRI part that
identifies a particular collection.

```http
GET /export/<collection_id>
```

The data is streamed as JSON-LD and the following query parameters are
available:

- `flatten`: Flatten each Annotation.
- `zip`: Return the data as a ZIP file.
