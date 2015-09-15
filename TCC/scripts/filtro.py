#!/usr/bin/env python
import rospy
import numpy as np
import scipy.signal as sg
from std_msgs.msg import Float64MultiArray

fs=250
n_order=250
f1_2=[8,20]
b = sg.firwin(n_order,f1_2,pass_zero=False,window='blackman',nyq=fs/2)


  
    
def filtro():
    global pub
    rospy.init_node('filtro', anonymous=True)
    pub=rospy.Publisher('canal2', Float64MultiArray, queue_size=10)
    rospy.Subscriber('canal1', Float64MultiArray, callback)
    rospy.spin()

def callback(data):
    global pub	
    saida=sg.convolve(data.data,b,mode='full')
    #print(saida)
    msg=Float64MultiArray(data=saida)
    pub.publish(msg)

if __name__ == '__main__':
    filtro()
