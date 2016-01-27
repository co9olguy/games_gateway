from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')
  
@app.route('/figure1')
def figure1():
  return render_template('figure1.html')
  
@app.route('/figure2')
def figure2():
  return render_template('figure2.html')  

if __name__ == '__main__':
  app.run(port=33507)
