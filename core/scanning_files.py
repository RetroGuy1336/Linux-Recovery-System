import subprocess
import os
import time
import pathlib
import json
import re

def clear():
    subprocess.run(['clear'])

def detect_partition():
    result = subprocess.run(["lsblk", "-f"], capture_output=True, text=True)
    print(result.stdout)


def mount_sys():
    try:
        root = input("Root partition (ex: /dev/sda2): ").strip()

        if not root.startswith("/dev/"):
            print("Invalid partition format!")
            return False

        # Monta root primeiro
        result = subprocess.run(
            ["sudo", "mount", root, "/mnt"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("Root mount error:", result.stderr)
            return False

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
        return True

    except Exception as e:
        print("Error:", e)
        return False
    
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
    subprocess.run(["sudo", "chroot", "/mnt", "/bin/bash"])
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

def main():  
    print("Starting the Linux scan errors...")
    time.sleep(3.22)
    detect_partition()
    if mount_sys():
        if detect_system():
            chroot()
            distro = detect_distro()
            if distro:
                print(f"Detected system: {distro}")
                if distro == "ubuntu":
                    root_partition = pathlib.Path("/")
                    grub_file = pathlib.glob("***/grub")
                    for find_file in grub_file:
                        print(find_file)
                        if "/mnt/boot/grub" not in grub_file:
                            print("GRUB didn't find")
                            print("Trying to install GRUB")
                            disk = re.sub(r'\d+$', '', mount_sys.root())
                            subprocess.run([f"grub-install {disk}"])
                            subprocess.run("update-grub")
            else:
                while True:
                    print("Could not detect Linux system")
                    break
    else:
        print("Failed to mount the system")
if __name__ == "__main__":
    main()