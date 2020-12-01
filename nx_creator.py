import datetime
import h5py
import logging
import os

# TODO
# [ ] create header
# [ ] create entry group
#   [ ] create instrument group
#       [ ] create beam group
#       [ ] create detector group
#       [ ] create monitor groups
#       [ ] create positioner groups
#   [ ] create data group
# [ ] create process groups

logger = logging.getLogger(__name__)

def write_file_header(h5parent):
    """optional header metadata"""
    timestamp = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
    logger.debug('timestamp: %s', str(timestamp))

    # give the HDF5 root some more attributes
    h5parent.attrs['file_name'] = h5parent.filename
    h5parent.attrs['file_time'] = timestamp
    h5parent.attrs['instrument'] = 'APS XPCS at 8-ID-I'
    h5parent.attrs['creator'] = __file__             # TODO: better choice?
    h5parent.attrs['HDF5_Version'] = h5py.version.hdf5_version
    h5parent.attrs['h5py_version'] = h5py.version.version


def create_entry_group(h5parent, md):
    """
    all information about the measurement

    see: https://manual.nexusformat.org/classes/base_classes/NXentry.html
    """
    nxentry = h5parent.create_group('entry')
    nxentry.attrs['NX_class'] = 'NXentry'

    title = os.path.splitext(md["datafilename"])[0]
    ds = nxentry.create_dataset('title', data=title)
    ds.attrs["target"] = ds.name      # we'll re-use this
    logger.debug("title: %s", title)

    # NeXus structure: point to this group for default plot
    h5parent.attrs['default'] = nxentry.name.split("/")[-1]

    return nxentry