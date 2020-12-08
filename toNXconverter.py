#!/usr/bin/env python

"""
Conversion from any (supported) ptycho file to NXcxi_ptycho.
"""

import logging
import sys

import nx_creator
import loaders


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
    load_data = loaders.cxiLoader()
    load_data.get_data(input_filename)
    # TODO: Need real ptycho data

    # FIXME: these are examples for demo purposes only
    # FIXME: writer does not know what data to write now
    metadata = dict(
        # used in header and NXinstrument
        instrument=load_data.source_name,
        # used in NXentry
        title="The first NX ptycho file demo",
        experiment_description="simple",
        
        energy=load_data.energy,
        x_pixel_size = load_data.x_pixel_size,
        y_pixel_size = load_data.y_pixel_size,
        distance = load_data.distance,
        data = load_data.data,

        # not used anywhere
        other="some other metadata that will be ignored",
    )

    # write the data to a NeXus file
    creator = nx_creator.NX_Creator()
    creator.write_new_file(output_filename, md=metadata)
    logger.info("Wrote HDF5 file: %s", output_filename)


if __name__ == "__main__":
    main()
