from flask import Flask,render_template,url_for, request
import requests

import pandas as pd
from datetime import datetime
from dateutil.relativedelta import * 

from bokeh.embed import components
from bokeh.plotting import figure, show, output_file
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8


app= Flask(__name__)

@app.route("/")
@app.route("/home")
def hello():
	return render_template('home.html')

@app.route("/bokeh", methods=['GET','POST'])
def bokeh():
	if request.method == 'POST':
		ticker = request.form.get('ticker')
		start_date = request.form.get('start_date')
		select_col = request.form.getlist('features')
		if start_date=='':start_date='2018-08-01'
		if ticker=='':ticker='AAPL'
		my_plot = create_graph(ticker,start_date,select_col)

		# grab the static resources
		js_resources = INLINE.render_js()
		css_resources = INLINE.render_css()

		# render template
		script, div = components(my_plot)
		html = render_template('index.html',
			plot_script=script,
			plot_div=div,
			js_resources=js_resources,
			css_resources=css_resources,)
		return encode_utf8(html)

	

def create_graph(ticker,start_date,select_col):
	base_url = "https://www.quandl.com/api/v3/datasets/EOD/"
	#ticker='AAPL'
	#start_date='2018-08-01'
	end_date = datetime.strptime(start_date,'%Y-%m-%d')+relativedelta(months=+1)
	my_api="-Jpgts4njXysaGiUaz8X"
	url = f"{base_url}{ticker}.json?start_date={start_date}&end_date={end_date}&api_key={my_api}"

	raw_data = requests.get(url).json()
	col_names = raw_data['dataset']['column_names']
	data = raw_data['dataset']['data']
	df=pd.DataFrame(data,columns=col_names)
	df= df[['Date','Open','Adj_Open','Close','Adj_Close']]
	df['Date']=df['Date'].astype('datetime64[ns]')

	#select_col = ['Open','Close']
	colors = ['#006400','#DC143C','#FB9A99','#8A2BE2']
	col=0
	mean_price = df[select_col].mean()
	#output_notebook()
	p = figure(x_axis_type="datetime", title=f"{ticker} Stock Prices")
	p.grid.grid_line_alpha=0.3
	p.xaxis.axis_label = 'Date'
	p.yaxis.axis_label = 'Price'

	for cur_col in select_col:
	    p.line(df.Date,df[cur_col], color=colors[col], legend=cur_col)
	    col=col+1
	#p.line(df.Date,mean_price, color='black', legend="Avg Closing Price")
	p.legend.location = "top_right"

	return p

if __name__ == '__main__':
	app.run(port=33507)

#
#export FLASK_APP=FlaskBlog.py
#flask run

#export FLASK_DEBUG=1
