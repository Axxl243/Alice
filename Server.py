from flask import Flask, render_template, request 

app= Flask(__name__)

@app.route("/")#Route principal
def index():
    return (render_template('index.html'))


@app.route("/formulario", methods=['GET', 'POST'])
def registro():
    return render_template('formulario.html')

@app.route('/Perfil')
def perfil():
    return render_template('perfil.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    return render_template('login.html')

if "__main__" == "__name__":
    app.run(host="0.0.0.0", port=8088, debug=True)

#primero se debe de dar click derecho, corrrer python en la terminal y luego en consola se debe de usaar el comando 
#flask --app server run --debug (debug crea el modo depurador para guardar cambios en tiempo real sin necesidad de reiniciar el servidor)ñ 