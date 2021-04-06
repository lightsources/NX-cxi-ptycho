from creator.nx_creator_ptycho import NXCreator
import numpy as np

with NXCreator('test.nx') as creator:
    creator.create_entry_group()
    creator.create_beam_group()
