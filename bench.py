from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from subprocess import run
from os import getuid
from pathlib import Path
from functools import reduce
from shutil import move
import numpy as np
from collect import detect

def get_cpuinfo_x64():
    cpuinfo = []
    raw = []
    tmp = {}
    with open("/proc/cpuinfo") as f:
        raw = f.readlines()
    for e in raw:
        e = e.strip()
        if e == "":
            cpuinfo.append(tmp)
            tmp = {}
        else:
            key = e.split(":")[0].strip().strip("'")
            value = e.split(":")[1].strip().strip("'")
            if key == "processor":
                tmp["processor"] = int(value)
            if key == "cpu MHz":
                tmp["cpuMHz"] = float(value)
    return cpuinfo

def get_cpuinfo_armlinux():
    cpuinfo = []
    raw = []
    tmp = {}
    frq = float(run(["dmidecode | grep MHz"], shell=True, capture_output=True, text=True).stdout.split("\n")[1].split(":")[1].split()[0])
    with open("/proc/cpuinfo") as f:
        raw = f.readlines()
    for e in raw:
        e = e.strip()
        if e == "":
            cpuinfo.append(tmp)
            tmp = {}
        else:
            key = e.split(":")[0].strip().strip("'")
            value = e.split(":")[1].strip().strip("'")
            if key == "processor":
                tmp["processor"] = int(value)
                tmp["cpuMHz"] = frq
    return cpuinfo

def get_cpuinfo_asahi():
    cpuinfo = []
    raw = []
    tmp = {}
    res = run(["dmidecode | grep MHz"], shell=True, capture_output=True, text=True).stdout.split("\n")
    # frq = float(res[1].split(":")[1].split()[0])
    num_cpu = int(run(['ls /sys/devices/system/cpu/ | grep -w "cpu[0-9]*" | wc -l'], shell=True, capture_output=True, text=True).stdout)
    def info_cpu(i, key):
        with open(Path(f"/sys/devices/system/cpu/cpu{i}") / key) as f:
            return f.readlines()
    cpuinfo = [
        {
            "processor" : i,
            "cpuMHz" : int(info_cpu(i, "cpufreq/cpuinfo_cur_freq")[0])/1000,
        }
        for i in range(num_cpu)
    ]
    return cpuinfo

def get_cpuinfo():
    if detect()["cpu_type"] in ["AMD", "Intel"]:
        return get_cpuinfo_x64()
    elif detect()["os"] == "Ubuntu":
        return get_cpuinfo_armlinux()
    elif detect()["os"] == "Fedora Linux Asahi Remix":
        return get_cpuinfo_asahi()

def get_tscfreq_x64():
    with open("/var/log/dmesg") as f:
        raw = f.readlines()
    Mhz = 0
    for l in raw:
        l = l.strip()
        l = reduce(lambda s,x:s+x, l.split(":")[1:]).strip()
        data = l.split(" ")
        sub = data[0]
        if sub == "tsc":
            print(data)
            if data[1] == "Detected" and data[4] == "processor":
                Mhz = float(data[2])
            if data[1] == "Detected" and data[4] == "TSC":
                Mhz = float(data[2])
            if data[1] == "Refined" and data[2] == "TSC":
                Mhz = float(data[5])
    return Mhz

def get_tscfreq_armlinux():
    with open("/var/log/dmesg") as f:
        raw = f.readlines()
    Mhz = 0
    for l in raw:
        l = l.strip()
        l = reduce(lambda s,x:s+x, l.split(":")[1:]).strip()
        data = l.split(" ")
        sub = data[0]
        if sub == "arch_timer":
            # print(data)
            if data[1] == "cp15":
                Mhz = float(data[5][:-3])
    return Mhz

def get_tscfreq_asahi():
    raw = run(["dmesg"], shell=True, capture_output=True, text=True).stdout
    Mhz = 0
    for l in raw.split("\n"):
        l = l.strip()
        l = reduce(lambda s,x:s+x, l.split("]")[1:], "").strip()
        data = l.split(" ")
        sub = data[0]
        if sub == "arch_timer:":
            if data[1] == "cp15":
                Mhz = float(data[5][:-3])
    return Mhz

def get_tscfreq():
    if detect()["cpu_type"] in ["AMD", "Intel"]:
        return get_tscfreq_x64()
    elif detect()["os"] == "Ubuntu":
        return get_tscfreq_armlinux()
    elif detect()["os"] == "Fedora Linux Asahi Remix":
        return get_tscfreq_asahi()

def main():
    if getuid() != 0:
        print("please use sudo")
        return
    data = load(open("setting.yml"), Loader=Loader)
    targets = list(data["targets"])
    impl_path = Path(data["impl"])

    print("TSC {} Mhz".format(get_tscfreq()))

    run(["rm -rf result/*"], shell=True)
    for s, t in data["benchset"]:
        foldername = "result-{}-{}".format(s, t)
        run(["mkdir",  "-p",  Path("result") / foldername])
        for target in targets:
            cpuinfo = get_cpuinfo()
            lfreq = np.array([ obj["cpuMHz"] for obj in cpuinfo ])
            pcore = lfreq.argmax()
            print(cpuinfo)
            print("cpu{} has the highest freq, {}".format(cpuinfo[pcore]["processor"], lfreq[pcore]))
            run(["sudo",  impl_path / "{}/bench".format(target), "{}".format(s), "{}".format(t), "{}".format(pcore), "{}".format(int(get_tscfreq() * 1000000)), "{}".format(int(lfreq[pcore] * 1000000))])
            for re in Path("result").iterdir():
                if re.is_file() and not(re.stem.split(".")[0] in targets):
                    move(re, "result/{}.{}".format(target, re.name))
            run(["python", "tool/cpbgraph.py", target])
        run(["python", "tool/cpbgraph.py"])
        run("find result -maxdepth 1 -type f -exec mv {{}} result/{} \;".format(foldername), shell=True)
        #run(["mv -f result/* {}".format(foldername)], shell=True)
        #run(["mv -f {} result/{}".format(foldername, foldername)], shell=True)

main()