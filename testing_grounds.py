"""Box packing algorithm for CSE 464.

Copyright (c) 2018 - Nick Jarvis & Nick Wayne
"""

import sys

def can_fit(object_dim, volume):
    """Checks if an object can fit inside a volume."""

    assert len(object_dim) == len(volume)

    while object_dim:
        if max(object_dim) > max(volume):
            return False

        object_dim.remove(max(object_dim))
        volume.remove(max(volume))
    return True

def get_dim(obj):
    """Returns the dimensions of a dimension-pos list"""
    return obj[:3]

def get_pos(obj):
    """Returns the pos of a dimension-pos list"""
    return obj[3:]

def set_dim(obj, dim):
    """sets the dimensions of a dimension-pos list"""
    obj[:3] = dim

def set_pos(obj, pos):
    """sets the pos of a dimension-pos list"""
    obj[3:] = pos

def num_sharing_dim(current_dim, volume):
    """calculates the number of elements that are the same between the two arrays.
    Make sure to pass current[1][:3] in to only get the dimensions."""

    assert len(current_dim) == len(volume)
    curr_dim_copy = current_dim[:]
    vol_copy = volume[:]
    for dim in current_dim:
        if dim in vol_copy:
            curr_dim_copy.remove(dim)
            vol_copy.remove(dim)

    return 3 - len(curr_dim_copy)

def str_to_dim(string):
    """Takes a string like "10 5 3" and turns it into a list like
    [10, 5, 3, 0, 0, 0]"""

    return list(map(int, string.split(" "))) + [0, 0, 0]

