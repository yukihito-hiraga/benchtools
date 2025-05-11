from subprocess import run
from os import environ
from pathlib import Path

def detect():
	cpu = None
	os = None
	osname = None
	uname = run(["uname -ar"], shell=True, capture_output=True, text=True).stdout
	if("Darwin" in uname):
		os = "Mac"
	if("Linux" in uname):
		os = "Linux"
  
	if(os == "Mac"):
		if("arm" in uname):
			cpu = "ARM"
		else:
			cpu = "Intel"
		osname = run(["system_profiler SPSoftwareDataType"], shell=True, capture_output=True, text=True).stdout.split("System Version: ")[1].split("\n")[0]

	if(os == "Linux"):
		cpuinfo = run(["cat /proc/cpuinfo"], shell=True, capture_output=True, text=True).stdout
		osname = run(["cat /etc/os-release"], shell=True, capture_output=True, text=True).stdout.split("\nNAME=")[1].split("\n")[0][1:-1]
		if("AMD" in cpuinfo):
			cpu = "AMD"
		if("Intel" in cpuinfo):
			cpu = "Intel"
		if("BogoMIPS" in cpuinfo):
			cpu = "ARM"
	return {
		"cpu_type" : cpu,
		"os_type" : os,
		"os" : osname
	}

def main():
	info = detect()
	cpu = info["cpu_type"]
	os = info["os_type"]
	dir = Path(__file__).parent
	with open(dir / "target_cpu", "w") as f:
		f.write(f"{cpu}\n")
	with open(dir / "target_os", "w") as f:
		f.write(f"{os}\n")


if __name__ == "__main__":
	main()