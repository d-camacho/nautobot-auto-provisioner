from nautobot.apps.jobs import Job, StringVar, ObjectVar, IPAddressVar, register_jobs
from nautobot.dcim.models import Device, DeviceType, Platform
from nautobot.extras.models.roles import Role
from nautobot.dcim.models.locations import Location
from nautobot.extras.models import Status

name = "Device Auto Provisioning"

ACTIVE_STATUS = Status.objects.get(name="Active")

class ProvisionNewDevice(Job):
    device_name = StringVar(description="Hostname for the device")
    location = ObjectVar(model=Location, description="Location to assign")
    device_type = ObjectVar(model=DeviceType, description="Device type")
    device_role = ObjectVar(model=Role, description="Device role")
    platform = ObjectVar(model=Platform, required=True) # changed to required because pushing configs relies on network driver based on platform 

    class Meta:
        name = "Provision New Device"
        description = "Provision a new device"

    def run(self, device_name, location, device_type, device_role, platform):
        if Device.objects.filter(name=device_name).exists():
            self.logger.error(f"Device {device_name} already exists. Use 'Replace Existing Device' job.")
            return f"Device {device_name} already exists."
    
        else:
            device = Device.objects.create(
                name=device_name,
                location=location,
                device_type=device_type,
                role=device_role,
                platform=platform,
                status=ACTIVE_STATUS,
            )
            device.validated_save()
            self.logger.debug(f"Created device {device.name}")
            return f"Device {device_name} created successfully."
        


        


