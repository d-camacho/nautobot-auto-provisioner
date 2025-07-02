from nautobot.apps.jobs import Job, ObjectVar
from nautobot.dcim.models import Device
from nautobot.extras.models import Secret, GitRepository

from nautobot_auto_provisioner.utils import ConfigPusher, GitRepoPathResolver

name = "Device Auto Provisioning"

class BaselineExistingDevice(Job):
    device_to_baseline = ObjectVar(
        model=Device,
        description="Device to baseline."
    )
    repo_source = ObjectVar(
        model=GitRepository,
        description="Select the Git Repo to pull configurations from (e.g. intended_configs or backup_configs).",
        required=True
    )
    username_secret = ObjectVar(
        model=Secret,
        description="Secret containing the device connection username.",
        required=True
    )
    password_secret = ObjectVar(
        model=Secret,
        description="Secret containing the device connection password.",
        required=True
    )

    class Meta:
        name = "Baseline Device by pushing updated configs."
        description = "Use this job to simply push updated configs."

    def run(self, device_to_baseline, repo_source, username_secret, password_secret):
        device = device_to_baseline
        self.logger.info(f"Baselining {device.name} configs.")

        try:
            # Retrieve Secrets
            username = username_secret.get_value()
            password = password_secret.get_value()

            if not username:
                raise ValueError("Username secret is empty.")
            if not password:
                raise ValueError("Password secret is empty.")            

            # --- Resolve Git Repository Path ---
            resolver = GitRepoPathResolver(
                git_repo_obj=repo_source,
                repo_name_key=repo_source.name,
                logger=self.logger
            )
            config_file_path = resolver.get_local_path(device)

            if not config_file_path:
                raise RuntimeError("Config path resolution failed.")

            # --- Push Configuration ---
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
                raise RuntimeError(f"Config push failed for {device.name}.")

            self.logger.info(f"Config push succeeded for {device.name}")
            return f"Config push succeeded for {device.name}"

        except ValueError as e:
            self.logger.critical(f"Input validation error: {e}")
            return f"Config update failed: {e}"
        except RuntimeError as e:
            self.logger.critical(f"Runtime error: {e}")
            return f"Config update failed: {e}"
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return f"Config update failed due to unexpected error: {e}"
