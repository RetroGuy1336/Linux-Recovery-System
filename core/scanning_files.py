import subprocess
import os
import time
import pathlib
import re

def clear():
    subprocess.run(['clear'])

def detect_partition():
    result = subprocess.run(["lsblk", "-f"], capture_output=True, text=True)
    print(result.stdout)


def mount_sys():
    """Mount the target root (and optionally EFI) and return the root device path.

    Returns the root partition string on success, or None on failure.
    """
    try:
        root = input("Root partition (ex: /dev/sda2): ").strip()

        if not root.startswith("/dev/"):
            print("Invalid partition format!")
            return None

        # mount root first
        result = subprocess.run([
            "sudo", "mount", root, "/mnt"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("Root mount error:", result.stderr)
            return None

        efi = input("Do you have a separate EFI partition? [Y/N] ").lower().strip()

        if efi == 'y':
            efi_part = input("EFI partition (ex: /dev/sda1): ").strip()
            os.makedirs("/mnt/boot/efi", exist_ok=True)

            subprocess.run(
                ["sudo", "mount", efi_part, "/mnt/boot/efi"],
                capture_output=True,
                text=True
            )

        print("System mounted successfully!")
        return root

    except Exception as e:
        print("Error:", e)
        return None
    
def detect_system():
    if os.path.exists("/mnt/etc/os-release"):
        print("Linux installation detected!")
        return True
    else:
        print("No Linux system found in /mnt")
        return False

def chroot():
    print("Preparing chroot environment...")

    mounts = ["/dev", "/dev/pts", "/proc", "/sys", "/run"]

    for m in mounts:
        target = f"/mnt{m}"
        os.makedirs(target, exist_ok=True)

        result = subprocess.run(
            ["sudo", "mount", "--bind", m, target],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Failed to mount {m}: {result.stderr}")
            return False

    print("Entering chroot...")
    subprocess.run(["sudo chroot /mnt /bin/bash"], text=True, shell=True)
    return True

def detect_distro():
    try:
        with open("/mnt/etc/os-release") as f:
            data = f.read().lower()

        if "ubuntu" in data:
            return "ubuntu"
        elif "fedora" in data:
            return "fedora"
        elif "arch" in data:
            return "arch"
        else:
            return "unknown"

    except FileNotFoundError:
        return None

def scanning_files():
    print("Starting the Linux scan errors...")
    time.sleep(3.22)
    detect_partition()
    root = mount_sys()
    if root:
        if detect_system():
            chroot()
            distro = detect_distro()
            if distro:
                print(f"Detected system: {distro}")
                if distro == "ubuntu":
                    grub_path = pathlib.Path("/mnt/boot/grub")
                    if not grub_path.exists():
                        print("GRUB not found")
                        print("Trying to install GRUB")
                        # disk is root without partition number
                        disk = re.sub(r"\d+$", "", root)
                        subprocess.run(["sudo", "grub-install", disk])
                        subprocess.run(["sudo", "update-grub"])
                    else:
                        print("GRUB appears to be installed")
            else:
                print("Could not detect Linux system")
    else:
        print("Failed to mount the system")

scanning_files()