from flask import Flask, render_template, request, url_for
from config_Server import config

import os


#variables globales
app= Flask(__name__)
app.config.from_object(config)

#Rutas 
@app.route("/")#Route principal
def index(): 
    return (render_template('index.html'))

#ruta de registro
@app.route("/formulario", methods=['GET', 'POST'])
def registro():
    return render_template('formulario.html')



#Ruta de login
@app.route('/login', methods = ['GET', 'POST'])
def login():
    msj = "No data"

    if request.method == 'POST':
        logUser = request.form.get('lUser')
        logPass = request.form.get('lPass')

        msj = f"Nombre: {logUser} Contraseña: {logPass}"

        return render_template('login.html', msj=msj)



    return render_template('login.html', msj=msj)

#Ruta de perfil
@app.route('/perfil')
def perfil():
    return render_template('perfil.html')

#Ruta inventario 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

#primero se debe de dar click derecho, corrrer python en la terminal y luego en consola se debe de usaar el comando 
#flask --app Server run --debug (debug crea el modo depurador para guardar cambios en tiempo real sin necesidad de reiniciar el servidor)ñ 
#Ya no se usara el flask --app, etc. Dado que usaremos el comando python3 Server.py para correr el servidor, ya que es mas facil y rapido
# con el nuevo puerto 8080, ya que el puerto 5000 es usado por otro programa y no se pueden usar los dos al mismo tiempo  