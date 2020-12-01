"""
Conversion from any (supported) ptycho file to NXcxi_ptycho.
"""

# TODO: import loader
import logging
import nx_creator

logger = logging.getLogger(__name__)
logging.basicConfig(level="DEBUG")

# TODO: call the loader
# TODO: Need real ptycho data

# FIXME: these are examples for demo purposes only
# FIXME: writer does not know what data to write now
output_filename = "example_nxptycho.nx"
metadata = dict(
    instrument="ptycho demo",
    title="The first NX ptycho file demo",
    experiment_description="simple",
    other="some other metadata that will be ignored",
)

# write the data to a NeXus file
creator = nx_creator.NX_Creator()
creator.write_new_file(output_filename, md=metadata)
