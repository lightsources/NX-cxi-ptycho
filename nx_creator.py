import datetime
import h5py
import logging
import os

# TODO
# [x] load data (in loader module)
# [x] call this code (from toNXconverter module?)

# [-] put data into the tree
# [-] add option for user input on execution
# [-] option to add multiple dataset to multiple entries
# [-] add positioner data and define names per axis

# FIXME
# [ ] check why nxs file is x times larger than the original cxi file

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
        print('H5PARENT:', h5parent)
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
                self.create_process_group(group, nm, current_entry=1, md=md)

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

    def create_beam_group(self, h5parent, nm, current_entry=None, md=None):
        """Write the NXbeam group."""
        group, md = self.__init_group__(h5parent, nm, "NXbeam", md)

        ds = group.create_dataset("energy", data=md["energy"][f"entry_{current_entry}"])
        ds.attrs["units"] = "J" #FIXME allow for other units eV | keV | J
        ds.attrs["target"] = ds.name

        #TODO Either energy or wavelength : one of these is required
        # wavelength (NX_FLOAT)
        #     @units (NX_WAVELENGTH) = A | nm
        # extent (NX_FLOAT) = Size of the beam at sample position
        #     @units (NX_LENGTH) = m
        # polarization (NX_FLOAT) = polarization vector
        #     @units ?

    def create_data_group(self, h5parent, nm, current_entry, md=None):
        """Write a NXdata group."""
        # TODO: will need to get and add data
        group, md = self.__init_group__(h5parent, nm, "NXdata", md)

        # TODO:
        # describes the plottable data and related dimension scales
        # items here could be HDF5 datasets or links to datasets
        # what should be represented here? --> tbd

    def create_detector_group(self, h5parent, nm, md=None, current_entry=None):
        """Write a NXdetector group."""
        # TODO: will need to get and add data
        group, md = self.__init_group__(h5parent, nm, "NXdetector", md)

        # FIXME no hard-coded entries --> naming helper function (addressing function)
        ds = group.create_dataset("data", data=md["data"][f"entry_{current_entry}"])
        ds.attrs["units"] = "counts"  # FIXME allow for other units
        ds.attrs["target"] = ds.name

        ds = group.create_dataset("distance", data=md["distance"][f"entry_{current_entry}"])
        ds.attrs["units"] = "m"  # FIXME allow for other units
        ds.attrs["target"] = ds.name

        ds = group.create_dataset("x_pixel_size", data=md["x_pixel_size"][f"entry_{current_entry}"])
        ds.attrs["units"] = "m" #FIXME allow for other units
        ds.attrs["target"] = ds.name

        ds = group.create_dataset("y_pixel_size", data=md["y_pixel_size"][f"entry_{current_entry}"])
        ds.attrs["units"] = "m"  # FIXME allow for other units
        ds.attrs["target"] = ds.name

        # transformation_type = ["translation", "rotation"]
        # vector =
        # FIXME Geometry (NXTransformation)
        # ds = group.create_dataset("geometry", data=)
        # ds.attrs["transformation_type"] = transformation_type[0]  # FIXME allow for other units
        # ds.attrs["vector"] = vector
        # AXISNAME (NX_NUMBER)
        # @transformation_type (NX_CHAR)
        # @vector (NX_NUMBER)

    def create_entry_group(self, h5parent, md=None, current_entry=None):
        """
        all information about the measurement
        see: https://manual.nexusformat.org/classes/base_classes/NXentry.html
        """
        group, md = self.__init_group__(h5parent, f"entry_{current_entry}", "NXentry", md)
        #print('group', group, 'md', md)

        group.create_dataset("definition", data="NXcxi_ptycho")

        experiment_description = md.get("experiment_description")
        if experiment_description is not None:
            group.create_dataset("experiment_description", data=experiment_description)

        title = md.get("title", "")
        ds = group.create_dataset("title", data=title)
        ds.attrs["target"] = ds.name  # we'll re-use this
        logger.debug("title: %s", title)

        # NeXus structure: point to this group for default plot
        h5parent.attrs["default"] = group.name.split("/")[-1]

        self.create_instrument_group(h5parent=group, md=md, current_entry=current_entry)
        self.create_data_group(group, "data", md=md, current_entry=current_entry)
        self.create_process_group(group, "process_1", current_entry=current_entry, md=md)

        return group

    def create_instrument_group(self, h5parent, md=None, current_entry=None):
        """Write the NXinstrument group."""
        group, md = self.__init_group__(
            h5parent, "instrument", "NXinstrument", md
        )

        name_field = md.get("instrument", "")[f"entry_{current_entry}"]
        ds = group.create_dataset("name", data=name_field)
        ds.attrs["target"] = ds.name  # we'll re-use this
        logger.debug("instrument: %s", name_field)

        self.create_beam_group(group, "beam", md=md, current_entry=current_entry)
        self.create_detector_group(group, "detector_1", md=md, current_entry=current_entry)
        #TODO allow to add different detector group data
        # self.create_detector_group(group, "detector_2", md=md)
        self.create_monitor_group(group, "monitor", md=md)
        for n in range(md["translation"][f"entry_{current_entry}"].shape[1]):
            self.create_positioner_group(group, f"positioner_{n+1}", current_entry=current_entry, count_positioner=n, md=md)

    def create_monitor_group(self, h5parent, nm, md=None):
        """Write a NXmonitor group."""
        # TODO: will need to get and add data
        group, md = self.__init_group__(h5parent, nm, "NXmonitor", md)

        # TODO:
        # Data [npts] (NX_FLOAT)
        #     @units (NX_ANY) = unit of the monitor data

    def create_positioner_group(self, h5parent, nm, current_entry, count_positioner, md=None):
        """Write a NXpositioner group."""
        group, md = self.__init_group__(h5parent, nm, "NXpositioner", md)

        ds = group.create_dataset("value", data=md["translation"][f"entry_{current_entry}"][:,count_positioner])
        ds.attrs["units"] = "m" #FIXME allow for other units
        ds.attrs["target"] = ds.name

        #TODO add other optional values such as raw, target
        # Name (NXchar) = define positioner name (stage axis?)
        # Value [n] (NXnumber) = n position values for positioner 1
        #     @unit (NX_ANY) = unit related to the positioner (angle or m)
        # Raw_value
        # target_value

    def create_process_group(self, h5parent, nm, current_entry, md=None):
        """Write a NXprocess group."""
        # TODO: will need to get and add data
        group, md = self.__init_group__(h5parent, nm, "NXprocess", md)

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
        instrument_name = md.get("instrument")['entry_1']
        if instrument_name is not None:
            h5parent.attrs["instrument"] = instrument_name
        h5parent.attrs["creator"] = __file__  # TODO: better choice?
        h5parent.attrs["HDF5_Version"] = h5py.version.hdf5_version
        h5parent.attrs["h5py_version"] = h5py.version.version

    def write_new_file(self, output_filename, number_of_entries=1, md=None):
        """Write the complete NeXus file."""
        if md is None:
            md = {}
        with h5py.File(output_filename, "w") as root:
            self.write_file_header(root, md=md)
            for entry in range(1, number_of_entries+1):
            # for entry in range(1, len(md['energy'])+1):
                print(f'writing entry_{entry}')
                self.create_entry_group(root, md=md, current_entry=entry)
        root.close()
