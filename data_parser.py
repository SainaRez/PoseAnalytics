import json
import math
import matplotlib.pyplot as plt
import numpy as np


"""
NOTES:

the number of points for each box is not the same in different loops. 
Does timing matter in measuring accuracy?

One loop might not have a box activated at all. What to do?

How to calculate the accuracy?

Why are there zeros?

"""


def get_data(file_path):
    with open(file_path) as stats_file:
        data = json.load(stats_file)
    
    data = data[0]
    return data


def get_shortest_loop(data):
    shortest_loop = 0
    for i in range(len(data)):
        if len(data[i]) <= len(data[shortest_loop]):
            shortest_loop = i

    #print(shortest_loop)
    return shortest_loop


def get_distance(joints1, joints2):
    joint_distance = []
    sum = 0
    for joint_index in range(min(len(joints1), len(joints2))):
        if joint_index % 10 == 0:
            print("JOINTS 1: ", joints1[joint_index], "JOINTS 2: ", joints2[joint_index])
            #pass
        
        x = (joints1[joint_index]["x"] - joints2[joint_index]["x"]) ** 2
        y = (joints1[joint_index]["y"] - joints2[joint_index]["y"]) ** 2
        z = (joints1[joint_index]["z"] - joints2[joint_index]["z"]) ** 2

        distance = math.sqrt(x + y + z)
        joint_distance.append(distance)
        sum += distance
    average = sum/(min(len(joints1), len(joints2)))
    return joint_distance, average



def print_box_data(box):
    for i in range(len(box)):
        print(box[i], "\n")



def put_box_data_in_list(box_data):

    box_data_dicts = []
    for i in range(len(box_data)):
        box_data_dicts.append(box_data[i]['pose'][0]['joints'])

    #print_box_data(box_data_dicts)
    return box_data_dicts



def interpolate_points(shortest_loop_box, current_loop_box):
    shortest_loop_box_data = put_box_data_in_list(shortest_loop_box)
    current_loop_box_data = put_box_data_in_list(current_loop_box)
    
    new_interpolated_box = []

    if (len(shortest_loop_box_data) < len(current_loop_box_data)):
        coefficient = math.ceil(len(current_loop_box_data)/len(shortest_loop_box_data))
        box = current_loop_box_data
        flag = 'current'

    if (len(shortest_loop_box_data) > len(current_loop_box_data)):
        coefficient = math.ceil(len(shortest_loop_box_data)/len(current_loop_box_data))
        box = shortest_loop_box_data
        flag = 'shortest'

        
        for i in range(math.floor(len(box)/coefficient)):
            
            temp_joint_dict = {}
            dict_list = []
            j = i*coefficient
            
            for joint_index in range(32):
                
                c = 0
                temp_j = j
                x_sum = 0
                y_sum = 0
                z_sum = 0
                
                while c < coefficient:
                    #print("c: ", c)
                    #print("temp_j: ", temp_j)
                    x_sum += box[temp_j][joint_index]['x']
                    y_sum += box[temp_j][joint_index]['y']
                    z_sum += box[temp_j][joint_index]['z']  
                    c += 1
                    temp_j += 1

                temp_joint_dict['x'] = x_sum / coefficient
                temp_joint_dict['y'] = y_sum /coefficient
                temp_joint_dict['z'] = z_sum / coefficient
                
                # new_interpolated_box[i][joint_index] = temp_joint_dict
                dict_list.append(temp_joint_dict)
                #new_interpolated_box[i].append(temp_joint_dict)
            new_interpolated_box.append(dict_list)
        
        if flag == 'current':
            current_loop_box_data = new_interpolated_box 
        elif flag == 'shortest':
            shortest_loop_box_data = new_interpolated_box 

    return shortest_loop_box_data, current_loop_box_data


def normalize_accuracy(accuracy_list):
    max_val = 0
    #normalized_accuracy_list = []

    for i in accuracy_list:
        for val in i.values():
            if val > max_val:
                max_val = val
    
    for loop_index, loop_val in enumerate(accuracy_list):
        #normalized_box = {}
        for key in loop_val.keys():
            accuracy_list[loop_index][key] = accuracy_list[loop_index][key]/max_val

    return accuracy_list


