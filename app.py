from flask import Flask, redirect, render_template, url_for, request, session, send_from_directory, abort, jsonify, make_response
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
import logging
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest

plt.switch_backend('Agg') 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'leroyJenkins'

# Only set SERVER_NAME for production deployment
if os.getenv('FLASK_ENV') == 'production' or os.getenv('PRODUCTION'):
    app.config['SERVER_NAME'] = 'www.datangleranking.com'
    app.config['PREFERRED_URL_SCHEME'] = 'https'
else:
    # For sitemap generation in development, still set the production scheme
    app.config['PREFERRED_URL_SCHEME'] = 'https'

# Configure logging
if not app.debug:
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

ext = Sitemap(app=app)

# Error handlers for better SEO and user experience
@app.errorhandler(404)
def not_found_error(error):
    app.logger.warning(f'404 error: {request.url}')
    return render_template('error.html', 
                         error_code='404',
                         error_title='Page Not Found',
                         error_message="The page you're looking for doesn't exist or has been moved."), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'500 error: {str(error)}')
    return render_template('error.html',
                         error_code='500',
                         error_title='Server Error', 
                         error_message='Something went wrong on our end. Please try again later.'), 500

@app.errorhandler(403)
def forbidden_error(error):
    app.logger.warning(f'403 error: {request.url}')
    return render_template('error.html',
                         error_code='403',
                         error_title='Access Forbidden',
                         error_message="You don't have permission to access this resource."), 403

@app.errorhandler(BadRequest)
def bad_request_error(error):
    app.logger.warning(f'400 error: {str(error)}')
    return render_template('error.html',
                         error_code='400',
                         error_title='Bad Request',
                         error_message='Your request was invalid. Please check and try again.'), 400

# Health check endpoint for monitoring
@app.route('/health')
def health_check():
    try:
        # Basic health checks
        static_path = os.path.join(app.root_path, 'static')
        templates_path = os.path.join(app.root_path, 'templates')
        
        if not os.path.exists(static_path):
            raise Exception("Static directory not found")
        if not os.path.exists(templates_path):
            raise Exception("Templates directory not found")
            
        return jsonify({
            'status': 'healthy',
            'timestamp': str(uuid.uuid4())
        }), 200
    except Exception as e:
        app.logger.error(f'Health check failed: {str(e)}')
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# Redirect old URLs or common misspellings
@app.route('/practise')  # Common misspelling
def practise_redirect():
    return redirect(url_for('practice'), code=301)

@app.route('/game')  # Alternative URL
def game_redirect():
    return redirect(url_for('practice'), code=301)

# Serve favicon.ico from /static/favicon.ico at the root URL
@app.route('/favicon.ico')
def favicon():
    try:
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except FileNotFoundError:
        app.logger.warning('Favicon not found')
        abort(404)

# Serve robots.txt from root
@app.route('/robots.txt')
def robots_txt():
    try:
        response = make_response(send_from_directory(os.path.join(app.root_path, 'static'), 'robots.txt'))
        response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
        return response
    except FileNotFoundError:
        app.logger.error('robots.txt not found')
        abort(404)

# Where to input the angle differential
@app.route('/', methods=['GET', 'POST'])
def send():
    try:
        if request.method == 'POST':
            variance_input = request.form.get('variance')
            if not variance_input:
                app.logger.warning('No variance input provided')
                return render_template('user_input.html', error='Please enter a variance value')
            
            try:
                tolerance_val = int(variance_input)
                if tolerance_val <= 0 or tolerance_val > 50:
                    return render_template('user_input.html', error='Variance must be between 1 and 50')
                session['tolerance'] = str(tolerance_val)
            except ValueError:
                app.logger.warning(f'Invalid variance input: {variance_input}')
                return render_template('user_input.html', error='Please enter a valid number')
            
            session['plot_exists'] = None
            return redirect(url_for('practice'))
        
        return render_template('user_input.html')
    except Exception as e:
        app.logger.error(f'Error in send route: {str(e)}')
        abort(500)


# Register sitemap generators for main routes
@ext.register_generator
def index():
    # Generator for homepage
    yield 'send', {}

