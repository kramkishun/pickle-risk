from flask import Flask
from flask_pymongo import PyMongo

import pprint, json

# To launch (in Windows Powershell/VSCode):
# > $env:FLASK_APP="pr-server.py"
# > $env:FLASK_ENV="development"
# > flask run

ERROR_NO_SUCH_SYMBOL = '{"error": "NoSuchSymbol"}'

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/pickleRisk"
mongo = PyMongo(app)

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Check out /history'

@app.route('/history')
@app.route('/history/<symbol>')
def stock_history(symbol=None):
    time_series_data = mongo.db.timeSeriesDailyAdjusted.find_one({'symbol': symbol})
    if time_series_data:
        return json.dumps(basic_time_series(time_series_data["entries"]))
    else:
        return ERROR_NO_SUCH_SYMBOL

def basic_time_series(time_series):
    basic_series = dict()
    for entry in time_series:
        basic_series[entry['date']] = entry['close']
    return basic_series

