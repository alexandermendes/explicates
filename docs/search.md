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
given ranges. The query below will return all Annotations created between
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

The `range` query accepts the following parameters:

| gte | Greater-than or equal to |
| gt  | Greater-than             |
| lte | Less-than or equal to    |
| lt  | Less-than                |
