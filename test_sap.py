from hdbcli import dbapi
import traceback

try:
    print("Intentando conectar a SAP HANA...")
    conn = dbapi.connect(
        address='10.1.0.70',
        port=30015,
        user='SUPRALIVE',
        password='uGDH6%Yr$K'
    )
    print(" Conexión exitosa a SAP HANA")

    cursor = conn.cursor()
    cursor.execute('SELECT CURRENT_USER, CURRENT_DATE FROM DUMMY')
    result = cursor.fetchall()
    print(" Resultado de prueba:", result)

    cursor.close()
    conn.close()

except dbapi.Error as e:
    print("Error de conexión a SAP HANA:", e)
    traceback.print_exc()  
except Exception as ex:
    print(" Otro error no controlado:")
    traceback.print_exc()
