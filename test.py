from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from subprocess import run
from pathlib import Path

def main():
    data = load(open("setting.yml"), Loader=Loader)
    targets = list(data["targets"])
    testgen_path = Path(data["testgen"])
    impl_path = Path(data["impl"])
    run(["rm -rf testvector/*"], shell=True)
    for target in targets:
        run(["python", testgen_path/ target / "gen_testvector.py", "-m", target])

main()