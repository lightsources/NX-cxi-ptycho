"""
    This file serves the purpose to provide a simple dictionary that mimics the NeXus structure of the
    NXptycho defintion as described in the NXptycho.nxdl.xml file
    This originated to start off a simple integration of writing NXptycho NeXus structure at the
    COSMIC Imaging beamline at ALS after the frames underwent pre-processing.
"""

groups = {
    "instrument": "entry/instrument/",
    "beam": "entry/instrument/beam/",
    "detector": "entry/instrument/detector/",
    "detector_transformations": "entry/instrument/detector/transformations",
    "sample": "entry/sample/",
    "sample_transformations": "entry/instrument/sample/transformations",
}

datasets = {
    "definition": "entry/definition",
    "experiment_description": "entry/experiment_description",
    "title": "entry/title",
    # instrument fields
    "instrument_name": groups["instrument"] + "instrument_name",
    # beam fields
    "energy": groups["beam"] + "incident_beam_energy",
    # detector fields
    "x_pixel_size": groups["detector"] + "x_pixel_size",
    "y_pixel_size": groups["detector"] + "y_pixel_size",
    "distance": groups["detector"] + "distance",
    "data": groups["detector"] + "data",
    "x_translation": groups["detector_transformations"] + "x_translation",
    "y_translation": groups["detector_transformations"] + "y_translation",
    "z_translation": groups["detector_transformations"] + "z_translation",
    # sample fields
    "positioner_1_value": groups["sample"] + "positioner_1/raw_value",
    "positioner_1_name": groups["sample"] + "positioner_1/name",
    "positioner_2_value": groups["sample"] + "positioner_2/raw_value",
    "positioner_2_name": groups["sample"] + "positioner_2/name",
    "x_coarse_translation": groups["sample_transformations"] + "x_coarse_translation",
    "y_coarse_translation": groups["sample_transformations"] + "y_coarse_translation",
    "z_coarse_translation": groups["sample_transformations"] + "z_coarse_translation",
    "x_fine_translation": groups["sample_transformations"] + "x_fine_translation",
    "y_fine_translation": groups["sample_transformations"] + "y_fine_translation",
    "z_fine_translation": groups["sample_transformations"] + "z_fine_translation",
    "alpha_rotation": groups["sample_transformations"] + "alpha_rotation",
    "beta_rotation": groups["sample_transformations"] + "beta_rotation",
    "gamma_rotation": groups["sample_transformations"] + "gamma_rotation",

}
