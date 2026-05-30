# Linux Recovery System

The Linux Recovery System is a command-line utility designed to repair Linux installations that fail to boot or are otherwise corrupted.

## Overview

This tool provides an automated recovery workflow for a mounted Linux installation, including partition discovery, root and EFI mounting, chroot environment preparation, distribution detection, and GRUB reinstallation.

## Features

- Enumerates available block devices and partitions using `lsblk`.
- Mounts the target Linux root partition to `/mnt`.
- Supports optional separate EFI partition mounting at `/mnt/boot/efi`.
- Configures a chroot-ready environment by bind mounting `/dev`, `/dev/pts`, `/proc`, `/sys`, and `/run` into `/mnt`.
- Detects the distribution under `/mnt` by parsing `/mnt/etc/os-release`.
- Reinstalls and updates GRUB for Debian/Ubuntu, Fedora, and Arch Linux systems.

## Project Structure

- `main.py`: application entrypoint. Validates root privileges and invokes the recovery workflow.
- `core/scanning_files.py`: implements partition listing, mounting logic, chroot preparation, distribution detection, and GRUB repair.

## Usage

Run the tool with elevated privileges:

```bash
sudo python3 main.py
```

Follow the prompts to:

1. Select the root partition of the target system.
2. Optionally provide a separate EFI partition if one exists.
3. Allow the utility to mount the filesystem, prepare the chroot environment, and reinstall the bootloader.

## Notes

- Use this utility for recovery operations only and exercise caution when mounting and modifying system partitions.
- Required system utilities include: `lsblk`, `mount`, `umount`, `chroot`, `grub-install`, `update-grub`, and `grub2-install`.
- The current implementation is primarily targeted at Debian/Ubuntu, Fedora, and Arch Linux distributions.
