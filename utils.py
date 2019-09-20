from math import atan, sqrt, tan


def log_str(str):
    print(str)


def true_anomaly(E, ecc):
    return 2.0 * atan(sqrt((1.0 + ecc) / (1.0 - ecc)) * tan(E / 2.0))
