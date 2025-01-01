from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# def appStart():
#     app.run(debug=True)

if __name__ == '__main__':
    app.run(host='35.157.99.90')