def get_accuracy(data, shortest_loop):
    
    boxes = ['notchair-0.6129701841008188', 'notchair-0.1380646850436077', 'notchair-0.12773989756762405', 'notchair-0.5470203078667342', 'notchair-0.8918255995143329']
    time = False
    all_accuracies = []
    fig = plt.figure()
    ax1 = fig.add_subplot(321)
    ax2 = fig.add_subplot(322)
    ax3 = fig.add_subplot(323)
    ax4 = fig.add_subplot(324)
    ax5 = fig.add_subplot(325)
    box_plots = [ax1, ax2, ax3, ax4, ax5]


    for l_index, loop in enumerate(data):
        
        single_loop_accuracy_values = {}
        
        for b_index, box in enumerate(boxes):

            shortest_box_data = []
            current_box_data = []


            counter_sh = 0
            for x in data[shortest_loop]['points']:
                if x['sequenceId'] == box:
                    shortest_box_data.append(x)
                    counter_sh += 1

            
            counter_current = 0
            for y in data[l_index]['points']:
                if y['sequenceId'] == box:
                    current_box_data.append(y)
                    counter_current += 1

            
            box_accuracy_points = {}
            accuracy = 0
            j = 0
            joint_distance_list = []
            if time == True:
                print("Entered time true")
                for j in range(min(counter_sh, counter_current)):
                    joint_distance_list, accuracy = get_distance(shortest_box_data[j]['pose'][0]['joints'], current_box_data[j]['pose'][0]['joints'])
            else:
                print("Entered time false")
                shortest_box, current_box = interpolate_points(shortest_box_data, current_box_data)
                for j in range(min(len(shortest_box), len(current_box))):
                    joint_distance_list, accuracy = get_distance(shortest_box[j], current_box[j])
                 
            box_accuracy_points[j] = accuracy

            print("JOINT DISTANCE LIST: \n")
            print(joint_distance_list, "\n")
            box_plots[b_index].plot([*range(0, len(joint_distance_list))], joint_distance_list, label=l_index)
            
            acc_sum = 0
            for acc in box_accuracy_points.values():
                acc_sum += acc

            box_accuracy_value = acc_sum/len(box_accuracy_points)

            single_loop_accuracy_values[box] = box_accuracy_value
            
        all_accuracies.append(single_loop_accuracy_values)

    accuracies = normalize_accuracy(all_accuracies) 
    # for elem in range(len(accuracies)):
    #     print('Loop Number: ', elem, "\n")
    #     print(all_accuracies[elem], "\n")

    #print(accuracies)
    #plot_accuracy(accuracies)

    for index, box_plot in enumerate(box_plots):
        box_plot.set_xlabel("Timestep")
        box_plot.set_ylabel("Distance")
        box_plot.set_title(boxes[index])

    #plt.set_title("Distance vs Time")
    plt.legend()
    plt.show()

    return accuracies
                

def plot_accuracy(accuracy_list):
    accuracy_per_box = {'notchair-0.6129701841008188': [] , 'notchair-0.1380646850436077' : [], 'notchair-0.12773989756762405' : [], 'notchair-0.5470203078667342' : [], 'notchair-0.8918255995143329': []}
    for i in range(len(accuracy_list)):
        for key in accuracy_list[i].keys():
            accuracy_per_box[key].append(accuracy_list[i][key])
    # print (accuracy_per_box)

    # my_list = [*range(0, len(accuracy_per_box['notchair-0.6129701841008188']))]
    # print(my_list)

    for key in accuracy_per_box:
        plt.plot([*range(0, len(accuracy_per_box[key]))], accuracy_per_box[key], label=key)

    plt.legend()
    plt.show()



if __name__ == "__main__":
    path = './stats.json'
    data_points = get_data(path)
    shortest_loop_index = get_shortest_loop(data_points)
    get_accuracy(data_points, shortest_loop_index)

    # path = './loops.json'
    # data_points = get_data(path)
    # shortest_loop_index = 0
    # get_accuracy(data_points, shortest_loop_index)


    # Matrix Profile for getting the Motifs that compare the singular actions
    # Sparse optical flow for tracking points. 
    # #Key point detection and which ones I should track and you figure out what happens between the two frames
    # Dense optical flow (better)
    # umap for reducing dimensionality *(better to use variational autoencoder)

    #Three methods of using pose data, neural network and using Sparse optical flow