def run(volumes, objects):
    """Does the main algorithm, and returns a list containing the dimensions
    and positions for each object."""

    finished_objects = []

    # Sort all the objects based on the largest of their dimensions
    objects = sorted(objects, key=lambda x: sorted(get_dim(x[1]), reverse=True), reverse=True)
    while objects and volumes:
        current = objects.pop(0)

        # Sort the volumes based on how many dimensions they share with the current object.
        volumes_by_fit = sorted(volumes, key=lambda v: num_sharing_dim(get_dim(current[1]),
                                                                       get_dim(v)))
        best_fitting = volumes_by_fit.pop(0)
        while not can_fit(get_dim(current[1]), get_dim(best_fitting)):
            if not volumes_by_fit: # Empty
                print(volumes)
                print("{} objects couldn't fit".format(len(objects)))
                sys.exit(1)

            best_fitting = volumes_by_fit.pop(0)

        # set the current objects x,y,z the same as the best fitting volume
        set_pos(current[1], get_pos(best_fitting))
        #num_sharing = len([dim for dim in current[1] if dim in best_fitting[:3]])
        num_sharing = num_sharing_dim(get_dim(current[1]), get_dim(best_fitting))

        if num_sharing == 0:
            # Shares no dimensions with the "best fit"
            # Create 3 new volumes
            finished_objects.append(current)

            # Volume on top of the object added
            top_volume = current[1][:2] + [best_fitting[2] - current[1][2]] + best_fitting[3:5] + [current[1][2]]

            # Volume on width side of the object added
            width_volume = [best_fitting[0] - current[1][0]] + best_fitting[1:3] + [best_fitting[3] + current[1][0]] + current[1][4:6]

            # Volume on length side of the object added
            length_volume = [current[1][0]] + [best_fitting[1] - current[1][1]] + best_fitting[2:4] + [best_fitting[4] + current[1][1]] + [best_fitting[5]]

            volumes.remove(best_fitting)

            volumes.append(top_volume)
            volumes.append(width_volume)
            volumes.append(length_volume)

        elif num_sharing == 1:
            # 2 possible orientations, not equivalent
            # Shares one dimension with the best fit
            # Create 2 new volumes

            # Find WHICH dimensions are shared,
            swap_index = 0
            for i in range(3):
                if current[1][i] in get_dim(best_fitting):
                    swap_index = i
            swap_best = get_dim(best_fitting).index(current[1][swap_index])
            tmp = current[1][swap_best]
            current[1][swap_best] = current[1][swap_index]
            current[1][swap_index] = tmp
            finished_objects.append(current)
            if swap_best == 0:
                top_volume = current[1][:2] + [best_fitting[2] - current[1][2]] + best_fitting[3:5] + [current[1][2]]
                side_volume = [best_fitting[0]] + [best_fitting[1] - current[1][1]] + best_fitting[2:4] + [best_fitting[4] + current[1][1]] + [best_fitting[5]]
            if swap_best == 1:
                top_volume = current[1][:2] + [best_fitting[2] - current[1][2]] + best_fitting[3:5] + [current[1][2]]
                side_volume = [best_fitting[0] - current[1][0]] + best_fitting[1:2] + [best_fitting[3] + current[1][0]] + best_fitting[3:6]
            if swap_best == 2:
                top_volume = [best_fitting[0] - current[1][0]] + current[1][1:3] + [best_fitting[3] + current[1][0]] + best_fitting[4:6]
                side_volume = [best_fitting[0]] + [best_fitting[1] - current[1][1]] + best_fitting[2:4] + [best_fitting[4] + current[1][1]] + [best_fitting[5]]

            volumes.remove(best_fitting)
            volumes.append(top_volume)
            volumes.append(side_volume)

        elif num_sharing == 2:
            # Shares two dimensions with the best fit
            # Create 1 new volume

            # Find WHICH dimensions are different and swap them. If only one differs,
            # don't do anything. For example: 10x10x2 object vs 10x10x10 volume.

            swap_indices = []
            for dim in range(3):
                if current[1][dim] != best_fitting[dim]:
                    swap_indices.append(dim)

            # swap to make the dimensions the same for the object and volume
            if len(swap_indices) == 2:
                tmp = current[1][swap_indices[0]]
                current[1][swap_indices[0]] = current[1][swap_indices[1]]
                current[1][swap_indices[1]] = tmp

            finished_objects.append(current)

            non_matching_dim = [dim for dim in range(3) if get_dim(current[1])[dim] != get_dim(best_fitting)[dim]][0]

            position_offset = [0, 0, 0]
            position_offset[non_matching_dim] += current[1][non_matching_dim]

            new_pos = get_pos(best_fitting) # position of best fitting
            new_pos[non_matching_dim] += position_offset[non_matching_dim]

            new_volume = get_dim(best_fitting)
            new_volume[non_matching_dim] -= position_offset[non_matching_dim]

            created_volume = new_volume + new_pos

            volumes.remove(best_fitting)
            volumes.append(created_volume)

        elif num_sharing == 3:
            # Volume is a perfect fit for the object
            # Create no new volumes
            set_dim(current[1], get_dim(best_fitting))
            # regardless of how the volume is oriented, we want the object oriented that way too.

            volumes.remove(best_fitting)
            finished_objects.append(current)

    return finished_objects, volumes

if __name__ == "__main__":
    VOLUMES = []
    OBJECTS = []

    INPUT_TEXT = "test_case1.txt"
    if len(sys.argv) > 1:
        INPUT_TEXT = sys.argv[1]

    with open(INPUT_TEXT) as f:
        VOL_STR = f.readline()
        VOLUMES.append(str_to_dim(VOL_STR))

        OBJ_STR = f.readline()
        i = 0
        while OBJ_STR != "":
            OBJ_DATA = str_to_dim(OBJ_STR)
            OBJECTS.append([i, OBJ_DATA])
            i += 1
            OBJ_STR = f.readline()

    final = run(VOLUMES, OBJECTS)
    print("ID\tLocation\tOrientation")
    for obj in final[0]:
        print("{}\t{}\t{}".format(obj[0], get_pos(obj[1]), get_dim(obj[1])))
