import requests
from bs4 import BeautifulSoup

def scrap_update_ameli_excel():
    url = "https://www.assurance-maladie.ameli.fr/etudes-et-donnees/mp-indicateurs-selon-age-sexe-profession-exposition"
    reponse = requests.get(url)
    soup = BeautifulSoup(reponse.text, 'html.parser')
    
    # Maintenant on prend tous les liens qui finissent par .xlsx ou .xls
    links = soup.find_all('a')
    excel_url = None
    for link in links:
        href = link.get('href')
        if href and ('.xlsx' in href or '.xls' in href):
            excel_url = href
            break # Le premier est le plus récent
    
    if excel_url and excel_url != "https://www.assurance-maladie.ameli.fr/sites/default/files/2023_Risque-MP-par-%C3%A2ge-sexe-et-profession_serie-annuelle.xlsx": # Si existe et est différent du fichier 2023 
        print(f"Téléchargement de : {excel_url}")
        data = requests.get(excel_url).content
        
        filename = excel_url.split('/')[-1]
        annee = filename.split('_')[0]
        nom = "mp" + annee + ".xlsx"
        
        with open(nom, "wb") as f:
            f.write(data)
        print("Mise à jour réussie")
    else:
        print("Votre base de donnée est déjà à la dernière version.")
        

if __name__ == "__main__":
    scrap_update_ameli_excel() 