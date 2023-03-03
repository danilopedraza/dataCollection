from host_lookup import shodanHostLookup
import json
import bitdotio

DB_NAME = open('./db_name.txt', 'r').read()

class ServiceAdder:
    # Añade una dirección IP y sus servicios asociados

    def __init__(self):
        self.API_KEY_BITIO = open('./bitio_api_key.txt', 'r').read()
        self.sqlFile = None
    
    def formatValues(self, value):
        if value == None:
            return "NULL"
        if isinstance(value, str):
            return "'{}'".format(value)
        return value

    def toSql(self, statement):
        self.sqlFile.write(statement + ";\n")

    def query(self, statement):
            bitio = bitdotio.bitdotio(self.API_KEY_BITIO)
            with bitio.get_connection(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(statement)
                return cursor.fetchall()

    def insert(self, statement):
        bitio = bitdotio.bitdotio(self.API_KEY_BITIO)
        with bitio.get_connection(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(statement + "RETURNING id")
            id = cursor.fetchone()[0]
            conn.commit()
            return id

    def loadServices(self, dominio, ip, ipKey):
        # Esta rutina (y toda la clase) es similar a la que está en fillDB.py.
        # Solo que en este caso se añade información sobre los hosts y 
        # los servicios que ofrecen.

        self.sqlFile = open("servicios.sql", "a")
        self.toSql("--======================SERVICIOS==================")
        self.toSql("--##############" + dominio + "#######################")
        self.toSql("----------------" + ip + "-----------------------")
        host = shodanHostLookup(ip)["data"]

        for servicio in host:
            servicio_val = servicio.get("product", None)
            version = servicio.get("version", None)

            if servicio_val is not None and version is not None:
                servicioKey = None
                statement = "SELECT ID FROM SERVICIO_U WHERE SERVICIO = '{}' AND N_VERSION = '{}'".format(servicio_val, version)
                print(statement)
                provsSameAsn = self.query(statement)
                if provsSameAsn == []:
                    values = "{}, {}".format(self.formatValues(servicio_val),
                    self.formatValues(version))
                    statement = "INSERT INTO SERVICIO_U(servicio, n_version) VALUES ({})".format(values)
                    print(statement)
                    self.toSql(statement)
                    servicioKey = self.insert(statement)
                else:
                    servicioKey = provsSameAsn[0][0]
                statement = "INSERT INTO SERVICIO_IP_U(ip, servicio) VALUES({}, {})".format(ipKey, servicioKey)
                print(statement)
                self.toSql(statement)
