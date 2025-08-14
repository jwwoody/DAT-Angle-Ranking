from flask import Flask, redirect, render_template, url_for, request, session, send_from_directory
from flask_sitemap import Sitemap
import os
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

ext = Sitemap(app=app)

# Serve favicon.ico from /static/favicon.ico at the root URL
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Serve robots.txt and sitemap.xml from root
@app.route('/robots.txt')
def robots_txt():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'robots.txt')

@app.route('/sitemap.xml')
def sitemap_xml():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')

# Where to input the angle differential
@app.route('/', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        variance_input = request.form['variance']
        session['tolerance'] = variance_input
        session['plot_exists'] = None
        return redirect(url_for('practice'))
    
    return render_template('user_input.html')


# Register sitemap generators for main routes
@ext.register_generator
def practice():
    yield 'practice', {}

# The Plot Page

@app.route('/practice', methods=['GET', 'POST'])
def practice():
    # Ensure required session variables are set
    if 'tolerance' not in session:
        # Set a default tolerance and redirect to input page
        session['tolerance'] = 30
        session['plot_exists'] = None
        return redirect(url_for('send'))

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
                resultOutput = 'Wrong... {}<{}<{}<{}'.format(
                    np.where(np.array(answer) == 1)[0][0] + 1,
                    np.where(np.array(answer) == 2)[0][0] + 1,
                    np.where(np.array(answer) == 3)[0][0] + 1,
                    np.where(np.array(answer) == 4)[0][0] + 1)
        elif "Change Angle Difference" in request.form:
            session.clear()
            return redirect(url_for('send'))
        elif "Play Again (Same Angle Difference)" in request.form:
            session['plot_exists'] = None

    if session.get('plot_exists') is None:
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
    return render_template('game_play.html', form=form, result=resultOutput, tmpID=session['id'])

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
    import os
    import glob
    buf = BytesIO()
    fig.savefig(buf, format="png")

    # Clean up old images if more than 30 exist
    image_files = sorted(
        glob.glob('static/tmp*.png'),
        key=os.path.getmtime
    )
    max_images = 30
    if len(image_files) >= max_images:
        for f in image_files[:len(image_files)-max_images+1]:
            try:
                os.remove(f)
            except Exception:
                pass

    session['id'] = str(uuid.uuid4())[:8]
    # Ensure 'static' directory exists before saving
    os.makedirs('static', exist_ok=True)
    plt.savefig('static/tmp' + session['id'] + '.png')
    return buf

class Form(FlaskForm):
    smallest = SelectField('smallest', choices=[('1'), ('2'), ('3'), ('4')], default = 1)
    secondSmallest = SelectField('secondSmallest', choices=[('1'), ('2'), ('3'), ('4')], default = 2)
    secondLargest = SelectField('secondLargest', choices=[('1'), ('2'), ('3'), ('4')], default = 3)
    largest = SelectField('largest', choices=[('1'), ('2'), ('3'), ('4')], default = 4)
    

if __name__ == "__main__":
    app.run(debug=True)