from rest_framework import serializers
from .models import Car, Category, Product, Image

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    images = ImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = [ 'id', "name", "price", "category", "images" ]

    def get_category(self, obj):
        return {
            "id": obj.category.id,
            "name": obj.category.name
        }

    def get_images(self, obj):
        return [
            {
                "id": image.id,
                "image": image.image.url
            }
            for image in obj.images.all()
        ]