@ext.register_generator
def practice_sitemap():
    # Generator for practice page
    yield 'practice', {}

# The Plot Page

@app.route('/practice', methods=['GET', 'POST'])
def practice():
    try:
        # Ensure required session variables are set
        if 'tolerance' not in session:
            # Set a default tolerance and redirect to input page
            session['tolerance'] = '30'
            session['plot_exists'] = None
            return redirect(url_for('send'))

        resultOutput = 'Push Submit to check answer'

        if request.method == 'POST':
            try:
                if 'Submit!' in request.form:
                    userAnswers = request.form
                    userAnswer = [0,0,0,0]
                    
                    # Validate form inputs
                    required_fields = ['smallest', 'secondSmallest', 'secondLargest', 'largest']
                    for field in required_fields:
                        if field not in userAnswers:
                            app.logger.warning(f'Missing form field: {field}')
                            abort(400)
                    
                    try:
                        smallest = int(userAnswers['smallest'])
                        userAnswer[smallest-1] = 1
                        secondSmallest = int(userAnswers['secondSmallest'])
                        userAnswer[secondSmallest-1] = 2
                        secondLargest = int(userAnswers['secondLargest'])
                        userAnswer[secondLargest-1] = 3
                        largest = int(userAnswers['largest'])
                        userAnswer[largest-1] = 4
                    except (ValueError, IndexError) as e:
                        app.logger.warning(f'Invalid form data: {str(e)}')
                        abort(400)
                    
                    # Check if session has required answer data
                    required_session_keys = ['smallest', 'secondSmallest', 'secondLargest', 'largest']
                    for key in required_session_keys:
                        if key not in session:
                            app.logger.warning(f'Missing session key: {key}')
                            session['plot_exists'] = None
                            break
                    else:
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
            except Exception as e:
                app.logger.error(f'Error processing form: {str(e)}')
                return redirect(url_for('send'))

        if session.get('plot_exists') is None:
            try:
                TOLERANCE = int(session['tolerance'])
                if TOLERANCE <= 0 or TOLERANCE > 50:
                    app.logger.warning(f'Invalid tolerance value: {TOLERANCE}')
                    return redirect(url_for('send'))
                
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
            except Exception as e:
                app.logger.error(f'Error generating plot: {str(e)}')
                return redirect(url_for('send'))

        form = Form()
        return render_template('game_play.html', form=form, result=resultOutput, tmpID=session.get('id', 'default'))
    except Exception as e:
        app.logger.error(f'Error in practice route: {str(e)}')
        abort(500)

def test(angles):
    try:
        # unpack and create angles
        if len(angles) != 4:
            raise ValueError("Expected 4 angles")
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
        try:
            image_files = sorted(
                glob.glob('static/tmp*.png'),
                key=os.path.getmtime
            )
            max_images = 30
            if len(image_files) >= max_images:
                for f in image_files[:len(image_files)-max_images+1]:
                    try:
                        os.remove(f)
                    except Exception as e:
                        app.logger.warning(f'Failed to remove old image {f}: {str(e)}')
        except Exception as e:
            app.logger.warning(f'Error cleaning up images: {str(e)}')

        session['id'] = str(uuid.uuid4())[:8]
        # Ensure 'static' directory exists before saving
        try:
            os.makedirs('static', exist_ok=True)
            plt.savefig('static/tmp' + session['id'] + '.png')
        except Exception as e:
            app.logger.error(f'Error saving plot: {str(e)}')
            raise
        
        return buf
    except Exception as e:
        app.logger.error(f'Error in test function: {str(e)}')
        raise

class Form(FlaskForm):
    smallest = SelectField('smallest', choices=[('1'), ('2'), ('3'), ('4')], default = 1)
    secondSmallest = SelectField('secondSmallest', choices=[('1'), ('2'), ('3'), ('4')], default = 2)
    secondLargest = SelectField('secondLargest', choices=[('1'), ('2'), ('3'), ('4')], default = 3)
    largest = SelectField('largest', choices=[('1'), ('2'), ('3'), ('4')], default = 4)
    

if __name__ == "__main__":
    app.run(debug=True)