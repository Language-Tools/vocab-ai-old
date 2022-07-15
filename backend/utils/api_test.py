import requests
import pprint

API_TOKEN='tmOwGbF2dn9k45x2CTiyxpyPB7FHbghA'

def list_fields():
    response = requests.get(
    "http://localhost:8000/api/database/fields/table/262/",
    headers={
        "Authorization": f"Token {API_TOKEN}"
    }
    )

    pprint.pprint(response.json())

def list_database_tables():
    response = requests.get(
    "http://localhost:8000/api/database/tables/database/51/",
    headers={
        "Authorization": f"JWT {API_TOKEN}"
    }
    )

    pprint.pprint(response.json())    

def get_clt_language_data():
    response = requests.get(
    "http://localhost:8000/api/database/cloudlanguagetools/transliteration_options",
    headers={
        "Authorization": f"Token {API_TOKEN}"
    }
    )

    if response.status_code != 200:
        print(response.content)
    else:
        pprint.pprint(response.json())    

def get_translation_services():
    response = requests.get(
    "http://localhost:8000/api/database/cloudlanguagetools/translation_services/fr/en",
    headers={
        "Authorization": f"Token {API_TOKEN}"
    }
    )

    if response.status_code != 200:
        print(response.content)
    else:
        pprint.pprint(response.json())    


if __name__ == '__main__':
    # list_fields()
    # list_database_tables()
    # get_clt_language_data()
    get_translation_services()