from host_lookup import *
from dns_lookup import *
import bitdotio

class AddDomain:
    # Clase para hacer las consultas de un dominio
    def __init__(self) -> None:
        self.API_KEY_BITIO = open('./bitio_api_key.txt', 'r').read()

        # esta variable apuntará a un archivo para añdir sentencias SQL.
        self.sqlFile = None

    def toSql(self, statement):
        # escribe una sentencia SQL en el archivo que ya se creó para ello.
        # No hay chequeos de ningún tipo!
        self.sqlFile.write(statement + ";\n")

    def fillIps(self, ip, id_for_key, typeIp, table, columns):
        # Realiza una consulta de host a Shodan y crea una fila en la tabla correspondiente
        # con la nueva información

        data = {"ports":[], "pais":None, "ciudad": None, "organizacion": None, "isp": None}
        host = shodanHostLookup(ip)
        if(host != None and host["data"] != None):
            data["ports"]=host["ports"]
            data["pais"]=host["country_name"]
            data["ciudad"]=host["city"]
            data["organization"]=host["org"]
            data["isp"]=host["isp"]
            data["asn"]=host["asn"]

            idProvHost = None

            provsSameAsn = self.query("SELECT ID FROM PROV_HOSTING WHERE ASN = '{}'".format(data["asn"]))
            #print(provsSameAsn)
            if provsSameAsn == []:
                provColumns = ["pais", "ciudad", "organization", "isp", "asn"]
                dataToInsert = [data["pais"], data["ciudad"], data["organization"], data["isp"], data["asn"]]
                dataToInsert = [x for x in dataToInsert if x is not None]
                provColumns = [x for x in provColumns if data[x] is not None]

                statement = "INSERT INTO PROV_HOSTING({}) VALUES({})".format(", ".join(provColumns), "'" + "', '".join(dataToInsert) + "'")
                print(statement)
                self.toSql(statement)
                idProvHost = self.insert(statement)
            else:
                idProvHost = provsSameAsn[0][0]

            print("\n")


            dataToInsert = [ip, ", ".join(str(v) for v in data["ports"])]
            statement = "INSERT INTO {}({}) VALUES({})".format(table, columns, "'" + "', '".join(dataToInsert) + "', " +  str(id_for_key) + ", " + str(idProvHost) +", " + typeIp)
            print(statement)  
            self.toSql(statement)

        else:
            print("Error ip: " + ip)
            errorTable = "IP_ERROR_MX"if table == "IP_MX" else "IP_ERROR"
            statement = "INSERT INTO {}(ip, dominio, type_ip) VALUES({})".format(errorTable,"'" + ip + "', " + str(id_for_key) + ", " + typeIp)
            print(statement)  
            self.toSql(statement)
        print("------------------------------------------------------\n")

    def fillRegs(self, reg, regValue, idOng):
        # toma información sobre un registro DNS y lo convierte en una fila para la base de datos
        statement = "INSERT INTO {}({}) VALUES({})".format(reg, reg + ", dominio", "'" + regValue + "', " + str(idOng) )
        print(statement)  
        self.toSql(statement)
        
    def insert(self, statement):
        # Hace una inserción en alguna tabla de la base de datos
        # alojada en bit.io. No hay ningún tipo de verificación!
        bitio = bitdotio.bitdotio(self.API_KEY_BITIO)
        with bitio.get_connection("jusanchez/ongs") as conn:
            cursor = conn.cursor()
            cursor.execute(statement + "RETURNING id")
            id = cursor.fetchone()[0]
            conn.commit()
            return id
    
    def query(self, statement):
        # Realiza una consulta en la base de datos alojada en bit.io
        # Tampoco hay verificaciones, la diferencia con insert es casi de nombre
        bitio = bitdotio.bitdotio(self.API_KEY_BITIO)
        with bitio.get_connection("jusanchez/ongs") as conn:
            cursor = conn.cursor()
            cursor.execute(statement)
            return cursor.fetchall()
    
    def fillDB(self, domain, country):
        # Realiza todas las consultas derivadas de un dominio.
        # Consulta los registros DNS y los procesa
        # Luego consulta las IP encontradas en esos registros y en los dominios de correo
        jsn = shodanDNSLookup(domain)["data"]
        self.sqlFile = open("db.sql", "a")
        self.toSql("--##############" + domain + "#######################")
        print("##############" + domain + "#######################")
        if jsn != None:
            data = {"A": set(), "AAAA": set(),"MX": set(), "NS": set(), "SOA": set(), "TXT": set(), "CNAME": set()}

            for reg in jsn:
                typereg = reg["type"]
                if typereg in data:
                    data[typereg].add(reg["value"])
            #print(json.dumps(data, indent=4))

            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            dataToInsert = [domain, country]
            statement = "INSERT INTO ONGS({}) VALUES({})".format("dominio, pais, prov_dominio_iana_id", "'" + "', '".join(dataToInsert) + "', NULL")

            self.toSql(statement)
            idOng = self.insert(statement)

            print("-----------------A------------------------")
            self.toSql("-----------------A------------------------")
            for A in data["A"]:
                self.fillIps(A, idOng, "FALSE", "IP","ip, ip_ports, dominio, prov_hosting, type_ip")

            print("-----------------AAAA------------------------")
            self.toSql("-----------------AAAA------------------------")
            for AAAA in data["AAAA"]:
                self.fillIps(AAAA, idOng, "TRUE", "IP", "ip, ip_ports, dominio, prov_hosting, type_ip")
            print("-----------------CNAME------------------------")
            self.toSql("-----------------CNAME------------------------")
            for cname in data["CNAME"]:
                self.fillRegs("CNAME", cname, idOng)
            print("-----------------NS------------------------")
            self.toSql("-----------------NS------------------------")
            for NS in data["NS"]:
                self.fillRegs("NS", NS, idOng)
            print("-----------------SOA------------------------")
            self.toSql("-----------------SOA------------------------")
            for SOA in data["SOA"]:
                self.fillRegs("SOA", SOA, idOng)
            print("-----------------TXT------------------------")
            self.toSql("-----------------TXT------------------------")
            for TXT in data["TXT"]:
                self.fillRegs("TXT", TXT, idOng)
            print("-----------------NX------------------------")
            self.toSql("-----------------MX------------------------")
            for MX in data["MX"]:
                jsnMx = shodanDNSLookup(MX)["data"]
                
                if jsnMx != None:
                    statement = "INSERT INTO MX(mx,dominio) VALUES({})".format("'" + MX + "', " + str(idOng))
                    print(statement)
                    self.toSql(statement)
                    idMx = self.insert(statement)
                    dataMx = {"A": set(), "AAAA": set()}
                    for reg in jsnMx:
                        typereg = reg["type"]
                        if typereg in dataMx:
                            dataMx[typereg].add(reg["value"])
                    print("-----------------A------------------------")
                    self.toSql("-----------------A------------------------")
                    for A in dataMx["A"]:
                        self.fillIps(A, idMx, "FALSE", "IP_MX", "ip_mx, ip_ports, mx, prov_hosting, type_ip")
                    print("-----------------AAAA------------------------")
                    self.toSql("-----------------AAAA------------------------")
                    for AAAA in dataMx["AAAA"]:
                        self.fillIps(AAAA, idMx, "TRUE", "IP_MX", "ip_mx, ip_ports, mx, prov_hosting, type_ip")
                else:
                    statement = "INSERT INTO ONG_ERROR(DOMINIO) VALUES({})".format(MX)
                    print(statement)
                    self.sqlFile(statement)
        else:
            statement = "INSERT INTO ONG_ERROR(DOMINIO) VALUES({})".format(domain)
            print(statement)
            self.sqlFile(statement)
        self.sqlFile.close()
