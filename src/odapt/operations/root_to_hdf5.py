import h5py
import awkward as ak
import uproot
from skhep_testdata import data_path

def root_to_hdf5(read_path, write_path, *, compression=None):
    out_file = h5py.File(write_path, "w")
    in_file = uproot.open(read_path)
    keys = in_file.keys()
    tree = in_file[keys[0]]
    
    for key in keys:
        print(in_file[key].classname)
        if in_file[key].classname == "TTree":
            print("here?")
            in_file[key].branches
            sub_group = out_file.create_group(in_file[key].name)
            recur_write_hdf5(in_file[key], sub_group)
        else:
            print("here")
            # if in_file[key].classname.startswith("TH"):

            # if in_file[key].classname == "TBranch": #what?
            #     shape_1 = in_file[key].num_entries
            # else:
            #     ...
            dset = out_file.create_dataset(in_file[key].name, shape=(100, 1), chunks=(20, 1))
            for chunk in dset.iter_chunks():
                dset[chunk] = [i for i in in_file[key].iterate(step_size=in_file[key].num_baskets)]


def recur_write_hdf5(root, group): # How set attributes?? Is it automatic? Check with printing gour.attrs or dataset attrs
    branches = root.branches
    for branch in branches:
        # print("classname", branch.classname)
        if branch.classname == "TTree":
            sub_group = group.create_group(branch.name)
            for branch in branches:
                print(branch)
                if branch.classname.startswith("Model_TTree") or branch.classname == "TBranch":
                    # print("Making group ", branch.name)
                    recur_write_hdf5(branch, sub_group)
        else:
            print("else?")
            shape_1 = branch.num_entries
            dset = group.create_dataset(branch.name, shape=(branch.num_entries), chunks=(branch.num_entries))
            
            if branch.classname == "TBranch" and len(branch.branches) == 0: #what?
                chunks = [chunk for chunk in dset.iter_chunks()]
                indx = 0
                for i in uproot.iterate(branch):
                    print(i)
                    dset[chunks[indx]] = i
                    indx+=1

# So iterate may be worse due to arbitrarily picked batch size? TBasket is likely better choice, but
# this may be dependent on size of baskets...bad I/O... but:
# .entries_to_ranges_or_baskets
# .num_baskets
# .basket(basket_num)
# .basket_compressed/uncompressed_bytes

tree = uproot.open(data_path("uproot-HZZ.root"))
# print(tree.keys())
root_to_hdf5(data_path("uproot-HZZ.root"), "/Users/zobil/Documents/odapt/tests/samples/mytestfile.hdf5",)
