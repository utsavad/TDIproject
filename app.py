from flask import Flask, render_template,url_for,redirect, request
import my_plot as mp
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
		mp.my_graph(ticker,start_date,select_col)
	return render_template('home.html')

if __name__ == '__main__':
	app.run(debug=True)


#
#export FLASK_APP=FlaskBlog.py
#flask run

#export FLASK_DEBUG=1
