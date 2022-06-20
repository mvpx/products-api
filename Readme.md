# Products API

## Seed database with some initial data:
```
$ docker-compose exec server python manage.py flush
$ docker-compose exec server python manage.py loaddata products.json
```

## Seed elasticsearch with the data from database
```
$ docker-compose exec server python manage.py bulk_update
```

## Check if the records are in elasticsearch
```
$ curl http://localhost:9200/product/_count?pretty

{
  "count" : 1000,
  "_shards" : {
    "total" : 1,
    "successful" : 1,
    "skipped" : 0,
    "failed" : 0
  }
}
```