import mysql.connector

def conectar_mysql():
    return mysql.connector.connect(
        host="192.168.1.14",
        database="bdSupraliveRRHH",
        user="root",
        password="Sw28Cw37",
        port=3306
    )