import requests
import pandas as pd
from sqlalchemy import create_engine

URL = "https://pokeapi.co/api/v2/pokemon"
BANCO = "postgresql://admin:admin@localhost:5433/pokemon"
TOTAL = 151


def extrair():
    dados = []
    for i in range(1, TOTAL + 1):
        resposta = requests.get(f"{URL}/{i}", timeout=10)
        resposta.raise_for_status()
        dados.append(resposta.json())
        print(f"Buscando {i}/{TOTAL}", end="\r")
    print()
    return dados


def transformar(dados):
    linhas = []
    for p in dados:
        status = {s["stat"]["name"]: s["base_stat"] for s in p["stats"]}
        tipos = [t["type"]["name"] for t in p["types"]]
        linhas.append({
            "id": p["id"],
            "nome": p["name"],
            "altura_dm": p["height"],
            "peso_hg": p["weight"],
            "tipo_1": tipos[0],
            "tipo_2": tipos[1] if len(tipos) > 1 else None,
            "hp": status["hp"],
            "ataque": status["attack"],
            "defesa": status["defense"],
            "ataque_especial": status["special-attack"],
            "defesa_especial": status["special-defense"],
            "velocidade": status["speed"],
        })
    df = pd.DataFrame(linhas)
    df["total_status"] = df[
        ["hp", "ataque", "defesa", "ataque_especial",
         "defesa_especial", "velocidade"]
    ].sum(axis=1)
    return df


def carregar(df):
    engine = create_engine(BANCO)
    df.to_sql("pokemon", engine, if_exists="replace", index=False)


def main():
    dados = extrair()
    df = transformar(dados)
    carregar(df)
    print(f"{len(df)} Pokémon salvos no banco.")
    print(df[["nome", "tipo_1", "total_status"]].head())


if __name__ == "__main__":
    main()
