# Explicates

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

The Web Annotation endpoints are served from `/annotations`.

### Search

A search service is implemented at `/search/<tablename>`.

Search results are returned as an
[OrderedCollection](https://www.w3.org/ns/activitystreams#OrderedCollection).

```json
HTTP/1.1 200 OK
Content-Type: application/ld+json; profile="http://www.w3.org/ns/anno.jsonld"
ETag: "_87e52ce123123"
Allow: GET,OPTIONS,HEAD
Content-Length: 315

{
  "@context": "http://www.w3.org/ns/anno.jsonld",
  "id": "http://example.org/search/collection/?query=foo",
  "type": "as:OrderedCollection",
  "total": 42023,
  "first": "http://example.org/search/collection/?page=0&query=foo",
  "last": "http://example.org/search/collection/?page=42&query=foo"
}
```

#### Search Annotations

Endpoint: `/search/annotation`

#### Search Collections

Endpoint: `/search/collection`

#### Available parameters

All search endpoints provide the following parameters:

- `contains`: Search for objects that contain some nested value
(e.g. `contains={"motivation":"commenting", "body":{"value":"foo"}}`)
