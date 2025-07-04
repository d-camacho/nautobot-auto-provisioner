from nautobot.extras.models import SecretsGroup
from nautobot.extras.secrets.exceptions import SecretError

class CredentialsHandler:
    def __init__(self, secrets_group, logger=None, obj=None):
        self.secrets_group = secrets_group
        self.logger = logger
        self.obj = obj
        self.username = None
        self.password = None

    def fetch_credentials(self):
        try:
            self.username = self.secrets_group.get_secret_value("Generic", "username", obj=self.obj)
            self.password = self.secrets_group.get_secret_value("Generic", "password", obj=self.obj)
        except SecretError as e:
            if self.logger:
                self.logger.critical(f"Error retrieving secrets: {e}")
            raise

        if not self.username or not self.password:
            raise ValueError("Username or password is empty.")

        return self.username, self.password
