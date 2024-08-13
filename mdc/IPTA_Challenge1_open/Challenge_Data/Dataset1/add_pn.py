import subprocess
import sys

par = sys.argv[1]
tim = sys.argv[2]
pn_tim = sys.argv[3]

t2_output_str = "{file} {freq} {sat} {err} AXIS -pn {npulse}\\n"
t2_cmd = f"tempo2 -output general2 -f {par} {tim} -s \"{t2_output_str}\""
print(t2_cmd)
res = subprocess.check_output(t2_cmd, shell=True).decode()
res_lines = res.splitlines()
toas = res_lines[14:-2]
with open(pn_tim, 'w') as f:
    print("FORMAT 1", file=f)
    print("MODE 1", file=f)
    for toa in toas:
        print(toa, file=f)