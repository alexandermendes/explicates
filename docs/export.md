All Annotations in an Annotation Collection can be exported from the database
via the following endpoint:

```http
GET /export/<collection_id>/
```

The Annotations are streamed back to the client as a JSON list. This endpoint
is intended for programmatic use only. It is not recommended to access it via
a web browser as, depending on the number of Annotations to be exported, it is
likely the browser would run out of memory before the request finishes.

!!! summary "Curl example"

    ```bash
    curl https://example.org/annotations/my-container/ > out.json
    ```

!!! summary "Python pandas example"

    ```python
    import pandas

    iri = 'https://example.org/annotations/my-container/'
    df = pandas.read_json(iri, orient='records')
    ```
