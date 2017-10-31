from __future__ import division
from flask import Flask, render_template, request, jsonify
from check_zip import checkZip

app = Flask(__name__)
zip_model = checkZip()

@app.route('/')
def index():
    supported_counties = zip_model.get_supported_counties()
    return render_template('index.html', counties = supported_counties)

@app.route('/response_to_sign_up', methods=['POST'])
def check_one_zip():
    user_data = request.json
    first_name, last_name, phone, zip_code = user_data['fname'], user_data['lname'], user_data['phone'], int(user_data['zip_code'])
    return jsonify({'response': zip_model.check_zip(zip_code)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
