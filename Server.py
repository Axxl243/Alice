from flask import Flask, flash, render_template, request, url_for, redirect, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo, DataRequired
 
from werkzeug.security import generate_password_hash, check_password_hash
 
from config_Server import config
 
from flask_mysqldb import MySQL
 
# variables globales
app = Flask(__name__)
app.config.from_object(config)
 
database = MySQL(app)
 
# Categorías del menú (deben coincidir con la columna "categoria" de la tabla productos)
CATEGORIAS = ["Nintendo", "PlayStation", "Xbox", "PC", "Accesorios"]
 
 
# Hace que "categorias_menu" esté disponible en TODAS las plantillas
@app.context_processor
def datos_globales():
    return {"categorias_menu": CATEGORIAS}
 
 
def listar_productos(busqueda=None, categoria=None, limite=12):
    """Consulta productos con filtros opcionales (consulta parametrizada)."""
    sql = "SELECT id_producto, nombre, precio, imagen, categoria FROM productos WHERE 1=1"
    params = []
 
    if busqueda:
        sql += " AND nombre LIKE %s"
        params.append(f"%{busqueda}%")
    if categoria:
        sql += " AND categoria = %s"
        params.append(categoria)
 
    sql += " ORDER BY id_producto DESC LIMIT %s"
    params.append(limite)
 
    try:
        cursor = database.connection.cursor()
        cursor.execute(sql, tuple(params))
        filas = cursor.fetchall()
        cursor.close()
    except Exception as e:
        # Por ejemplo, si todavía no se creó la tabla productos
        print(f"Error al consultar productos: {e}")
        return []
 
    return [
        {"id": f[0], "nombre": f[1], "precio": f[2], "imagen": f[3], "categoria": f[4]}
        for f in filas
    ]
 
 
# Rutas
@app.route("/")  # Route principal
def index():
    # El saludo solo aparece una vez por sesión
    if not session.get("bienvenida"):
        flash("Bienvenido!!, espero que encuentres lo que necesites :D", "info")
        session["bienvenida"] = True
 
    categoria = request.args.get("categoria")
    productos = listar_productos(categoria=categoria)
    return render_template("index.html", productos=productos, categoria=categoria)
 
 
@app.route("/buscar")
def buscar():
    q = request.args.get("q", "").strip()
    productos = listar_productos(busqueda=q) if q else []
    return render_template("index.html", productos=productos, categoria=None)
 
 
class Registro(FlaskForm):
 
    rNombre = StringField("Nombre", validators=[Length(min=3, max=50, message="Ingrese un nombre valido")])
    rApellidos = StringField("Apellidos", validators=[InputRequired(), Length(min=1, max=150)])
    rCorreo = StringField("Correo", validators=[InputRequired(), Email()])
    rPass = PasswordField("Contraseña", validators=[DataRequired(message="Este campo es obligatorio"), Length(min=8, message="La contraseña debe tener al menos 8 caracteres")])
    rConfirmar = PasswordField("Confirmar Contraseña", validators=[DataRequired(message="Este campo es obligatorio"), EqualTo("rPass", message="Las contraseñas no coinciden")])
    rTYC = BooleanField("Aceptar Términos y Condiciones", validators=[DataRequired()])
    rSubmit = SubmitField("Registrarse")
 
 
# ruta de registro
@app.route("/formulario", methods=['GET', 'POST'])
def registro():
    form = Registro()
    if form.validate_on_submit():
        inNombre = form.rNombre.data
        inApellidos = form.rApellidos.data
        inCorreo = form.rCorreo.data
        inPass = form.rPass.data
 
        cursor = database.connection.cursor()
 
        # Evita registrar dos veces el mismo correo
        cursor.execute("SELECT 1 FROM usuarios WHERE email_user = %s", (inCorreo,))
        if cursor.fetchone():
            cursor.close()
            flash("Ese correo ya está registrado", "warning")
            return render_template('formulario.html', form=form)
 
        password_hashed = generate_password_hash(inPass)
        sqlCreateUsuario = "INSERT INTO usuarios(Name_user, email_user, pass_user, Apellidos_user) VALUES(%s,%s,%s,%s)"
        cursor.execute(sqlCreateUsuario, (inNombre, inCorreo, password_hashed, inApellidos))
        database.connection.commit()
        cursor.close()
 
        flash("La cuenta ha sido registrada", "success")
        return redirect(url_for("login"))
 
    return render_template('formulario.html', form=form)
 
 
# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    msj = ""
 
    if request.method == 'POST':
        logUser = request.form.get('logUser')
        logPass = request.form.get('logPass')
 
        if logUser and logPass:
            Loginsql = "SELECT name_User, email_user, pass_user FROM usuarios WHERE email_user = %s"
            loginCon = database.connection.cursor()
            loginCon.execute(Loginsql, (logUser,))
            reslogin = loginCon.fetchone()
            loginCon.close()
 
            if reslogin and check_password_hash(reslogin[2], logPass):
                session['nameUser'] = reslogin[0]
                session['emailUser'] = reslogin[1]
                flash("Bienvenido a la pagina", "success")
                return redirect(url_for('index'))
 
            flash("Los datos son incorrectos", "danger")
        else:
            flash("Ingrese los datos completos", "danger")
 
    return render_template('login.html', msj=msj)
 
 
@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for('index'))
 
 
# Ruta de perfil
@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    # Solo usuarios con sesión iniciada
    if not session.get('emailUser'):
        flash("Inicia sesión para ver tu perfil", "warning")
        return redirect(url_for('login'))
 
    consulta_perfil = database.connection.cursor()
    sql_consulta = "SELECT * FROM usuarios"
    consulta_perfil.execute(sql_consulta)
    res_consulta = consulta_perfil.fetchall()
    consulta_perfil.close()
 
    usuarios = []
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
        usuarios = None
    return render_template('perfil.html', tabla=usuarios)
 
 
# Ruta inventario (pendiente: alta de productos)
 
if __name__ == "__main__":
    # 127.0.0.1 = solo tu computadora. Cambia a "0.0.0.0" solo si quieres probar desde el celular en tu red.
    app.run(host="0.0.0.0", port=8080, debug=True)
 
