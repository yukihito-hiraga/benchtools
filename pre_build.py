from collect import detect
from subprocess import run
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from pathlib import Path

def main():
    type = ""
    if detect()["cpu_type"] in ["AMD", "Intel"]:
        type = "x64"
    elif detect()["os"] == "Ubuntu":
        type = "armlinux"
    elif detect()["os"] == "Fedora Linux Asahi Remix":
        type = "asahi"
    data = load(open("setting.yml"), Loader=Loader)
    impl_path = Path(data["impl"])
    run([f"./preprocess.sh {type}"], shell=True, capture_output=True, cwd=impl_path/"common")

if __name__=="__main__":
    main()