# pywa

A PostgreSQL-backed Web Annotation server.

## Setup

### Development

A virtual machine setup is provided for easily getting a development server up
and running. Download and install
[Vagrant](https://www.vagrantup.com/) >= 4.2.10 and
[VirtualBox](https://www.virtualbox.org/) >= 1.2.1,
then run:

```bash
# setup the virtual machine
vagrant up

# enter the virtual machine
vagrant ssh

# run
python run.py
```

By default the server will now be available at http://127.0.0.1:3000.

### Production

The requirements for production servers are:

- Ubuntu 18.04 LTS
- Python 2.7, >= 3.4
- PostgreSQL >= 10

## Usage

Following are some examples of how to use the server.

### AnnotationCollection

#### Create

Request:

```http
POST http://example.com/

Accept: application/ld+json; profile="http://www.w3.org/ns/anno.jsonld"
Content-Type: application/ld+json; profile="http://www.w3.org/ns/anno.jsonld"
Slug: my-container

{
  "label": "A Container for Web Annotations",
  "creator": "http://client.example.com/user1"
}
```

Response:

HTTP/1.1 201 CREATED

Accept-Post: application/ld+json; profile="http://www.w3.org/ns/anno.jsonld"
Allow: POST,GET,OPTIONS,HEAD
Content-Location: http://example.org/my-container/
Content-Type: application/ld+json;charset=UTF-8
Link: <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/TR/annotation-protocol/>; rel="http://www.w3.org/ns/ldp#constrainedBy"
Location: http://example.org/my-container/
Vary: Origin, Accept, Prefer

{
  "@context": [
    "http://www.w3.org/ns/anno.jsonld",
    "http://www.w3.org/ns/ldp.jsonld"
  ],
  "id": "http://example.org/my-container/",
  "type": [
    "BasicContainer",
    "AnnotationCollection"
  ],
  "label": "A Container for Web Annotations",
  "first": "http://example.org/w3c/my-container/?page=0",
  "last": "http://example.org/w3c/my-container/?page=0",
  "total": 0
}
