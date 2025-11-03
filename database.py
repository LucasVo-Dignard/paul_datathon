import sqlite3
from requests import get
import re

DBNAME = "paul.db"

#=================================================
def _select(requete, params=None):               #
    """ Exécute une requête type select"""       #
    with sqlite3.connect(DBNAME) as db:          #
        c = db.cursor()                          #
        if params is None:                       #
            c.execute(requete)                   #
        else:                                    #
            c.execute(requete, params)           #
        res = c.fetchall()                       #
    return res                                   #
#=================================================

def insert_zone(nomDev):
    requete = f"""insert into zone (name) values ('{nomDev}')"""
    return _select(requete)

def insert_secteur(nomDev):
    requete = f"""insert into secteur (name) values ('{nomDev}')"""
    return _select(requete)

def get_cId(nam):
    return _select(f"""select id from company where company.name = "{nam}" """)[0][0]

def get_cId_from_ticker(tick):
    return _select(f"""select id from company where company.ticker = "{tick}" """)[0][0]

def get_zoneId(nam):
    return _select(f"""select id from zone where zone.name = "{nam}" """)[0][0]

def get_sectorId(nam):
    return _select(f"""select id from secteur where secteur.name = "{nam}" """)[0][0]

def get_countries():
    return _select(f"""select name from zone""")

def get_sectors():
    return _select(f"""select name from secteur""")

def insert_mul(nam, idS):
    print(get_cId(nam))
    requete = f"""insert into companysectors (id_company, id_secteur) values ({get_cId(nam)}, {idS})"""
    return _select(requete)

def insert_muli(nam, idS):
    print(get_cId(nam))
    requete = f"""insert into companyzones (id_company, id_secteur) values ({get_cId(nam)}, {idS})"""
    return _select(requete)

def get_all_company_inf():
    requete = f"""select id, ticker from company"""
    return _select(requete)

def insert_10k(p1, p1a, p7, p7a, idC, issuedDate):
    requete = f"""insert into TenK (business, riskFactors, commentary, marketRisk, issuedDate, id_company) values ("{p1}", "{p1a}", "{p7}", "{p7a}", "{issuedDate}", {idC})"""
    return _select(requete)

def insert_company(ticker, name, marketcap, price):
    requete = f"""insert into company (ticker, name, marketcap, price) values ("{ticker}","{name}",{marketcap},{price});"""
    return _select(requete)

def update_company(ticker, desc):
    _select(f"""update company set description = "{desc}" where ticker = "{ticker}" """)

def insert_company_zone(tick, zname, desc):
    cId = get_cId_from_ticker(tick)
    zId = get_zoneId(zname)
    _select(f"""insert into companyzones (id_company, id_zone, description) values ({cId}, {zId}, "{desc}")""")

def get_desc_comp(tick):
    return _select(f"""select description from company where ticker = "{tick}" """)

def delete_last_ticker_entries(tick):
    cId = get_cId_from_ticker(tick)
    _select(f"""delete from companyzones where companyzones.id_company = {cId}""")

def match_secteur(sectors, zones):
    '''
    Get a list of companies from an aggregation of sectors and countries.
    Parametres :
    - sectors : list of string
    - zones : list of string
    Returns :
    - List of string
    '''
    return _select(f"""SELECT DISTINCT 
    c.Ticker,
    c.description,
    s.Name AS SectorName
FROM Company c
JOIN CompanySectors cs ON c.id = cs.id_Company
JOIN Secteur s ON cs.id_Secteur = s.id
JOIN CompanyZones cz ON c.id = cz.id_Company
JOIN Zone z ON cz.id_Zone = z.id
WHERE s.Name IN ('{"', '".join(sectors)}')
  AND z.name IN ('{"', '".join(zones)}')""")


def match_zone(sectors, zones):
    '''
    Get a description of the operations of a company in specific countries. Reduce to certain sectors.
    Parametres :
    - sectors : list of string
    - zones : list of string
    Returns :
    - List of string
    '''
    return _select(f"""SELECT 
    c.Ticker,
    z.name AS ZoneName,
    cz.description AS ZoneDescription
FROM Company c
JOIN CompanySectors cs ON c.id = cs.id_Company
JOIN Secteur s ON cs.id_Secteur = s.id
JOIN CompanyZones cz ON c.id = cz.id_Company
JOIN Zone z ON cz.id_Zone = z.id
WHERE s.Name IN ('{"', '".join(sectors)}')
  AND z.name IN ('{"', '".join(zones)}')""")

    