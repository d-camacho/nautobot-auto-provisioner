# Installing the App in Nautobot

Here you will find detailed instructions on how to **install** and **configure** the App within your Nautobot environment.

---

## Prerequisites

1. The app relies on ```nautobot-golden-config``` and its associated dependencies.
2. It uses Golden Config's ```backup configs``` and ```intended configs``` as Git Repositories in Nautobot.
3. For help configuring these repositories, refer to the [Golden Config Documentation](https://docs.nautobot.com/projects/golden-config/en/latest/admin/install/#app-configuration).
4. The app is compatible with Nautobot 2.3.2 and higher and supports PostgreSQL and MySQL. Please check the [dedicated page](compatibility_matrix.md) for a full compatibility matrix and the deprecation policy.

---

## Installation Guide

**Auto Provisioner** can be installed from the [Python Package Index](https://pypi.org/) or locally. See the [Nautobot documentation](https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/installation/app-install/) for more details. The pip package name for this app is [`nautobot-auto-provisioner`](https://pypi.org/project/nautobot-auto-provisioner/).

#### Standard Install (non-Docker)

Install using pip:

```shell
pip install nautobot-auto-provisioner
```

To ensure Nautobot Auto Provisioner is automatically re-installed during future upgrades, create a file named `local_requirements.txt` (if not already existing) in the Nautobot root directory (alongside `requirements.txt`) and list the `nautobot-auto-provisioner` package:

```shell
echo nautobot-auto-provisioner >> local_requirements.txt
```

Once installed, the app needs to be enabled in your Nautobot configuration. The following block of code below shows the additional configuration required to be added to your `nautobot_config.py` file:

- Append `"nautobot_auto_provisioner"` to the `PLUGINS` list.
- Append the `"nautobot_auto_provisioner"` dictionary to the `PLUGINS_CONFIG` dictionary and override any defaults.

```python
# In your nautobot_config.py
PLUGINS = ["nautobot_auto_provisioner"]

# PLUGINS_CONFIG = {
#   "nautobot_auto_provisioner": {
#     ADD YOUR SETTINGS HERE
#   }
# }
```

Once the Nautobot configuration is updated, run the Post Upgrade command (`nautobot-server post_upgrade`) to run migrations and clear any cache:

```shell
nautobot-server post_upgrade
```

Then restart (if necessary) the Nautobot services which may include:

- Nautobot
- Nautobot Workers
- Nautobot Scheduler

```shell
sudo systemctl restart nautobot nautobot-worker nautobot-scheduler
```

#### Docker Compose Install

Follow these steps if you deploy your Nautobot instance uing Docker Compose:

Add the plugin to the project dependencies in ```pyproject.toml```

```bash
poetry add nautobot-auto-provisioner
```

Regenerate and lock dependencies:

```bash
poetry lock
poetry install
```

Update the Docker image:

```bash
invoke build
```

Start Nautobot:
```bash
invoke start
```
Or if you prefer debug mode:
```bash
invoke debug
```

Be sure to **update** the ```PLUGINS``` list in your ```nautobot_config.py```:

```python
PLUGINS = ["nautobot_auto_provisioner"]

# PLUGINS_CONFIG = {
#   "nautobot_auto_provisioner": {
#     ADD YOUR SETTINGS HERE
#   }
# }
```

## App Configuration

Current version does not require any additiona configurations.









