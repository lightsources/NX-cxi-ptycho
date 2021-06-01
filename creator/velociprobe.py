import h5py
import numpy as np

from .nx_creator_ptycho import NXCreator


def velociprobe2nexus(master_path, position_path, nexus_path):
    """Convert APS velociprobe data to the new Nexus format.

    Because the Velociprobe is collected with a Dectris Eiger detector the
    master file is very Nexus-like. It claims to follow the NXmx standard for
    macromolecular crystallography, but it also contains a bunch of nonsense
    in the NXTransformations.
    """

    with h5py.File(master_path, 'r') as f, NXCreator(nexus_path) as creator:

        entry = creator.create_entry_group(definition='basic')

        instrument = creator.create_instrument_group(entry=entry)

        # The beam group already exists in velociprobe data
        instrument['beam'] = h5py.ExternalLink(
            f.filename,
            '/entry/instrument/beam',
        )
        print('/entry/instrument/beam')

        # Collect the data and combine into a single virtual dataset. We have
        # to check whether each dataset is valid because Velociprobe data often
        # has empty links due to the links being created before the data is
        # actually collected.
        total_frame_count = 0
        frame_chunks = []
        for chunk in f['/entry/data'].values():
            if chunk is not None:
                frame_chunks.append(h5py.VirtualSource(chunk))
                chunk_shape = chunk.shape
                total_frame_count += chunk_shape[0]

        layout = h5py.VirtualLayout(
            shape=(total_frame_count, *chunk_shape[1:]),
            dtype=frame_chunks[0].dtype,
        )
        for i, chunk in zip(
                range(0, total_frame_count, chunk_shape[0]),
                frame_chunks,
        ):
            layout[i:i + chunk_shape[0]] = chunk

        # The detector group already exists in velociprobe data, but it is
        # filled with garbage, so we must copy the entries we need instead of
        # linking the whole group.
        detector = creator.create_detector_group(
            instrument=instrument,
            data=layout,
            # TODO: distance is redundant with transformation?
            distance=f['/entry/instrument/detector/detector_distance'][(
            )],  # meter
            x_pixel_size=f['/entry/instrument/detector/x_pixel_size'][(
            )],  # meter
            y_pixel_size=f['/entry/instrument/detector/y_pixel_size'][(
            )],  # meter
        )
        # TODO: Are unit attributes? Copied from source automatically or
        # overwritten by NXCreator?

        # NOTE: Create transformation function is slightly redundant because
        # there can only be one transformation per group.
        transformation = creator.create_transformation_group(h5parent=detector)
        creator.create_axis(
            transformation=transformation,
            axis_name='z',
            value=f['/entry/instrument/detector/detector_distance'][(
            )],  # meter,
            transformation_type='translation',
            vector=np.array([0, 0, 1], dtype=float),
            offset=np.zeros(3, dtype=float),
            depends_on=".",
        )

        positions = np.genfromtxt(position_path, delimiter=",")  # m

        sample = creator.create_sample_group(entry=entry, )

        transformation = creator.create_transformation_group(h5parent=sample)
        # Velociprobe sample positioner is horizontal stage on rotation stage
        # on vertical stage.
        creator.create_axis(
            depends_on='.',
            transformation=transformation,
            axis_name='vertical',
            value=positions[:, 1],
            units='m',
            transformation_type='translation',
            vector=np.array([0, 1, 0], dtype=float),
            offset=np.zeros(3, dtype=float),
        )
        creator.create_axis(
            depends_on="vertical",
            transformation=transformation,
            axis_name='rotation',
            # TODO: ExternalLink not allowed because we add additional
            # attributes?
            value=f['entry/sample/goniometer/chi'][0],
            units=f['entry/sample/goniometer/chi'].attrs['units'],
            transformation_type='rotation',
            vector=np.array([0, 1, 0], dtype=float),
            offset=np.zeros(3, dtype=float),
        )
        creator.create_axis(
            depends_on="rotation",
            transformation=transformation,
            axis_name='horizontal',
            value=positions[:, 0],
            units='m',
            transformation_type='translation',
            vector=np.array([1, 0, 0], dtype=float),
            offset=np.zeros(3, dtype=float),
        )
