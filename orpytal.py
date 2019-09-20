from math import fmod
import numpy as np
from SSE_utils import topo_to_bary
from constants import seconds_per_day, seconds_per_year
from orbit_utils import Orbit, get_time_since_periastron, solve_true_anomaly, calc_true_anomaly, get_mjd_for_phase
from par_utils import ParFile
import argparse
import matplotlib.pyplot as plt

'''
One can request the following:

1. Orbital phase of a given MJD
2. particular phase times close to a given MJD eg. conjunction
'''


def get_args():
    arg_parser = argparse.ArgumentParser(description="A pure python implementation of orbital analysis ")
    arg_parser.add_argument("-telescope_config", dest="telescope_config", help="telescope_config")
    arg_parser.add_argument("-get", dest="get", help="phase/time", required=True)
    arg_parser.add_argument("-mjd", dest="mjd", help="mjd", type=float)
    arg_parser.add_argument("-phase", dest="phase", help="mjd for this phase")
    arg_parser.add_argument("-num_mjds", dest="num_mjds", help="num_mjds")
    arg_parser.add_argument("-par_file", dest="par_file", help="par_file", required=True)
    arg_parser.add_argument("-bary", dest="bary", help="mjd is barycentric")
    return arg_parser.parse_args()


if __name__ == '__main__':

    args = get_args()
    parfile = ParFile(args.par_file)

    if args.bary is None: args.mjd = topo_to_bary(args.mjd, parfile)

    extra_omega = (args.mjd - parfile.orbit.t0) * seconds_per_day * parfile.orbit.omdot / seconds_per_year
    parfile.orbit.omega += extra_omega

    true_anomaly = calc_true_anomaly(args.mjd, parfile)  # in radians
    orbital_phase = true_anomaly / (2 * np.pi)
    print("Orbital phase corresponding to " + str(args.mjd) + " is " + str(orbital_phase))
    if args.get == "phase":
        print("Orbital phase corresponding to " + str(args.mjd) + " is " + str(orbital_phase))

    elif args.get == "time":
        required_phase = None
        if args.phase is None:
            raise ValueError("Specify an orbital phase needed (0-1) or superior or inferior or periastron or apastron")

        elif args.phase == "superior":
            required_phase = 0.25

        elif args.phase == "inferior":
            required_phase = 0.75

        elif args.phase == "periastron":
            required_phase = 0.25

        elif args.phase == "apastron":
            required_phase = 0.25

        else:
            try:
                required_phase = float(args.phase)
            except:
                raise ValueError(
                    "Specify an orbital phase needed (0-1) or superior or inferior or periastron or apastron")
        new_mjd = get_mjd_for_phase(args.mjd, parfile, required_phase)
        # if new_mjd < args.mjd: new_mjd += parfile.orbit.period / seconds_per_day
        print(new_mjd)

        true_anomaly = calc_true_anomaly(new_mjd, parfile)  # in radians
        print(true_anomaly * 180.0 / np.pi)
        print("*****************************")
        data = np.loadtxt("test/test.txt", usecols=(1, 2))
        for d in data:
            mjd = d[0]
            old_phase = d[1]
            inp = mjd + np.random.random() * 0.1022
            new_mjd = get_mjd_for_phase(inp, parfile, required_phase)
            true_anomaly = calc_true_anomaly(new_mjd, parfile)
            diff = true_anomaly * 180.0 / np.pi - old_phase
            if np.abs(diff) > 0.02:
                print(mjd, inp, inp-mjd, old_phase, new_mjd, true_anomaly * 180.0 / np.pi, diff)

