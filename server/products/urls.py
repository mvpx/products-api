from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (ESProductsView, LogInView, ProductDetailView,
                    ProductListView, ProductUpdateView, SignUpView)

urlpatterns = [
    path("api/sign_up/", SignUpView.as_view(), name="sign_up"),
    path("api/log_in/", LogInView.as_view(), name="log_in"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/products/", ProductListView.as_view()),
    path("api/products/<int:pk>/", ProductDetailView.as_view()),
    path("api/products/<int:pk>/rate/", ProductUpdateView.as_view()),
    path("api/es-products/<str:query>/", ESProductsView.as_view()),
]
