import bitdotio
import multiprocessing as mp
import pandas as pd
import re
import requests
import subprocess

DB_NAME = open('./db_name.txt', 'r').read()

def NmapHostLookup(host, IPv6=False):
    # Se ejecuta el timeout {tiempo} comando nmap -p- -verbose {host}
    # gtimeout es el identificador del comando timeout en MacOS
    # cambiar a timeout si es necesario (básicamente cualquier sistema POSIX salvo apple)
    if IPv6:
        command = ['gtimeout', '12h', 'nmap', '-p-', '-verbose', '-6', host]
    else:
        command = ['gtimeout', '12h', 'nmap', '-p-', '-verbose', host]

    res = subprocess.run(command, capture_output=True, text=True)

    ports = []
    if re.search('PORT( )+STATE( )+SERVICE( )*', res.stdout):
        # que ese trozo de texto exista o no es mi criterio para decidir si nmap terminó por si solo
        # o fue detenido por timeout. En este caso, asumo que nmap terminó
        # así que capturo las líneas siguientes con toda la información encontrada
        res = res.stdout.splitlines()
        for i in range(len(res)):
            if re.match('PORT( )+STATE( )+SERVICE( )*', res[i]):
                res = res[i+1:-3]
                break
    
        for line in res:
            portAndProtocol, state, service = line.split()
            port, protocol = portAndProtocol.split('/')
            ports.append(
                {
                    'address':host,
                    'port':port,
                    'protocol':protocol,
                    'state':state,
                    'service':service
                }
            ) 
    else:
        # si la línea no está, asumo que nmap fue detenido por timeout
        # y capturo la información obtenida con -verbose
        # por mis pocas exloraciones de los logs veo que solo se muestra el
        # descubrimiento de puertos abiertos (sin el servicio correspondiente)
        # así que capturo SÓLO esas líneas. Son de la forma:
        # Discovered open port: {puerto}/{protocolo}
        # el código que parsea es parafraseado del primer caso
        res = res.stdout.splitlines()
        for line in res:
            if line[:20] == 'Discovered open port':
                line = line.split()
                portAndProtocol, state, service = line[3], 'open', 'unknown'
                port, protocol = portAndProtocol.split('/')
                ports.append(
                    {
                        'address':host,
                        'port':port,
                        'protocol':protocol,
                        'state':state,
                        'service':service
                    }
                )

    print(host, 'terminado')
    return ports



API_KEY = open('./shodan_api_key.txt', 'r').read()

def shodanHostLookup(host):
    # Realiza una consulta de registros DNS a Shodan. Cada una de estas consultas
    # requiere un query credit
    request = requests.get('https://api.shodan.io/shodan/host/{}?key={}'.format(host, API_KEY))
    if request.status_code == 200:
        return request.json()
    else:
        return { "data": None }


if __name__ == '__main__':
    # Recoge todas las IP de la tabla en la base de datos
    API_KEY_BITIO = open('./bitio_api_key.txt', 'r').read()

    statement = '''
        SELECT ip, type_ip FROM ip;
    '''
    
    bitio = bitdotio.bitdotio(API_KEY_BITIO)
    with bitio.get_connection(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(statement)
        IPList = cursor.fetchall()
    
    print(len(IPList), 'direcciones a consultar')
    # Crea un hilo por cada IP  y ejecuta Nmap en este
    pool = mp.Pool(len(IPList))
    df = [
        pool.apply_async(NmapHostLookup, args=(row[0], row[1]))
        for row in IPList
        ]
    pool.close()
    pool.join()
    df = sum([worker.get() for worker in df], [])
    print('Terminado')

    df = pd.DataFrame.from_records(df, columns=['address', 'port', 'protocol', 'state', 'service'])
    print(df)
    # Escribe todo en un CSV
    df.to_csv('./hosts.csv', index=False)
