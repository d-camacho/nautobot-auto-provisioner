# Nautobot Auto Provisioner

<p align="center">
  <img src="https://github.com/d-camacho/testing_readme/blob/main/images/auto_prov_full_logo.png "class="logo" height="200px">
  <br>
  An <a href="https://networktocode.com/nautobot-apps/">App</a> for <a href="https://nautobot.com/">Nautobot</a>.
</p>

## Overview

**Auto Provisioner** is a Nautobot Plugin that enables you to push configurations to both new and existing devices. You can select a Git repository from Nautobot Git Repositories—currently supported with the backup or intended config repository managed by Golden Config—as the source for your configurations.

This project was inspired after the successful completion of [#100DaysOfNautobot](https://go.networktocode.com/100-days-of-nautobot).

Auto Provisioner provides three core Nautobot Jobs, each tailored to a specific operational use case.

![Auto Provisioner Jobs](images/all_jobs.png)

---

## Use Cases

This plugin addresses the following use cases:

### Use Case 1: Baseline Existing Device (from Backup)

**Baseline Existing Device Job** lets users push an entire configuration to a selected device to restore it to a known-good state. In dynamic environments where changes are made to support temporary operational needs, this job helps eliminate configuration drift by reverting the device to its last-known-good backup stored in the repo.

![Baseline Existing Device](images/baseline_job.png)

### Use Case 2: Baseline Existing Device (from Intended)

The **same job** can also be used to push newly generated **intended configurations**. For example, if your organization rolls out a new security standard or feature update, you can use this job to apply those changes to the device using your intent-based templates from the intended config repository.

### Use Case 3: Replace Existing Device

The **Replace Existing Device Job** is designed for situations where hardware must be replaced—whether due to failure, upgrade, or lifecycle refresh. This job retains all existing metadata in Nautobot (like role, location, IP, etc.) and applies it to the new device. It also allows for updates to attributes like device type and serial number, ensuring that your source of truth remains accurate.

![Replace Existing Device](images/replace_existing.png)

### Use Case 4: Provision New Device

**Provision New Device Job** enables users to create and provision a completely new device in Nautobot. The job prompts for required metadata (like hostname, IP address, and interface), creates the device object, and then pushes the appropriate configuration from the selected repository.

![Provision New Device](images/provision_new.png)


---

## Installing the App in Nautobot

### Prerequisites

1. The app relies on ```nautobot-golden-config``` and its associated dependencies.
2. It uses Golden Config's ```backup configs``` and ```intended configs``` as Git Repositories in Nautobot.
3. For help configuring Git Repositories, refer to the [Golden Config Documentation](https://docs.nautobot.com/projects/golden-config/en/latest/admin/install/#app-configuration).

### Install Guide

**Auto Provisioner** is Python package published in [pypi.org/project/nautobot-auto-provisioner](https://pypi.org/project/nautobot-auto-provisioner/).

#### Standard Install (non-Docker)

Install using pip:

```bash

pip install nautobot-auto-provisioner
```

After installation, **add** the plugin to the ```PLUGINS``` list in your ```nautobot_config.py```:

```python
PLUGINS = ["nautobot_auto_provisioner"]
```

Restart the Nautobot service.

To ensure Nautobot Auto Provisioner is automatically reinstalled during upgrades, **append** ```nautobot-auto-provisioner``` to your instance's ```requirements.txt```.

#### Docker Compose Install

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
```

## Feedback

All feedbacks are welcome! This project began as part of a Nautobot learning journey and demonstrates key concepts like Nautobot Job creation, class-based approach, and plugin development. Open a topic under **Discussion** to share your ideas or ask questions.

Let's learn Nautobot together!