Annotation Collections can be created, read, updated and deleted via the
following endpoints.

## Post

Create an Annotation Collection.

```http
POST /annotations/
```

## Get

Returns a Annotation Collection containing a minimal representation of all
Annotation Collections on the server.

```http
GET /annotations/
```

## Put

Update an Annotation Collection.

```http
PUT /annotations/my-container/
```

## Delete

Delete an Annotation Collection.

```http
DELETE /annotations/my-container/
```

!!! note "Deletion rules"

    Annotation Collections cannot be deleted if they are the last one
    remaining on the server, or if they contain Annotations.
