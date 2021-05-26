# TODO
# [ ] create loaders/parser for different ptycho input files at the different beamlines/facilities
# [ ] test class to check which loader is appropriate
# [ ] using projections to get keys
# [ ] future work to make converter multi-directional using projection
# [ ] write tests
# [ ] what to do if certain fields are missing in the original file? --> still writing the rest if essentials
#     are covered, but warning/info what is missing, red flag warning, when essentials are missing
# FIXME
# [ ] load memory efficient
# [-] fix classes --> load dictionary to GeneralLoader

import h5py
import dask


class CXILoader():
    """
    Class to load cxi file for conversion to NXcxi_ptycho
    - init a dictionary containing the path structure of the cxi file that should be converted
    - optional: add further special methods for extracting data special to cxi
    """
    def __init__(self, input_file):
        self.data_file = h5py.File(input_file, 'r')
        # TODO create key dictionary --> to be passed in GeneralLoader
    # def prepare_diff_data(self, entry_number, chunk_size):
    #     diff_data = self.data_file.get(f'entry_{entry_number}/data_1/data')
    #     number_of_chunks = 1+diff_data.shape[0]//chunk_size
    #     for n in range(number_of_chunks):
    #         if n == 0:
    #             chunk = diff_data[n:chunk_size,:,:]
    #         else:
    #             chunk = diff_data[n*chunk_size+1:(n+1)*chunk_size,:,:]

    def data_dict(self, entry_number):
        cxi_dict = dict(
            ### Beam/Source fields
            source_name=self.data_file.get(f'entry_{entry_number}/instrument_1/source_1/name'),
            energy=self.data_file.get(f'entry_{entry_number}/instrument_1/source_1/energy'),
            # data_illumination_key = 'instrument_1/source_1/data_illumination'
            # probe_key = 'instrument_1/source_1/probe'
            # probe_mask_key = 'instrument_1/source_1/probe_mask'
            # source_name_key = 'entry_1/instrument_1/source_1/name' # Lightsource Name
            # instrument_name_key = 'entry_1/instrument_1/name' # beamline name
            ### Detector fields
            data=self.data_file.get(f'entry_{entry_number}/instrument_1/detector_1/data'),
            x_pixel_size=self.data_file.get(f'entry_{entry_number}/instrument_1/detector_1/x_pixel_size'),
            y_pixel_size=self.data_file.get(f'entry_{entry_number}/instrument_1/detector_1/y_pixel_size'),
            distance=self.data_file.get(f'entry_{entry_number}/instrument_1/detector_1/distance'),
            translation=self.data_file.get(f'entry_{entry_number}/instrument_1/detector_1/translation'),
            # self.data_avg_key = 'instrument_1/detector_1/Data Average'
            ### Data (plottable data?) fields

        )
        return cxi_dict


class HDF_loader():
    ...


class ptyd_loader():
    ...


#see https://goodcode.io/articles/python-dict-object/ for passing key_dict to class
class GeneralLoader():
    """
    General loader class
    """
    def __init__(self, path):
        #TODO load dict with keys for all groups and fields in the NX file
        self.source_name = {}
        self.energy = {}
        self.x_pixel_size = {}
        self.y_pixel_size = {}
        self.distance = {}
        self.translation = {}
        self.data = {}
        self.data_avg = {}
        self.path = path
        self.key_dict = self.check_suffix(self.path).key_dict
        self.number_of_entries = None

    def check_suffix(self, path):
        if path.endswith('.cxi'):
            return CXILoader()
        elif path.endswith('hdf'):
            print('hdf converter not yet implemented')
        elif path.endswith('ptyd'):
            print('ptyd converter not yet implemented')
        #TODO add more checks

    def get_data(self, mode='single'):
        """
        Loading the data.
        Note: Original hierarchy is e.g. entry_1/instrument_1/energy/
        for the NX conversion this will be swapped so that NX fields like energy or pixel_size etc
        move to the top level in the dictionary and then contain the given number of entries
        for each NX field

        """

        self.file = h5py.File(self.path, 'r')
        #TODO add multiple input modes, such as single file or folder etc.
        if mode == 'single':
            self.number_of_entries = len([entry for entry in self.file.keys() if 'entry' in entry])
            print('Total number of entries in single file is:', self.number_of_entries)
        for n in range(1, self.number_of_entries+1):
            # print(f'loading entry_{n}')
            # self.source_name[f'entry_{n}'] = self.set_file_key(self.file, n, self.key_dict['source_name_key'])
            # self.energy[f'entry_{n}'] = self.set_file_key(self.file, n, self.key_dict['energy_key'])
            # self.x_pixel_size[f'entry_{n}'] = self.set_file_key(self.file, n, self.key_dict['x_pixel_size_key'])
            # self.y_pixel_size[f'entry_{n}'] = self.set_file_key(self.file, n, self.key_dict['y_pixel_size_key'])
            # self.distance[f'entry_{n}'] = self.set_file_key(self.file, n, self.key_dict['distance_key'])
            # self.translation[f'entry_{n}'] = self.set_file_key(self.file, n, self.key_dict['translation_key'])
            # self.data[f'entry_{n}'] = self.set_file_key(self.file, n, self.key_dict['data_key'])
            self.source_name = self.set_file_key(self.file, n, self.key_dict['source_name_key'])
            self.energy = self.set_file_key(self.file, n, self.key_dict['energy_key'])
            self.x_pixel_size = self.set_file_key(self.file, n, self.key_dict['x_pixel_size_key'])
            self.y_pixel_size = self.set_file_key(self.file, n, self.key_dict['y_pixel_size_key'])
            self.distance = self.set_file_key(self.file, n, self.key_dict['distance_key'])
            self.translation = self.set_file_key(self.file, n, self.key_dict['translation_key'])
            self.data = self.set_file_key(self.file, n, self.key_dict['data_key'])

    def set_file_key(self, file, n, key):
        return file.get(f'entry_{n}/{key}')