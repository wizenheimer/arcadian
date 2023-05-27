import os
import stripe
from datetime import datetime, timedelta
from assets.models import DataSource

stripe.api_key = os.environ.get("STRIPE_API_KEY", None)
stripe.api_version = "2020-08-27"


def query_subscription_data(api_key, data):
    """
    Query subscription data and populate the data dictionary
    """
    # initialize stripe client
    stripe.api_key = os.environ.get(api_key, None)
    stripe.api_version = "2020-08-27"

    # Retrieve the list of subscriptions
    subscriptions = stripe.Subscription.list(limit=100)

    mrr = total_revenue = 0

    # Iterate over each subscription
    for subscription in subscriptions.auto_paging_iter():
        created_timestamp = subscription.created
        created_date = datetime.fromtimestamp(created_timestamp)
        month_year = created_date.strftime("%Y-%m")

        total_revenue += subscription.plan.amount / 100

        if subscription.plan and subscription.plan.interval == "month":
            mrr += subscription.plan.amount / 100

        # Add the data points to the corresponding month
        if month_year not in data:
            data[month_year] = {
                "all subscription": 0,
                "active subscriptions": 0,
                "trial subscriptions": 0,
                "canceled subscriptions": 0,
                "monthly recurring revenue": 0,
                "total revenue": 0,
                "user churn": 0,
                "revenue churn": 0,
            }

        monthly_data = data[month_year]

        monthly_data["all subscription"] += 1

        monthly_data["monthly recurring revenue"] = mrr

        monthly_data["annual recurring revenue"] = mrr * 12

        monthly_data["total revenue"] = total_revenue

        monthly_data["timestamp"] = str(datetime.now())

        if subscription.status == "active":
            monthly_data["active subscription"] += 1
        elif subscription.status == "trialing":
            monthly_data["trial subscription"] += 1
        elif subscription.status == "canceled":
            monthly_data["canceled subscription"] += 1
            monthly_data["user churn"] += 1
            monthly_data["revenue churn"] += subscription.plan.amount

    return data


def query_customer_data(api_key, data):
    """
    Query customer data and populate the data dictionary
    """
    # Active Customers
    customers = stripe.Customer.list(limit=100)

    for customer in customers.auto_paging_iter():
        created_timestamp = customer.created
        created_date = datetime.fromtimestamp(created_timestamp)
        month_year = created_date.strftime("%Y-%m")

        if "active customers" not in data[month_year]:
            data[month_year]["active customers"] = 0
            data[month_year]["arpu"] = 0

        monthly_data = data[month_year]

        monthly_data["active customers"] += 1
        monthly_data["arpu"] = (
            monthly_data["total revenue"] / monthly_data["active customers"]
        )

        monthly_data["timestamp"] = str(datetime.now())

    return data


def fetch_data(datasource_id):
    """
    Fetch data associated with a given source
    """
    datasource = DataSource.objects.get(id=datasource_id)
    api_key = datasource.api_key

    # Create a dictionary to store subscriptions month-wise
    data = {}

    query_subscription_data(api_key, data)
    query_customer_data(api_key, data)

    return data
