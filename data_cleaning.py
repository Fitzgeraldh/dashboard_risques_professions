import pandas as pd

def charger_fusionner_et_nettoyer(fichier_2021, fichier_2023):
    """
    Docstring pour charger_et_nettoyer
    Cette fonction va charger les données depuis les deux fichiers Excel, les fusionner et les nettoyer.
    
    :param chemin: Le chemin vers le fichier excel
    """
    
    # On sélectionne uniquement les colonnes qui nous seront utiles lors du chargement
    colonnes_utiles = [
        'libellé profession', 
        'libellé tranche d\'age', 
        'libellé sexe', 
        'Libellé durée d\'exposition', 
        'Libellé syndrome/ CIM 10',
        'Nombre de MP en premier règlement', 
        'Nombre de nouvelles IP', 
        'dont IP avec taux < 10%',
        'dont IP avec taux >= 10%',
        'Nombre de décès', 
        'Nombre de journées perdues', 
        'Somme des taux d\'IP'
    ]
    df_21 = pd.read_excel(fichier_2021, usecols = colonnes_utiles, engine = 'openpyxl')
    df_23 = pd.read_excel(fichier_2023, usecols = colonnes_utiles, sheet_name= 1, engine = 'openpyxl')
    
    # On ajoute une colonne "Année" à chacun d'eux avant la fusion
    df_21['Année'] = 2021
    df_23['Année'] = 2023
    
    # La fameuse fusion
    df = pd.concat([df_21, df_23], ignore_index = True)
    
    # On force le format numérique pour les colonnes de calcul et on remplace les vides par des 0
    colonnes_num = [
        'Nombre de MP en premier règlement', 
        'Nombre de nouvelles IP', 
        'dont IP avec taux < 10%', 
        'dont IP avec taux >= 10%', 
        'Nombre de décès', 
        'Nombre de journées perdues', 
        'Somme des taux d\'IP'
    ]
    for col in colonnes_num:
        if col in df.columns:
            # On s'assure que c'est du texte pour pouvoir le manipuler
            df[col] = df[col].astype(str)
            # On enlève les espaces et on remplace les virgules par des points
            df[col] = df[col].str.replace(' ', '', regex=False).str.replace(',', '.', regex=False)
            # 3. Maintenant, on peut convertir en nombre en toute sécurité !
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    # On s'occupe ensuite des vaelurs textuelles vides
    colonnes_texte = [
        'libellé profession', 
        'libellé tranche d\'age', 
        'libellé sexe', 
        'Libellé durée d\'exposition', 
        'Libellé syndrome/ CIM 10'
    ]
    for col in colonnes_texte:
        df[col] = df[col].fillna('Non renseigné')
        
    return df

df_filtre = charger_fusionner_et_nettoyer("mp2021.xlsx", "mp2023.xlsx")

df_filtre = df_filtre[df_filtre['Année'] == 2023]
    
df_filtre = df_filtre[df_filtre['libellé profession'] == "Agents d'entretien dans les bureaux, les hôtels et autres établissements"]

"""print(df_filtre.dtypes)
print(df_filtre.index)"""

print("Total réel des cas dans Pandas :", df_filtre['Nombre de MP en premier règlement'].sum())
print(df_filtre.info())