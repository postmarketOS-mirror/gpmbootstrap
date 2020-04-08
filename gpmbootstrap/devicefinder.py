import glob
import os


def find_sdcard():
    results = []
    for path in glob.glob('/sys/block/*/removable'):
        with open(path) as handle:
            raw = handle.read()

        # Why special case mmc you think? it's because intel is stupid and marks
        # sd card slots as non-removable mmc busses
        if raw == "0\n" and 'mmc' not in path:
            continue
        device = path.split('/')[3]
        with open(os.path.join('/sys/block/', device, 'size')) as handle:
            raw = handle.read()

        if int(raw.strip()) == 0:
            continue

        size = str(int(raw.strip()) // 1000 // 1000) + " GB"
        results.append((device, size))
    return results

if __name__ == '__main__':
    print(find_sdcard())
