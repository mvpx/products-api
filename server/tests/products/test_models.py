import pytest

from products.models import Product


@pytest.mark.django_db
def test_product_model():
    product = Product(name="Nokia 3310", price=110.20, rating=3.1)
    product.save()
    assert product.name == "Nokia 3310"
    assert product.price == 110.20
    assert product.rating == 3.1
    assert product.created_at
    assert product.updated_at
    assert str(product) == product.name
