from sys import exit

def can_fit(object_dim, volume):

    assert len(object_dim) == len(volume)

    while object_dim:
        if max(object_dim) > max(volume):
            return False

        object_dim.remove(max(object_dim))
        volume.remove(max(volume))
    return True

def num_sharing_dim(current_dim, volume):
    # calculates the number of elements that are the same between the two arrays.
    # Make sure to pass current[1][:3] in to only get the dimensions.

    assert len(current_dim) == len(volume)
    curr_dim_copy = current_dim[:]
    vol_copy = volume[:]
    for dim in current_dim:
        if dim in vol_copy:
            curr_dim_copy.remove(dim)
            vol_copy.remove(dim)

    return 3 - len(curr_dim_copy)

def debug_print():
    print("objects:")
    if objects:
        for obj in objects:
            print("\tid={0}, l,w,h: {1},{2},{3} x,y,z:({4},{5},{6})".format(obj[0], *obj[1]))
    else:
        print("\t[]")
    print("Volumes:")
    if volumes:
        for vol in volumes:
            print("\tl,w,h: {0},{1},{2} x,y,z:({3},{4},{5})".format(*vol))
    else:
        print("\t[]")
    print("Finished Objects:")
    if finished_objects:
        for obj in finished_objects:
            print("\tid={0}, l,w,h: {1},{2},{3} x,y,z:({4},{5},{6})".format(obj[0], *obj[1]))
    else:
        print("\t[]")
    print()
    print("*" * 50)
    print()


# Initially contains the base trunk dimensions and position, will be used to hold split volumes.
# [[length, width, height, x,y,z]]
volumes = [[10, 10, 10, 0, 0, 0]]

# list of objects with the syntax: [ID, [length, width, height, x,y,z]]
objects = [[1, [1, 3, 1, 0, 0, 0]], [2, [10, 10, 5, 0, 0, 0]], [3, [10, 10, 3, 0, 0, 0]]]
finished_objects = []

# Sort all the objects based on the largest of their dimensions
objects = sorted(objects, key=lambda x: sorted(x[1][:3], reverse=True), reverse=True)
debug_print()
while objects and volumes:
    current = objects.pop(0)

    # Sort the volumes based on how many dimensions they share with the current object, and get the best fitting one.
    volumes_by_fit = sorted(volumes, key=lambda v: num_sharing_dim(current[1][:3], v[:3])) #len([dim for dim in current[1] if dim in v[:3]]))
    best_fitting = volumes_by_fit.pop(0)
    while not can_fit(current[1][:3], best_fitting[:3]):
        if len(volumes_by_fit) == 0:
            exit(1)

        best_fitting = volumes_by_fit.pop(0)

    # set the current objects x,y,z the same as the best fitting volume
    current[1][3:] = best_fitting[3:]
    #num_sharing = len([dim for dim in current[1] if dim in best_fitting[:3]])
    num_sharing = num_sharing_dim(current[1][:3], best_fitting[:3])
    print(current[1])

    if num_sharing == 0:
        print(0)
        # Shares no dimensions with the "best fit"
        # Create 3 new volumes
        # print(volumes[0])
        # print(current)
        finished_objects.append(current)

        # Volume on top of the object added
        top_volume = current[1][:2] + [volumes[0][2] - current[1][2]] + volumes[0][3:5] + [current[1][2]]

        # Volume on width side of the object added
        width_volume = [volumes[0][0] - current[1][0]] + volumes[0][1:3] + [volumes[0][3] + current[1][0]] + current[1][4:6]

        # Volume on length side of the object added
        length_volume = [current[1][0]] + [volumes[0][1] - current[1][1]] + volumes[0][2:4] + [volumes[0][4] + current[1][1]] + [volumes[0][5]]
        # print(top_volume)
        # print(width_volume)
        # print(length_volume)
        volumes.pop(0)
        volumes.append(top_volume)
        volumes.append(width_volume)
        volumes.append(length_volume)

    elif num_sharing == 1:
        print(1)
        # 2 possible orientations, not equivilent
        # Shares one dimension with the best fit
        # Create 2 new volumes

        # Find WHICH dimensions are shared,

    elif num_sharing == 2:
        print(2)
        # Shares two dimensions with the best fit
        # Create 1 new volume

        # Find WHICH dimensions are different and swap them. If only one differs, don't do anything
        # For example: 10x10x2 object vs 10x10x10 volume.

        swap_indices = []
        for i in range(3):
            if current[1][i] != best_fitting[i]:
                swap_indices.append(i)

        # swap to make the dimensions the same for the object and volume
        if len(swap_indices) == 2:
            tmp = current[1][swap_indices[0]]
            current[1][swap_indices[0]] = current[1][swap_indices[1]]
            current[1][swap_indices[1]] = tmp

        finished_objects.append(current)
        non_matching_dim = [i for i in range(3) if current[1][i] not in best_fitting[:3]][0]
        position_offset = [0, 0, 0]
        position_offset[non_matching_dim] += current[1][non_matching_dim]

        new_pos = best_fitting[3:] # position of best fitting
        new_pos[non_matching_dim] += position_offset[non_matching_dim]

        new_volume = best_fitting[:3]
        new_volume[non_matching_dim] -= position_offset[non_matching_dim]

        created_volume = new_volume + new_pos

        volumes.pop(0)
        volumes.append(created_volume)

    elif num_sharing == 3:
        print(3)
        # Volume is a perfect fit for the object
        # Create no new volumes
        current[1][:3] = best_fitting[:3]
        # regardless of how the volume is oriented, we want the object oriented that way too.
        volumes.pop(0)
        finished_objects.append(current)

    debug_print()

print("ALGORITHM COMPLETE!!!!!\n")
debug_print()
