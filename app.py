from flask import Flask, redirect, render_template, url_for, request, session
import numpy as np
import random
import math
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from flask_wtf import FlaskForm
from wtforms import SelectField
import uuid

plt.switch_backend('Agg') 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'leroyJenkins'

# Where to input the angle differential
@app.route('/', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        variance_input = request.form['variance']
        session['tolerance'] = variance_input
        session['plot_exists'] = None
        return redirect(url_for('visualize'))
    
    return render_template('user_input.html')

# The Plot Page
@app.route('/visualize', methods=['GET', 'POST'])
def visualize():  
    resultOutput = 'Push Submit to check answer'
    
    if request.method == 'POST':
        print(request)
        if 'Submit!' in request.form:
                        
            userAnswers = request.form

            userAnswer = [0,0,0,0]
            smallest = int(userAnswers['smallest'])
            userAnswer[smallest-1] = 1
            secondSmallest = int(userAnswers['secondSmallest'])
            userAnswer[secondSmallest-1] = 2
            secondLargest = int(userAnswers['secondLargest'])
            userAnswer[secondLargest-1] = 3
            largest = int(userAnswers['largest'])
            userAnswer[largest-1] = 4
            
            answer = [int(session['smallest']), int(session['secondSmallest']), int(session['secondLargest']), int(session['largest'])]

            if userAnswer == answer:
                resultOutput = 'Correct!'
            else:
                resultOutput = 'Wrong... {}<{}<{}<{}'.format(np.where(np.array(answer) == 1)[0][0] + 1,np.where(np.array(answer) == 2)[0][0] + 1,np.where(np.array(answer) == 3)[0][0] + 1,np.where(np.array(answer) == 4)[0][0] + 1)
        elif "Change Angle Difference" in request.form:
            session.clear()
            return redirect(url_for('send'))

        elif "Play Again (Same Angle Difference)" in request.form:
            session['plot_exists'] = None

    if session['plot_exists'] == None:
        TOLERANCE = int(session['tolerance'])
        
        base_angle = random.randint(40, 150 - 3 * TOLERANCE)
        
        test_angles = [base_angle,
                       base_angle + 1 * TOLERANCE,
                       base_angle + 2 * TOLERANCE,
                       base_angle + 3 * TOLERANCE]
        
        random.shuffle(test_angles)
    
        buf = test(test_angles)
        
        temp = np.argsort(test_angles)
        answers = np.empty_like(temp)
        answers[temp] = np.arange(len(test_angles)) + 1
        answers = list(answers)
        
        session['smallest'] = str(answers[0])
        session['secondSmallest'] = str(answers[1])
        session['secondLargest'] = str(answers[2])
        session['largest'] = str(answers[3])
        
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        
        session['plot_exists'] = 'yip!'
        
    form = Form()    
    
    return render_template('game_play.html', form=form, result = resultOutput, tmpID = session['id'])

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
        
    # plt.show(block=False)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    
    session['id'] = str(uuid.uuid4())[:8]
    plt.savefig('static/tmp' + session['id'] + '.png')
    return buf

class Form(FlaskForm):
    smallest = SelectField('smallest', choices=[('1'), ('2'), ('3'), ('4')], default = 1)
    secondSmallest = SelectField('secondSmallest', choices=[('1'), ('2'), ('3'), ('4')], default = 2)
    secondLargest = SelectField('secondLargest', choices=[('1'), ('2'), ('3'), ('4')], default = 3)
    largest = SelectField('largest', choices=[('1'), ('2'), ('3'), ('4')], default = 4)
    

if __name__ == "__main__":
    app.run(debug=True)


