from flask import Flask, flash, render_template, request, url_for, flash, redirect, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo, DataRequired

from werkzeug.security import generate_password_hash, check_password_hash 

from config_Server import config

from flask_mysqldb import MySQL

#variables globales
app= Flask(__name__)
app.config.from_object(config)

database = MySQL(app)


#Rutas 
@app.route("/")#Route principal
def index(): 
    flash("Bienvenido!!, espero que encuentres lo que necesites :D", "danger")
    return (render_template("index.html"))

class Registro(FlaskForm):
    
    rNombre = StringField("Nombre", validators=[Length(min=3, max=50, message="Ingrese un nombre valido")])
    rApellidos = StringField("Apellidos", validators=[InputRequired(), Length(min=1, max=150)])
    rCorreo = StringField("Correo", validators=[InputRequired(), Email()])
    rPass = PasswordField("Contraseña", validators=[DataRequired(message="Este campo es obligatorio"), Length(min=8, message="La contraseña debe tener al menos 8 caracteres")])
    rConfirmar = PasswordField("Confirmar Contraseña", validators=[DataRequired(message="Este campo es obligatorio"), EqualTo("rPass", message="Las contraseñas no coinciden")])
    rTYC = BooleanField("Aceptar Términos y Condiciones", validators=[DataRequired()])
    rSubmit = SubmitField("Registrarse")


#ruta de registro
@app.route("/formulario", methods=['GET', 'POST'])
def registro():
    form = Registro()
    if form.validate_on_submit():
        inNombre = form.rNombre.data
        inApellidos = form.rApellidos.data
        inCorreo = form.rCorreo.data
        inPass = form.rPass.data
        inConfirmar = form.rConfirmar.data
        inTYC = form.rTYC.data

        #values = f"nombre: {inNombre}, apellidos: {inApellidos}, correo: {inCorreo}, contraseña: {inPass}, confirmar contraseña: {inConfirmar}, TYC: {inTYC}"
        #print(values)
        if inPass == inConfirmar and inTYC != False:
           
           password_hashed = generate_password_hash(inPass) 
           sqlCreateUsuario = "INSERT INTO usuarios(Name_user, email_user, pass_user, Apellidos_user) VALUES(%s,%s,%s,%s)"

           CreateUsuario = database.connection.cursor()
           CreateUsuario.execute(sqlCreateUsuario,(inNombre, inCorreo, password_hashed, inApellidos))
           database.connection.commit()
           CreateUsuario.close()

           flash("La cuenta ha sido registrada", "SUCCESS")
           return redirect("login")

    return render_template('formulario.html', form=form)


#Ruta de login
@app.route('/login', methods = ['GET', 'POST'])
def login():
    msj = "No data"

    if request.method == 'POST':
        logUser = request.form.get('lUser')
        logPass = request.form.get('lPass')

        if logUser and logPass:
           Loginsql = "SELECT name_User, email_user, pass_user FROM usuarios WHERE email_user = %s"
           loginCon = database.connection.cursor()
           loginCon.execute(Loginsql,(logUser,))
           reslogin = loginCon.fetchone()

           if reslogin:
               passDB = reslogin[2]
               if check_password_hash(passDB, logPass):
                   session['nameUser']= reslogin[0]
                   session['emailUser']= reslogin[1]

                   flash("Bienvenido a la pagina")
                   redirect(url_for('perfil')) 

               else:
                flash("Los datos son incorrectos", "Peligro")

        else:
            flash("Ingrese los datos completos", "Peligro")    

        #msj = f"Nombre: {logUser}, Contraseña: {logPass}"

        return render_template('login.html', msj=msj)
   
    return render_template('login.html', msj=msj)

#Ruta de perfil
@app.route('/perfil', methods = ['GET', 'POST'])
def perfil():
    consulta_perfil = database.connection.cursor()
    sql_consulta = "SELECT * FROM usuarios" 
    consulta_perfil.execute(sql_consulta)
    res_consulta = consulta_perfil.fetchall()
    usuarios=[]
    if res_consulta:
        for campo in res_consulta:
            usuarios.append(
               {
                   "uid": campo[0],
                   "unombre": campo[1],
                   "uapellidos": campo[2],
                   "ucorreo": campo[3],
                   "upass": "pass"
               }

            )
    else:
        usuarios= None
    return render_template('perfil.html', tabla = usuarios)

#Ruta inventario 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

#primero se debe de dar click derecho, corrrer python en la terminal y luego en consola se debe de usaar el comando 
#flask --app Server run --debug (debug crea el modo depurador para guardar cambios en tiempo real sin necesidad de reiniciar el servidor)ñ 
#Ya no se usara el flask --app, etc. Dado que usaremos el comando python3 Server.py para correr el servidor, ya que es mas facil y rapido
# con el nuevo puerto 8080, ya que el puerto 5000 es usado por otro programa y no se pueden usar los dos al mismo tiempo  