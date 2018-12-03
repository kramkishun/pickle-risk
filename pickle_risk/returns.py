from flask import Blueprint, current_app
from flask_pymongo import PyMongo

import numpy as np

import json, logging

bp = Blueprint('returns', __name__, url_prefix='/returns')

ERROR_NO_SUCH_SYMBOL = '{"error": "NoSuchSymbol"}'

logger = logging.getLogger(__name__)

@bp.route('/')
@bp.route('/<symbol>')
def symbol_returns(symbol=None):
    mongo = PyMongo(current_app)
    symbol = symbol.upper()
    time_series_data = mongo.db.timeSeriesDailyAdjusted.find_one({'symbol': symbol})
    logger.info('Grabbing symbol returns for: {0}'.format(symbol))
    if time_series_data:
        return json.dumps(basic_histogram_returns(time_series_data["entries"]))
    else:
        logger.warning('No such symbol detected.')
        return ERROR_NO_SUCH_SYMBOL

def basic_histogram_returns(time_series):
    daily_returns = [100 * ((entry['close'] - entry['open']) / entry['open']) for entry in time_series]
    (hist, edges) =  np.histogram(daily_returns, bins=100)
    return (hist.tolist(), edges.tolist())

    