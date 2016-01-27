from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html','figure1.html','figure2.html')
  
@app.route('/figure1')
def index():
  return render_template('figure1.html')
  
@app.route('/figure2')
def index():
  return render_template('figure2.html')  

if __name__ == '__main__':
  app.run(port=33507)
