from hdbcli import dbapi

try:
    cnsap = dbapi.connect(address='10.1.0.70', port=30015, user='SUPRALIVE', password='uGDH6%Yr$K')
    #cnsap = dbapi.connect(address='10.254.254.254', port=30015, user='SVAGRT_DBREADER', password='dPtWhDwV2aRHR5bA')
    print("Conexión exitosa a SAP HANA.")
except dbapi.Error as e:
    print(f"Error al conectar con SAP HANA: {e}")
