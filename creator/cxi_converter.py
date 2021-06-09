import sys
import numpy as np
import h5py
from nx_creator_ptycho import NXCreator

def get_user_parameters():
    """configure user's command line parameters from sys.argv"""
    import argparse

    parser = argparse.ArgumentParser(
        prog=sys.argv[0], description="NXcxi_ptycho writer"
    )

    # thanks to: https://stackoverflow.com/a/34065768/1046449
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="logging verbosity",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        help="print version and exit",
        version="development version",
    )

    #TODO check if this input makes sense
    parser.add_argument(
        "Input_file",
        action="store",
        help="NXcxi_ptycho (input) data file name",
    )

    parser.add_argument(
        "NeXus_file",
        action="store",
        help="NXcxi_ptycho (output) data file name",
    )

    return parser.parse_args()

def main():
    options = get_user_parameters()
    input_filename = options.Input_file
    output_filename = options.NeXus_file
    data_file = h5py.File(input_filename, 'r')

    def data_dict(entry_index):
        cxi_dict = dict(
                        ### Beam/Source fields
                        source_name=data_file.get(f'entry_{entry_index}/instrument_1/source_1/name'),
                        energy=data_file.get(f'entry_{entry_index}/instrument_1/source_1/energy'),
                        # data_illumination_key = 'instrument_1/source_1/data_illumination'
                        # probe_key = 'instrument_1/source_1/probe'
                        # probe_mask_key = 'instrument_1/source_1/probe_mask'
                        # source_name_key = 'entry_1/instrument_1/source_1/name' # Lightsource Name
                        # instrument_name_key = 'entry_1/instrument_1/name' # beamline name
                        ### Detector fields
                        data=data_file.get(f'entry_{entry_index}/instrument_1/detector_1/data'),
                        x_pixel_size=data_file.get(f'entry_{entry_index}/instrument_1/detector_1/x_pixel_size'),
                        y_pixel_size=data_file.get(f'entry_{entry_index}/instrument_1/detector_1/y_pixel_size'),
                        distance=data_file.get(f'entry_{entry_index}/instrument_1/detector_1/distance'),
                        translation=data_file.get(f'entry_{entry_index}/instrument_1/detector_1/translation'),
                        # self.data_avg_key = 'instrument_1/detector_1/Data Average'
                        ### Data (plottable data?) fields

                        )
        return cxi_dict

    number_of_entries = 1
    with NXCreator(output_filename) as creator:
        for n in range(1, number_of_entries + 1):
            entry = creator.create_entry_group(definition='NXptycho',
                                               entry_index=n,
                                               experiment_description="basic",
                                               title='test_experiment')
            instrument = creator.create_instrument_group(parent=entry,
                                                         name="COSMIC")
            creator.create_beam_group(parent=instrument,
                                      incident_beam_energy=data_dict(n)["energy"])
            detector = creator.create_detector_group(parent=instrument,
                                                     data= data_dict(n)["data"],
                                                     distance= data_dict(n)["distance"],
                                                     x_pixel_size=data_dict(n)["x_pixel_size"],
                                                     y_pixel_size=data_dict(n)["y_pixel_size"])
            # NOTE: Create transformation function is slightly redundant because
            # there can only be one transformation per group.
            transformation = creator.create_transformation_group(h5parent=detector)
            creator.create_axis(transformation=transformation,
                                axis_name='x_translation',
                                value=34,
                                transformation_type='translation',
                                vector=np.array([1, 0, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                offset_units="m",
                                depends_on=".")
            creator.create_axis(transformation=transformation,
                                axis_name='y_translation',
                                value=34,
                                transformation_type='translation',
                                vector=np.array([0, 1, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                offset_units="m",
                                depends_on="x_translation")
            creator.create_axis(transformation=transformation,
                                axis_name='z_translation',
                                value=34,
                                transformation_type='translation',
                                vector=np.array([0, 0, 1], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                offset_units="m",
                                depends_on="y_translation")

            sample = creator.create_sample_group(entry=entry)
            transformation = creator.create_transformation_group(h5parent=sample)
            #create positioner groups
            x = creator.create_positioner_group(h5parent=sample,
                                                name='horizontal',
                                                raw_value=np.empty(7),
                                                positioner_index=1)
            y = creator.create_positioner_group(h5parent=sample,
                                                name='vertical',
                                                raw_value=np.empty(7),
                                                positioner_index=2)
            #create transformation axes
            creator.create_axis(transformation=transformation,
                                axis_name='x_coarse_translation',
                                value=0,  # value is linked from positioner group
                                transformation_type='translation',
                                vector=np.array([1, 0, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                offset_units="m",
                                depends_on=".")
            creator.create_axis(transformation=transformation,
                                axis_name='x_fine_translation',
                                value=x['raw_value'],
                                transformation_type='translation',
                                vector=np.array([1, 0, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                offset_units="m",
                                depends_on=".")
            creator.create_axis(transformation=transformation,
                                axis_name='y_coarse_translation',
                                value=0,
                                transformation_type='translation',
                                vector=np.array([0, 1, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                offset_units="m",
                                depends_on='.')
            creator.create_axis(transformation=transformation,
                                axis_name='y_fine_translation',
                                value=y['raw_value'],
                                transformation_type='translation',
                                vector=np.array([0, 1, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                offset_units="m",
                                depends_on='.')
            creator.create_axis(transformation=transformation,
                                axis_name='z_coarse_translation',
                                value=0,
                                transformation_type='translation',
                                vector=np.array([0, 0, 1], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                offset_units="m",
                                depends_on='.')
            creator.create_axis(transformation=transformation,
                                axis_name='alpha_rotation',
                                value=0,
                                transformation_type='rotation',
                                vector=np.array([1, 0, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                offset_units="degree",
                                depends_on='.')
            creator.create_axis(transformation=transformation,
                                axis_name='beta_rotation',
                                value=0,
                                transformation_type='rotation',
                                vector=np.array([0, 1, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                offset_units="degree",
                                depends_on='.')
            creator.create_axis(transformation=transformation,
                                axis_name='gamma_rotation',
                                value=0,
                                transformation_type='rotation',
                                vector=np.array([0, 0, 1], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                offset_units="degree",
                                depends_on='.')



if __name__ == "__main__":
    main()