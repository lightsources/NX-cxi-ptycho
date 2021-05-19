import h5py
import numpy as np

from .nx_creator_ptycho import NXCreator


def velociprobe2nexus(master_path, position_path, nexus_path):
    """Convert APS velociprobe data to the new Nexus format.

    Interestingly, the Velociprobe master file is already mostly Nexus. It
    claims to follow the NXmx standard for macromolecular crystallography, but
    it also contains a bunch of nonsense in the NXTransformations.
    """

    with h5py.File(master_path, 'r+') as f, NXCreator(nexus_path) as creator:

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

        x = creator.create_positioner_group(
            h5parent=sample,
            name='horizontal',
            raw_value=positions[:, 0],
        )
        y = creator.create_positioner_group(
            h5parent=sample,
            name='vertical',
            raw_value=positions[:, 1],
        )

        transformation = creator.create_transformation_group(h5parent=sample)
        creator.create_axis(
            transformation=transformation,
            axis_name='x',
            value=x['raw_value'],
            transformation_type='translation',
            vector=np.array([1, 0, 0], dtype=float),
            offset=np.zeros(3, dtype=float),
            depends_on=".",
        )
        creator.create_axis(
            transformation=transformation,
            axis_name='y',
            value=y['raw_value'],
            transformation_type='translation',
            vector=np.array([0, 1, 0], dtype=float),
            offset=np.zeros(3, dtype=float),
            depends_on='x',
        )
