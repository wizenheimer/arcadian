import stripe


def validate_api_key(api_key=None, agent=None):
    if api_key is None or agent is None:
        return False
    stripe.api_key = api_key
    stripe.api_version = "2020-08-27"
    try:
        account = stripe.Account.retrieve()
        return True
    except stripe.error.AuthenticationError:
        # The API key is invalid or unauthorized
        return False
