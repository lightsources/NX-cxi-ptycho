import datetime
import h5py
import logging
import os

# TODO
# [ ] load data (in loader module)
# [ ] call this code (from toNXconverter module?)
# [ ] put data into the tree

logger = logging.getLogger(__name__)


class NX_Creator:
    """
    Manage HDF5 file creation for Ptychography data.

    USAGE::

        example_metadata = dict(
            instrument="ptycho demo",
            title="The first NX ptycho file demo",
            experiment_description="simple",
            other="some other metadata that will be ignored"
        )
        example_hdf5_filename = "/tmp/ptycho.nx"

        creator = NX_Creator()
        creator.write_new_file(example_hdf5_filename, md=example_metadata)

        # later, can add additional process data via:
        creator.add_process_group(
            example_hdf5_filename,
            entrygroup="/entry"
        )

    """

    def __init_group__(self, h5parent, nm, NX_class, md=None):
        """Common steps to initialize a NeXus HDF5 group."""
        if md is None:
            md = {}

        group = h5parent.create_group(nm)
        group.attrs["NX_class"] = NX_class
        return group, md

    def add_process_group(
        self,
        hdf5filename,
        entrygroup="/entry",
        nm=None,  # name of process group
        md=None,
    ):
        """Add a new NXprocess group to an existing HDF5 file."""
        # TODO: will need to get and add data
        nxclass = "NXprocess"
        if os.path.exists(hdf5filename):
            with h5py.File(hdf5filename, "a") as root:
                group = root[entrygroup]
                if nm is None:
                    nm = (
                        f"process_{1+self.count_subgroups(group, nxclass)}"
                    )
                logger.debug(
                    "Adding NXprocess group '%s' to '%s' in file %s",
                    nm,
                    group.name,
                    hdf5filename,
                )
                self.create_process_group(group, nm, md=md)

    def count_subgroups(self, h5parent, nxclass):
        """Count the number of subgroups of a specific NX_class."""
        count = 0
        for key in h5parent.keys():
            obj = h5parent[key]
            if not isinstance(obj, h5py.Group):
                continue
            nxclass = obj.attrs.get("NX_class")
            if nxclass == "NXprocess":
                count += 1
        return count

    def create_beam_group(self, h5parent, nm, md=None):
        """Write the NXbeam group."""
        # TODO: will need to get and add data
        group, md = self.__init_group__(h5parent, nm, "NXbeam", md)

        # TODO:
        # Either Energy or Wavelength : one of these is required
        # Energy (NX_FLOAT)
        #     @units (NX_ENERGY) = eV | keV | J
        # Wavelength (NX_FLOAT)
        #     @units (NX_WAVELENGTH) = A | nm
        # Extent (NX_FLOAT) = Size of the beam at sample position
        #     @units (NX_LENGTH) = m
        # Polarization (NX_FLOAT) = polarization vector
        #     @units ?

    def create_data_group(self, h5parent, nm, md=None):
        """Write a NXdata group."""
        # TODO: will need to get and add data
        group, md = self.__init_group__(h5parent, nm, "NXdata", md)

        # TODO:
        # describes the plottable data and related dimension scales
        # items here could be HDF5 datasets or links to datasets

    def create_detector_group(self, h5parent, nm, md=None):
        """Write a NXdetector group."""
        # TODO: will need to get and add data
        group, md = self.__init_group__(h5parent, nm, "NXdetector", md)

        # TODO:
        # data [npts, frame_size_x, frame_size_y]  =
        #   $n 2-dimensional diffraction patterns with $frame_size_x pixels
        # in horizontal and $frame_size_y pixels in vertical direction.
        # E.g. Eiger 1M → 10000 DP x 1028 pixel_x x 1062 pixel_y
        # X_pixel_size (NX_FLOAT) = horizontal pixel size of the detector
        #     @units (NX_LENGTH) = m
        # Y_pixel_size (NX_FLOAT) = vertical pixel size of the detector
        #     @units (NX_LENGTH) = m
        # Distance = Sample to detector distance
        # @units (NX_LENGTH) = m
        # Geometry (NXTransformation)

        # AXISNAME (NX_NUMBER)
        #     @transformation_type (NX_CHAR)
        # @vector (NX_NUMBER)

    def create_entry_group(self, h5parent, md=None):
        """
        all information about the measurement

        see: https://manual.nexusformat.org/classes/base_classes/NXentry.html
        """
        group, md = self.__init_group__(h5parent, "entry", "NXentry", md)

        group.create_dataset("definition", data="NXcxi_ptycho")

        experiment_description = md.get("experiment_description")
        if experiment_description is not None:
            group.create_dataset(
                "experiment_description", data=experiment_description
            )

        title = md.get("title", "")
        ds = group.create_dataset("title", data=title)
        ds.attrs["target"] = ds.name  # we'll re-use this
        logger.debug("title: %s", title)

        # NeXus structure: point to this group for default plot
        h5parent.attrs["default"] = group.name.split("/")[-1]

        self.create_instrument_group(group, md=md)
        self.create_data_group(group, "data", md=md)
        self.create_process_group(group, "process1", md=md)

        return group

    def create_instrument_group(self, h5parent, md=None):
        """Write the NXinstrument group."""
        # TODO: will need to get and add data
        group, md = self.__init_group__(
            h5parent, "instrument", "NXinstrument", md
        )

        name_field = md.get("instrument", "")
        ds = group.create_dataset("name", data=name_field)
        ds.attrs["target"] = ds.name  # we'll re-use this
        logger.debug("instrument: %s", name_field)

        self.create_beam_group(group, "beam", md=md)
        self.create_detector_group(group, "detector1", md=md)
        self.create_detector_group(group, "detector2", md=md)
        self.create_monitor_group(group, "monitor", md=md)
        self.create_positioner_group(group, "positioner1", md=md)
        self.create_positioner_group(group, "positioner2", md=md)

    def create_monitor_group(self, h5parent, nm, md=None):
        """Write a NXmonitor group."""
        # TODO: will need to get and add data
        group, md = self.__init_group__(h5parent, nm, "NXmonitor", md)

        # TODO:
        # Data [npts] (NX_FLOAT)
        #     @units (NX_ANY) = unit of the monitor data

    def create_positioner_group(self, h5parent, nm, md=None):
        """Write a NXpositioner group."""
        # TODO: will need to get and add data
        group, md = self.__init_group__(h5parent, nm, "NXpositioner", md)

        # TODO:
        # Name (NXchar) = define positioner name (stage axis?)
        # Value [n] (NXnumber) = n position values for positioner 1
        #     @unit (NX_ANY) = unit related to the positioner (angle or m)
        # Raw_value
        # target_value

    def create_process_group(self, h5parent, nm, md=None):
        """Write a NXprocess group."""
        # TODO: will need to get and add data
        group, md = self.__init_group__(h5parent, nm, "NXprocess", md)

        # TODO:

    def create_sample_group(self, h5parent, nm, md=None):
        """Write a NXsample group."""
        # TODO: will need to get and add data
        group, md = self.__init_group__(h5parent, nm, "NXsample", md)

        # TODO:
        # Name (NX_CHAR) = name of the sample
        # Transformation (NXtransformations) =
        #   must contain two fields with the x and y
        #   positioners that are linked via the
        #   dependency tree according to the real-life
        #   positioner layout dependency. For raster
        #   scans, x and y will have shape (npts_x, npts_y).
        #   For arbitrary scans x and y will be (npts_x*npts_y,),
        #   An attribute with the units for each positioner
        #   is required.

    def write_file_header(self, h5parent, md=None):
        """optional header metadata"""
        if md is None:
            md = {}
        timestamp = datetime.datetime.now().isoformat(
            sep=" ", timespec="seconds"
        )
        logger.debug("timestamp: %s", str(timestamp))

        # give the HDF5 root some more attributes
        h5parent.attrs["file_name"] = h5parent.filename
        h5parent.attrs["file_time"] = timestamp
        instrument_name = md.get("instrument")
        if instrument_name is not None:
            h5parent.attrs["instrument"] = instrument_name
        h5parent.attrs["creator"] = __file__  # TODO: better choice?
        h5parent.attrs["HDF5_Version"] = h5py.version.hdf5_version
        h5parent.attrs["h5py_version"] = h5py.version.version

    def write_new_file(self, output_filename, md=None):
        """Write the complete NeXus file."""
        if md is None:
            md = {}
        with h5py.File(output_filename, "w") as root:
            self.write_file_header(root, md=md)
            self.create_entry_group(root, md=md)
