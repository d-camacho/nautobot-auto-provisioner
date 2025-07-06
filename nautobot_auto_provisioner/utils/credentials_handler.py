from nautobot.extras.models import SecretsGroup
from nautobot.extras.choices import SecretsGroupSecretTypeChoices

class CredentialsHandler:
    def __init__(self, secrets_group, logger=None, obj=None):
        self.secrets_group = secrets_group
        self.logger = logger
        self.obj = obj
        self.username = None
        self.password = None

    def fetch_credentials(self):
        username = None
        password = None

        for assoc in self.secrets_group.secrets.through.objects.filter(secrets_group=self.secrets_group):
            if assoc.secret_type == SecretsGroupSecretTypeChoices.TYPE_USERNAME and not username:
                username = assoc.secret.get_value(obj=self.obj)
            elif assoc.secret_type == SecretsGroupSecretTypeChoices.TYPE_PASSWORD and not password:
                password = assoc.secret.get_value(obj=self.obj)

        if not username or not password:
            raise ValueError(
                f"SecretsGroup '{self.secrets_group.name}' must include both a username and password secret."
            )

        self.username = username
        self.password = password

        return self.username, self.password
