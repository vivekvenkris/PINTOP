import math
import scipy.constants as const
import astropy
from astropy.coordinates import EarthLocation
from astropy.coordinates import get_body_barycentric_posvel
from astropy.time import Time
from astropy.utils.iers import conf,IERS_A, IERS_A_URL, IERS_B, IERS_B_URL, IERS
from astropy.utils.data import download_file

from utils import log_str


def topo_to_bary(topo_mjds, parfile, epoch="J2000", ephemeris='de436'):
    raj_string = parfile["RAJ"]

    if raj_string is None:
        log_str("par file does not contain RA, cannot perform topo <-> bary corrections")
        return topo_mjds

    decj_string = parfile["DECJ"]

    if decj_string is None:
        log_str("par file does not contain DEC, cannot perform topo <-> bary corrections")
        return topo_mjds

    pmra_string = parfile["PMRA"] if parfile["PMRA"] is not None else "0.0"
    pmdec_string = parfile["PMDEC"] if parfile["PMDEC"] is not None else "0.0"

    topo_times = Time(topo_mjds, format='jd', scale='utc')
    # for now
    lon = 21.4430
    lat = -30.7130
    alt = 0
    telescope_position = EarthLocation.from_geodetic(lon, lat, height=alt)

    return topo_mjds;


def bary_to_topo(bary_mjd, parfile, epoch="J2000", ephemeris='de436'):
    return bary_mjd


