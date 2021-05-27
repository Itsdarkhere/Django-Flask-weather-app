from flask import Flask, redirect, flash, render_template, request
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


class City(db.Model):
    name = db.Column(db.String(40), unique=True, primary_key=True)
    state = db.Column(db.String(30))
    temperature = db.Column(db.Integer, nullable=False)
    time_of_day = db.Column(db.String(80), nullable=False)


@app.route('/delete/<name>', methods=['POST'])
def delete(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


@app.route('/')
def index():
    try:
        result = City.query.all()
    except Exception:
        result = ''

    # This need to move to its own models.py folder with the model.
    if __name__ == "__main__":
        db.create_all()

    return render_template('index.html', weather=result)


@app.route('/add', methods=['POST'])
def add_city():

    # Getting city name from input field
    # Using the input info to query the place
    city = request.form.get('city_name')
    key = 'ef2524400d6668a26592f8b7326087a7'
    params = {
        'q': city,
        'appid': key
    }
    r = requests.get(f'http://api.openweathermap.org/data/2.5/weather?', params=params)
    # getting information received into a json form

    json_dict = json.loads(r.text)

    # if the query returns 404, logs a flash and redirects without further execution
    if json_dict['cod'] == '404':
        flash("The city doesn't exist!")
        return redirect("/", code=302)

    already_exists = bool(City.query.filter_by(name=city).first())

    if not already_exists:
        try:
            weather_state = json_dict['weather'][0]['main']
            temperature = int(json_dict['main']['temp'] - 273.15)
            new_place = City(name=city, state=weather_state, temperature=temperature, time_of_day='evening-morning')
            db.session.add(new_place)
            db.session.commit()

        except KeyError:
            print('Data Problems, sorry cant add')

    else:
        flash("The city has already been added to the list!")

    # Redirect to main
    return redirect("/", code=302)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
