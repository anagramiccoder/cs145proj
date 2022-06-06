
import os
import sys
from datetime import datetime

# Run tshark for 120 seconds and save the output to a file
def run_tshark(file_name=f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"):
    # set filename to the current date time
    print(file_name)
    os.system(f"touch tfiles/{file_name}.pcap")
    os.system(f"chmod o=rw tfiles/{file_name}.pcap")
    os.system(f"sudo tshark -a duration:120 -w tfiles/{file_name}.pcap")

fname=sys.argv[1]
run_tshark(fname)
