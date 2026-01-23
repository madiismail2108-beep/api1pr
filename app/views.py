from django.shortcuts import render
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from .models import Car, Product, Category
from .serializers import CarSerializer, ProductSerializer

class HundredPagination(PageNumberPagination):
    page_size = 100

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
        cache_key = "car_list_fbv"
        data = cache.get(cache_key)

        if data is None:
            print("DB dan olindi (FBV Car List)")
            cars = Car.objects.all()
            serializer = CarSerializer(cars, many=True)
            data = serializer.data
            cache.set(cache_key, data, 60 * 5)
        else:
            print("Cache dan olindi (FBV Car List)")

        return Response(data)

    if request.method == 'POST':
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete("car_list_fbv")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def car_detail(request, pk):
    try:
        car = Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        return Response({'error': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)

    cache_key = f"car_detail_fbv_{pk}"

    if request.method == 'GET':
        data = cache.get(cache_key)

        if data is None:
            print("DB dan olindi (FBV Car Detail)")
            serializer = CarSerializer(car)
            data = serializer.data
            cache.set(cache_key, data, 60 * 5)
        else:
            print("Cache dan olindi (FBV Car Detail)")

        return Response(data)

    if request.method == 'PUT':
        serializer = CarSerializer(car, data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(cache_key)
            cache.delete("car_list_fbv")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        car.delete()
        cache.delete(cache_key)
        cache.delete("car_list_fbv")
        return Response(status=status.HTTP_204_NO_CONTENT)

class CarListCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = "car_list"
        data = cache.get(cache_key)

        if data is None:
            print("DB dan olindi (Car List)")
            cars = Car.objects.select_related('brand').prefetch_related('owners')
            serializer = CarSerializer(cars, many=True)
            data = serializer.data
            cache.set(cache_key, data, 60 * 5)
        else:
            print("Cache dan olindi (Car List)")

        return Response(data)

    def post(self, request):
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete("car_list")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CarDetailAPIView(APIView):

    def get_object(self, pk):
        try:
            return Car.objects.get(pk=pk)
        except Car.DoesNotExist:
            return None

    def get(self, request, pk):
        cache_key = f"car_detail_{pk}"
        data = cache.get(cache_key)

        if data is None:
            print("DB dan olindi (Car Detail)")
            car = self.get_object(pk)
            if not car:
                return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = CarSerializer(car)
            data = serializer.data
            cache.set(cache_key, data, 60 * 5)
        else:
            print("Cache dan olindi (Car Detail)")

        return Response(data)

    def put(self, request, pk):
        car = self.get_object(pk)
        if not car:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CarSerializer(car, data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(f"car_detail_{pk}")
            cache.delete("car_list")
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        car = self.get_object(pk)
        if not car:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        car.delete()
        cache.delete(f"car_detail_{pk}")
        cache.delete("car_list")
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category') \
                              .prefetch_related('images')
    serializer_class = ProductSerializer

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        cache_key = f"product_detail_{pk}"

        data = cache.get(cache_key)

        if data is None:
            print("DB dan olindi (Product Detail)")
            response = super().retrieve(request, *args, **kwargs)
            data = response.data
            cache.set(cache_key, data, 60 * 5)
        else:
            print("Cache dan olindi (Product Detail)")

        return Response(data)

class ProductListByChildCategorySlug(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        cache_key = f"products_by_slug_{slug}"

        products = cache.get(cache_key)

        if products is None:
            print("DB dan olindi (Products by slug)")
            products = Product.objects.select_related('category') \
                                       .prefetch_related('images') \
                                       .filter(category__slug=slug)
            cache.set(cache_key, products, 60 * 5)
        else:
            print("Cache dan olindi (Products by slug)")

        return products


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()
        return Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_204_NO_CONTENT
        )
