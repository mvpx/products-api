ES_INDEX = "product"

ES_MAPPING = {
    "dynamic": "strict",
    "properties": {
        "name": {
            "type": "text",
            "analyzer": "english",
        },
        "price": {
            "type": "keyword",
        },
        "rating": {
            "type": "float",
        },
    },
}
