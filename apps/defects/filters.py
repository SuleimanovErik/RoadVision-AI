import django_filters
from .models import Defect, DefectCluster


class DefectFilter(django_filters.FilterSet):
    defect_type = django_filters.CharFilter(
        field_name="defect_type", lookup_expr="iexact"
    )
    severity = django_filters.CharFilter(
        field_name="severity", lookup_expr="iexact"
    )
    is_confirmed = django_filters.BooleanFilter()
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Defect
        fields = ("defect_type", "severity", "is_confirmed")


class DefectClusterFilter(django_filters.FilterSet):
    defect_type = django_filters.CharFilter(
        field_name="main_defect__defect_type", lookup_expr="iexact"
    )
    severity = django_filters.CharFilter(
        field_name="main_defect__severity", lookup_expr="iexact"
    )
    source_type = django_filters.CharFilter(
        field_name="main_defect__source_type", lookup_expr="iexact"
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    # фильтр по bbox карты: ?lat_min=42&lat_max=43&lng_min=74&lng_max=75
    lat_min = django_filters.NumberFilter(
        field_name="center_latitude", lookup_expr="gte"
    )
    lat_max = django_filters.NumberFilter(
        field_name="center_latitude", lookup_expr="lte"
    )
    lng_min = django_filters.NumberFilter(
        field_name="center_longitude", lookup_expr="gte"
    )
    lng_max = django_filters.NumberFilter(
        field_name="center_longitude", lookup_expr="lte"
    )

    class Meta:
        model = DefectCluster
        fields = ("defect_type", "severity", "source_type")