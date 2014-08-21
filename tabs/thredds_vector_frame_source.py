# class for creating animations.

import matplotlib
matplotlib.use('Agg')

import os
import json

import numpy as np
from mpl_toolkits.basemap import Basemap
import netCDF4 as netCDF

from octant_lite import rot2d, shrink

# Data File
DEFAULT_DATA_URI = 'http://barataria.tamu.edu:8080/thredds/dodsC/NcML/txla_nesting6.nc'  # noqa


class THREDDSVectorFrameSource(object):

    def __init__(self, data_uri=DEFAULT_DATA_URI, decimate_factor=1,
                 grdfile=None):
        self.data_uri = data_uri
        self.decimate_factor = decimate_factor

        self.ncfile = data_uri
        self.nc = netCDF.Dataset(data_uri)

        if grdfile is None:
            self.ncg = self.nc
        else:
            self.ncg = netCDF.Dataset(grdfile)

        self.dates = netCDF.num2date(self.nc.variables['ocean_time'][:],
                                     'seconds since 1970-01-01')

        self.basemap = Basemap(llcrnrlon=-95.1,
                               llcrnrlat=27.25,
                               urcrnrlon=-87.5,
                               urcrnrlat=30.95,
                               projection='lcc',
                               lat_0=30.0,
                               lon_0=-90.0,
                               resolution='i',
                               area_thresh=0.)

        maskv = self.ncg.variables['mask_psi'][:]
        lon = self.ncg.variables['lon_psi'][:]
        lat = self.ncg.variables['lat_psi'][:]

        # What is happening here? Why is this necessary?
        self.anglev = shrink(self.ncg.variables['angle'][:], lon.shape)

        idx, idy = np.where(maskv == 1.0)

        idv = np.arange(len(idx))
        np.random.shuffle(idv)

        Nvec = len(idx) / self.decimate_factor
        idv = idv[:Nvec]
        self.idx = idx[idv]
        self.idy = idy[idv]

        # save the grid locations as JSON file
        self.grid = {'lon': lon[self.idx, self.idy].tolist(),
                     'lat': lat[self.idx, self.idy].tolist()}

    def plot_vector_surface(self, frame_number):
        # Why can't we fancy slice here? [..., self.idx, self.idy]
        u = self.nc.variables['u'][frame_number, -1, :, :]
        v = self.nc.variables['v'][frame_number, -1, :, :]
        u, v = shrink(u, v)
        u, v = rot2d(u, v, self.anglev)

        vector = {'date': self.dates[frame_number].isoformat(),
                  'u': u[self.idx, self.idy],
                  'v': v[self.idx, self.idy]}
        return vector

    def __del__(self):
        """docstring for __del__"""
        self.nc.close()
        self.ncg.close()


def write_vector(vector, outfile):
    """ Save vector data for a timestep as JSON """
    out_dir = os.path.join(os.path.dirname(__file__), 'json_data')
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    filename = os.path.join(out_dir, outfile)
    vector = vector.copy()
    for k in vector:
        if isinstance(vector[k], np.ndarray):
            vector[k] = vector[k].round(4).tolist()
    with open(filename, 'w') as f:
        json.dump(vector, f, separators=(',', ': '), indent=4)
        f.write('\n')


# length of animation (number of frames)
def main(NFRAMES=90):
    np.random.seed(0xDEADBEEF)
    vector_frame_source = THREDDSVectorFrameSource(DEFAULT_DATA_URI,
                                                   decimate_factor=60)
    write_vector(vector_frame_source.grid, 'grd_locations.json')

    for tidx in range(NFRAMES):
        print(tidx)
        vector = vector_frame_source.plot_vector_surface(tidx)
        write_vector(vector, 'step{}.json'.format(vector_frame_source.n))
        print(' ... wrote frame {}'.format(vector_frame_source.n))


if __name__ == '__main__':
    main()