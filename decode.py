import struct
import csv
import re
import numpy as np

SYNC = 0xEB25
TMATS_TYPE = 0x01
PCM_TYPE = 0x02

param_names = []
scale = 1.0
param_count = 0

with open("data.ch10", "rb") as ch10, open("decodednpsd.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    while True:
        header = ch10.read(24)
        if len(header) < 24:
            break

        sync, ch, length, dtype, seq, _ = struct.unpack("<HHI I I 8s", header)
        payload = ch10.read(length - 24)

        if dtype == TMATS_TYPE:
            text = payload.decode("ascii", errors="ignore")
            param_names = re.findall(r"PM-\d+\\ID:([^;]+);", text)

            scale_match = re.search(r"SC:([0-9.]+);", text)
            scale = float(scale_match.group(1)) if scale_match else 1.0

            param_count = len(param_names)
            writer.writerow(param_names)

        elif dtype == PCM_TYPE and param_count > 0:
            raw = np.frombuffer(payload, dtype="<i2", count=param_count)
            eng = np.round(raw * scale, 1)
            writer.writerow(eng.tolist()) #this is my second commit wala s
            print ("finish the files")
