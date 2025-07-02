# cat __init__.py 
from nautobot.apps.jobs import register_jobs
from .baseline_existing_device import BaselineExistingDevice
from .replace_existing_device import ReplaceExistingDevice
from .provision_new_device import ProvisionNewDevice


register_jobs(
    BaselineExistingDevice,
    ReplaceExistingDevice,
    ProvisionNewDevice
)