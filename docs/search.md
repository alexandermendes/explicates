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

## offset

```json
{
    "offset": 42
}
```

## limit

```json
{
    "limit": 42
}
```
