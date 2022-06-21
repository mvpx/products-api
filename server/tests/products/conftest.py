import json
import pathlib
import uuid

import pytest
from django.conf import settings
from elasticsearch_dsl import connections

from products.constants import ES_MAPPING
from products.models import Product


@pytest.fixture(scope="function")
def add_product():
    def _add_product(name, price, rating):
        product = Product.objects.create(name=name, price=price, rating=rating)
        return product

    return _add_product


@pytest.fixture(scope="module")
def test_elasticsearch():
    index = f"test-product-{uuid.uuid4()}"
    connection = connections.get_connection()
    connection.indices.create(
        index=index,
        body={
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
            },
            "mappings": ES_MAPPING,
        },
    )

    fixture_path = pathlib.Path(settings.BASE_DIR / "products" / "fixtures" / "products.json")
    with open(fixture_path, "rt") as fixture_file:
        fixture_data = json.loads(fixture_file.read())
        for product in fixture_data:
            fields = product["fields"]
            connection.create(
                index=index,
                id=fields["id"],
                body={
                    "name": fields["name"],
                    "price": fields["price"],
                    "rating": fields["rating"],
                },
                refresh=True,
            )
    yield connection

    connection.indices.delete(index=index)
