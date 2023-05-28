from rest_framework import viewsets, parsers
from metrics.models import Metric, MetricCollection
from metrics.serializers import MetricCollectionSerializer, MetricSerializer


class MetricViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer


class MetricCollectionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = MetricCollection.objects.all()
    serializer_class = MetricCollectionSerializer
