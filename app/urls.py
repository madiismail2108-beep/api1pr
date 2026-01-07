from django.urls import path
from .views import car_list_create, car_detail

urlpatterns = [
    path('cars/', car_list_create),
    path('cars/<int:pk>/', car_detail),
]

'''from .views import CarListCreateAPIView, CarDetailAPIView

urlpatterns = [
    path('cars/', CarListCreateAPIView.as_view()),
    path('cars/<int:pk>/', CarDetailAPIView.as_view()),
]'''
