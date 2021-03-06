#!/usr/bin/env python
# Copyright (C) 2015 Swift Navigation Inc.
# Contact: Bhaskar Mookerji <mookerji@swiftnav.com>
#
# This source is subject to the license found in the file 'LICENSE' which must
# be be distributed together with this source. All other rights reserved.
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
# EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.

from swiftnav.single_diff import SingleDiff
import numpy as np
import pandas as pd
import swiftnav.almanac as sa


def load_yuma(yuma):
    """
    """
    yuma = yuma.readlines()
    almanacs = {}
    for n, line in enumerate(yuma):
        if line[:3] == "ID:":
            block = yuma[n:n + 13]
            fields = map(lambda x: x[25:], block)
            prn = int(fields[0])
            healthy = (int(fields[1]) == 0)
            ecc = float(fields[2])
            toa = float(fields[3])
            inc = float(fields[4])
            rora = float(fields[5])
            a = float(fields[6]) ** 2
            raaw = float(fields[7])
            argp = float(fields[8])
            ma = float(fields[9])
            af0 = float(fields[10])
            af1 = float(fields[11])
            week = int(fields[12])
            almanac = sa.Almanac(ecc, toa, inc, rora, a, raaw, argp, ma, af0, af1, week, prn, healthy)
            almanacs[prn] = almanac
    return almanacs


def load_data(data_filename, key):
    """
    """
    return pd.read_hdf(data_filename, key)


def load_ephs(eph_filename):
    """
    """
    return pd.read_hdf(eph_filename, 'eph')


def mk_swiftnav_sdiff(x):
    """
    """
    if np.isnan(x.C1):
        return np.nan
    return SingleDiff(x.C1,
                      x.L1,
                      x.D1,
                      np.array([x.sat_pos_x, x.sat_pos_y, x.sat_pos_z]),
                      np.array([x.sat_vel_x, x.sat_vel_y, x.sat_vel_z]),
                      x.min_snr,
                      x.prn)


def load_sdiffs(filename, key):
    """
    Given a filename and key for an hdf5 file for a pandas panel
    whose entries are the fields for sdiffs, this function will
    read the file and convert it into a pandas dataframe of our
    libswiftnav sdiffs.
    """
    return pd.read_hdf(filename, key).apply(mk_swiftnav_sdiff, axis=2)


def load_almanac(almanac_filename):
    return load_yuma(open(almanac_filename))


def save_analysis(point_analyses, aggregate_analysis, settings,
                  analysis_filename):
    """
    """
    store = pd.HDFStore(analysis_filename)
    store['analyses'] = point_analyses
    aggregate_analysis.store(store.get_storer('analyses').attrs)
    settings.store(store.get_storer('analyses').attrs)
    store.close()
