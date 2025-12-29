# Getting Started

This document provides additional guidance and troubleshooting tips for using the **Auto Provisioner** Nautobot App.

---

## Installing the App

To install the app, please follow the instructions detailed in the [Installation Guide](../admin/install.md).

---

## How to Use Each Job

> [!IMPORTANT]  
> For all use cases, it is assumed that **Nautobot has IP connectivity with the target device** being provisioned. Ensure devices are reachable before running any jobs.

### Baseline Existing Device

Use this job to push a full configuration to an existing device.  
This can pull either from:
- **Backup Config Repo** – to revert a device to its last-known-good state
- **Intended Config Repo** – to apply new enterprise-wide updates or changes

---

### Replace Existing Device

Use when replacing hardware while retaining all device metadata.  

- Preserves role, location, IPs, etc. and transfers to the new device. 
- Prompts for optional updates (e.g. serial number). Although not required to run the job, these fields are offered to ensure accuracy of data stored in Nautobot. 

---

### Provision New Device

Use this job to add a brand-new device to Nautobot and push a config.  
You’ll provide:
- Device metadata (hostname, platform, etc.). Because hostnames are entered as `strings` at this point, ensure that the entry matches the hostname stored in the repo as this entry is used to look for the file (including the location) i.e. `Los Angeles/lax-edg-r1`.
- Management interface and IP. This job relies on Nautobot object dependencies so some attributes must be configured first e.g. `Prefix` where the IP Address is being derived.
- Git repository to pull config from

> [!TIP]  
> To simplify provisioning, consider using technologies like **DHCP reservations**, **zero-touch provisioning**, or **DMVPN** to establish initial IP connectivity. Let Auto Provisioner handle the rest.

---

## Secrets & Authentication

Auto Provisioner uses [Nautobot Secrets Groups](https://docs.nautobot.com/projects/core/en/stable/models/extras/secretsgroup/) to retrieve credentials used for device connections.

Each Secrets Group should include:
- A **username** secret (e.g. secret_type: `username`)
- A **password** secret (e.g. secret_type: `password`)

---

## Common Errors & Troubleshooting

| Error Message | Description | Suggested Fix |
|---------------|-------------|----------------|
| `Error resolving Git repo path` | Couldn't match the filesystem path based on provided info e.g. repo, hostname, location, and file name. | GitRepoPathResolver combines base repo path and selected device to find the exact path in this example format: "/opt/nautobot/git/intended_configs/" + "{{obj.location.name}}/{{obj.name}}".intended_cfg. Double check location and name stored in the repo to make sure it matches entry in Nautobot. |
| `Secret must included both username and password.` | Misconfigured or missing element in Secrets Group | Ensure your Secrets Group contains both username and password |
| `Authentication Failed` | Possible mismatch of credentials stored in Secrets Group and the device itself | Verify that credentials match. Double check the secret_type as well e.g. "Generic", "SSH", etc. |
| `Device unreachable` | Nautobot can’t connect to the device | Verify IP, interface assignment, and routing between Nautobot and device |
| `Interface not found` | Interface name doesn't match Nautobot object | Use full or abbreviated name (e.g., `Gig0/0` or `GigabitEthernet0/0`) correctly |
