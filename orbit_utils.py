import numpy as np
from constants import *
from math import atan2, atan, sqrt, tan, fmod
from scipy.optimize import minimize_scalar


def get_true_anomaly(eccentric_anomaly, ecc):
    ecc_term = np.sqrt((1.0 + ecc) / (1.0 - ecc))
    return 2.0 * atan(ecc_term * tan(eccentric_anomaly * 0.5))


def kepler_eqn(eccentric_anomaly, eccentricity, mean_anomaly):
    return np.abs(eccentric_anomaly - eccentricity * np.sin(eccentric_anomaly) - mean_anomaly)


# Takes in (t-T0) and gives time since periastron in seconds.
def get_time_since_periastron(time_diff, parfile):
    time_since_periastron = np.fmod(time_diff, parfile.orbit.period)
    if time_since_periastron < 0: time_since_periastron += parfile.orbit.period
    return time_since_periastron


def calc_true_anomaly(mjd, parfile):
    time_diff = (mjd - parfile.orbit.t0) * seconds_per_day
    time_since_periastron = get_time_since_periastron(time_diff, parfile)  # in seconds

    mean_anomaly = parfile.orbit.n * (time_since_periastron
                                      - 0.5 * parfile.orbit.pbdot * time_since_periastron ** 2 / parfile.orbit.period)
    eccentric_anomaly = minimize_scalar(lambda x:
                                        kepler_eqn(x, parfile.orbit.ecc, mean_anomaly),
                                        bounds=(0, 2 * np.pi), method='bounded',
                                        options={'disp': 1, 'xatol': 1.0E-18, 'maxiter': 10000}).x
    ret = fmod(get_true_anomaly(eccentric_anomaly, parfile.orbit.ecc) + np.deg2rad(parfile.orbit.omega), 2 * np.pi)

    if ret < 0.0: ret += 2 * np.pi
    return ret


def solve_true_anomaly(mjd, parfile, required_phase):
    x = np.abs(calc_true_anomaly(mjd, parfile) - required_phase * 2 * np.pi)
    return x


def get_mjd_for_phase(old_mjd, parfile, required_phase):
    new_mjd = minimize_scalar(lambda mjd:
                              solve_true_anomaly(mjd, parfile, required_phase),
                              bounds=(old_mjd - 0 * parfile.orbit.period / seconds_per_day,
                                      old_mjd + 1 * parfile.orbit.period / seconds_per_day),
                              method='brent',
                              options={'disp': 3, 'xatol': 1.0E-21, 'maxiter': 10000}).x

    return new_mjd


class Orbit:
    def __init__(self, parfile):

        self.ecc = None

        if parfile["PB"] is not None:
            self.period = parfile["PB"] * seconds_per_day
            self.freq = 1 / self.period
            self.n = 2 * np.pi * self.freq
        else:
            raise ValueError("PB not found in par file")

        if parfile["A1"] is not None:
            self.x = parfile["A1"]
        else:
            raise ValueError("A1 not found in par file")

        if parfile["OM"] is not None:
            self.omega = parfile["OM"]

        elif parfile["EPS1"] is not None and parfile["EPS1"] is not None:
            self.eps1 = parfile["EPS1"]
            self.eps2 = parfile["EPS2"]
            self.ecc = np.sqrt(self.eps1 ** 2 + self.eps2 ** 2)
            self.omega = atan2(self.eps1, self.eps2);

        else:
            raise ValueError("OM (or) EPS1 and EPS2 not found in par file")

        if parfile["ECC"] is not None:
            self.ecc = parfile["ECC"]
        elif self.ecc is None:
            raise ValueError("ECC (or) EPS1 and EPS2 not found in par file")

        if parfile["T0"] is not None:
            self.t0 = parfile["T0"]
        elif parfile["TASC"] is not None:
            self.tasc = parfile["TASC"]
            self.t0 = self.tasc * self.omega / self.n

        self.omdot = parfile["OMDOT"] if parfile["OMDOT"] is not None else 0.0
        self.pbdot = parfile["PBDOT"] if parfile["PBDOT"] is not None else 0.0

    def __str__(self):
        return self.__dict__.__str__()
