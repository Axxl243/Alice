from flask import Flask, render_template, request 

app= Flask(__name__)

@app.route("/")#Route principal
def index():
    return (render_template('index.html'))


@app.route('/Formulary')
def Formulary():
    return render_template('Formulary.html')


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic here
        pass
    return render_template('login.html')

if "__main__" == "__name__":
    app.run(host="0.0.0.0", port=8088, debug=True)