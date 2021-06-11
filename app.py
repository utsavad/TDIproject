import os

from flask import Flask,render_template,url_for, request
import requests

from sklearn.externals import joblib
#import joblib
import numpy as np
import pandas as pd
import dill

from bokeh.embed import components
from bokeh.plotting import figure, show, output_file
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8

from bokeh.io import show, output_file, output_notebook, curdoc
from bokeh.models import Toggle, BoxAnnotation, CustomJS, ColumnDataSource, Plot, LinearAxis, Grid
from bokeh.models.glyphs import Text

from bokeh.layouts import layout, widgetbox
from bokeh.models.widgets import Tabs, Panel, Div, Paragraph


import cols_dict as cols

app= Flask(__name__)


@app.route("/")
@app.route("/Home")
def hello():
	return render_template('home.html')

@app.route("/about")
def abt():
	return render_template('About.html', title='About')

@app.route("/bokeh", methods=['GET','POST'])
def bokeh():
	cur_dict = cols.default_vals
	avg_sals = cols.avg_sal_dict
	final_score = 0.000
	if request.method == 'POST':
	#if request.form['action'] == 'Submit':
		name = request.form.get('name')
		emp_title = request.form.get('emp_title')
		cur_dict['emp_length'] = float(request.form.get('emp_length'))
		cur_dict['loan_amnt'] = float(request.form.get('loan_amnt'))
		cur_dict['term'] = float(request.form.get('term'))
		cur_dict['int_rate'] = float(request.form.get('int_rate'))
		cur_dict['emp_length'] = float(request.form.get('emp_length'))
		cur_dict['annual_inc'] = float(request.form.get('annual_inc'))
		cur_dict['verification_status'] = float(request.form.get('verification_status'))
		cur_dict['pymnt_plan'] = float(request.form.get('pymnt_plan'))
		cur_dict['delinq_2yrs'] = float(request.form.get('delinq_2yrs'))
		cur_dict['inq_last_6mths'] = float(request.form.get('inq_last_6mths'))
		cur_dict['open_acc'] = float(request.form.get('open_acc'))
		cur_dict['pub_rec'] = float(request.form.get('pub_rec'))
		cur_dict['loan_inc_ratio'] = cur_dict['loan_amnt']/cur_dict['annual_inc']
		grade = "grade_"+request.form.get('grade')
		cur_dict[grade] = 1.0 
		sub_grade = "sub_"+grade+request.form.get('sub_grade')
		cur_dict[sub_grade] = 1.0
		home_ownership = "home_ownership_" +request.form.get('home_ownership')
		cur_dict[home_ownership] =1.0
		#purpose = "purpose_"+request.form.get('purpose')
		
		# try:	
		# 	cur_dict['purpose'] = 1.0
		# except:
		# 	pass

		cur_state = request.form.get('addr_state').upper()
		addr_state = "addr_state_"+cur_state
		cur_dict[addr_state]= 1.0
		
		cur_dict['state_avg_sal'] = avg_sals[cur_state]

		classifier = joblib.load('tm2.pickle')
		p1 = np.array(list(cur_dict.values()))
		p1 = p1.reshape(1, -1)
		model_preds = classifier.predict_proba(p1)
		final_val = str(round(model_preds[0][1],2))	


		my_plot = create_graph(final_val, cur_dict,cur_state)

		
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
		#return str(final_val)




	

