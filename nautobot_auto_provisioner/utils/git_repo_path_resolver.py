import os
from jinja2 import Template
from nautobot.extras.models import GitRepository

class GitRepoPathResolver:
    """
    Resolves the local filesystem path to a device's configuration file based on a GitRepository
    and pre-defined path templates (used by Golden Config or custom repos).
    """

    REPO_PATH_MAPPINGS = {
        "intended_configs": "{{obj.location.name}}/{{obj.name}}.intended_cfg",
        "backup_configs": "{{obj.location.name}}/{{obj.name}}.cfg",
    }

    def __init__(self, git_repo_obj: GitRepository, repo_name_key: str, logger=None):     
        self.git_repo_obj = git_repo_obj
        self.repo_name_key = repo_name_key
        self.logger = logger

    def get_local_path(self, nautobot_object) -> str:
        try:
            base_repo_path = self.git_repo_obj.filesystem_path
            path_template = self.REPO_PATH_MAPPINGS.get(self.repo_name_key)

            if not path_template:
                raise ValueError(f"No path template found for repo: {self.repo_name_key}")

            rendered_path = Template(path_template).render(obj=nautobot_object)
            full_path = os.path.join(base_repo_path, rendered_path)

            if self.logger:
                self.logger.debug(f"Resolved Git repo path: {full_path}")

            return full_path

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error resolving Git repo path: {e}")
            raise
