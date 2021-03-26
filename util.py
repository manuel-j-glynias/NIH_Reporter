import json
import sys
import os
import requests
from neo4j import GraphDatabase
from datetime import datetime,timedelta

def init(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver

def send_query(query:str, server:str) -> str:
    url = "http://" + server + ":7474/graphql/"
    headers = {
      'Authorization': 'Basic bmVvNGo6b21uaQ==',
      'Content-Type': 'application/json',
    }
    responseBody = ''
    try:
        response = requests.request("POST", url, headers=headers, json={'query': query})
        if not response.ok:
            response.raise_for_status()
            sys.exit()

        responseBody: str = response.json()
        # print(responseBody)
        if 'errors' in responseBody:
            print(responseBody)
            sys.exit()
    except requests.exceptions.RequestException as err:
        print('error in request')
        print(err)
        print(responseBody)
        sys.exit()
    return responseBody


def send_mutation(mutation_payload:str, server:str) -> str:
    url = "http://" + server + ":7474/graphql/"
    headers = {
      'Authorization': 'Basic bmVvNGo6b21uaQ==',
      'Content-Type': 'application/json',
    }
    mutation_payload = '{"query":"mutation {' + mutation_payload + '}"}'
    # print(mutation_payload)
    responseBody = ''
    try:
        response = requests.request("POST", url, headers=headers, data = mutation_payload.encode('utf-8'))
        if not response.ok:
            response.raise_for_status()
            print(mutation_payload)
            # sys.exit()
        responseBody: str = response.json()
        # print(responseBody)
        if 'errors' in responseBody:
            print(mutation_payload)
            print(responseBody)
            # sys.exit()
    except requests.exceptions.RequestException as err:
        print('error in request')
        print(err)
        print(mutation_payload)
        print(response.text)
        # sys.exit()
    except UnicodeEncodeError as err:
        print('UnicodeEncodeError')
        print(err)
        print(mutation_payload)
        print(responseBody)
        # sys.exit()
    # print(responseBody)
    return responseBody

def close(driver):
        driver.close()

def read_schema(driver):
    with open('config/schema.graphql', 'r') as file:
        idl_as_string = file.read()
    with driver.session() as session:
        tx = session.begin_transaction()
        tx.run("match(a) detach delete(a)")
        result = tx.run("call graphql.idl('" + idl_as_string + "')")
        # print(result.single()[0])
        tx.commit()

def get_list_of_files(path):
    json_files = []
    for entry in os.scandir(path):
        if entry.is_file():
            json_files.append(entry.path)
    return json_files

def get_data_from_json_file(path):
    with open(path, 'r') as afile:
        data = json.loads(afile.read())
    return data

def replace_characters(a_string: str):
    if a_string is not None:
        a_string = a_string.replace('α', 'alpha')
        a_string = a_string.replace(u"\u0391", 'A')
        a_string = a_string.replace('β', 'beta')
        a_string = a_string.replace('γ', 'gamma')
        a_string = a_string.replace('δ', 'delta')
        a_string = a_string.replace('ε', 'epsilon')
        a_string = a_string.replace('ζ', 'zeta')
        a_string = a_string.replace('η', 'eta')
        a_string = a_string.replace('θ', 'theta')
        a_string = a_string.replace('ι', 'iota')
        a_string = a_string.replace('ɩ', 'iota')
        a_string = a_string.replace('κ', 'kappa')
        a_string = a_string.replace('λ', 'lamda')
        a_string = a_string.replace('μ', 'mu')
        a_string = a_string.replace('ν', 'nu')
        a_string = a_string.replace('π', 'pi')
        a_string = a_string.replace('ρ', 'rho')
        a_string = a_string.replace('σ', 'sigma')
        a_string = a_string.replace('χ', 'chi')

        a_string = a_string.replace('ω', 'omega')
        a_string = a_string.replace(u"\u0394", 'delta')

        a_string = a_string.replace(u"\u03c5", 'upsilon')
        a_string = a_string.replace(u"\u03a5", 'Upsilon')
        a_string = a_string.replace('Ψ', 'Psi')
        a_string = a_string.replace('Ω', 'Omega')

        a_string = a_string.replace(u"\u025b", 'e')
        a_string = a_string.replace(u"\u0190", 'e')
        a_string = a_string.replace(u"\u223c", '~')
        a_string = a_string.replace(u"\u301c", '~')
        a_string = a_string.replace(u"\u2029", '')


        a_string = a_string.replace("á", "a")
        a_string = a_string.replace("à", "a")
        a_string = a_string.replace("ä", "a")
        a_string = a_string.replace("å", "a")
        a_string = a_string.replace("ã", "a")
        a_string = a_string.replace("â", "a")
        a_string = a_string.replace("ą", "a")
        a_string = a_string.replace("æ", "ae")

        a_string = a_string.replace("ç", "c")
        a_string = a_string.replace("č", "c")
        a_string = a_string.replace("ć", 'c')
        #
        a_string = a_string.replace("ě", "e")
        a_string = a_string.replace("ė", "e")
        a_string = a_string.replace("ę", "e")
        a_string = a_string.replace("é", "e")
        a_string = a_string.replace("è", "e")
        a_string = a_string.replace("ë", "e")
        a_string = a_string.replace("ê", "e")
        #
        a_string = a_string.replace("ﬁ", "fi")
        a_string = a_string.replace("ğ", "g")

        a_string = a_string.replace("í", "i")
        a_string = a_string.replace("ì", "i")
        a_string = a_string.replace("î", "i")
        a_string = a_string.replace("ï", "i")

        a_string = a_string.replace("ń", "n")
        a_string = a_string.replace("ň", "n")
        a_string = a_string.replace("ñ", "n")

        a_string = a_string.replace("ő", "o")
        a_string = a_string.replace("õ", "o")
        a_string = a_string.replace("ö", "o")
        a_string = a_string.replace("ó", "o")
        a_string = a_string.replace("ό", "o")
        a_string = a_string.replace("ò", "o")
        a_string = a_string.replace("ô", "o")
        a_string = a_string.replace("ø", "o")


        a_string = a_string.replace("ř", "r")

        a_string = a_string.replace("ş", "s")
        a_string = a_string.replace("ś", "s")
        a_string = a_string.replace("š", "s")
        a_string = a_string.replace("Š", "S")
        a_string = a_string.replace("Ş", "S")
        a_string = a_string.replace("ß", "s")

        a_string = a_string.replace("ť", "t")
        a_string = a_string.replace("ů", "u")
        a_string = a_string.replace("ü", "u")
        a_string = a_string.replace("ū", "u")
        a_string = a_string.replace("ù", "u")
        a_string = a_string.replace("ú", "u")

        a_string = a_string.replace("ÿ", "y")
        a_string = a_string.replace("ý", "y")
        a_string = a_string.replace("ż", "z")
        a_string = a_string.replace("ź", "z")
        a_string = a_string.replace("ž", "z")

        a_string = a_string.replace("’", "")
        a_string = a_string.replace('"', '')
        a_string = a_string.replace('\\', ' ')
        a_string = a_string.replace(u"\u2216", ' ')

        a_string = a_string.replace(u"\u201c", '')
        a_string = a_string.replace(u"\u201d", '')
        a_string = a_string.replace(u"\u2018", '')
        a_string = a_string.replace(u"\u2019", '')
        a_string = a_string.replace(u"\u05f3", '')
        a_string = a_string.replace(u"\u2032", '_')
        a_string = a_string.replace(u"\u2020", '*')
        a_string = a_string.replace(u"\u0142", '')
        a_string = a_string.replace(u"\u202f", ' ')
        a_string = a_string.replace(u"\u200a", ' ')
        a_string = a_string.replace(u"\u2002", ' ')
        a_string = a_string.replace('→', '->')
        a_string = a_string.replace(u"\u2012", '-')
        a_string = a_string.replace(u"\u207b", '-')
        a_string = a_string.replace(u"\uff0c", ', ')

        a_string = a_string.replace(u"\u207a", '+')
        a_string = a_string.replace(u"\u2011", '-')
        a_string = a_string.replace(u"\u2013", '-')
        a_string = a_string.replace(u"\u2014", '-')
        a_string = a_string.replace(u"\u2044", '/')
        a_string = a_string.replace(u"\u2122", 'TM')
        a_string = a_string.replace(u"\u2005", ' ')
        a_string = a_string.replace(u"\u2009", ' ')
        a_string = a_string.replace(u"\u0131", 'i')
        a_string = a_string.replace(u"\u2081", '1')
        a_string = a_string.replace(u"\u2082", '2')
        a_string = a_string.replace(u"\u2265", '>=')
        a_string = a_string.replace(u"\u2264", '<=')
        a_string = a_string.replace(u"\u2264", '<=')
        a_string = a_string.replace(u"\u226b", ' >>')
        a_string = a_string.replace(u"\u2248", ' =')
        a_string = a_string.replace('\t',' ')
        a_string = a_string.replace('\r','')
        a_string = a_string.replace('\n',' ')
        a_string = a_string.replace('#',' ')
        a_string = a_string.replace('⁸⁸','')
        a_string = a_string.replace('⁹⁰','')
        a_string = a_string.replace('Ⅱ','II')
        a_string = a_string.replace('Ⅰ','I')
        a_string = a_string.replace('&', '')
        a_string = a_string.replace(':', '')
        a_string = a_string.replace('+', '_')
        a_string = a_string.replace('‐','_')
        a_string = a_string.replace('_x000D_','')
        a_string = a_string.replace('~','about ')

    return a_string


def to_graphql_boolean(value):
    g_value = 'false'
    if value:
        g_value = 'true'
    return g_value



def initialize_graph(server):
    driver = init("bolt://" + server + ":7687", "neo4j", "omni")
    read_schema(driver)
    close(driver)

def today_as_string():
    now = datetime.now()
    date_time = now.strftime("%m-%d-%Y %I:%M %p")
    return date_time

def yesterday_as_string():
    yesterday = datetime.now() - timedelta(1)
    date_time = yesterday.strftime("%m-%d-%Y")
    return date_time


def get_unique_id(tag):
    return tag + datetime.now().strftime("%Y%m%d%H%M%S%f")