from __future__ import division
from flask import Flask, render_template, request, jsonify
from check_zip import checkZip
import os

app = Flask(__name__)
# zip_model = checkZip()

@app.route('/')
def index():
    # supported_counties = zip_model.get_supported_counties()
    path_to_prediction_file_single = os.path.join(os.environ['HOME'],'incoming_rainbow_predictions_single.csv')
    with open(path_to_prediction_file_single, 'r') as f:
        message_list = f.readline().split(',')
        message = message_list[1].strip()
        probability = message_list[0].strip()
    if float(probability) >= .6:
        prob_words = 'very high'
    elif float(probability) >= .35:
        prob_words = 'fairly good'
    elif float(probability) >= .2:
        prob_words = 'quite modest'
    elif float(probability) > 0:
        prob_words = 'slim to none'
    else:
        prob_words = 'nonexistant'
    return render_template('index.html', message = message, probability = probability,
                    prob_words = prob_words)

# @app.route('/response_to_sign_up', methods=['POST'])
# def check_one_zip():
#     user_data = request.json
#     first_name, last_name, phone, zip_code = user_data['fname'], user_data['lname'], user_data['phone'], int(user_data['zip_code'])
#     return jsonify({'response': zip_model.check_zip(zip_code)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