def create_graph(final_val,cur_dict,cur_state):
	plot_df = dill.load(open('t1.pkd', 'rb'))
	cur_IR = cur_dict['int_rate']
	cur_rel_sal = cur_dict['annual_inc']/cols.avg_sal_dict[cur_state]
	
	df1 = plot_df[(plot_df['rel_sal'] >= (0.75*cur_rel_sal)) & (plot_df['rel_sal'] < (1.25*cur_rel_sal))]
	hist1, edges1 = np.histogram(df1.pred, density=True, bins=30)

	df1 = plot_df[plot_df['addr_state'] == cur_state]
	hist2, edges2 = np.histogram(df1.pred, density=True, bins=30)

	df1 = plot_df[(plot_df['int_rate'] >= (cur_IR-10)) & (plot_df['int_rate'] < (cur_IR+10))]
	hist3, edges3 = np.histogram(df1.pred, density=True, bins=30)

	#Model Prediction Score

	pred_score = figure(title='Probability to default',x_range=[0,1],
	             y_range=[0,1])
	pred_score.rect([0.5], [0.5], [0.7], [0.7],fill_alpha=0.8,fill_color='orange')

	pred_score.title.text_font_size = '14pt'
	pred_score.title.align ='center'

	pred_score.xgrid.visible = False
	pred_score.ygrid.visible = False
	pred_score.xaxis.ticker = []
	pred_score.yaxis.ticker = []

	x = [0.3]
	y = [0.4]
	text = [final_val]

	source = ColumnDataSource(dict(x=x, y=y, text=text))
	glyph = Text(x="x", y="y", text="text", text_color="black",text_font_size="96pt")
	pred_score.add_glyph(source, glyph)

	#First Figure
	p1 = figure(title='Score Comparison Based on Relative Salary')
	p1.quad(top=hist1, bottom=0, left=edges1[:-1], right=edges1[1:], line_color="white")

	box = BoxAnnotation(left=float(final_val)-0.0025, right=float(final_val)+0.0025, fill_color='pink', fill_alpha=0.8)
	p1.add_layout(box)
	p1.title.text_font_size = '14pt'
	p1.title.align ='center'

	p1.xaxis.axis_label = 'Probability Distribution'
	p1.yaxis.axis_label = 'Weighted Frequency'


	para1 = Div(text="""<b><i>
		The plot shows the probability distribution for the borrowers with the similar income. The red zone shows where the borrower stands compared to
		other borrowers with similar income. Range of income covered: 0.75x - 1.25x where x is the normalized income of the borrower</i></b>""",
		width=300, height=100)
	p11 = widgetbox(para1)		


	#Second Figure
	p2 = figure(title='Score Comparison Based on State')
	p2.quad(top=hist2, bottom=0, left=edges2[:-1], right=edges2[1:], line_color="white")

	box2 = BoxAnnotation(left=float(final_val)-0.0025, right=float(final_val)+0.0025, fill_color='pink', fill_alpha=0.8)
	p2.add_layout(box2)

	p2.title.text_font_size = '14pt'
	p2.title.align ='center'

	p2.xaxis.axis_label = 'Probability Distribution'
	p2.yaxis.axis_label = 'Weighted Frequency'


	para2 = Div(text="""<b><i>
		The plot shows the probability distribution for the borrower's state. The red zone shows where the borrower stands compared to
		other borrowers in the state </i> </b>""",
		width=300, height=100)
	p22 = widgetbox(para2)		


	#Third Plot
	p3 = figure(title='Score Comparison Based on Interest Rate')
	p3.quad(top=hist3, bottom=0, left=edges3[:-1], right=edges3[1:], line_color="white")

	box3 = BoxAnnotation(left=float(final_val)-0.0025, right=float(final_val)+0.0025, fill_color='pink', fill_alpha=0.8)
	p3.add_layout(box3)

	p3.title.text_font_size = '14pt'
	p3.title.align ='center'

	p3.xaxis.axis_label = 'Probability Distribution'
	p3.yaxis.axis_label = 'Weighted Frequency'


	para3 = Div(text="""<b><i>
		The plot shows the probability distribution for the borrowers who took out loan at similar interest rate as the borrower. The red zone shows where the borrower stands.
		Range of income covered: x-10 to x+10 where x is interest rate for the borrower </i> </b>""",
		width=300, height=100)
	p33 = widgetbox(para3)		


	#Layouts
	l0 = layout([[pred_score]], sizing_mode='fixed')
	l1 = layout([[p1,p11]], sizing_mode='fixed')
	l2 = layout([[p2,p22]],sizing_mode='fixed')
	l3 = layout([[p3,p33]],sizing_mode='fixed')

	tab0 = Panel(child=l0,title="Score")
	tab1 = Panel(child=l1,title="Relative Salary")
	tab2 = Panel(child=l2,title="State Analysis")
	tab3 = Panel(child=l3,title="Interest Rate")

	tabs = Tabs(tabs=[ tab0,tab1, tab2, tab3 ])

	return tabs


if __name__ == '__main__':
	app.run(debug=True)

#
#export FLASK_APP=FlaskBlog.py
#flask run

#export FLASK_DEBUG=1
