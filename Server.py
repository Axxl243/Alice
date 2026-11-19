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

def consultar_lista(sql):
    """Devuelve una lista de textos a partir de una consulta de una sola columna."""
    try:
        cursor = database.connection.cursor()
        cursor.execute(sql)
        filas = cursor.fetchall()
        cursor.close()
        return [f[0] for f in filas]
    except Exception as e:
        print(f"Error al consultar el menú: {e}")
        return []


# Hace que las listas del menú estén disponibles en TODAS las plantillas.
# Salen de la base de datos: si agregas una categoría o marca, aparece sola.
@app.context_processor
def datos_globales():
    return {
        "categorias_menu": consultar_lista("SELECT nombre FROM categorias ORDER BY nombre"),
        "marcas_menu": consultar_lista("SELECT nombre FROM companias ORDER BY nombre"),
    }


def listar_productos(busqueda=None, categoria=None, marca=None, limite=12):
    """Consulta productos con filtros opcionales (consulta parametrizada)."""
    sql = """
        SELECT p.id_producto, p.nombre, p.precio, p.imagen,
               c.nombre, co.nombre
        FROM productos p
        JOIN categorias c ON p.id_categoria = c.id_categoria
        JOIN companias co ON p.id_compania  = co.id_compania
        WHERE 1=1
    """
    params = []

    if busqueda:
        sql += " AND p.nombre LIKE %s"
        params.append(f"%{busqueda}%")
    if categoria:
        sql += " AND c.nombre = %s"
        params.append(categoria)
    if marca:
        sql += " AND co.nombre = %s"
        params.append(marca)

    sql += " ORDER BY p.id_producto DESC LIMIT %s"
    params.append(limite)

    try:
        cursor = database.connection.cursor()
        cursor.execute(sql, tuple(params))
        filas = cursor.fetchall()
        cursor.close()
    except Exception as e:
        # Por ejemplo, si todavía no se crearon las tablas
        print(f"Error al consultar productos: {e}")
        return []

    return [
        {"id": f[0], "nombre": f[1], "precio": f[2], "imagen": f[3],
         "categoria": f[4], "compania": f[5]}
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
    marca = request.args.get("marca")
    productos = listar_productos(categoria=categoria, marca=marca)
    return render_template("index.html", productos=productos, categoria=categoria, marca=marca)


@app.route("/buscar")
def buscar():
    q = request.args.get("q", "").strip()
    productos = listar_productos(busqueda=q) if q else []
    return render_template("index.html", productos=productos, categoria=None, marca=None)


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
@app.route('/perfil')
def perfil():
    # Solo usuarios con sesión iniciada
    if not session.get('emailUser'):
        flash("Inicia sesión para ver tu perfil", "warning")
        return redirect(url_for('login'))

    # Solo se consultan los datos del usuario que tiene la sesión abierta
    cursor = database.connection.cursor()
    cursor.execute(
        "SELECT Name_user, Apellidos_user, email_user FROM usuarios WHERE email_user = %s",
        (session['emailUser'],)
    )
    fila = cursor.fetchone()
    cursor.close()

    # Si la cuenta ya no existe en la base de datos, se cierra la sesión
    if not fila:
        session.clear()
        flash("No se encontró tu cuenta", "danger")
        return redirect(url_for('login'))

    usuario = {"nombre": fila[0], "apellidos": fila[1], "correo": fila[2]}
    return render_template('perfil.html', usuario=usuario)


# Ruta inventario (pendiente: alta de productos)

if __name__ == "__main__":
    # 127.0.0.1 = solo tu computadora. Cambia a "0.0.0.0" solo si quieres probar desde el celular en tu red.
    app.run(host="0.0.0.0", port=8080, debug=True)
