import logging
import sys
import numpy as np
import h5py
from nxptycho.creator import NXCreator

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

    choices = "WARNING INFO DEBUG".split()
    logLevel = min(max(0, options.verbose), len(choices) - 1)
    logging.basicConfig(level=choices[logLevel])
    logger = logging.getLogger(__name__)

    data_file = h5py.File(input_filename, 'r')

    def data_dict(entry_index):
        """
        load data from ALS cxi file

        :param entry_index:
        :return: cxi_dict dictionary holding key-value pairs that is needed to fill the nexus datasets
        """
        cxi_dict = dict(
                        ### Beam/Source fields
                        source_name=data_file.get(f'entry_{entry_index}/instrument_1/source_1/name'),
                        instrument_name=data_file.get(f'entry_{entry_index}/instrument_1/name'),  # beamline name
                        energy=data_file.get(f'entry_{entry_index}/instrument_1/source_1/energy'),
                        # data_illumination_key = 'instrument_1/source_1/data_illumination'
                        # probe_key = 'instrument_1/source_1/probe'
                        # probe_mask_key = 'instrument_1/source_1/probe_mask'
                        ### Detector fields
                        data=data_file.get(f'entry_{entry_index}/instrument_1/detector_1/data'),
                        data_average=data_file.get(f'entry_{entry_index}/instrument_1/detector_1/Data Average'),
                        x_pixel_size=data_file.get(f'entry_{entry_index}/instrument_1/detector_1/x_pixel_size'),
                        y_pixel_size=data_file.get(f'entry_{entry_index}/instrument_1/detector_1/y_pixel_size'),
                        distance=data_file.get(f'entry_{entry_index}/instrument_1/detector_1/distance'),
                        translation=data_file.get(f'entry_{entry_index}/instrument_1/detector_1/translation')
                        )
        return cxi_dict

    number_of_entries = len([entry for entry in data_file.keys() if 'entry' in entry])
    with NXCreator(output_filename) as creator:
        for n in range(1, number_of_entries + 1):
            entry = creator.create_entry_group(definition='NXptycho',
                                               entry_index=n,
                                               experiment_description="basic",
                                               title='test_experiment')
            instrument = creator.create_instrument_group(h5parent=entry,
                                                         name=f"{data_dict(n)['source_name']} {data_dict(n)['instrument_name']}")
            creator.create_beam_group(h5parent=instrument,
                                      incident_beam_energy=data_dict(n)["energy"],
                                      energy_units='eV')
            detector = creator.create_detector_group(h5parent=instrument,
                                                     data=data_dict(n)["data"],
                                                     data_units='counts',
                                                     distance=data_dict(n)["distance"],
                                                     distance_units='m',
                                                     x_pixel_size=data_dict(n)["x_pixel_size"],
                                                     y_pixel_size=data_dict(n)["y_pixel_size"],
                                                     pixel_size_units='um')
            creator.create_data_group(h5parent=entry, signal_data='data')
            transformation = creator.create_transformation_group(h5parent=detector)
            # create transformation axes
            creator.create_axis(transformation=transformation,
                                axis_name='x_translation',
                                transformation_type='translation',
                                vector=np.array([1, 0, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                units="m",
                                depends_on=".")
            creator.create_axis(transformation=transformation,
                                axis_name='y_translation',
                                transformation_type='translation',
                                vector=np.array([0, 1, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                units="m",
                                depends_on="x_translation")
            creator.create_axis(transformation=transformation,
                                axis_name='z_translation',
                                transformation_type='translation',
                                vector=np.array([0, 0, 1], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                units="m",
                                depends_on="y_translation")

            sample = creator.create_sample_group(h5parent=entry)
            transformation = creator.create_transformation_group(h5parent=sample)
            # create positioner groups
            x = creator.create_positioner_group(h5parent=sample,
                                                name='horizontal',
                                                raw_value=data_dict(n)["translation"][:,0],
                                                positioner_index=1)
            y = creator.create_positioner_group(h5parent=sample,
                                                name='vertical',
                                                raw_value=data_dict(n)["translation"][:,1],
                                                positioner_index=2)
            #create transformation axes
            creator.create_axis(transformation=transformation,
                                axis_name='x_coarse_translation',
                                transformation_type='translation',
                                vector=np.array([1, 0, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                units="m",
                                depends_on=".")
            creator.create_axis(transformation=transformation,
                                axis_name='x_fine_translation',
                                value=x['raw_value'],
                                transformation_type='translation',
                                vector=np.array([1, 0, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                units="m",
                                depends_on=".")
            creator.create_axis(transformation=transformation,
                                axis_name='y_coarse_translation',
                                transformation_type='translation',
                                vector=np.array([0, 1, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                units="m",
                                depends_on='.')
            creator.create_axis(transformation=transformation,
                                axis_name='y_fine_translation',
                                value=y['raw_value'],
                                transformation_type='translation',
                                vector=np.array([0, 1, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                units="m",
                                depends_on='.')
            creator.create_axis(transformation=transformation,
                                axis_name='z_coarse_translation',
                                transformation_type='translation',
                                vector=np.array([0, 0, 1], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                units="m",
                                depends_on='.')
            creator.create_axis(transformation=transformation,
                                axis_name='alpha_rotation',
                                transformation_type='rotation',
                                vector=np.array([1, 0, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                units="degree",
                                depends_on='.')
            creator.create_axis(transformation=transformation,
                                axis_name='beta_rotation',
                                transformation_type='rotation',
                                vector=np.array([0, 1, 0], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                units="degree",
                                depends_on='.')
            creator.create_axis(transformation=transformation,
                                axis_name='gamma_rotation',
                                transformation_type='rotation',
                                vector=np.array([0, 0, 1], dtype=float),
                                offset=np.zeros(3, dtype=float),
                                units="degree",
                                depends_on='.')
    logger.info("Wrote HDF5 file: %s", output_filename)


if __name__ == "__main__":
    main()
