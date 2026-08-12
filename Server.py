from flask import Flask, render_template 

app= Flask(__name__)

@app.route('/')
def index():
    return (render_template('index.html'))




if "__main__" == "__name__":
    app.run(host="0.0.0.0", port=8088, debug=True)