# Linux Recovery System
A simple and automated Linux recovery tool designed to repair GRUB bootloader issues directly from a Live USB environment.

This project was created to simplify the recovery process for broken Linux installations, especially after dual-boot problems, GRUB corruption, or incorrect bootloader installation.

## 🚀 Features
- Optional EFI partition mounting
- Chroot environment preparation
- Linux distribution detection
- Automatic GRUB reinstallation
- Support for Debian/Ubuntu-based systems
- Early structure for Fedora and Arch support

## 🛠 Supported Distributions
Currently fully supported:
Ubuntu
Linux Mint
Debian
Pop!_OS
Zorin OS

Planned support:
Fedora
Arch Linux

## 🧠 Requirements
- Live Linux environment (Mint, Ubuntu, etc.)
- Root privileges
- Python 3

## ▶️ Usage
Boot into a Live USB environment and run:
```sudo python3 main.py```
Follow the on-screen instructions to select the root partition.

## ⚠️ Warning
This tool modifies the system bootloader.
Make sure you select the correct root partition and disk device before proceeding.
The developer is not responsible for data loss caused by incorrect usage.

## 🎯 Project Goal

The goal of this project is to create a universal Linux boot repair utility that works across major distributions with minimal user input.
Future improvements include:

- Full automatic partition detection
- BIOS / UEFI automatic detection
- Full multi-distro GRUB repair
- Interactive terminal interface
- Advanced recovery features
