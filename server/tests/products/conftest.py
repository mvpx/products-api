import pytest

from products.models import Product


@pytest.fixture(scope="function")
def add_product():
    def _add_product(name, price, rating):
        product = Product.objects.create(name=name, price=price, rating=rating)
        return product

    return _add_product
