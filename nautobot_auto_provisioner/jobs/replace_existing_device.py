from django.db import transaction

from nautobot.apps.jobs import Job, StringVar, ObjectVar
from nautobot.dcim.models import Device, DeviceType, Platform
from nautobot.extras.models import GitRepository, Secret, SecretsGroup

from nautobot_auto_provisioner.utils import ConfigPusher, CredentialsHandler, GitRepoPathResolver

name = "Device Auto Provisioning"

class ReplaceExistingDevice(Job):
    device_to_replace = ObjectVar(
        model=Device,
        description="Select the device you are replacing"
    )
    replacement_device_type = ObjectVar(
        model=DeviceType,
        description="New device type. Warning, if new Device Type is different, other parameters might have to change (e.g. platform)",
        required=False
    )
    replacement_platform = ObjectVar(
        model=Platform,
        description="Platform for replacement device",
        required=False
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
    secret_group = ObjectVar(
        model=SecretsGroup,
        description="Secrets Group with username/password",
        required=True
    )

    class Meta:
        name = "Replace Existing Device"
        description = "Replace hardware while preserving device data"

    def run(
        self, 
        device_to_replace, 
        replacement_device_type, 
        replacement_platform, 
        serial_number, 
        repo_source, 
        secret_group
    ):
        self.logger.info(f"Starting replacement for device: {device_to_replace.name}")
        device = device_to_replace

        try:
            with transaction.atomic():
                # --- Update Device Attributes ---
                if replacement_device_type:
                    device.device_type = replacement_device_type
                    self.logger.info(f"  - Updated device type to: {replacement_device_type}")
                if replacement_platform:
                    device.platform = replacement_platform
                    self.logger.info(f"  - Updated platform to: {replacement_platform}")
                if serial_number:
                    device.serial = serial_number
                    self.logger.info(f"  - Updated serial number to: {serial_number}")

                device.validated_save()
                self.logger.info(f"Device attributes updated successfully.")

            # --- Resolve Git Repository Path ---
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
            self.logger.info(f"Pushing config to device: {device.name}")

            # Retrieve Secrets
            handler = CredentialsHandler(secret_group, logger=self.logger)
            username, password = handler.fetch_credentials()
            
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

            self.logger.info(f"Replacement and config push succeeded for {device.name}")
            return f"Replacement and config push succeeded for {device.name}"

        except ValueError as e:
            self.logger.critical(f"Input validation error: {e}")
            return f"Replacement failed: {e}"
        except RuntimeError as e:
            self.logger.critical(f"Runtime error: {e}")
            return f"Replacement failed: {e}"
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return f"Replacement failed due to unexpected error: {e}"
