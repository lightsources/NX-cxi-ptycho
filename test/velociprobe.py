"""Test conversion from velociprobe data to nexus.

Expects this dataset
https://drive.google.com/drive/folders/1jIBwDuBcYVFkWvKJwLuONPYMo7ja5_Jz in the
test/data folder.
"""


from nxptycho.converter import velociprobe2nexus


if __name__ == "__main__":

    velociprobe2nexus(
        master_path="./data/fly001/fly001_master.h5",
        position_path="./data/fly001/fly001_pos.csv",
        nexus_path="./data/fly001.nx",
    )
