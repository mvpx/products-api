import base64
import json

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse

from products.models import Product

PASSWORD = "pAssw0rd!"


@pytest.mark.django_db
def test_user_can_sign_up(client):
    resp = client.post(
        reverse("sign_up"),
        data={
            "username": "test",
            "password1": PASSWORD,
            "password2": PASSWORD,
        },
    )
    user = get_user_model().objects.last()
    assert status.HTTP_201_CREATED, resp.status_code
    assert resp.data["id"], user.id
    assert resp.data["username"], user.username


@pytest.mark.django_db
def test_user_can_log_in(client):
    user = get_user_model().objects.create_user(username="test", password=PASSWORD)
    resp = client.post(
        reverse("log_in"),
        data={
            "username": user.username,
            "password": PASSWORD,
        },
    )

    access = resp.data["access"]
    header, payload, signature = access.split(".")
    decoded_payload = base64.b64decode(f"{payload}==")
    payload_data = json.loads(decoded_payload)

    assert status.HTTP_200_OK, resp.status_code
    assert resp.data["refresh"]
    assert payload_data["id"], user.id
    assert payload_data["username"], user.username


@pytest.mark.django_db
def test_add_product(client, django_user_model):
    user = django_user_model.objects.create_user(username="test", password=PASSWORD)
    client.force_login(user)
    products = Product.objects.all()
    assert len(products) == 0

    resp = client.post(
        "/api/products/",
        {"name": "Nokia 3310", "price": "200.20", "rating": 3.1},
        content_type="application/json",
    )
    assert resp.status_code == 201
    assert resp.data["name"] == "Nokia 3310"

    products = Product.objects.all()
    assert len(products) == 1


@pytest.mark.django_db
def test_add_product_invalid_json(client, django_user_model):
    user = django_user_model.objects.create_user(username="test", password=PASSWORD)
    client.force_login(user)

    products = Product.objects.all()
    assert len(products) == 0

    resp = client.post("/api/products/", {}, content_type="application/json")
    assert resp.status_code == 400

    products = Product.objects.all()
    assert len(products) == 0


@pytest.mark.django_db
def test_add_product_invalid_json_keys(client, django_user_model):
    user = django_user_model.objects.create_user(username="test", password=PASSWORD)
    client.force_login(user)

    products = Product.objects.all()
    assert len(products) == 0

    resp = client.post(
        "/api/products/",
        {"name": "Nokia 3310"},
        content_type="application/json",
    )
    assert resp.status_code == 400

    products = Product.objects.all()
    assert len(products) == 0


@pytest.mark.django_db
def test_get_single_product(client, add_product, django_user_model):
    user = django_user_model.objects.create_user(username="test", password=PASSWORD)
    client.force_login(user)

    product = add_product(name="Nokia 3310", price="200.20", rating=3.1)
    resp = client.get(f"/api/products/{product.id}/")

    assert resp.status_code == 200
    assert resp.data["name"] == "Nokia 3310"


def test_get_single_product_incorrect_id(client):
    resp = client.get("/api/products/foo/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_get_all_products(client, add_product):
    add_product(name="Nokia 3310", price="200.20", rating=3.1)
    add_product(name="Nokia 5210", price="100.20", rating=4.1)
    resp = client.get("/api/products/")
    assert resp.status_code == 200
    assert resp.data["count"] == 2


@pytest.mark.django_db
def test_remove_product(client, add_product, django_user_model):
    user = django_user_model.objects.create_user(username="test", password=PASSWORD)
    client.force_login(user)

    product = add_product(name="Nokia 3310", price="200.20", rating=3.1)

    resp = client.get(f"/api/products/{product.id}/")
    assert resp.status_code == 200
    assert resp.data["name"] == "Nokia 3310"

    resp_two = client.delete(f"/api/products/{product.id}/")
    assert resp_two.status_code == 204

    resp_three = client.get("/api/products/")
    assert resp_three.status_code == 200
    assert len(resp_three.data["results"]) == 0


@pytest.mark.django_db
def test_remove_product_incorrect_id(client, django_user_model):
    user = django_user_model.objects.create_user(username="test", password=PASSWORD)
    client.force_login(user)
    resp = client.delete("/api/products/123542323/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_update_product(client, add_product, django_user_model):
    user = django_user_model.objects.create_user(username="test", password=PASSWORD)
    client.force_login(user)

    product = add_product(name="Nokia 3310", price="200.20", rating=3.1)

    resp = client.put(
        f"/api/products/{product.id}/",
        {"name": "Lemon Pie", "price": "20.5", "rating": 4},
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.data["name"] == "Lemon Pie"
    assert resp.data["rating"] == 4

    resp_two = client.get(f"/api/products/{product.id}/")
    assert resp_two.status_code == 200
    assert resp_two.data["name"] == "Lemon Pie"
    assert resp.data["rating"] == 4


@pytest.mark.django_db
def test_update_product_incorrect_id(client, django_user_model):
    user = django_user_model.objects.create_user(username="test", password=PASSWORD)
    client.force_login(user)
    resp = client.put(f"/api/products/123542323/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_update_product_invalid_json(client, add_product, django_user_model):
    user = django_user_model.objects.create_user(username="test", password=PASSWORD)
    client.force_login(user)
    product = add_product(name="Nokia 3310", price="200.20", rating=3.1)
    resp = client.put(f"/api/products/{product.id}/", {}, content_type="application/json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_update_product_invalid_json_keys(client, add_product, django_user_model):
    user = django_user_model.objects.create_user(username="test", password=PASSWORD)
    client.force_login(user)
    product = add_product(name="Nokia 3310", price="200.20", rating=3.1)

    resp = client.put(
        f"/api/products/{product.id}/",
        {"name": "Lemon Pie", "test": "20.5", "rating": 4},
        content_type="application/json",
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_query_matches_products_name(client):
    resp = client.get("/api/es-products/Paper/")
    assert 6 == len(resp.data)
    assert "668" == resp.data[0]["id"]
