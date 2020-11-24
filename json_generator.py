import os
import ast
import json
import matplotlib.pyplot as plt

boxes = {"notchair-0.6129701841008188":False,"notchair-0.1380646850436077":False,"notchair-0.12773989756762405":False,"notchair-0.5470203078667342":False,"notchair-0.8918255995143329":False}

# Stats is a list[0] of a list of dictionaries and each element of this list starts with startTime and includes the points key as well, 
# so each element of the list is a dictionary with keys startTime and points. Each dictionary is a loop. Points is a list of dictionaries. 
# Each dictionary has the keys time and pose, notes, sequenceFirst and sequenceID. Each element that starts with time is a dictionary and 
# refers to one line in the other file format. Pose is a list of two dictionaries. One for human and one for robot. The first dictionary has id and joints.
# Joints is a list of 33 dictionaries. Each dictionary has the x y z values. 
# notes is a dictionary of box names and true false values
# sequenceID is a string of the colliding box name

# Text file:
# Each line is one dictionary. Each dictionary has time and msg. msg is a list of dictionaries, but only has one item. This dictionary has id and joints.
# Joints is a list of dictionaries and each dict has x y z values. 

# Points: time, pose, notes, sequenceFirst, sequenceId                          Each line: time, msg
# pose: id, joints (two dictionaries)                                           msg: id, joints (it has only one dict item)  
# joints: x, y, z                                                               joints: x, y, z

loop_list = []
loop_list_element = {"points":[]}
points_element = {"time": None, "pose": [{"id": None, "joints": None}], "sequenceId": None}

def check_box_collision(point_list):

    box_3 = {"name": "notchair-0.12773989756762405", "x":-2.4603330486518047,"y":1.000000000745058,"z":1.9437374568306593,"width":6,"height":6,"depth":6}

    #box_3 = {"name": "notchair-0.12773989756762405", "x":-2.4603330486518047,"y":1.000000000745058,"z":1.9437374568306593,"width":0.8,"height":2,"depth":0.8}
    box_4 = {"name": "notchair-0.5470203078667342", "x":-4.186641944318453,"y":1.000000000745058,"z":-0.011528967213319086,"width":0.8,"height":2,"depth":0.8}

    for point in point_list:
        #print ("point[x] ", point['x'], 'point[y]')
        if (point["x"] >= (box_3["x"] - box_3["width"]/2) and 
            point["x"] <= (box_3["x"] + box_3["width"]/2) and 
            point["y"] >= (box_3["y"] - box_3["height"]/2) and 
            point["y"] <= (box_3["y"] + box_3["height"]/2) and 
            point["z"] >= (box_3["z"] - box_3["depth"]/2) and
            point["z"] <= (box_3["z"] + box_3["depth"]/2)):

            #print ("we collided 1!")
            return box_3["name"]

        elif (point["x"] >= box_4["x"] - box_4["width"]/2 and
            point["x"] <= box_4["x"] + box_4["width"]/2 and
            point["y"] >= box_4["y"] - box_4["height"]/2 and
            point["y"] <= box_4["y"] + box_4["height"]/2 and
            point["z"] >= box_4["z"] - box_4["depth"]/2 and
            point["z"] <= box_4["z"] + box_4["depth"]/2):
        
            #print ("we collided 2!")
            return box_4["name"]

        else:
            return "No Collision"


def change_x(dict_list, subject):
    #print(dict_list)
    for coord_dict in dict_list:
        if subject == "human":
            coord_dict["x"] = coord_dict["x"] * -1
        else:
            coord_dict["x"] = (coord_dict["x"] - 10) * -1
    #print(dict_list)
    return dict_list

def add_offset(dict_list):
    for coord_dict in dict_list:
        coord_dict["x"] = coord_dict["x"] - 10
    #print(dict_list)
    return dict_list

