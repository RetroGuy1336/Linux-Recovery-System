import time
from core import scanning_files
import os

def main():
    if os.geteuid() != 0:
        exit()
    scanning_files()

if __name__ == "main":
    main()