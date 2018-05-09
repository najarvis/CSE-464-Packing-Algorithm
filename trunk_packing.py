"""Box packing algorithm for CSE 464.

Copyright (c) 2018 - Nick Jarvis & Nick Wayne
"""

import sys
from timeit import default_timer as timer

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

def set_orientation(obj, ori):
    new_ori = [obj[ori[0]],
               obj[ori[1]],
               obj[ori[2]]]

    set_dim(obj, new_ori)

def num_sharing_dim(current_dim, volume, for_sorting=True):
    """Calculates the number of elements that are the same between the two arrays."""

    assert len(current_dim) == 6 and len(volume) == 6

    # These are the indices for each orientation
    orientations = [
        (0, 1, 2),
        (0, 2, 1),
        (1, 0, 2),
        (1, 2, 0),
        (2, 0, 1),
        (2, 1, 0)
    ]

    # Set up the scores list
    scores = [-1] * 6

    # Test each orientation, and store its score
    for i in range(6):
        ori = orientations[i]
        test_dim = [current_dim[ori[0]], current_dim[ori[1]], current_dim[ori[2]]] + get_pos(current_dim)

        # Only score orientations that actually can fit.
        if exact_fit_works(test_dim, volume):
            scores[i] = 0
            for j in range(3):
                if test_dim[j] == volume[j]:
                    scores[i] += 1

    # If for sorting, we simply return the max of the scores.
    # If not, we return the actual orientation that scored the highest
    if not for_sorting:
        return orientations[scores.index(max(scores))]
    return max(scores)

def str_to_dim(string):
    """Takes a string like "10 5 3" and turns it into a list like
    [10, 5, 3, 0, 0, 0]"""

    return list(map(int, string.split(" "))) + [0, 0, 0]

def exact_fit_works(obj, vol):
    """Check to make sure an object in its current orientation will fit in the volume."""

    for i in range(3):
        if obj[i] > vol[i]:
            return False
    return True

def fits(obj, vol):
    """A check to make sure a volume fits."""

    try:
        assert exact_fit_works(obj, vol)
    except AssertionError as err:
        print(obj, vol)
        print("Furthest coords: {}".format([obj[i]+obj[3+i] for i in range(3)]))
        raise err

def check_valid(vol, base):
    """Check if a volume fits inside the base volume (i.e. doesn't stick out of the trunk)."""

    for i in range(3):
        assert vol[3+i] + vol[i] <= base[i]

