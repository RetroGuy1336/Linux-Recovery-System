import subprocess
import os
import re


def clear_screen():
    subprocess.run(["clear"])


def list_partitions():
    print("=== Available Partitions ===")
    result = subprocess.run(
        ["lsblk", "-o", "NAME,FSTYPE,SIZE,MOUNTPOINT,LABEL"],
        capture_output=True,
        text=True
    )
    print(result.stdout)


def mount_system():
    try:
        mount_system_info = input("Enter the ROOT partition (e.g. /dev/sda2): ").strip()

        if not os.path.exists(mount_system_info):
            print(f"[!] Partition not found: {mount_system_info}")
            return None

        print(f"[+] Mounting {mount_system_info} to /mnt...")
        result = subprocess.run(
            ["mount", mount_system_info, "/mnt"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"[!] Mount error: {result.stderr}")
            return None

        efi_partition = None
        has_efi = False

        efi_mount_system_info = input(
            "Is there a separate EFI partition? [y/N]: "
        ).lower().strip()

        if efi_mount_system_info == "y":
            efi_partition = input(
                "Enter the EFI partition (e.g. /dev/sda1): "
            ).strip()

            os.makedirs("/mnt/boot/efi", exist_ok=True)

            subprocess.run(["mount", efi_partition, "/mnt/boot/efi"])

            has_efi = True

        print("[✔] System mounted successfully.")

        return {
            "mount_system_info": mount_system_info,
            "has_efi": has_efi,
            "efi_partition": efi_partition
        }

    except Exception as e:
        print(f"[!] Unexpected error while mounting: {e}")
        return None


def prepare_chroot():
    """
    Bind required virtual filesystems for chroot operations.
    """
    print("[+] Preparing chroot environment...")
    for fs in ["/dev", "/dev/pts", "/proc", "/sys", "/run"]:
        target = f"/mnt{fs}"
        os.makedirs(target, exist_ok=True)
        subprocess.run(["mount", "--bind", fs, target])


def detect_distro():
    """
    Detects the Linux distribution from /etc/os-release.
    """
    os_release = "/mnt/etc/os-release"

    if not os.path.exists(os_release):
        return None

    with open(os_release, "r") as f:
        data = f.read().lower()

    if "debian" in subprocess.run(f"grep '^ID=' /etc/os-release | cut -d= -f2") or "ubuntu" in subprocess.run(f"grep '^ID=' /etc/os-release | cut -d= -f2"):
        return "debian_based"

    if "fedora" in subprocess.run(f"grep '^ID=' /etc/os-release | cut -d= -f2"):
        return "fedora_based"

    if "arch" in subprocess.run(f"grep '^ID=' /etc/os-release | cut -d= -f2"):
        return "arch_based"

    else:
        return "unknown"


def run_in_chroot(command):
    """
    Executes a command inside the mounted system using chroot.
    """
    print(f"[chroot] {command}")
    return subprocess.run(
        ["chroot", "/mnt"] + command.split(),
        text=True
    )

def installing_grub():
    mount_system_info = mount_system()
    distro = detect_distro()
    efi_partition = mount_system_info["has_efi"]
    not_efi_partition = mount_system_info["root_partition"]

    disk = re.sub(r"p?\d+$", "", mount_system_info)
    print(f"[+] Reinstalling GRUB on {disk}...")

    if distro == "debian_based":
        if not_efi_partition:
            print(f"[+] Reinstalling GRUB on {disk}...")

            run_in_chroot(f"grub-install {disk}")
            run_in_chroot("update-grub")
        elif efi_partition:
            run_in_chroot("grub-install \
    --target=x86_64-efi \
    --efi-directory=/boot/efi \
    --bootloader-id=GRUB")
            run_in_chroot("update-grub")

    elif distro == "fedora_based":
        if efi_partition:
            run_in_chroot(f"grub2-install \
    --target=x86_64-efi \
    --efi-directory=/boot/efi \
    --bootloader-id=GRUB")
            run_in_chroot("grub2-mkconfig -o /boot/grub2/grub.cfg")

            print("\n[✔] GRUB repair completed successfully!")
            print("You can now reboot your system.")
        elif not_efi_partition:
            run_in_chroot(f"grub2-install {disk}")
            run_in_chroot("grub2-mkconfig -o /boot/grub2/grub.cfg")

    elif distro == "arch_based":
        if efi_partition:
            run_in_chroot("grub-install \
    --target=x86_64-efi \
    --efi-directory=/boot/efi \
    --bootloader-id=GRUB")
            run_in_chroot("grub-mkconfig -o /boot/grub/grub.cfg")
        elif not_efi_partition:
            run_in_chroot(f"grub-install {disk}")
            run_in_chroot("grub-mkconfig -o /boot/grub/grub.cfg")

    print("\n[✔] GRUB repair completed successfully!")
    print("You can now reboot your system.")


def main():
    clear_screen()
    print("=== Linux Recovery System ===\n")

    list_partitions()

    mount_system_info = mount_system_info()
    if not mount_system_info:
        print("[!] Aborting recovery.")
        return

    distro = detect_distro()
    if not distro:
        print("[!] No Linux system detected in /mnt.")
        subprocess.run(["umount", "-R", "/mnt"])
        return

    print(f"[✔] Detected distribution: {distro.upper()}")

    prepare_chroot()

    # === GRUB repair (BIOS only for now) ===
    
    installing_grub()

main()