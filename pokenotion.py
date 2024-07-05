import os
import requests
from dotenv import load_dotenv

# Fetching Pokémons from Poke API
def get_pokemons(first_pokemon=1, last_pokemon=11):
    pokemons = []

    for i in range(first_pokemon, last_pokemon):
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{i}')
        if response.status_code == 200:
            data = response.json()
            types = [t['type']['name'] for t in data['types']]
            hp = next(stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'hp')
            sprite = data['sprites']['other']['official-artwork']['front_default']
            pokemons.append({
                'id': i,
                'name': data['name'],
                'hp': hp,
                'types': types,
                'sprite': sprite  # Cambiado de artWork a sprite
            })
            print(f'Fetching pokemon {i}: {data["name"]}')
        else:
            print(f"Error {response.status_code}: in pokemon {i}")

    return pokemons

# Injecting data to Notion Data Base
def insert_pokemons(pokemons):
    load_dotenv(dotenv_path="myenv/.env")
    NOTION_KEY = os.getenv('NOTION_KEY')
    NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

    CREATE_URL = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {NOTION_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    for pokemon in pokemons:
        new_page_data = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "cover": {
                "type": "external",
                "external": {"url": pokemon["sprite"]}
            },
            "properties": {
                "ID": {
                    "number": pokemon['id']
                },
                "NAME": {
                    "title": [
                        {
                            "text": {
                                "content": pokemon['name']
                            }
                        }
                    ]
                },
                "HP": {
                    "number": pokemon['hp']
                },
                "TYPES": {
                    "multi_select": [
                        {"name": type_} for type_ in pokemon['types']
                    ]
                },
            }
        }

        response = requests.post(CREATE_URL, headers=headers, json=new_page_data)
        if response.status_code == 200:
            print(f"Pokemon {pokemon['name']} inserted successfully.")
        else:
            print(f"Error inserting pokemon {pokemon['name']}: {response.status_code}")
            print(response.json())

def main():
    pokemons = get_pokemons()
    insert_pokemons(pokemons)

if __name__ == "__main__":
    main()
