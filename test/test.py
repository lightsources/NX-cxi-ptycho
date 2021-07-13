import numpy as np

from nxptycho.creator import NXCreator


def main():
    """Create a NeXus Ptycho file of random data using only required fields.

    NXCreator is a convenience class which does the following:

        (1) keywords are automatically assigned to attributes or fields
        (2) default values are automatically provided
        (3) enforces required fields
        (4) some HDF5 hierarchy is automatically handled

    At this point, we assume the user has enough working knowledge of the
    format to call the NXCreator.create_foo() functions in the correct order.
    """

    with NXCreator('dummy.nx') as creator:

        entry = creator.create_entry_group(definition='basic')

        instrument = creator.create_instrument_group(entry=entry)

        creator.create_beam_group(
            instrument=instrument,
            incident_energy=44,
        )
        detector = creator.create_detector_group(
            instrument=instrument,
            data=np.empty((4, 32, 32), dtype=np.int16),
            distance=34,  # TODO: distance is redundant with transformation?
            x_pixel_size=244,
            y_pixel_size=244,
        )
        # NOTE: Create transformation function is slightly redundant because
        # there can only be one transformation per group.
        transformation = creator.create_transformation_group(h5parent=detector)
        creator.create_axis(
            transformation=transformation,
            axis_name='z',
            value=34,
            transformation_type='translation',
            vector=np.array([0, 0, 1], dtype=float),
            offset=np.zeros(3, dtype=float),
            depends_on=".",
        )

        sample = creator.create_sample_group(entry=entry, )

        theta = creator.create_positioner_group(
            h5parent=sample,
            name='rotation',
            raw_value=np.empty(7),
        )
        x = creator.create_positioner_group(
            h5parent=sample,
            name='horizontal',
            raw_value=np.empty(7),
        )
        y = creator.create_positioner_group(
            h5parent=sample,
            name='vertical',
            raw_value=np.empty(7),
        )

        transformation = creator.create_transformation_group(h5parent=sample)
        creator.create_axis(
            transformation=transformation,
            axis_name='rotation',
            value=theta['raw_value'],  # value is linked from positioner group
            transformation_type='rotation',
            vector=np.array([0, 1, 0], dtype=float),
            offset=np.zeros(3, dtype=float),
            depends_on=".",
        )
        creator.create_axis(
            transformation=transformation,
            axis_name='x',
            value=x['raw_value'],
            transformation_type='translation',
            vector=np.array([1, 0, 0], dtype=float),
            offset=np.zeros(3, dtype=float),
            depends_on="rotation",
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


if __name__ == "__main__":
    main()
