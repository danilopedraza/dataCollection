import pandas as pd
from fill_db import AddDomain

def main():
    # El que se suponía iba a ser el hilo principal del programa.
    # Con la verificación manual entre consultas,
    # la expectativa de que todo fuera una rutina conectada desapareció. 
    domains = pd.read_csv('./domains.csv')
    adder = AddDomain()
    
    for index, row in domains.iterrows():
        adder.fillDB(row["domain"], row["country"])
if __name__ == "__main__":
    main()
