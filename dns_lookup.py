# Módulos para solicitudes DNS
import dns.rdtypes
import dns.name
import dns.message
import dns.query
import dns.flags
import json

# Módulo de solicitudes HTTP(S)
import requests

# función para consulta de registros DNS
# parámetros por defecto buscan cualquier registro en los DNS de Google (8.8.8.8)
# domain: string con el dominio a consultar
# record: tipo de registro DNS a consultar, usar los tipos de dato dns.rdatatype
# name_server: string con la dirección (IPv4, IPv6 nunca probado) del DNS.
def dig(domain, record=dns.rdatatype.ANY, name_server='8.8.8.8'):
    ADDITIONAL_RDCLASS = 4096

    domain = dns.name.from_text(domain)
    if not domain.is_absolute():
        domain = domain.concatenate(dns.name.root)

    request = dns.message.make_query(domain, record)
    request.flags |= dns.flags.AD
    request.find_rrset(request.additional, dns.name.root, ADDITIONAL_RDCLASS,
                       dns.rdatatype.OPT, create=True, force_unique=True)
    response = dns.query.tcp(request, name_server)


    return response

API_KEY = open('./shodan_api_key.txt', 'r').read()

# función para consulta en Shodan
# La consulta "domain" de Shodan retorna también todos los registros DNS
# domain: string con el dominio a consultar
def shodanDNSLookup(domain):
    request = requests.get('https://api.shodan.io/dns/domain/{}?key={}'.format(domain, API_KEY))
    if request.status_code == 200:
        return request.json()
    else:
        return { "data": None }