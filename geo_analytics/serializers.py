from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Field


class FieldSerializer(GeoFeatureModelSerializer):
    """Серіалізатор для моделі Field з підтримкою GeoJSON."""

    class Meta:
        model = Field
        geo_field = 'geom'
        fields = ('id', 'company', 'name', 'area_hectares', 'crop_status')