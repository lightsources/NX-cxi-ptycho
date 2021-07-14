import h5py
import logging
import sys

from nxptycho.creator import NXCreator
from nxptycho.loader import CXILoader


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
    output_filename = options.NeXus_file
    input_filename = options.Input_file

    choices = "WARNING INFO DEBUG".split()
    logLevel = min(max(0, options.verbose), len(choices) - 1)

    logging.basicConfig(level=choices[logLevel])
    logger = logging.getLogger(__name__)

    # TODO: have options to call different loaders based on file suffix
    loader = CXILoader(input_filename)
    number_of_entries = len([entry for entry in loader.data_file.keys() if 'entry' in entry])
    print('Total number of entries in single file is:', number_of_entries)
    #TODO remove after testing
    number_of_entries = 1
    with NXCreator(output_filename) as creator:
        for n in range(1, number_of_entries+1):
            data_dict = loader.data_dict(n)
            entry = creator.create_entry_group(entry_index=n,
                                               experiment_description="Ptycho experiment",
                                               title="Ptychography")
            # Create instrument group(s), create multiple instances if multiple instruments produced the data,
            # if more than one instrument group is created, add index as arg instrument_index
            instrument = creator.create_instrument_group(parent=entry,
                                                         name="COSMIC")
            # Create beam group(s), create multiple instances if multiple beams produced the data,
            # if more than one beam group is created, add index as arg beam_index
            # set the correct instrument as parent
            beam = creator.create_beam_group(parent=instrument,
                                             incident_beam_energy=data_dict.get("energy"))
            detector = creator.create_detector_group(parent=beam,
                                                     data=data_dict.get("data"),
                                                     distance=data_dict.get("distance"),
                                                     x_pixel_size=data_dict.get("x_pixel_size"),
                                                     y_pixel_size=data_dict.get("y_pixel_size"))
            transformation = creator.create_transformation_group(h5parent=detector)
            sample = creator.create_sample_group(entry=entry)
            # TODO get axis information from some sort of config file
            # creator.create_axis()

            creator.create_positioner_group(h5parent=sample,
                                            name='vertical',
                                            raw_value=data_dict.get("translation")[:,1],
                                            positioner_index=1)
            creator.create_positioner_group(h5parent=sample,
                                            name='horizontal',
                                            raw_value=data_dict.get("translation")[:,0],
                                            positioner_index=2)


    logger.info("Wrote HDF5 file: %s", output_filename)


if __name__ == "__main__":
    main()
