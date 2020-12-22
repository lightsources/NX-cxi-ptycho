# TODO
# [ ] create loaders/parser for different ptycho input files at the different beamlines/facilities
# [ ] test class to check which loader is appropriate
# [ ] using projections to get keys
# [ ] future work to make converter multi-directional using projection
# FIXME
# [ ] load memory efficient
# [ ] fix classes
# [ ] write tests

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

    # def get_data(self, path):
    #     # Loading the Data
    #     self.file = h5py.File(path, 'r')
    #     number_of_entries = len([entry for entry in self.file.keys() if 'entry' in entry])
    #     print(number_of_entries)
    #     self.source_name = self.file['entry_{}/{}'.format(number_of_entries, self.source_name_key)][()]
    #     self.energy = self.file[self.energy_key][()]
    #     self.x_pixel_size = self.file[self.x_pixel_size_key][()]
    #     self.y_pixel_size = self.file[self.y_pixel_size_key][()]
    #     self.distance = self.file[self.distance_key][()]
    #     self.translation = self.file[self.translation_key][()]
    #     self.data = self.file[self.data_key][()]



class cxiLoader(GeneralLoader):

    def __init__(self):
        super(cxiLoader, self).__init__()
        ### Defining the Keys
        # self.entry_key = 'entry_1'
        # instrument_keys =
        ### Beam/Source fields
        self.source_name_key = 'instrument_1/source_1/name'
        self.energy_key = 'instrument_1/source_1/energy'
        # probe_key = '{}/instrument_1/source_1/data_illumination'.format(entry_key)
        # probe_key = '{}/instrument_1/source_1/probe'.format(entry_key)
        # probe_mask_key = '{}/instrument_1/source_1/probe_mask'.format(entry_key)
        ### Detector fields
        self.x_pixel_size_key = 'instrument_1/detector_1/x_pixel_size'
        self.y_pixel_size_key = 'instrument_1/detector_1/y_pixel_size'
        self.distance_key = 'instrument_1/detector_1/distance'
        self.translation_key = 'instrument_1/detector_1/translation'
        # self.data_avg_key = '{}/instrument_1/detector_1/Data Average'.format(self.entry_key)
        ### Data (plottable data?) fields
        self.data_key = 'data_1/data'

        self.source_name = {}
        self.energy = {}
        self.x_pixel_size = {}
        self.y_pixel_size = {}
        self.distance = {}
        self.translation = {}
        self.data = {}
        self.data_avg = {}


    def get_data(self, path):
        # Loading the Data
        self.file = h5py.File(path, 'r')
        self.number_of_entries = len([entry for entry in self.file.keys() if 'entry' in entry])
        print('Number of entries:', self.number_of_entries)
        #TODO iterate through entries
        for n in range(self.number_of_entries):
            print('entry_', n+1)
            self.source_name['entry_{}'.format(n+1)] = str(self.file['entry_{}/{}'.format(n+1, self.source_name_key)][()])
            self.energy['entry_{}'.format(n+1)] = self.file['entry_{}/{}'.format(n+1, self.energy_key)][()]
            self.x_pixel_size['entry_{}'.format(n+1)] = self.file['entry_{}/{}'.format(n+1, self.x_pixel_size_key)][()]
            self.y_pixel_size['entry_{}'.format(n+1)] = self.file['entry_{}/{}'.format(n+1, self.y_pixel_size_key)][()]
            self.distance['entry_{}'.format(n+1)] = self.file['entry_{}/{}'.format(n+1, self.distance_key)][()]
            self.translation['entry_{}'.format(n+1)] = self.file['entry_{}/{}'.format(n+1, self.translation_key)][()]
            self.data['entry_{}'.format(n+1)] = self.file['entry_{}/{}'.format(n+1, self.data_key)][()]
        # self.data_avg = self.file[self.data_avg_key]


