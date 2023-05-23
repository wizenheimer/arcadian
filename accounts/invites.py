from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse


def get_invite_url(request, sender_id, workspace_id, receipient):
    """
    Generate invite url for a given workspace and email
    """
    # Encode the workspace and email information using URL-safe base64 encoding
    workspace_id = workspace_id
    sender_id = sender_id
    receipient_email = receipient

    encoded_workspace_id = urlsafe_base64_encode(str(workspace_id).encode())
    encoded_email = urlsafe_base64_encode(str(receipient_email).encode())
    encoded_sender_id = urlsafe_base64_encode(str(sender_id).encode())
    current_site = get_current_site(request).domain
    relativeLink = reverse("workspace-invite", kwargs={"pk": workspace_id})
    absurl = (
        "http://"
        + current_site
        + relativeLink
        + f"?workspace={encoded_workspace_id}&from={encoded_sender_id}&to={encoded_email}"
    )

    return absurl


def decode_absurl(workspace, sender, receipient):
    """
    Get receipt email, sender id and workspace id from request parameters
    """
    workspace_id = urlsafe_base64_decode(workspace).decode()
    sender_id = urlsafe_base64_decode(sender).decode()
    email_id = urlsafe_base64_decode(receipient).decode()

    return {
        "workspace_id": workspace_id,
        "sender_id": sender_id,
        "email_id": email_id,
    }
