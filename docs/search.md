Presented below are the available options for retrieving Annotations from the
search endpoint at:

```http
GET /search/
```

Results are returned as an AnnotationCollection that uses the usual
structure.

The queries should be sent as JSON, although Using URL parameters should also
work. If both a JSON body and URL parameters are sent with the request then
the JSON body will take preference.

## limit

Limit the Annotations returned.

```json
{
    "limit": 42
}
```

## offset

Offset the first Annotation to be returned.

```json
{
    "offset": 42
}
```

## collection

Return Annotations that belong to the given AnnotationCollection.

```json
{
    "collection": "https://example.org/annotations/my-container/"
}
```

## range

Return Annotations where the values for a set of keys fall within the
given ranges. The query below will return all Annotations `created` between
`2018-05-15T00:00:00Z` and `2018-05-17T00:00:00Z`. Note that when querying
a datetime field the ISO 8601 format shown here should be used.

```json
{
    "range": {
        "created": {
            "gte": "2018-05-15T00:00:00Z",
            "lte": "2018-05-17T00:00:00Z"
        }
    }
}
```

The `range` query accepts the following parameters for each field:

| key | description              |
|-----|--------------------------|
| gte | Greater-than or equal to |
| gt  | Greater-than             |
| lte | Less-than or equal to    |
| lt  | Less-than                |

## contains

Return Annotations that contain a specific value. The query below will
return all Annotations that contain a `body` where the `id` is
`https://example.org/page1/`.

```json
{
    "contains": {
        "body": {
            "id": "https://example.org/page1/"
        }
    }
}
```

## fts

Return Annotations where the specified keys contain a `query`. The following
query will return all Annotations where the `body` contains any of the words
in `some keywords`.

```json
{
    "fts": {
        "body": {
            "query": "some keywords"
        }
    }
}
```

The `fts` query accepts the following parameters for each field:

| key      | description                                    |
|----------|------------------------------------------------|
| query    | The search query (required)                    |
| operator | Join tokens with `and` or `or` (default `and`) |
| prefix   | Treat each token as a prefix (default `True`)  |

!!! info "Full-text search language"

    The dictionary used for full-text searches is defined for each Annotation
    by the first `language` code found in the Annotation's `body`. If no
    such language code is found then the server default is used. See the
    [Configuration](/setup.md#configuration) section for more details of
    the available dictionaries.

## fts_phrase

Return Annotations where the specified keys contain a `query` phrase. The
following query will return all Annotations where the `body` contains the
phrase that begins with `Some partial phras`.

```json
{
    "fts_phrase": {
        "body": {
            "query": "Some partial phras"
        }
    }
}
```

The `fts_phrase` query accepts the following parameters for each field:

| key      | description                                  |
|----------|----------------------------------------------|
| query    | The search query (required)                  |
| prefix   | Treat the query as a prefix (default `True`) |
| distance | The distance between tokens (default `1`)    |

!!! note "Exact phrase searches"

    Note that all phrase queries will be treated as prefixes; to search for
    exact phrases use [`contains`](/search.md#contains) instead.

## deleted

Return or include deleted Annotations.

```json
{
    "deleted": "include"
}
```

The `deleted` query accepts the following parameters:

| key     | description                           |
|---------|---------------------------------------|
| exclude | Exclude deleted Annotations (default) |
| include | Include deleted Annotations           |
| only    | Return only deleted Annotations       |
