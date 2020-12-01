#!/usr/bin/env python

"""
Conversion from any (supported) ptycho file to NXcxi_ptycho.
"""

import logging
import sys

# TODO: import loader
import nx_creator


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
        "NeXus_file",
        action="store",
        help="NXcxi_ptycho (output) data file name",
    )

    return parser.parse_args()


def main():
    options = get_user_parameters()
    output_filename = options.NeXus_file

    choices = "WARNING INFO DEBUG".split()
    logLevel = min(max(0, options.verbose), len(choices) - 1)

    logging.basicConfig(level=choices[logLevel])
    logger = logging.getLogger(__name__)

    # TODO: call the loader
    # TODO: Need real ptycho data

    # FIXME: these are examples for demo purposes only
    # FIXME: writer does not know what data to write now
    metadata = dict(
        # used in header and NXinstrument
        instrument="ptycho demo",
        # used in NXentry
        title="The first NX ptycho file demo",
        experiment_description="simple",
        # not used anywhere
        other="some other metadata that will be ignored",
    )

    # write the data to a NeXus file
    creator = nx_creator.NX_Creator()
    creator.write_new_file(output_filename, md=metadata)
    logger.info("Wrote HDF5 file: %s", output_filename)


if __name__ == "__main__":
    main()
