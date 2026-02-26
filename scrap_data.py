import requests
from bs4 import BeautifulSoup

def scrap_ameli_excel():
    url = "https://www.assurance-maladie.ameli.fr/etudes-et-donnees/mp-indicateurs-selon-age-sexe-profession-exposition"
    reponse = requests.get(url)
    soup = BeautifulSoup(reponse.text, 'html.parser')
    
    # Maintenant on prend tous les liens qui finissent par .xlsx ou .xls
    links = soup.find_all('a')
    excel_urls = []
    for link in links:
        href = link.get('href')
        if href and ('.xlsx' in href or '.xls' in href):
            excel_urls.append(href)
    
    if len(excel_urls) != 0 :
        for excel_url in excel_urls:
            print(f"Téléchargement de : {excel_url}")
            data = requests.get(excel_url).content
            
            filename = excel_url.split('/')[-1]
            annee = filename.split('_')[0]
            nom = "mp_" + annee + ".xlsx"
            
            with open(nom, "wb") as f:
                f.write(data)
            print("Téléchargement réussi")
    else:
        print("Aucun fichier excel trouvé")
    
    print("Téléchargement des fichiers terminé")
        

if __name__ == "__main__":
    scrap_ameli_excel() 