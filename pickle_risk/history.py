from flask import Blueprint, current_app
from flask_pymongo import PyMongo

import json, logging

bp = Blueprint('history', __name__, url_prefix='/history')

ERROR_NO_SUCH_SYMBOL = '{"error": "NoSuchSymbol"}'

logger = logging.getLogger(__name__)

@bp.route('/')
@bp.route('/<symbol>')
def symbol_history(symbol=None):
    mongo = PyMongo(current_app)
    time_series_data = mongo.db.timeSeriesDailyAdjusted.find_one({'symbol': symbol})
    logger.info('Grabbing symbol history for: {0}'.format(symbol))
    if time_series_data:
        return json.dumps(basic_time_series(time_series_data["entries"]))
    else:
        logger.warning('No such symbol detected.')
        return ERROR_NO_SUCH_SYMBOL

def basic_time_series(time_series):
    basic_series = dict()
    for entry in time_series:
        basic_series[entry['date']] = entry['close']
    return basic_series

