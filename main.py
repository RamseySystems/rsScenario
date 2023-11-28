from flask import Flask, render_template, jsonify, request
import config

app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])
def home():
  return render_template('index.html', **locals())

# @app.route('/', methods = ['POST', 'GET'])
# def home():
#   return render_template('home.html', **locals())



if __name__ == '__main__':
  app.run(debug=True)