# Visualization
def plot_loop(loop_points):

    x = []
    y = []
    z = []
    x_mean =[]
    y_mean = []
    z_mean = []
    loop_count = 0


    # [[33 points], [33 points], [33 points]]
    for list_element in loop_points:
        #print("********************list_element:", list_element)
        x_sum = 0
        y_sum = 0
        z_sum = 0
        count = 0
        loop_count += 1
        for point in list_element:
            #print("############# Point:", point)
            x.append(point['x'])
            y.append(point['y'])
            z.append(point['z'])

            x_sum += point['x']
            y_sum += point['y']
            z_sum += point['z']

            count += 1
        
        x_mean.append(x_sum/count)
        y_mean.append(y_sum/count)
        z_mean.append(z_sum/count)
        
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # plt.set_xlabel("time")
    # plt.set_ylabel("x_mean")
    # plt.set_zlabel("y_mean")
    #pnt3d=ax.scatter(x,y,z,c=z)
    pnt3d=ax.scatter(range(loop_count), x_mean,y_mean,c=z_mean)

    cbar=plt.colorbar(pnt3d)
    cbar.set_label("coord")
    plt.show()
# Visualization

def plot_loop_robot(loop_points):
    x = []
    y = []
    z = []
    loop_count = 0
    for list_element in loop_points:
        loop_count += 1
        print("################ List_Element_plot: ", list_element)
        for point in list_element:
            x.append(point['x'])
            y.append(point['y'])
            z.append(point['z'])
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # plt.set_xlabel("time")
    # plt.set_ylabel("x_mean")
    # plt.set_zlabel("y_mean")
    # pnt3d=ax.scatter(x,y,z,c=z)
    pnt3d=ax.scatter(range(loop_count), x, y, c=z)

    cbar=plt.colorbar(pnt3d)
    cbar.set_label("coord")
    plt.show()


def create_json_dict(file_path, subject):
    files = os.listdir(file_path)
    for _file in files:
        dir_path = os.path.dirname(os.path.realpath(_file))
        loop_list_element = {"points":[]}
        # Visualization
        loop_points = []
        # Visualization


        with open(os.path.join(dir_path, "data", subject, _file)) as fh:
            print("FILE: ", fh)
            lines = fh.readlines()
            for line in lines:
                points_element = {"time": None, "pose": [{"id": None, "joints": None}], "sequenceId": None}

                try:
                    # print ("line ", line)
                    line_dict = json.loads(line)
                    # print ("line dict: ", line_dict, "\n")

                    joints_list = line_dict["msg"][0]["joints"]
                    # print ("joint_list: ", joints_list, '\n')
                    joints_list = change_x(joints_list, subject)
                    #joints_list = add_offset(joints_list)
                    # print ("joint_list new: ", joints_list, '\n')


                    points_element["time"] = line_dict["time"]
                    # print("joints list", joints_list)
                    points_element["pose"][0]["id"] = line_dict["msg"][0]["id"]
                    points_element["pose"][0]["joints"] = joints_list
                    # print("points element ", points_element, "\n")

                    box_name = check_box_collision(joints_list)

                    if box_name == "No Collision":
                        print("No Collision, skipping point")
                        continue
                        # pass
                    else:
                        if subject == "robot" and line_dict["msg"][0]["id"] != "mir":
                            continue                            

                        elif subject == "human" and line_dict["msg"][0]["id"] == "mir":
                            continue
                        
                        print("******************* Collision Happened ************************** ")
                        points_element["sequenceId"] = box_name
                    
                    # Visualization
                    loop_points.append(joints_list)
                    # Visualization
                    # print("points element ", points_element, "\n")

                    loop_list_element["points"].append(points_element)
                    #print("loop list elem:", loop_list_element["points"] , "\n")
                except:
                    pass
                    # print ("skipping line", line)
                
            # Visualization
            #print("loop_points:", loop_points, "\n")
            if subject == "human":
                plot_loop(loop_points)
            else:
                plot_loop_robot(loop_points)
            # Visualization


        loop_list.append(loop_list_element)

    parent_list = [loop_list]

    # print(parent_list)

    with open(subject + ".json", 'w') as outfile:

        json.dump(parent_list, outfile)

address = "data\\human"
subject = "human"
# address = "data\\robot"
# subject = "robot"

create_json_dict(address, subject)


