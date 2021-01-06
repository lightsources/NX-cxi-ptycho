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
        #TODO load dict with key for each field
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



class cxiLoader():

    def __init__(self):
        # TODO create key dictionary --> to be passed in GeneralLoader
        # key_dict =
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
        """
        Loading the data.
        Note: Original hierarchy is e.g. entry_1/instrument_1/energy/
        for the NX conversion this will be swapped so that NX groups like instrument_group
        or detector_group etc move to the top level in the dictionary and then contain the given number of entries
        for each NX field

        """
        self.file = h5py.File(path, 'r')
        self.number_of_entries = len([entry for entry in self.file.keys() if 'entry' in entry])
        print('Total number of entries:', self.number_of_entries)
        for n in range(1, self.number_of_entries+1):
            print(f'processing entry_{n}')
            self.source_name[f'entry_{n}'] = self.set_file_key(self.file, n, self.source_name_key)
            self.energy[f'entry_{n}'] = self.set_file_key(self.file, n, self.energy_key)
            self.x_pixel_size[f'entry_{n}'] = self.set_file_key(self.file, n, self.x_pixel_size_key)
            self.y_pixel_size[f'entry_{n}'] = self.set_file_key(self.file, n, self.y_pixel_size_key)
            self.distance[f'entry_{n}'] = self.set_file_key(self.file, n, self.distance_key)
            self.translation[f'entry_{n}'] = self.set_file_key(self.file, n, self.translation_key)
            self.data[f'entry_{n}'] = self.set_file_key(self.file, n, self.data_key)

    def set_file_key(self, file, n, key):
        return file[f'entry_{n}/{key}']

