from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ramon_gutierrez_subirtupagina_key"

# Contraseña por defecto para acceder al panel administrativo
ADMIN_PASSWORD = "adminortolook"
DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Inicialización de la Base de Datos con valores predeterminados (Ubicaciones reales)
def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db()
        # Tabla para registro de citas
        conn.execute('''
            CREATE TABLE IF NOT EXISTS citas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT NOT NULL,
                sucursal TEXT NOT NULL,
                fecha TEXT NOT NULL
            )
        ''')
        # Tabla autoadministrable para sucursales
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sucursales (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                zona TEXT NOT NULL,
                direccion TEXT NOT NULL,
                referencia TEXT NOT NULL,
                mapa_url TEXT NOT NULL
            )
        ''')
        # Insertar los datos de las dos sucursales oficiales de Ortolook
        conn.execute("""
            INSERT INTO sucursales VALUES (
                1, 
                'Sucursal Zapopan SUR', 
                'Las Águilas', 
                'Río Cuitzmala 5439 A, Col. Las Águilas, Zapopan', 
                'Hacemos esquina con 18 de Marzo', 
                'https://www.google.com/maps/search/?api=1&query=Rio+Cuitzmala+5439+A+Las+Aguilas+Zapopan'
            )
        """)
        conn.execute("""
            INSERT INTO sucursales VALUES (
                2, 
                'Sucursal Guadalajara NORTE', 
                'Unidad Médica', 
                'Av. Experiencia 2721, Santa Elena de la Cruz, Guadalajara', 
                'Consultorio #4', 
                'https://www.google.com/maps/search/?api=1&query=Av+Experiencia+2721+Santa+Elena+de+la+Cruz+Guadalajara'
            )
        """)
        conn.commit()
        conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db()
    sucursales = conn.execute('SELECT * FROM sucursales').fetchall()
    conn.close()
    return render_template('index.html', sucursales=sucursales)

@app.route('/agendar', methods=['POST'])
def agendar_cita():
    nombre = request.form.get('nombre')
    telefono = request.form.get('telefono')
    sucursal = request.form.get('sucursal')
    fecha = request.form.get('fecha')
    
    conn = get_db()
    conn.execute('INSERT INTO citas (nombre, telefono, sucursal, fecha) VALUES (?, ?, ?, ?)',
                 (nombre, telefono, sucursal, fecha))
    conn.commit()
    conn.close()
    
    flash("¡Tu solicitud de cita se ha enviado con éxito! Nos comunicaremos contigo pronto.", "success")
    return redirect(url_for('index'))

# --- PANEL DE ADMINISTRACIÓN ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
        else:
            flash("Contraseña incorrecta", "error")
    
    if not session.get('logged_in'):
        return render_template('login.html')
        
    conn = get_db()
    citas = conn.execute('SELECT * FROM citas ORDER BY id DESC').fetchall()
    sucursales = conn.execute('SELECT * FROM sucursales').fetchall()
    conn.close()
    return render_template('admin.html', citas=citas, sucursales=sucursales)

@app.route('/admin/update_sucursal/<int:id>', methods=['POST'])
def update_sucursal(id):
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
        
    nombre = request.form.get('nombre')
    zona = request.form.get('zona')
    direccion = request.form.get('direccion')
    referencia = request.form.get('referencia')
    mapa_url = request.form.get('mapa_url')
    
    conn = get_db()
    conn.execute('''
        UPDATE sucursales 
        SET nombre=?, zona=?, direccion=?, referencia=?, mapa_url=? 
        WHERE id=?
    ''', (nombre, zona, direccion, referencia, mapa_url, id))
    conn.commit()
    conn.close()
    flash("Sucursal actualizada correctamente", "success")
    return redirect(url_for('admin'))

@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)