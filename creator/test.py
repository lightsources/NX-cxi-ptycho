import numpy as np

from nx_creator_ptycho import NXCreator


def main():
    """Create a NeXus Ptycho file of random data using only required fields.

    NXCreator is a convenience class which does the following:

        (1) keywords are automatically assigned to attributes or fields
        (2) default values are automatically provided
        (3) enforces required fields
        (4) some HDF5 hierarchy is automatically handled

    """
    with NXCreator('dummy.nx') as creator:

        creator.create_entry_group(
            entry_number=1,  # TODO: just use 'count' or 'number'
            definition='basic',
        )

        creator.create_instrument_group()
        creator.create_beam_group(incident_energy=44, )
        detector = creator.create_detector_group(
            data=np.empty((400, 1023, 513), dtype=np.int16),
            distance=34,  # TODO: distance is redundant with transformation?
            x_pixel_size=244,
            y_pixel_size=244,
        )
        creator.create_transformation(
            axis_name='z',
            value=34,
            transformation_type='translation',
            vector=np.array([0, 0, 1], dtype=float),
            offset=np.zeros(3, dtype=float),
            depends_on=".",
        )

        creator.create_sample_group()
        theta = creator.create_positioner_group(
            name='rotation',
            raw_value=np.empty(2346),
        )
        creator.create_transformation(
            axis_name='rotation',
            value=theta,
            transformation_type='rotation',
            vector=np.array([0, 1, 0], dtype=float),
            offset=np.zeros(3, dtype=float),
            depends_on=".",
        )
        x = creator.create_positioner_group(
            name='horizontal',
            raw_value=np.empty(2346),
        )
        creator.create_transformation(
            axis_name='x',
            value=x,
            transformation_type='translation',
            vector=np.array([1, 0, 0], dtype=float),
            offset=np.zeros(3, dtype=float),
            depends_on="rotation",
        )
        y = creator.create_positioner_group(
            name='vertical',
            raw_value=np.empty(2346),
        )
        creator.create_transformation(
            axis_name='y',
            value=y,
            transformation_type='translation',
            vector=np.array([0, 1, 0], dtype=float),
            offset=np.zeros(3, dtype=float),
            depends_on='x',
        )

        creator.create_data_group(
            data=detector['data'],
            x=x,
            y=y,
        )


if __name__ == "__main__":
    main()
