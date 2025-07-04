from nautobot.apps.jobs import Job, ObjectVar
from nautobot.dcim.models import Device
from nautobot.extras.models import Secret, SecretsGroup, GitRepository

from nautobot_auto_provisioner.utils import ConfigPusher, CredentialsHandler, GitRepoPathResolver 

name = "Device Auto Provisioning"

class BaselineExistingDevice(Job):
    device_to_baseline = ObjectVar(
        model=Device,
        description="Select device to baseline"
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
        name = "Baseline Device"
        description = "Use this job to push an entire updated configs"

    def run(self, device_to_baseline, repo_source, secret_group):
        device = device_to_baseline
        self.logger.info(f"Baselining {device.name} configs.")

        try:
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
