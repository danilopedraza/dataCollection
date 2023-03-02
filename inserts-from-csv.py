import bitdotio
import pandas as pd


if __name__ == '__main__':
    # Convierte lo obtenido con host_lookup.py en filas para la base de datos
    
    API_KEY_BITIO = open('./bitio_api_key.txt', 'r').read()

    statement = '''
        SELECT ip, id FROM ip;
    '''
    bitio = bitdotio.bitdotio(API_KEY_BITIO)
    with bitio.get_connection("jusanchez/ongs") as conn:
        cursor = conn.cursor()
        cursor.execute(statement)
        IPIDList = cursor.fetchall()
    
    IPIDList = {row[0]:row[1] for row in IPIDList}
    serviceList = pd.read_csv('./hosts.csv')

    res = 'INSERT INTO SERVICIO_NMAP(ip, puerto, protocolo, estado, servicio) VALUES\n'
    for index, row in serviceList.iterrows():
        res += '({}, {}, {}, {}, {}),\n'.format(
            str(IPIDList[row['address']]),
            str(row['port']),
            "'"+row['protocol']+"'",
            "'"+row['state']+"'",
            "'"+row['service']+"'"
        )

    res = res[:-2]
    res += ';\n'

    with open('nmap-inserts.sql', 'a') as f:
        f.write(res)
