import h5py
import logging
import sys

from creator.nx_creator_ptycho import NXCreator
from creator.loaders import CXILoader


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
    #load_data = loaders.cxiLoader()
    loader = CXILoader(input_filename)
    number_of_entries = len([entry for entry in loader.data_file.keys() if 'entry' in entry])
    print('Total number of entries in single file is:', number_of_entries)
    #TODO remove after testing
    number_of_entries = 3
    creator = NXCreator(output_filename)
    creator.init_file()
    for n in range(1, number_of_entries+1):
        data_dict = loader.data_dict(n)
    # write the data to a NeXus file
        creator.create_entry_group(entry_number=n, experiment_description="Ptycho experiment",
                                           title="Ptychography")
        creator.create_instrument_group("Ptychography Beamline")
        creator.create_beam_group(energy=data_dict.get("energy"))
        creator.create_detector_group(distance=data_dict.get("distance"),
                                      x_pixel_size=data_dict.get("x_pixel_size"),
                                      y_pixel_size=data_dict.get("y_pixel_size")
                                      )


    logger.info("Wrote HDF5 file: %s", output_filename)


if __name__ == "__main__":
    main()