def run(volumes, objects):
    """Does the main algorithm, and returns a list containing the dimensions
    and positions for each object."""

    finished_objects = []
    base_volume = volumes[0]

    #want_to_see = [14, 1, 13, 17, 12, 2]

    # Sort all the objects based on the largest of their dimensions
    objects = sorted(objects, key=lambda x: sorted(get_dim(x[1]), reverse=True), reverse=True)
    #objects = [o for o in objects[:] if o[0] in want_to_see]
    while objects and volumes:
        current = objects.pop(0)

        # Sort the volumes based on how many dimensions they share with the current object.
        volumes_by_fit = sorted(volumes, key=lambda v: num_sharing_dim(current[1], v), reverse=True)
        valid_volumes = [vol for vol in volumes_by_fit if can_fit(get_dim(current[1]), get_dim(vol))]

        if not valid_volumes: # Empty
            print("{} objects couldn't fit".format(len(objects)))
            print("However, the objects could fit: ")
            return finished_objects, volumes

        best_fitting = valid_volumes.pop(0)

        # set the current objects x,y,z the same as the best fitting volume
        set_pos(current[1], get_pos(best_fitting))

        num_sharing = num_sharing_dim(current[1], best_fitting)
        best_orientation = num_sharing_dim(current[1], best_fitting, False)
        set_orientation(current[1], best_orientation)

        #print("ID: {} - Going into {}".format(current[0], num_sharing))

        if num_sharing == 0:
            # Shares no dimensions with the "best fit"
            # Create 3 new volumes

            finished_objects.append(current)
            current_data = current[1]
            # Volume on top of the object added
            top_volume = current_data[:2] + [best_fitting[2] - current_data[2]] + best_fitting[3:5] + [best_fitting[5] + current_data[2]]

            # Volume on width side of the object added
            length_volume = [best_fitting[0] - current_data[0]] + best_fitting[1:3] + [best_fitting[3] + current_data[0]] + current_data[4:6]

            # Volume on length side of the object added
            width_volume = [current_data[0]] + [best_fitting[1] - current_data[1]] + best_fitting[2:4] + [best_fitting[4] + current_data[1]] + [best_fitting[5]]

            volumes.remove(best_fitting)

            try:
                check_valid(top_volume, base_volume)
                check_valid(width_volume, base_volume)
                check_valid(length_volume, base_volume)
                assert exact_fit_works(current[1], best_fitting)
            except AssertionError as err:
                print(top_volume, width_volume, length_volume)
                print(current[1])
                print(best_fitting)
                print(exact_fit_works(current[1], best_fitting))
                raise err

            volumes.append(top_volume)
            volumes.append(width_volume)
            volumes.append(length_volume)

        elif num_sharing == 1:
            # 2 possible orientations, not equivalent
            # Shares one dimension with the best fit
            # Create 2 new volumes

            swap_best = 0
            for i in range(3):
                if current[1][i] == best_fitting[i]:
                    swap_best = i
                    break

            finished_objects.append(current)
            current_data = current[1]

            if swap_best == 0:
                top_volume = current_data[:2] + [best_fitting[2] - current_data[2]] + best_fitting[3:5] + [best_fitting[5] + current_data[2]]
                side_volume = [best_fitting[0]] + [best_fitting[1] - current_data[1]] + best_fitting[2:4] + [best_fitting[4] + current_data[1]] + [best_fitting[5]]
            if swap_best == 1:
                top_volume = current_data[:2] + [best_fitting[2] - current_data[2]] + best_fitting[3:5] + [best_fitting[5] + current_data[2]]
                side_volume = [best_fitting[0] - current_data[0]] + best_fitting[1:3] + [best_fitting[3] + current_data[0]] + best_fitting[4:6]
            if swap_best == 2:
                top_volume = [best_fitting[0] - current_data[0]] + current_data[1:3] + [best_fitting[3] + current_data[0]] + best_fitting[4:6]
                side_volume = [best_fitting[0]] + [best_fitting[1] - current_data[1]] + best_fitting[2:4] + [best_fitting[4] + current_data[1]] + [best_fitting[5]]

            check_valid(top_volume, base_volume)
            check_valid(side_volume, base_volume)

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

            check_valid(created_volume, base_volume)

            volumes.remove(best_fitting)
            volumes.append(created_volume)

        elif num_sharing == 3:
            # Volume is a perfect fit for the object
            # Create no new volumes

            # set_dim(current[1], get_dim(best_fitting))
            # regardless of how the volume is oriented, we want the object oriented that way too.

            volumes.remove(best_fitting)
            finished_objects.append(current)

    return finished_objects, volumes

if __name__ == "__main__":
    VOLUMES = []
    OBJECTS = []

    TRUNCATE = False
    INPUT_TEXT = "tests/test_case1.txt"
    if len(sys.argv) > 1:
        INPUT_TEXT = sys.argv[1]
        if len(sys.argv) == 3:
            TRUNCATE = sys.argv[2].lower() == "true"

    original_vol = None
    with open(INPUT_TEXT) as f:
        VOL_STR = f.readline()
        VOLUMES.append(str_to_dim(VOL_STR))
        original_vol = str_to_dim(VOL_STR)

        OBJ_STR = f.readline()
        i = 0
        while OBJ_STR != "":
            OBJ_DATA = str_to_dim(OBJ_STR)
            OBJECTS.append([i, OBJ_DATA])
            i += 1
            OBJ_STR = f.readline()

    """
    with open("timings.csv", "w") as f:
        f.write("number of objects,time(seconds)\n")
        for i in range(1000):
            VOLUMES = [[100, 100, 100, 0, 0, 0]]
            OBJECTS = [[x, [1, 1, 1, 0, 0, 0]] for x in range(i)]
            start = timer()
            final = run(VOLUMES, OBJECTS)
            end = timer()
            f.write("{0},{1:.4f}\n".format(i, end-start))
    """
    with open("results.txt", "w") as f:
        f.write("{} {} {} {} {} {}\n".format(*original_vol))
        final = run(VOLUMES, OBJECTS)
        print("ID\tLocation\tOrientation")

        if TRUNCATE:
            for obj in final[0][:15]:
                print("{}\t{}\t{}".format(obj[0], get_pos(obj[1]), get_dim(obj[1])))
            if len(final[0]) > 15:
                print("...")
        else:
            for obj in final[0]:
                # fits(obj[1], original_vol)
                print("{}\t{}\t{}".format(obj[0], get_pos(obj[1]), get_dim(obj[1])))
                f.write("o{} {} {} {} {} {}\n".format(*obj[1]))
            for vol in final[1]:
                f.write("v{} {} {} {} {} {}\n".format(*vol))
