from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/omg')
def page2():
    return render_template('omg.html')

@app.route('/winteriscoming')
def page3():
    return render_template('winteriscoming.html')

if __name__ == '__main__':
    app.run(debug=True)