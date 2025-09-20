import requests

def main():
    place = input("Digite apenas o nome do lugar (ex: 'lugar=Tamandaré, UF=Pernambuco, País=Brazil'): ")

    query = f"""
        [out:json][timeout:25];
        area["name"="{place}"]["admin_level"="8"]->.a;
        (
        way["highway"](area.a);
        );
        out tags;
    """

    url = "http://overpass-api.de/api/interpreter"
    response = requests.get(url, params={"data": query})
    data = response.json()

    # extrai tipos de highway
    highways = set()

    for element in data['elements']:
        hw = element['tags'].get('highway')
        if hw:
            highways.add(hw)

    with open("./logs/highway_types.txt", "w") as f:
        for hw in sorted(highways):
            f.write(f"{hw}\n")

    print(f"Tipos de highways salvos em ./logs/highway_types.txt")
    print("Tipos de highways encontrados:")
    for hw in sorted(highways):
        print(hw)

if __name__ == "__main__":
    main()