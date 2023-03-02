import bitdotio
import requests
import time


def getVulnsFrom(CPECode):
    # Busca vulnerabilidades relacionadas a un código CPE
    # El uso anónimo de la API de la NVD tiene un límite 
    # de 5 consultas cada 30 segundos. Por esto se hace una
    # consulta cada 6 segundos.

    print('Solicitando vulns para', CPECode)
    request = requests.get('https://services.nvd.nist.gov/rest/json/cves/2.0?cpeName={}'.format(CPECode))
    request = request.json()
    res = request['vulnerabilities']

    totalResults = request['totalResults']
    print('Resultados totales:', totalResults)
    time.sleep(6)
    while len(res) < totalResults:
        request = requests.get('https://services.nvd.nist.gov/rest/json/cves/2.0?cpeName={}&startIndex={}'.format(CPECode, len(res)))
        request = request.json()
        res += request['vulnerabilities']
        time.sleep(6)
    
    print('Terminado')
    return res

def processVulnsInfoFrom(CPEDict):
    # Toma un dict CPE->IDs de servicio_u
    # para cada CPE consulta todas las vulns y crea inserts para cada servicio,
    # pues hay filas distintas en servicio_u con el mismo CPE
    res = []
    for CPECode in CPEDict:
        vulnerabilities = getVulnsFrom(CPECode)
        for vulnerability in vulnerabilities:
            temp = vulnerability['cve']
            CVECode = temp['id']
            try:
                CVSSData = temp['metrics']['cvssMetricV2'][0]['cvssData']
                res += [
                    "('{}', {}, {}, '{}', '{}', '{}', '{}', '{}', '{}')".format(
                        CVECode,
                        CVSSData['baseScore'],
                        id,
                        CVSSData['accessVector'][0], # aprovechando que la correspondencia es
                                                    # {'LOCAL':'L', 'ADJACENT_NETWORK':'A', 'NETWORK':'N'}
                        CVSSData['accessComplexity'][0], # caso similar al anterior
                        CVSSData['authentication'][0], # igual
                        CVSSData['confidentialityImpact'][0],
                        CVSSData['integrityImpact'][0],
                        CVSSData['availabilityImpact'][0]
                    )
                    for id in CPEDict[CPECode]
                ]
            except:
                print('Falla de JSON con', CVECode)
    return res

if __name__ == '__main__':
    # Busca las filas de la tabla de servicios únicos que tengan
    # un código CPE asignado.
    API_KEY_BITIO = open('./bitio_api_key.txt', 'r').read()
    statement = '''
        SELECT cpe, id FROM servicio_u where cpe is not null;
    '''
    
    bitio = bitdotio.bitdotio(API_KEY_BITIO)
    with bitio.get_connection("jusanchez/ongs") as conn:
        cursor = conn.cursor()
        cursor.execute(statement)
        serviceList = cursor.fetchall()
    
    # El diccionario evita las consultas repetidas, cosa importante por
    # las limitaciones de la API
    CPEDict = {}
    for cpe, id in serviceList:
        if cpe in CPEDict:
            CPEDict[cpe].append(id)
        else:
            CPEDict[cpe] = [id]
    
    vulns = processVulnsInfoFrom(CPEDict)
    
    # Escribe los resultados en un archivo
    inserts = 'INSERT INTO vulnerabilidad_nvd(CVE, SCORE, SERVICIO_U, ACCESS_VECTOR, ACCESS_COMPLEXITY, AUTHENTICATION_REQUIREMENT, CONFIDENTIALITY_IMPACT, INTEGRITY_IMPACT, AVAILABILITY_IMPACT) VALUES'
    inserts += '\n' + ',\n'.join(vulns) + ';\n'
    with open('vulns.sql', 'a') as f:
        f.write(inserts)
