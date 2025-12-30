"""App declaration for nautobot_auto_provisioner."""

# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

from nautobot.apps import NautobotAppConfig

__version__ = metadata.version(__name__)


class NautobotAutoProvisionerConfig(NautobotAppConfig):
    """App configuration for the nautobot_auto_provisioner app."""

    name = "nautobot_auto_provisioner"
    verbose_name = "Nautobot Auto Provisioner"
    version = __version__
    author = "Dwayne Camacho"
    description = "Easily provision new or existing devices based on pre-defined intended configurations."
    base_url = "https://github.com/d-camacho/nautobot-auto-provisioner"
    required_settings = []
    default_settings = {}
    docs_view_name = "plugins:nautobot_auto_provisioner:docs"
    searchable_models = []


config = NautobotAutoProvisionerConfig  # pylint:disable=invalid-name
