from rest_framework import serializers
from metrics.models import Metric, MetricCollection


class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = (
            "time",
            "type",
            "data",
        )


class MetricCollectionSerializer(serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()

    class Meta:
        model = MetricCollection
        fields = (
            "type",
            "metrics",
        )

    def get_metrics(self, metric_collection):
        metrics = metric_collection.metrics.all()
        serializer = MetricCollectionSerializer(
            metrics,
            many=True,
        )
        return serializer.data
