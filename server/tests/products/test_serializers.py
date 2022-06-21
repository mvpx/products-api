import pytest

from products.serializers import ProductSerializer


@pytest.mark.django_db
def test_valid_product_serializer():
    valid_serializer_data = {"name": "Nokia 3310", "price": "100.20", "rating": 3.1}
    serializer = ProductSerializer(data=valid_serializer_data)
    assert serializer.is_valid()


@pytest.mark.django_db
def test_invalid_product_serializer():
    invalid_serializer_data = {"name": "Nokia 3310", "price": 100.20, "rating": "test"}
    serializer = ProductSerializer(data=invalid_serializer_data)
    assert not serializer.is_valid()
