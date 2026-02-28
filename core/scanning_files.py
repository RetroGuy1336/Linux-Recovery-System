import subprocess
import os
import time
import pathlib
import re

def clear_screen():
    subprocess.run(['clear'])

def list_partitions():
    print("--- Current Partitions ---")
    result = subprocess.run(["lsblk", "-o", "NAME,FSTYPE,SIZE,MOUNTPOINT,LABEL"], capture_output=True, text=True)
    print(result.stdout)

def mount_system():
    """Mounts the target root and optional EFI partition."""
    try:
        root_part = input("Enter the Root partition (exemple: /dev/sda2): ").strip()

        if not os.path.exists(root_part):
            print(f"Error: Partition {root_part} not found.")
            return None

        # Mount root to /mnt
        result = subprocess.run(["sudo", "mount", root_part, "/mnt"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Mount error: {result.stderr}")
            return None

        # Check for EFI
        has_efi = input("Is there a separate EFI partition? [y/N]: ").lower().strip()
        if has_efi == 'y':
            efi_part = input("Enter the EFI partition (e.g., /dev/sda1): ").strip()
            os.makedirs("/mnt/boot/efi", exist_ok=True)
            subprocess.run(["sudo", "mount", efi_part, "/mnt/boot/efi"])

        print("System mounted successfully at /mnt.")
        return root_part

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def prepare_chroot_environment():
    """Binds necessary system directories for GRUB to work inside chroot."""
    print("Preparing virtual filesystems...")
    mounts = ["/dev", "/dev/pts", "/proc", "/sys", "/run"]
    for m in mounts:
        target = f"/mnt{m}"
        subprocess.run(["sudo", "mount", "--bind", m, target])

def detect_distro():
    """Detects the Linux distribution by looking inside the mounted /mnt."""
    os_release_path = "/mnt/etc/os-release"
    if not os.path.exists(os_release_path):
        return None
    
    with open(os_release_path) as f:
        data = f.read().lower()
        if "ubuntu" in data: return "ubuntu"
        if "fedora" in data: return "fedora"
        if "arch" in data: return "arch"
    return "unknown"

def run_chroot_command(command):
    """Executes a command inside the chroot environment without blocking."""
    full_cmd = f"sudo chroot /mnt {command}"
    print(f"Running in chroot: {command}")
    return subprocess.run(full_cmd, shell=True)

def scanning_files():
    clear_screen()
    print("=== Linux System Repair Tool ===")
    list_partitions()
    
    root_device = mount_system()
    if not root_device:
        return

    distro = detect_distro()
    if not distro:
        print("No Linux installation detected in /mnt. Unmounting...")
        subprocess.run(["sudo", "umount", "-R", "/mnt"])
        return

    print(f"Detected System: {distro.capitalize()}")
    prepare_chroot_environment()

    # Automating the GRUB repair
    if distro == "ubuntu":
        # Extract disk name from partition (e.g., /dev/sda2 -> /dev/sda)
        disk = re.sub(r"\d+$", "", root_device)
        
        print(f"Reinstalling GRUB on {disk}...")
        # We run commands directly. No 'bash' blocking the script.
        run_chroot_command(f"grub-install {disk}")
        run_chroot_command("update-grub")
        
        print("\nRepair finished! You can now reboot.")
    else:
        print(f"Auto-repair for {distro} is not implemented yet.")

    # Cleanup: Optional but recommended
    # subprocess.run(["sudo", "umount", "-R", "/mnt"])

scanning_files()