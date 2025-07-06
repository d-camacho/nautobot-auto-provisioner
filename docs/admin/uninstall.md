# Uninstall the App from Nautobot

Here you will find any steps necessary to cleanly remove the App from your Nautobot environment.

## Database Cleanup

Prior to removing the app from the `nautobot_config.py`, run the following command to roll back any migration specific to this app.

```shell
nautobot-server migrate nautobot_auto_provisioner zero
```

## Remove App configuration

Remove the configuration you added in `nautobot_config.py` from `PLUGINS` & `PLUGINS_CONFIG`.

## Uninstall the package

#### Standard Install (non-Docker)

```bash
pip3 uninstall nautobot-auto-provisioner
```

You also have to remove it from the ```local_requirements.txt```.

#### Docker Compose Install

To remove an app (i.e., a dependency) from your pyproject.toml using Poetry, you can use:

```bash
poetry remove nautobot-auto-provisioner
```
