strength_values = dict()

fnames = ["readings-01", "readings-02"]

for name in fnames:
    with open(f"./python/rssi-readings/{name}", "r") as f:
        for line in f:
            name, rssi = line.split(" ")
            if name not in strength_values:
                strength_values[name] = [rssi]
            else:
                strength_values[name].append(rssi)

for key in strength_values:
    print(key, len(strength_values[key]))