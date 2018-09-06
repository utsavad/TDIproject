from flask import Flask, render_template,url_for,redirect, request
import requests

import pandas as pd
from datetime import datetime
from dateutil.relativedelta import * 

from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file

app= Flask(__name__)

@app.route("/")
@app.route("/home")
def hello():
	return render_template('home.html',posts=posts)

@app.route("/graph", methods=['GET','POST'])
def graph():
	if request.method == 'POST':
		ticker = request.form.get('ticker')
		start_date = request.form.get('start_date')
		select_col = request.form.getlist('features')
		if start_date=='':start_date='2018-08-01'
		if ticker=='':ticker='AAPL'
		my_graph(ticker,start_date,select_col)
	return render_template('home.html')


def my_graph(ticker,start_date,select_col):
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

	show(p)

#
#export FLASK_APP=FlaskBlog.py
#flask run

#export FLASK_DEBUG=1
