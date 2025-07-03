from netaddr import IPNetwork, IPAddress as NetIPAddress
from django.db import transaction

from nautobot.apps.jobs import Job, StringVar, ObjectVar
from nautobot.dcim.models import Device, DeviceType, Platform
from nautobot.extras.models.roles import Role
from nautobot.dcim.models.locations import Location
from nautobot.extras.models import Status
from nautobot.ipam.models import IPAddress, Namespace, Prefix
from nautobot.dcim.models.device_components import Interface
from nautobot.extras.models import GitRepository, Secret

from nautobot_auto_provisioner.utils import ConfigPusher, GitRepoPathResolver




name = "Device Auto Provisioning"

ACTIVE_STATUS = Status.objects.get(name="Active")

def resolve_interface_name(device, user_input):
    shorthand_map = {
        "gig": "GigabitEthernet",
        "fa": "FastEthernet",
        "eth": "Ethernet",
        "mgmt": "Management",
        "lo": "Loopback",
        "se": "Serial",
        "te": "TenGigabitEthernet"
    }

    user_input = user_input.lower()

    for short, full in shorthand_map.items():
        if user_input.startswith(short):
            normalized_name = user_input.replace(short, full, 1)
            return device.interfaces.filter(name__iexact=normalized_name).first()

    return device.interfaces.filter(name__iexact=user_input).first()


class ProvisionNewDevice(Job):
    device_name = StringVar(
        description="Hostname for the device. Note: Name must match name in repo", 
        required=True
    )
    location = ObjectVar(
        model=Location, 
        description="Location to assign", 
        required=True
    )
    device_type = ObjectVar(
        model=DeviceType, 
        description="Device type", 
        required=True
    )
    device_role = ObjectVar(
        model=Role, 
        description="Device role", 
        required=True
    )
    platform = ObjectVar(
        model=Platform, 
        required=True)
    ip_address = StringVar(
        description="Enter IP Address for device e.g. 192.168.1.1/24. This IP will be used to connect to the device", 
        required=True
    )
    interface_name = StringVar(
        description="Interface to use for provisioning (e.g., Mgmt0, Gig0/0)",
        required=True,
    )
    namespace = ObjectVar(
        model=Namespace,
        description="Namespace where the IP and Prefix reside.",
        required=True
    )
    serial_number = StringVar(
        description="Serial Number of the replacement device",
        required=False
    )
    repo_source = ObjectVar(
        model=GitRepository,
        description="Select the Git Repo to pull configurations from (e.g. intended_configs or backup_configs)",
        required=True
    )
    username_secret = ObjectVar(
        model=Secret,
        description="Secret containing the device username",
        required=True
    )
    password_secret = ObjectVar(
        model=Secret,
        description="Secret containing the device password",
        required=True
    )
        
    class Meta:
        name = "Provision New Device"
        description = "Provision a new device"
        
    def run(
            self, 
            device_name, 
            location, 
            device_type, 
            device_role, 
            platform, 
            serial_number,
            ip_address, 
            interface_name, 
            namespace,
            repo_source,
            username_secret,
            password_secret
    ):
        try:
            with transaction.atomic():
                if Device.objects.filter(name=device_name).exists():
                    self.logger.error(f"Device {device_name} already exists. Please use 'Replace Existing Device' job.")
                    return f"Device {device_name} already exists."
            
                else:
                    self.logger.debug(f"Creating {device_name}")
                    device = Device.objects.create(
                        name=device_name,
                        location=location,
                        device_type=device_type,
                        role=device_role,
                        platform=platform,
                        status=ACTIVE_STATUS,
                        serial=serial_number
                    )
                    device.validated_save()            

                # --- Find or Create IP Address ---
                self.logger.info(f"Finding or creating IP Address to assign to device...")  
                # Parse the input and normalize it
                ip_net = IPNetwork(ip_address)        # includes the CIDR e.g. 10.0.1.0/30
                ip_only = NetIPAddress(ip_net.ip)     # Just the IP part

                # Find parent prefix using both IP and namespace
                parent_prefix = Prefix.objects.filter(
                    namespace=namespace,
                    network__net_contains_or_equals=ip_only
                ).first()

                if not parent_prefix:
                    self.logger.error(f"No matching parent prefix found for {ip_only} in namespace {namespace}.")
                    return f"Failed: No parent prefix found for {ip_only} in namespace {namespace}."

                # Check if IP exists under this prefix
                ip_address_obj = IPAddress.objects.filter(address=str(ip_net), parent=parent_prefix).first()

                if ip_address_obj:
                    self.logger.debug(f"{ip_address_obj} already exists under {namespace}. Will re-use.")
                else:
                    ip_address_obj = IPAddress.objects.create(
                        address=str(ip_net),
                        parent=parent_prefix,
                        status=ACTIVE_STATUS,
                    )
                    ip_address_obj.validated_save()
                    self.logger.info(f"Created IP {ip_address_obj.address} under {namespace}.")

                    
                # --- Assign IP to interface and assign the IP as Primary IPv4 of device ---
                try:
                    interface = resolve_interface_name(device, interface_name)
                    self.logger.debug(f"Assigning {ip_address_obj} to {interface}")
                    interface.ip_addresses.add(ip_address_obj)
                    device.primary_ip4=ip_address_obj
                    device.validated_save()
                    self.logger.info(f"Successfuly assigned {ip_address_obj} to {interface}")
                    self.logger.info(f"{ip_address_obj} is now the primary_ipv4 for {device.name}")
                except Interface.DoesNotExist:
                    self.logger.error(f"Interface {interface_name} not found on {device.name}")
                    return f"Failed: Interface {interface_name} not found. Check the format e.g. GigabitEthernet, Gig, etc."
                        

                # --- Config Push Phase ---
                self.logger.info(f"Device {device_name} created successfully. Preparing {device_name} for provisioning.")
                            
            
                self.logger.info(f"Attempting to resolve Git repo path...")
                resolver = GitRepoPathResolver(
                        git_repo_obj=repo_source,
                        repo_name_key=repo_source.name,
                        logger=self.logger
                    )
                config_file_path = resolver.get_local_path(device)
                self.logger.debug(f"Resolved repo path: {config_file_path}")

                if not config_file_path:
                    raise RuntimeError("Config path resolution failed.")
                
                # --- Push Configuration ---
                # Retrieve Secrets
                username = username_secret.get_value()
                password = password_secret.get_value()

                if not username:
                    raise ValueError("Username secret is empty.")
                if not password:
                    raise ValueError("Password secret is empty.")
                
                self.logger.info(f"Pushing config to device: {device.name}")
                pusher = ConfigPusher(
                    device=device,
                    config_path=config_file_path,
                    logger=self.logger,
                    username=username,
                    password=password
                )

                push_result = pusher.push()

                if not push_result:
                    raise RuntimeError(f"Config push failed for {device.name}. Rolling back any changes.")

                self.logger.info(f"New device {device.name} successfully provisioned!")
                return f"New device {device.name} successfully provisioned!"

        except ValueError as e:
            self.logger.critical(f"Input validation error: {e}")
            return f"Replacement failed: {e}"
        except RuntimeError as e:
            self.logger.critical(f"Runtime error: {e}")
            return f"Replacement failed: {e}"
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return f"Replacement failed due to unexpected error: {e}"
            
        except Exception as e:
            self.logger.error(f"Failed to resolve Git repo path: {e}")
            return f"Failed during repo path resolution: {e}"

        
        


        
