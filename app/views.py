from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Car, Product, Category
from .serializers import CarSerializer, ProductSerializer
from rest_framework import viewsets
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Car
from rest_framework.permissions import BasePermission
from django.utils import timezone
from datetime import timedelta

class CanUpdateWithin4Hours(BasePermission):
    message = "You can edit this object within 4 hours"
    
    def has_object_permission(self, request, view, obj):
        if request.method not in ['PUT', 'PATCH']:
            return True
        
        time_limit = obj.created_at + timedelta(hours=4)
        return timezone.now() <= time_limit


@api_view(['GET', 'POST'])
def car_list_create(request):
    if request.method == 'GET':
        cars = Car.objects.all()
        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def car_detail(request, pk):
    try:
        car = Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        return Response({'error': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CarSerializer(car)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = CarSerializer(car, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        car.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CarListCreateAPIView(APIView):
    def get(self, request):
        cars = Car.objects.all()
        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CarDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Car.objects.get(pk=pk)
        except Car.DoesNotExist:
            return None

    def get(self, request, pk):
        car = self.get_object(pk)
        if not car:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CarSerializer(car)
        return Response(serializer.data)

    def put(self, request, pk):
        car = self.get_object(pk)
        if not car:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CarSerializer(car, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        car = self.get_object(pk)
        if not car:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        car.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD:
    GET    /api/products/
    POST   /api/products/
    GET    /api/products/{id}/
    PUT    /api/products/{id}/
    DELETE /api/products/{id}/
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductListByChildCategorySlug(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Product.objects.filter(category__slug=slug)

# Create your views here.
