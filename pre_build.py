from collect import detect
from subprocess import run
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from pathlib import Path

def compile_option(type):
    if type == "x64":
        return "-O3 -funroll-all-loops -march=native -DNDEBUG `pkg-config --cflags --libs glib-2.0` -Wno-psabi -Wno-unused-function -Wno-unused-result -Wno-stringop-overflow -Wno-implicit-function-declaration"
    if type == "armlinux":
        return "-O3 -Wno-psabi -Wno-unused-function -Wno-unused-result -funroll-all-loops -march=native -DNDEBUG -Wno-stringop-overflow `pkg-config --cflags --libs glib-2.0` -Wno-discarded-qualifiers"
    if type == "asahi":
        return "-O3 -Wno-psabi -Wno-unused-function -Wno-unused-result -funroll-all-loops -march=native -mcpu=native -DNDEBUG -Wno-stringop-overflow `gtk-config --cflags --libs`"
    return "-O3 -funroll-all-loops -march=native -DNDEBUG `pkg-config --cflags --libs glib-2.0` -Wno-psabi -Wno-unused-function -Wno-unused-result -Wno-stringop-overflow -Wno-implicit-function-declaration"

def main():
    gh = open(Path(__file__).parents[3]/"token").readline()
    print(gh)
    type = ""
    if detect()["cpu_type"] in ["AMD", "Intel"]:
        type = "x64"
    elif detect()["os"] == "Ubuntu":
        type = "armlinux"
    elif detect()["os"] == "Fedora Linux Asahi Remix":
        type = "asahi"
    data = load(open("setting.yml"), Loader=Loader)
    impl_path = Path(data["impl"])
    if not (impl_path/"common").exists():
        run(["git clone https://{gh}@github.com/yukihito-hiraga/benchcommon.git"], shell=True, cwd = impl_path)
        run(["mv benchcommon common"], shell=True, cwd=impl_path)
        
    lines = []
    with open(impl_path/"Makefile") as f:
        for l in f.readlines():
            if "FLAG=" in l:
                lines.append(f"FLAG={compile_option(type)}\n")
            else:
                lines.append(l)
    print(lines)
    with open(impl_path/"Makefile", "w") as f:
        f.write("".join(lines))
        
    run([f"./preprocess.sh {type}"], shell=True, cwd=impl_path/"common")

if __name__=="__main__":
    main()