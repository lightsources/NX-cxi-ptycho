# TODO
# [ ] create loaders/parser for different ptycho input files at the different beamlines/facilities
# [ ] test class to check which loader is appropriate
# [ ] using projections to get keys
# [ ] future work to make converter multi-directional using projection

import h5py
import dask

class GeneralLoader():
    def __init__(self):
        self.source_name = None
        self.energy = None
        self.x_pixel_size = None
        self.y_pixel_size = None
        self.distance = None
        self.translation = None
        self.data = None
        self.data_avg = None

    def get_data(self, path):
        # Loading the Data
        self.file = h5py.File(path, 'r')
        self.source_name = self.file[self.source_name_key][()]
        self.energy = self.file[self.energy_key][()]
        self.x_pixel_size = self.file[self.x_pixel_size_key][()]
        self.y_pixel_size = self.file[self.y_pixel_size_key][()]
        self.distance = self.file[self.distance_key][()]
        self.translation = self.file[self.translation_key][()]
        self.data = self.file[self.data_key][()]
        # self.data_avg = self.file[self.data_avg_key]


class cxiLoader(GeneralLoader):

    def __init__(self):
        super(cxiLoader, self).__init__()
        ### Defining the Keys
        self.entry_key = 1
        # instrument_keys =

        ### Beam/Source fields
        self.source_name_key = 'entry_{}/instrument_1/source_1/name'.format(self.entry_key)
        self.energy_key = 'entry_{}/instrument_1/source_1/energy'.format(self.entry_key)
        # probe_key = 'entry_{}/instrument_1/source_1/data_illumination'.format(entry_key)
        # probe_key = 'entry_{}/instrument_1/source_1/probe'.format(entry_key)
        # probe_mask_key = 'entry_{}/instrument_1/source_1/probe_mask'.format(entry_key)

        ### Detector fields
        self.x_pixel_size_key = 'entry_{}/instrument_1/detector_1/x_pixel_size'.format(self.entry_key)
        self.y_pixel_size_key = 'entry_{}/instrument_1/detector_1/y_pixel_size'.format(self.entry_key)
        self.distance_key = 'entry_{}/instrument_1/detector_1/distance'.format(self.entry_key)
        self.translation_key = 'entry_{}/instrument_1/detector_1/translation'.format(self.entry_key)
        # self.data_avg_key = 'entry_{}/instrument_1/detector_1/Data Average'.format(self.entry_key)

        ### Data (plottable data?) fields
        self.data_key = 'entry_{}/data_1/data'.format(self.entry_key)




