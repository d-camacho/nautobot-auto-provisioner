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
    description = "Nautobot Auto Provisioner."
    base_url = "auto-provisioner"
    required_settings = []
    min_version = "2.3.2"
    max_version = "2.9999"
    default_settings = {}
    caching_config = {}
    docs_view_name = "plugins:nautobot_auto_provisioner:docs"


config = NautobotAutoProvisionerConfig  # pylint:disable=invalid-name
