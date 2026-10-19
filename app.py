import sqlite3
from flask import Flask, request, jsonify

def crear_app(db_path="pedidos.db"):
    app = Flask(__name__)
    app.config["DB"] = db_path

    def conectar():
        con = sqlite3.connect(app.config["DB"])
        con.row_factory = sqlite3.Row
        return con

    # Modulo 1: base de datos
    with conectar() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL)""")

    # Modulo 2: API
    @app.post("/pedidos")
    def crear_pedido():
        datos = request.get_json(silent=True) or {}
        producto = datos.get("producto")
        cantidad = datos.get("cantidad")
        if not producto or not isinstance(cantidad, int) or cantidad <= 0:
            return jsonify(error="Datos invalidos"), 400
        with conectar() as con:
            cur = con.execute("INSERT INTO pedidos (producto, cantidad) VALUES (?, ?)",
                              (producto, cantidad ))
            nuevo_id = cur.lastrowid
        return jsonify(id=nuevo_id, producto=producto, cantidad=cantidad), 201

    @app.get("/pedidos/<int:pid>")
    def ver_pedido(pid):
        with conectar() as con:
            fila = con.execute("SELECT * FROM pedidos WHERE id = ?", (pid,)).fetchone()
        if fila is None:
            return jsonify(error="No encontrado"), 404
        return jsonify(dict(fila)), 200

    return app

if __name__ == "__main__":
    crear_app().run(debug=True)
