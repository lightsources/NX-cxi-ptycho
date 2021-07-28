"""Test conversion from velociprobe data to nexus.

Expects this dataset
https://drive.google.com/drive/folders/1jIBwDuBcYVFkWvKJwLuONPYMo7ja5_Jz in the
test/data folder.
"""
import os
import unittest

from nxptycho.converter import velociprobe2nexus


__folder__ = os.path.dirname(__file__)

def test_velociprobe_conversion():
    velociprobe2nexus(
        master_path=f"{__folder__}/data/fly001/fly001_master.h5",
        position_path=f"{__folder__}/data/fly001/fly001_pos.csv",
        nexus_path=f"{__folder__}/data/fly001.nx",
    )


if __name__ == "__main__":
    unittest.main()
