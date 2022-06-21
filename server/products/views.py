from django.contrib.auth import get_user_model
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match, Term
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from . import constants
from .filters import ProductFilterSet
from .models import Product
from .pagination import DefaultPagination
from .permissions import CustomPermission
from .serializers import (
    LogInSerializer,
    ProductSerializer,
    ProductRatingSerializer,
    TokenObtainPairResponseSerializer,
    UserSerializer,
)


class SignUpView(CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class LogInView(TokenObtainPairView):
    serializer_class = LogInSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TokenObtainPairResponseSerializer,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProductListView(ListCreateAPIView):
    permission_classes = [CustomPermission]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilterSet
    pagination_class = DefaultPagination
    ordering_fields = (
        "id",
        "price",
        "rating",
    )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING),
                "price": openapi.Schema(type=openapi.TYPE_STRING),
                "rating": openapi.Schema(type=openapi.TYPE_STRING),
            },
        )
    )
    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING),
                "price": openapi.Schema(type=openapi.TYPE_STRING),
                "rating": openapi.Schema(type=openapi.TYPE_NUMBER),
            },
        )
    )
    def put(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductUpdateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={"rating": openapi.Schema(type=openapi.TYPE_NUMBER)}
        )
    )
    def patch(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductRatingSerializer(product, data=request.data)
        if serializer.is_valid():
            if product.users_rated.filter(id=request.user.id):
                return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
            serializer.save()
            product.users_rated.add(request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ESProductsView(APIView):
    def get(self, request, *args, **kwargs):
        price = self.request.query_params.get("price")
        rating = self.request.query_params.get("rating")

        query = kwargs["query"]

        search = Search(index=constants.ES_INDEX)
        q = {"should": [], "filter": []}

        if query:
            q["should"] = [Match(name=query)]
            q["minimum_should_match"] = 1

        if price:
            q["filter"].append(Term(price=price))
        if rating:
            q["filter"].append(Term(rating=rating))

        response = search.query("bool", **q).params(size=100).execute()

        if response.hits.total.value > 0:
            return Response(
                data=[
                    {
                        "id": hit.meta.id,
                        "name": hit.name,
                        "price": hit.price,
                        "rating": hit.rating,
                    }
                    for hit in response
                ]
            )
        else:
            return Response(data=[])
