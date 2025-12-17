import struct
import csv

SYNC = 0xEB25
TMATS_TYPE = 0x01
PCM_TYPE = 0x02
SCALE = 10

seq = 0

with open("data.csv", newline="") as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)

    param_names = header[1:]
    param_count = len(param_names)
    payload_bytes = param_count * 2

    with open("data.ch10", "wb") as ch10:

        tmats = []
        tmats.append("G\\PN:CSV_TO_CH10;")
        tmats.append("G\\CH:1;")
        tmats.append("R-1\\ID:REC1;")
        tmats.append("R-1\\CH:1;")
        tmats.append("C-1\\ID:PCM_CH1;")
        tmats.append("C-1\\DT:PCM;")
        tmats.append("P-1\\ID:PCM1;")
        tmats.append("P-1\\WD:16;")
        tmats.append(f"P-1\\DL:{payload_bytes};")
        tmats.append("P-1\\MF:1;")
        tmats.append(f"P-1\\PL:{payload_bytes * 8};")

        for i, name in enumerate(param_names, start=1):
            tmats.append(f"P-1\\PM-{i}\\ID:{name.upper()};")
            tmats.append(f"P-1\\PM-{i}\\WD:{i};")
            tmats.append("P-1\\PM-{i}\\BL:16;".replace("{i}", str(i)))
            tmats.append("P-1\\PM-{i}\\DT:SIGNED;".replace("{i}", str(i)))
            tmats.append("P-1\\PM-{i}\\SC:0.1;".replace("{i}", str(i)))
            tmats.append("P-1\\PM-{i}\\UN:RAW;".replace("{i}", str(i)))

        tmats_bytes = ("\n".join(tmats) + "\n").encode("ascii")

        tmats_len = 24 + len(tmats_bytes)
        tmats_header = struct.pack(
            "<HHI I I 8s",
            SYNC, 0, tmats_len, TMATS_TYPE, seq, b'\x00' * 8
        )

        ch10.write(tmats_header)
        ch10.write(tmats_bytes)
        seq += 1

        for row in reader:
            values = [int(float(v) * SCALE) for v in row[1:]]
            pcm_payload = struct.pack("<" + "h" * param_count, *values)

            pkt_len = 24 + len(pcm_payload)
            pcm_header = struct.pack(
                "<HHI I I 8s",
                SYNC, 1, pkt_len, PCM_TYPE, seq, b'\x00' * 8
            )

            ch10.write(pcm_header)
            ch10.write(pcm_payload)
            seq += 1
