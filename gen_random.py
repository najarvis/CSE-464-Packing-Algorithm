import random

def limit(v):
    return max(1, int(v))

with open("random_test.txt", "w") as f:
    r_vol_w = int(random.gauss(10, 2))
    r_vol_h = int(random.gauss(10, 2))
    r_vol_l = int(random.gauss(10, 2))
    f.write("{} {} {}\n".format(r_vol_w, r_vol_h, r_vol_l))
    for i in range(20):
        r_w = limit(random.gauss(4, 1.5))
        r_h = limit(random.gauss(4, 1.5))
        r_l = limit(random.gauss(4, 1.5))
        f.write("{} {} {}\n".format(r_w, r_h, r_l))
