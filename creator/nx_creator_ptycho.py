import datetime
import h5py
import logging
import os
import numpy as np

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
NX_APP_DEF_NAME = "NXptycho"
NX_EXTENSION = ".nxs"

class NXCreator:
    """
    Manage NeXus file creation for Ptychography data.

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
    
    def __init__(self, h5root):
        self._h5root = h5root

    def _init_group(self, h5parent, nm, NX_class):
        """Common steps to initialize a NeXus HDF5 group."""
        group = h5parent.create_group(nm)
        group.attrs["NX_class"] = NX_class
        return group

    def _create_dataset(self, group, name, value, chunk_size=None, auto_chunk=False, **kwargs):
        """
        use this to create datasets in different (sub-)groups
        """
        if value is None:
            return
        if chunk_size is not None and auto_chunk is False:
            ds = group.create_dataset(name, data=value, chunks=chunk_size)
        elif auto_chunk is True:
            ds = group.create_dataset(name, data=value, chunks=auto_chunk)
        else:
            ds = group.create_dataset(name, data=value)
        for k, v in kwargs.items():
            ds.attrs[k] = v
        ds.attrs["target"] = ds.name
        return ds

    def create_entry_group(self,
                           entry_number: int = 1,
                           experiment_description: str = None,
                           title: str = None,
                           count_entry=None):
        #TODO check if other NX converters can share this method for less duplication
        """
        all information about the measurement
        see: https://manual.nexusformat.org/classes/base_classes/NXentry.html
        """

        if entry_number is None:
            entry_name = "entry"
        else:
            # TODO how will count_entry be defined when connecting to the loader?
            entry_name = f"entry_{entry_number}"
        group = self._init_group(self._h5root, nm=entry_name, NX_class="NXentry")

        group.create_dataset("definition", data=NX_APP_DEF_NAME)
        if experiment_description is not None:
            experiment_description = experiment_description
        else:
            experiment_description = 'Default Ptychography experiment'
        self._create_dataset(group, "experiment_description", experiment_description)
        title = title if title is not None else "default"
        self._create_dataset(group, "title", title)
        logger.debug("title: %s", title)

        # FIXME: Check NeXus structure: point to this group for default plot
        self._h5root.attrs["default"] = group.name.split("/")[-1]
        return group

    def create_instrument_group(self,
                                h5parent,
                                name_of_instrument: str = None,
                                *args,
                                **kwargs):
        instrument_group = self._init_group(h5parent, "instrument", "NX_CHAR")
        return instrument_group

    def create_beam_group(self,
                          h5parent,
                          entry_number: int=1,
                          energy: float = None,
                          wavelength: float = None,
                          extent: float = None,
                          polarization: float = None,
                          *args,
                          **kwargs):

        """Write the NXbeam group."""
        beam_group = self._init_group(h5parent, "Beam", "NXbeam")

        self._create_dataset(beam_group, "energy", energy, unit='eV')
        self._create_dataset(beam_group, "wavelength", wavelength, unit='m')
        self._create_dataset(beam_group, "extend", extent, unit='m')
        self._create_dataset(beam_group, "polarization", polarization, unit='a.u')

    def create_detector_group(self,
                              h5parent,
                              data: np.ndarray = None,
                              distance: float = None,
                              x_pixel_size: float = None,
                              y_pixel_size: float = None,
                              *args,
                              **kwargs):

        """Write a NXdetector group."""
        detector_group = self._init_group(h5parent, "Detector", "NXdetector")

        self._create_dataset(detector_group, "distance", distance, unit='m')
        self._create_dataset(detector_group, "x_pixel_size", x_pixel_size, unit='m')
        self._create_dataset(detector_group, "y_pixel_size", y_pixel_size, unit='m')
        self._create_dataset(detector_group, "data", data, unit='m')

    def create_positioner_group(self,
                                positioner_name: str=None,
                                pos_values: float=None,
                                ):
        pass

    def create_data_group(self, h5parent, nm, current_entry, md=None):
        """ Write a NXdata group.
            describes the plottable data and related dimension scales
            items here could be HDF5 datasets or links to datasets
        """
        # TODO: will need to get and add data
        # TODO: what should be the plottable data?
        pass

### Add other groups later ###

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

    # def create_instrument_group(self, h5parent, md=None, current_entry=None):
    #     """Write the NXinstrument group."""
    #     group, md = self.__init_group__(
    #         h5parent, "instrument", "NXinstrument", md
    #     )
    #
    #     name_field = md.get("instrument", "")[f"entry_{current_entry}"]
    #     ds = group.create_dataset("name", data=name_field)
    #     ds.attrs["target"] = ds.name  # we'll re-use this
    #     logger.debug("instrument: %s", name_field)
    #
    #     self.create_beam_group(group, "beam", md=md, current_entry=current_entry)
    #     self.create_detector_group(group, "detector_1", md=md, current_entry=current_entry)
    #     #TODO allow to add different detector group data
    #     # self.create_detector_group(group, "detector_2", md=md)
    #     self.create_monitor_group(group, "monitor", md=md)
    #     for n in range(md["translation"][f"entry_{current_entry}"].shape[1]):
    #         self.create_positioner_group(group, f"positioner_{n+1}", current_entry=current_entry, count_positioner=n, md=md)



    def create_monitor_group(self, h5parent, nm, md=None):
        """Write a NXmonitor group."""
        # TODO: will need to get and add data
        pass

    def create_process_group(self, h5parent, nm, current_entry, md=None):
        """Write a NXprocess group."""
        # TODO: will need to get and add data
        pass

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
        #TODO check how this can be implemented in a better way
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
        #TODO check if this can be shared with other converters or moved to different module
        if md is None:
            md = {}
        with h5py.File(output_filename, "w") as root:
            self.write_file_header(root, md=md)
            for entry in range(1, number_of_entries+1):
            # for entry in range(1, len(md['energy'])+1):
                print(f'writing entry_{entry}')
                self.create_entry_group(root, md=md, current_entry=entry)
        root.close()
