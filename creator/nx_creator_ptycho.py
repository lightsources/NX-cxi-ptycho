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
# [ ] update NXCreator usage documentation

logger = logging.getLogger(__name__)
NX_APP_DEF_NAME = "NXptycho"
NX_EXTENSION = ".nxs"


class NXCreator:
    """Manage NeXus file creation for Ptychography data.

    USAGE::
        example_metadata = dict(
            instrument="ptycho demo",
            title="The first NX ptycho file demo",
            experiment_description="simple",
            other="some other metadata that will be ignored"
        )
        example_hdf5_filename = "/tmp/ptycho.nx"

        with NX_Creator(example_hdf5_filename) as creator:

            creator.create_entry_group(example_metadata)

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
        self.detector_group_name = None
        self.beam_group = None
        self.monitor_group = None
        self.positioner_group = None
        self.file_handle = None

    def __enter__(self):
        """Write a basic NeXus file.

        This is only called once per file
        writing some header information. Then file is closed.
        Actual data will be added opening the file in "a" mode
        see below in the different create_group methods
        """
        self.file_handle = h5py.File(self._output_filename, "w")
        self.write_file_header(self.file_handle)
        return self

    def __exit__(self, type, value, traceback):
        self.file_handle.close()

    def write_file_header(self, output_file: h5py.File):
        """optional header metadata for writing a new file"""
        # TODO check how this can be implemented in a better way
        timestamp = datetime.datetime.now().isoformat(
            sep=" ",
            timespec="seconds",
        )
        # intentionally time stamp is recorded on file initialization only
        # each dataset can have on time stamps when adding it later
        logger.debug("timestamp: %s", str(timestamp))
        output_file.attrs["start_time"] = timestamp
        # give the HDF5 root some more attributes
        output_file.attrs["file_name"] = output_file.filename
        output_file.attrs["file_time"] = timestamp
        # TODO does instrument name belong in header? --> move to instrument
        # group instead
        output_file.attrs["instrument"] = "instrument_name"
        output_file.attrs["creator"] = __file__  # TODO: better choice?
        output_file.attrs["HDF5_Version"] = h5py.version.hdf5_version
        output_file.attrs["h5py_version"] = h5py.version.version
        # TODO what time stamp do we need? postpone this discussion for now!
        # output_file.attrs["end_time"] = timestamp

    def _init_group(self, h5parent: h5py.Group, name: str, NX_class: str):
        """Conveniently initialize a NeXus HDF5 group."""
        group = h5parent.create_group(name)
        group.attrs["NX_class"] = NX_class
        print(group.name)
        return group

    def _create_dataset(self,
                        group: h5py.Group,
                        name: str,
                        value: np.ndarray,
                        chunk_size: int = None,
                        auto_chunk: bool = False,
                        **kwargs):
        """Conveniently create a dataset in a Nexus HDF5 group."""
        if value is None:
            return
        ds = group.create_dataset(name, data=value)
        for k, v in kwargs.items():
            ds.attrs[k] = v
        ds.attrs["target"] = ds.name
        return ds

    # TODO: check if other NX converters can share this method for less duplication
    def create_entry_group(self,
                           definition: str = NX_APP_DEF_NAME,
                           entry_index: int = None,
                           experiment_description: str = None,
                           title: str = None):
        """ Create Entry group
        All information about the measurement.
        see: https://manual.nexusformat.org/classes/base_classes/NXentry.html

        :param defnition: Official NeXus NXDL schema to which this file conforms in our case NXptycho or NXcxi_ptycho
        :param entry_index: index number of the entry for multi-scan/projection datasets
        :param args:
        :param kwargs:
        :return entry_group
        """
        if entry_index is None:
            entry_name = "entry"
        else:
            entry_name = f"entry_{entry_index}"

        entry_group = self._init_group(self.file_handle, entry_name, "NXentry")
        self.entry_group_name = entry_group.name

        entry_group.create_dataset("definition", data=definition)
        if experiment_description is not None:
            experiment_description = experiment_description
        else:
            experiment_description = 'Default Ptychography experiment'
        self._create_dataset(entry_group,
                             "experiment_description",
                             experiment_description)
        title = title if title is not None else "default"
        self._create_dataset(entry_group, "title", title)
        logger.debug("title: %s", title)

        # FIXME: Check NeXus structure: point to this group for default plot
        self.file_handle.attrs["default"] = entry_group.name.split("/")[-1]

        return entry_group

    def create_instrument_group(self,
                                parent: h5py.Group,
                                name: str,
                                instrument_index: int = None,
                                *args,
                                **kwargs):
        """
        Create instrument group

        :param parent: h5 parent in this case is entry group
        :param name: actual name of the instrument/beamline/endstation
        :param instrument_number: index number of the instrument that created the data
        :param args:
        :param kwargs:
        :return:
        """

        if instrument_index is None:
            instrument_name = "instrument"
        else:
            instrument_name = f'instrument_{instrument_index}'

        instrument_group = self._init_group(parent,
                                            instrument_name,
                                            "NXinstrument")
        self._create_dataset(instrument_group, 'instrument_name', name)
        self.instrument_group_name = instrument_group.name
        return instrument_group

    def create_beam_group(self,
                          parent: h5py.Group,
                          incident_beam_energy: float,
                          energy_untis: str,
                          wavelength_units: str = None,
                          extent_untis: str = None,
                          beam_index: int = None,
                          wavelength: float = None,
                          extent: float = None,
                          polarization: float = None,
                          *args,
                          **kwargs):
        """Create the NXbeam group.

        :param parent: h5 parent in this case is instrument group
        :param incident_beam_energy: incident beam energy in units of energy
        :param wavelength: incident wavelength energy in units of length
        :param extent: spatial extend of the beam
        :param polarization: polarization of the beam
        :param beam_index: index number of the beam that created the data
        :param args:
        :param kwargs:
        :return:
        """

        if beam_index is None:
            beam_name = "beam"
        else:
            beam_name = f'beam{beam_index}'

        self.beam_group = self._init_group(parent,
                                           #self.file_handle[self.instrument_group_name],
                                           beam_name,
                                           "NXbeam")

        self._create_dataset(self.beam_group,
                             "energy",
                             incident_beam_energy,
                             units=energy_untis)
        self._create_dataset(self.beam_group,
                             "wavelength",
                             wavelength,
                             units=wavelength_units)
        self._create_dataset(self.beam_group,
                             "extent", extent,
                             units=extent_untis)
        self._create_dataset(self.beam_group,
                             "polarization",
                             polarization)
        return self.beam_group

    def create_detector_group(self,
                              parent,
                              data: np.ndarray,
                              data_units: str,
                              distance: float,
                              distance_units: str,
                              x_pixel_size: float,
                              y_pixel_size: float,
                              pixel_size_units: str,
                              detector_index: int = None,
                              *args,
                              **kwargs):
        """
        Write a NXdetector group.

        :param parent: h5 parent in this case is instrument group
        :param data: actual diffraction patterns as a 3D array [npts, frame_size_x, frame_size_y]
        :param distance distance between sameple and detector
        :param x_pixel_size pixel size of the detector in horizontal direction
        :param y_pixel_size pixel size of the detector in vertical direction
        :param detector_index: index number of the detector that created the data
        :param args:
        :param kwargs:
        :return:
        """

        if detector_index is None:
            detector_name = "detector"
        else:
            detector_name = f'detector{detector_index}'

        self.detector_group = self._init_group(parent,
                                               #self.file_handle[self.instrument_group_name],
                                               detector_name,
                                               "NXdetector")
        self.detector_group_name = self.detector_group.name

        self._create_dataset(self.detector_group,
                             "distance",
                             distance,
                             unit=distance_units)
        self._create_dataset(self.detector_group,
                             "x_pixel_size",
                             x_pixel_size,
                             unit=pixel_size_units)
        self._create_dataset(self.detector_group,
                             "y_pixel_size",
                             y_pixel_size,
                             unit=pixel_size_units)
        self._create_dataset(self.detector_group,
                             "data",
                             data,
                             unit=data_units)

        return self.detector_group

    def create_sample_group(self, entry):
        """Write a NXsample group."""
        sample_group = self._init_group(entry,
                                        "sample",
                                        "NXsample")
        return sample_group

    def create_positioner_group(
                                self,
                                h5parent: h5py.Group,
                                name: str,
                                raw_value: float = None,
                                target_value: float = None,
                                positioner_index: int = None,
                                ):
        """
        Write positions

        :param h5parent: parent group is this case is the sample group
        :param name: a descriptive name of the positioner axis such as translation_x
        :param raw_value: raw values, e.g. encoder values, of the positions
        :param target_value: target values, i.e. as commanded, of the positions
        :param positioner_index: index number for the postioner
        :return:
        """
        if positioner_index is None:
            positioner_name = "positioner"
        else:
            positioner_name = f'positioner_{positioner_index}'

        self.positioner_group = self._init_group(h5parent,
                                                 positioner_name,
                                                "NXpositioner")
        self._create_dataset(group=self.positioner_group,
                             name="name",
                             value=name)

        if raw_value is not None:
            self._create_dataset(
                group=self.positioner_group,
                name='raw_value',
                value=raw_value,
            )
        if target_value is not None:
            self._create_dataset(
                group=self.positioner_group,
                name='target_value',
                value=target_value,
            )
        return self.positioner_group

    def create_transformation_group(self, h5parent: h5py.Group):
        """Create an NXTransformations group.

        seealso:: https://manual.nexusformat.org/classes/base_classes/NXtransformations.html
        """
        transformation_group = self._init_group(
            h5parent,
            "transformations",
            "NXtransformations",
        )
        return transformation_group

    def create_axis(
        self,
        transformation: h5py.Group,
        axis_name: str,
        value: np.ndarray,
        transformation_type: str,
        vector: np.ndarray,
        offset: np.ndarray,
        offset_units: str,
        depends_on: str,
    ):
        axis = self._create_dataset(
            group=transformation,
            name=axis_name,
            value=value,
        )
        axis.attrs['transformation_type'] = transformation_type
        axis.attrs['vector'] = vector
        axis.attrs['offset'] = offset
        axis.attrs['depends_on'] = depends_on
        return axis

    def create_data_group(self, entry_number):
        """Write a NXdata group.

        Describes the plottable data and related dimension scales. Items here
        could be HDF5 datasets or links to datasets.
        """
        # TODO: will need to get and add data
        # TODO: what should be the plottable data?
        pass

### Add other groups later ###
    def create_monitor_group(self):
        """Write a NXmonitor group."""
        # TODO: will need to get and add data
        pass

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
                    nm = (f"process_{1+self.count_subgroups(group, nxclass)}")
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
