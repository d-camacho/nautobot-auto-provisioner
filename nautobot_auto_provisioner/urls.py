"""Django urlpatterns declaration for nautobot_auto_provisioner app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter


# Uncomment the following line if you have views to import
# from nautobot_auto_provisioner import views


app_name = "nautobot_auto_provisioner"
router = NautobotUIViewSetRouter()

# Here is an example of how to register a viewset, you will want to replace views.NautobotAutoProvisionerUIViewSet with your viewset
# router.register("nautobot_auto_provisioner", views.NautobotAutoProvisionerUIViewSet)


urlpatterns = [
    path("docs/", RedirectView.as_view(url=static("nautobot_auto_provisioner/docs/index.html")), name="docs"),
]

urlpatterns += router.urls
