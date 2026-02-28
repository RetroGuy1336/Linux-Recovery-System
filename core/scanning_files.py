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
    """
    Mounts the Linux root partition and optionally the EFI partition.
    Returns the root partition path or None on failure.
    """
    try:
        root_partition = input("Enter the ROOT partition (e.g. /dev/sda2): ").strip()

        if not os.path.exists(root_partition):
            print(f"[!] Partition not found: {root_partition}")
            return None

        print(f"[+] Mounting {root_partition} to /mnt...")
        result = subprocess.run(
            ["mount", root_partition, "/mnt"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"[!] Mount error: {result.stderr}")
            return None

        efi_choice = input("Is there a separate EFI partition? [y/N]: ").lower().strip()
        if efi_choice == "y":
            efi_partition = input("Enter the EFI partition (e.g. /dev/sda1): ").strip()
            os.makedirs("/mnt/boot/efi", exist_ok=True)
            subprocess.run(["mount", efi_partition, "/mnt/boot/efi"])

        print("[✔] System mounted successfully.")
        return root_partition

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

    if "id_like=debian" in data or "id_like=ubuntu" in data:
        return "debian_based"

    if "id=fedora" in data or "id_like=\"rhel fedora\"" in data:
        return "fedora_based"

    if "id=arch" in data:
        return "arch"

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


def scanning_files():
    clear_screen()
    print("=== Linux Recovery System ===\n")

    list_partitions()

    root_partition = mount_system()
    if not root_partition:
        print("[!] Aborting recovery.")
        return

    distro = detect_distro()
    if not distro:
        print("[!] No Linux system detected in /mnt.")
        subprocess.run(["umount", "-R", "/mnt"])
        return
    if distro != "debian_based":
        print("For now, the program only supports Debian or Ubuntu-based distributions. The developer who wrote the code is too lazy for that.")

    print(f"[✔] Detected distribution: {distro.upper()}")

    prepare_chroot()

    # === GRUB repair (BIOS only for now) ===
    if distro == "ubuntu":
        disk = re.sub(r"\d+$", "", root_partition)
        print(f"[+] Reinstalling GRUB on {disk}...")

        run_in_chroot(f"grub-install {disk}")
        run_in_chroot("update-grub")

        print("\n[✔] GRUB repair completed successfully!")
        print("You can now reboot your system.")

    else:
        print(f"[!] Automatic repair for {distro} is not implemented yet.")

scanning_files()