import json

class LineChartResponse:
    def __init__(self, chart_title='Line Chart', x_axis_title='Time', y_axis_title='Price', 
                 x_axis_labels = [], x_axis_data=[], y_axis_data = []):
        self.resp = {}
        self.resp['Chart Title'] = chart_title
        self.resp['X Axis Title'] = x_axis_title
        self.resp['Y Axis Title'] = y_axis_title
        self.resp['X Axis Labels'] = x_axis_labels
        self.resp['Y Axis Data'] = y_axis_data

    def json_response(self):
        return json.dumps(self.resp)
    
