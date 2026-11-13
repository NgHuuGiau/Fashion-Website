from django.urls import path
from .views import SubscribeView, UnsubscribeView, AdminCampaignView, AdminSubscriberView

app_name = "newsletter"

urlpatterns = [
    path("subscribe/", SubscribeView.as_view(), name="subscribe"),
    path("unsubscribe/", UnsubscribeView.as_view(), name="unsubscribe"),
    path("admin/campaigns/", AdminCampaignView.as_view(), name="admin_campaigns"),
    path("admin/subscribers/", AdminSubscriberView.as_view(), name="admin_subscribers"),
]