from django.urls import path, include
from .views import car_list_create, car_detail, CarListCreateAPIView,CarDetailAPIView, ProductViewSet, ProductListByChildCategorySlug
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('cars/', car_list_create),
    path('cars/<int:pk>/', car_detail),
    path('cars/', CarListCreateAPIView.as_view()),
    path('cars/<int:pk>/', CarDetailAPIView.as_view()),
    path('api/', include(router.urls)),
    path(
        'products/by-child-category/<slug:slug>/',
         ProductListByChildCategorySlug.as_view(),
        name='products-by-child-category'
    ),

]
