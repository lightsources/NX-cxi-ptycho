import os
import unittest

import numpy as np

from nxptycho.creator import NXCreator


__folder__ = os.path.dirname(__file__)


def test_creator():
    """Create a NeXus Ptycho file of random data using only required fields.

    NXCreator is a convenience class which does the following:

        (1) keywords are automatically assigned to attributes or fields
        (2) default values are automatically provided
        (3) enforces required fields
        (4) some HDF5 hierarchy is automatically handled

    At this point, we assume the user has enough working knowledge of the
    format to call the NXCreator.create_foo() functions in the correct order.
    """

    with NXCreator(f'{__folder__}/data/dummy.nx') as creator:

        entry = creator.create_entry_group(definition='NXptycho')

        instrument = creator.create_instrument_group(
            h5parent=entry,
            name='imaginary beamline',
        )

        creator.create_beam_group(
            h5parent=instrument,
            incident_beam_energy=44,
            energy_units='eV',
        )
        detector = creator.create_detector_group(
            h5parent=instrument,
            data=np.empty((4, 32, 32), dtype=np.int16),
            data_units='counts',
            distance=34,  # TODO: distance is redundant with transformation?
            distance_units='cm',
            x_pixel_size=244,
            y_pixel_size=244,
            pixel_size_units='µm',
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

        sample = creator.create_sample_group(h5parent=entry, )

        theta = creator.create_positioner_group(
            h5parent=sample,
            name='rotation',
            raw_value=np.empty(7),
            positioner_index=0,
        )
        x = creator.create_positioner_group(
            h5parent=sample,
            name='horizontal',
            raw_value=np.empty(7),
            positioner_index=1,
        )
        y = creator.create_positioner_group(
            h5parent=sample,
            name='vertical',
            raw_value=np.empty(7),
            positioner_index=2,
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
    unittest.main()
