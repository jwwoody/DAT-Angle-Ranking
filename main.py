# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 22:29:16 2021

@author: armen
"""

import numpy as np
import random
import math
import matplotlib.pyplot as plt
plt.switch_backend('Agg') 

CONTINUE = True
 
def test(angles):
    # unpack and create angles
    angle1, angle2, angle3, angle4 = angles
    
    # calculate the end points
    def findEndPoints(angle):
        length1 = random.randint(3, 5)
        length2 = random.randint(3, 5)
        
        randTheta = random.randint(0, 360)
        theta1 = 0 + randTheta
        theta2 = angle + randTheta
        
        x = 5 + random.randint(-2,2)
        y = 5 + random.randint(-2,2)
        
        endx1 = x + length1 * math.cos(math.radians(theta1))
        endy1 = y + length1 * math.sin(math.radians(theta1))
        
        endx2 = x + length2 * math.cos(math.radians(theta2))
        endy2 = y + length2 * math.sin(math.radians(theta2))
        
        return (x, y, endx1, endy1, endx2, endy2)
       
    # Plot the points
    fig, axs = plt.subplots(2, 2)
    
    x, y, endx1, endy1, endx2, endy2 = findEndPoints(angle1)
    axs[0, 0].plot([x, endx1], [y, endy1], 'k')
    axs[0, 0].plot([x, endx2], [y, endy2], 'k')
    axs[0, 0].set_title('Angle 1')
    
    x, y, endx1, endy1, endx2, endy2 = findEndPoints(angle2)
    axs[0, 1].plot([x, endx1], [y, endy1], 'k')
    axs[0, 1].plot([x, endx2], [y, endy2], 'k')
    axs[0, 1].set_title('Angle 2')
    
    x, y, endx1, endy1, endx2, endy2 = findEndPoints(angle3)
    axs[1, 0].plot([x, endx1], [y, endy1], 'k')
    axs[1, 0].plot([x, endx2], [y, endy2], 'k')
    axs[1, 0].set_title('Angle 3')
    
    x, y, endx1, endy1, endx2, endy2 = findEndPoints(angle4)
    axs[1, 1].plot([x, endx1], [y, endy1], 'k')
    axs[1, 1].plot([x, endx2], [y, endy2], 'k')
    axs[1, 1].set_title('Angle 4')
    
    # Hide labels and axis
    for ax in axs.flat:
        ax.axis('off')
        ax.label_outer()
        ax.set_aspect('equal', adjustable='box')
        ax.set_ylim([0, 10])   # set the bounds to be 10, 10
        ax.set_xlim([0, 10])
        
    plt.show(block=False)
        
while CONTINUE:
    TOLERANCE = int(input('Enter angle variance (degrees): '))
    
    base_angle = random.randint(40,150 - 3 * TOLERANCE)
    
    test_angles = [base_angle,
                   base_angle + 1 * TOLERANCE,
                   base_angle + 2 * TOLERANCE,
                   base_angle + 3 * TOLERANCE]
    
    random.shuffle(test_angles)
    
    temp = np.argsort(test_angles)
    answers = np.empty_like(temp)
    answers[temp] = np.arange(len(test_angles)) + 1
    answers = list(answers)
    
    test(test_angles)
    
    userAnswer = [0,0,0,0]
    
    smallest = int(input('Which angle is smallest? Angle: '))
    userAnswer[smallest-1] = 1
    secondSmallest = int(input('Which angle is second smallest? Angle: '))
    userAnswer[secondSmallest-1] = 2
    secondLargest = int(input('Which angle is second largest? Angle: '))
    userAnswer[secondLargest-1] = 3
    largest = int(input('Which angle is largest? Angle: '))
    userAnswer[largest-1] = 4
    
    print('')
    
    if answers == userAnswer:
        print('Nice work')
    else:
        print('Naw...')
        print('The smallest angle was angle ' + str(answers.index(1)+1))
        print('The second smallest angle was angle ' + str(answers.index(2)+1))
        print('The second largest angle was angle ' + str(answers.index(3)+1))
        print('The largest angle was angle ' + str(answers.index(4)+1))
        
    if input("Play again?\ny/n: ") == 'y':
        CONTINUE = True
    else:
        CONTINUE = False