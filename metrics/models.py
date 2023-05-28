from django.db import models
from assets.models import DataSource


class Metric(models.Model):
    """A model for collecting metrics related to a datasource."""

    METRIC_TYPE = (
        # customer metrics
        ("customers/total", "customers/total"),
        ("customers/active", "customers/active"),
        # subscription metrics
        ("subscription/total", "subscription/total"),
        ("subscription/active", "subscription/active"),
        ("subscription/trial", "subscription/trial"),
        ("subscription/canceled", "subscription/canceled"),
        # revenue metrics
        ("mrr", "mrr"),
        ("revenue/total", "revenue/total"),
        ("arpu", "arpu"),
        ("arr", "arr"),
        # churn related metrics
        ("churn/user", "churn/user"),
        ("churn/revenue", "churn/revenue"),
    )
    metric_type = models.CharField(
        max_length=255,
        choices=METRIC_TYPE,
    )
    # holds the month + year
    # currentMonth = datetime.now().month
    # currentYear = datetime.now().year
    time = models.CharField(
        index=True,
        max_length=4,
    )
    data = models.DecimalField(
        max_digits=9,
        max_length=12,
    )
    source = models.ForeignKey(
        DataSource,
        related_name="metrics",
        on_delete=models.CASCADE,
    )
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"
