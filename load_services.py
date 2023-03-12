from service_adder import *

adder = ServiceAdder()
resSet = adder.query("SELECT IP.ID, IP.IP, ONGS.DOMINIO FROM IP INNER JOIN ONGS ON IP.DOMINIO = ONGS.ID")
for res in resSet:
    print(res[2], res[1], res[0])
    adder.loadServices(res[2], res[1], res[0])