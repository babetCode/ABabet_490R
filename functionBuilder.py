"this is a drafting space for functions to be used in IMU gait analysis"

import numpy as np
from math import *
from ezc3d import c3d
import matplotlib.pyplot as plt
import pandas as pd


#multiply  two quaternions, given as 4-item lists
def multiplyQuaternion(q1, q2):
    [w1, x1, y1, z1] = [value for value in q1]
    [w2, x2, y2, z2] = [value for value in q2]
    scalar = w1*w2 - x1*x2 - y1*y2 - z1*z2
    i = w1*x2 + x1*w2 + y1*z2 - z1*y2
    j = w1*y2 + y1*w2 + z1*x2 - x1*z2
    k = w1*z2 + z1*w2 + x1*y2 -y1*x2
    return([scalar, i, j, k])


# Rotates point (3 item list) by angle (radians) around axis through origin (3 item list)
def rotateQuaternion(point, angle, axis):
    normalizedAxis = axis/np.linalg.norm(axis)
    q_inv = [cos(angle/2)]
    q = [cos(angle/2)]
    q_inv = [cos(angle/2)]
    for value in normalizedAxis:
        q.append(sin(angle/2)*value)
        q_inv.append(-sin(angle/2)*value)
    pointQuat = [0, point[0], point[1], point[2]]
    rotation = multiplyQuaternion(multiplyQuaternion(q, pointQuat), q_inv)
    result = [float(i) for i in rotation[1:]]
    roundedPoint = [round(i, 3) for i in point]
    roundedAngle = round(angle, 3)
    roundedAxis = [round(i, 3) for i in axis]
    roundedResult = [round(i, 3) for i in result]
    return(result)


# Class object for IMUs
default_orientation = np.array([[1,0,0], [0,1,0], [0,0,1]])
default_position = np.array([0,0,0])
class imu:
    def __init__(self, name, initial_axes, initial_pos):
        self.name = name
        self.local_axes = initial_axes
        self.position = initial_pos
        self.display_axes = np.array(
        [[round(xyz, 2) for xyz in axis] for axis in self.local_axes])
        self.display_position = np.array([round(xyz, 2) for xyz in self.position])
    def __str__(self):
        return f"{self.name} \
        \norientation: x{self.display_axes[0]}, y{self.display_axes[1]}, z{self.display_axes[2]} \
        \nposition: {self.position}"
    def update_display(self):
        self.display_axes = np.array(
            [[round(xyz, 2) for xyz in axis] for axis in self.local_axes])
        self.display_position = np.array([round(xyz, 2) for xyz in self.position])
    def rotate(self, angle, axis):
        new_orientation = [rotateQuaternion(i, angle, axis) for i in self.local_axes]
        self.local_axes = new_orientation
        self.update_display()


# Returns dataframe with 109 labeled indices
def c3d_analogs_df(participant, speed, trial, path):
    filename = (
        participant+'_C3D/'+participant+'_'+speed+'_'+trial+'.c3d')
    file_path = path+filename
    myc3d = c3d(file_path)
    point_data = myc3d['data']['points']
    analog_data = myc3d['data']['analogs']
    analogs = analog_data[0, :, :]
    analog_labels = myc3d['parameters']['ANALOG']['LABELS']['value']
    df = pd.DataFrame(data=analogs, index=analog_labels)
    return df


def adrienC3Dpath():
    if str(__file__) == 'c:\\Users\\goper\\Files\\vsCode\\490R\\ABabet_490R-1\\functionBuilder.py':
        mypath = ('C:/Users/goper/Files/vsCode/490R/Walking_C3D_files/')
    elif str(__file__) == '/Users/adrienbabet/Documents/490R/IMU_gait_analysis/functionBuilder.py':
        mypath = '/Users/adrienbabet/Documents/490R/Walking C3D files/'
    return mypath


def get_sensor_data(sensor_placement, ACCorGYR, PitRolYaw, df):
    axis_dict = {'P': 'Pitch', 'Y': 'Yaw', 'R': 'Roll'}
    if type(sensor_placement) == str:
        OneToEleven = [i+1 for i in range(11)]
        IMU_placements = []
        for side in ['L', 'R']:
            for part in ['Thigh', 'Shank']:
                for place in ['Proximal', 'Distal']:
                    IMU_placements.append(side+place+part)
            IMU_placements.append(side+'Foot')
        IMU_placements.append('Sacrum')
        IMU_dict = dict(zip(IMU_placements, OneToEleven))
        index = 'DelsysTrignoBase 1: Sensor '+str(IMU_dict[sensor_placement])+'IM '+ACCorGYR+' '+axis_dict[PitRolYaw]
    elif type(sensor_placement) == int:
        index = 'DelsysTrignoBase 1: Sensor '+str(sensor_placement)+'IM '+ACCorGYR+' '+axis_dict[PitRolYaw]
    return df.loc[index]


def main():
    mypath = adrienC3Dpath()
    df = c3d_analogs_df('C07', 'Fast', '07', mypath)
    data = get_sensor_data('LDistalShank', 'GYR', 'P', df)
    plt.plot(data)
    plt.show()


if __name__ == '__main__':
    main()