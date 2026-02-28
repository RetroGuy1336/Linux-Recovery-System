import time
from core import scanning_files
import os

def main():
    if os.geteuid() != 0:
        print("Execute with sudo!")
        exit()
    scanning_files()

main()