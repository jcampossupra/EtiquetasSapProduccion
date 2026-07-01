import mysql.connector
from tkinter import messagebox

def conectar_mysql():
    try:
        conexion = mysql.connector.connect(
            host="192.168.1.14",
            database="bdSupraliveRRHH",
            user="root",
            password="Sw28Cw37",
            port=3306
        )

        return conexion

    except Exception as e:
        messagebox.showerror(
            "Error MySQL",
            f"{type(e).__name__}\n{str(e)}"
        )
        return None