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


class MissingRequiredDataError(TypeError):
    pass


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

    def __init__(self, output_filename):
        self._output_filename = output_filename
        self.entry_group_name = None
        self.instrument_group_name = None
        self.detector_group = None
        self.beam_group = None
        self.monitor_group = None
        self.positioner_group = None

    def _init_group(self, h5parent, name, NX_class):
        """Common steps to initialize a NeXus HDF5 group."""
        group = h5parent.create_group(name)
        group.attrs["NX_class"] = NX_class
        print(group.name)
        return group

    def __enter__(self):
        """Write the complete NeXus file."""
        #TODO check how this can be shared with other converters or moved to different module
        with h5py.File(self._output_filename, "w") as file:
            self.write_file_header(file)
        return self

    def __exit__(self, type, value, traceback):
        if type is TypeError:
            raise MissingRequiredDataError(
                'Check the above TypeError; data required for the NXPtycho'
                ' format was possibly omitted.') from value

    def write_file_header(self, output_file):
        """optional header metadata"""
        #TODO check how this can be implemented in a better way
        timestamp = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
        logger.debug("timestamp: %s", str(timestamp))
        # give the HDF5 root some more attributes
        output_file.attrs["file_name"] = output_file.filename
        output_file.attrs["file_time"] = timestamp
        #TODO does instrument name belong in header?
        output_file.attrs["instrument"] = "instrument_name"
        output_file.attrs["creator"] = __file__  # TODO: better choice?
        output_file.attrs["HDF5_Version"] = h5py.version.hdf5_version
        output_file.attrs["h5py_version"] = h5py.version.version

    def _create_dataset(self, group, name, value, chunk_size=None, auto_chunk=False, **kwargs):
        """
        use this to create datasets in different (sub-)groups
        """
        if value is None:
            return
        ds = group.create_dataset(name, data=value)
        for k, v in kwargs.items():
            ds.attrs[k] = v
        ds.attrs["target"] = ds.name
        return ds

    def create_entry_group(self,
                           entry_number: int = None,
                           experiment_description: str = None,
                           title: str = None):
        #TODO check if other NX converters can share this method for less duplication
        """
        all information about the measurement
        see: https://manual.nexusformat.org/classes/base_classes/NXentry.html
        """

        if entry_number is None:
            entry_name = "entry"
        else:
            entry_name = f"entry_{entry_number}"

        with h5py.File(self._output_filename, "a") as file:
            entry_group = self._init_group(file, entry_name, "NXentry")
            self.entry_group_name = entry_group.name

            entry_group.create_dataset("definition", data=NX_APP_DEF_NAME)
            if experiment_description is not None:
                experiment_description = experiment_description
            else:
                experiment_description = 'Default Ptychography experiment'
            self._create_dataset(entry_group, "experiment_description", experiment_description)
            title = title if title is not None else "default"
            self._create_dataset(entry_group, "title", title)
            logger.debug("title: %s", title)

            # FIXME: Check NeXus structure: point to this group for default plot
            file.attrs["default"] = entry_group.name.split("/")[-1]


    def create_instrument_group(self,
                                h5parent,
                                name_of_instrument: str = None,
                                *args,
                                **kwargs):
        with h5py.File(self._output_filename, "a") as file:
            instrument_group = self._init_group(file[self.entry_group_name], "instrument", "NXinstrument")
            self.instrument_group_name = instrument_group.name


    def create_beam_group(self,
                          energy: float,
                          entry_number: int=1,
                          wavelength: float = None,
                          extent: float = None,
                          polarization: float = None,
                          *args,
                          **kwargs):

        """Write the NXbeam group."""
        with h5py.File(self._output_filename, "a") as file:
            self.beam_group = self._init_group(file[self.instrument_group_name], "Beam", "NXbeam")

            self._create_dataset(self.beam_group, "energy", energy, unit='eV')
            self._create_dataset(self.beam_group, "wavelength", wavelength, unit='m')
            self._create_dataset(self.beam_group, "extend", extent, unit='m')
            self._create_dataset(self.beam_group, "polarization", polarization, unit='a.u')

    def create_detector_group(self,
                              data: np.ndarray,
                              distance: float,
                              x_pixel_size: float,
                              y_pixel_size: float,
                              *args,
                              **kwargs):

        """Write a NXdetector group."""
        with h5py.File(self._output_filename, "a") as file:
            #TODO adding multiple detector entries (add counting index)
            self.detector_group = self._init_group(file[self.instrument_group_name], "Detector", "NXdetector")

            self._create_dataset(self.detector_group, "distance", distance, unit='m')
            self._create_dataset(self.detector_group, "x_pixel_size", x_pixel_size, unit='m')
            self._create_dataset(self.detector_group, "y_pixel_size", y_pixel_size, unit='m')
            self._create_dataset(self.detector_group, "data", data, unit='m')

    def create_positioner_group(self,
                                positioner_name: str=None,
                                count_group: int=1,
                                pos_values: float=None,
                                ):
        #TODO take care of positioner name or counting (count_group)
        with h5py.File(self._output_filename, "a") as file:
            self.positioner_group = self._init_group(file[self.instrument_group_name], f"Positioner_{count_group}", "NXpositioner")


    def create_monitor_group(self):
        """Write a NXmonitor group."""
        # TODO: will need to get and add data
        pass

    def create_data_group(self,
                          entry_number):
        """ Write a NXdata group.
            describes the plottable data and related dimension scales
            items here could be HDF5 datasets or links to datasets
        """
        # TODO: will need to get and add data
        # TODO: what should be the plottable data?
        pass

### Add other groups later ###

    def create_process_group(
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

