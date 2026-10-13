#Befehl für die Power Shell

Set-Content -Path "C:\work\Python08.2026\network_analysis.py" -Encoding UTF8 -Value @'
import os
import glob
import itertools
import re
import pandas as pd
import networkx as nx

# 1. Datei lokalisieren (prüft texts_archiv_alle.csv oder Fallback-Namen)
DATA_DIR = r"C:\work\Python08.2026"
csv_files = glob.glob(os.path.join(DATA_DIR, "texts_archiv_alle*.csv"))

if not csv_files:
    raise FileNotFoundError("Keine 'texts_archiv_alle*.csv' Datei gefunden!")

target_file = csv_files[0]
print(f"Analysiere Datensatz: {target_file}")
df = pd.read_csv(target_file)

# 2. Relevantes Akteurs- und Entitäten-Vokabular (Politiker, Staaten, Formate)
ENTITY_PATTERNS = {
    # Aktuelle deutsche Akteure
    "Wadephul": r"\b(Wadephul|Johann Wadephul)\b",
    "Güler": r"\b(Güler|Serap Güler)\b",
    "Castellucci": r"\b(Castellucci|Lars Castellucci)\b",
    "Baerbock": r"\b(Baerbock|Annalena Baerbock)\b",
    "Maas": r"\b(Heiko Maas|Maas)\b",
    "Scholz": r"\b(Olaf Scholz|Scholz)\b",
    
    # Internationale Staaten & Schwerpunkte
    "USA": r"\b(USA|Vereinigte Staaten|Washington|Blinken)\b",
    "Ukraine": r"\b(Ukraine|Kiew|Kyjiw|Selenskyj)\b",
    "Russland": r"\b(Russland|Moskau|Putin|Lavrov|Lawrow)\b",
    "Frankreich": r"\b(Frankreich|Paris|Macron|Séjourné|Barrot)\b",
    "Polen": r"\b(Polen|Warschau|Sikorski)\b",
    "Israel": r"\b(Israel|Jerusalem|Tel Aviv|Netanjahu)\b",
    "Palästina/Gaza": r"\b(Gaza|Palästin\w+|Westjordanland|Hamas)\b",
    "China": r"\b(China|Peking|Beijing|Wang Yi)\b",
    "Großbritannien": r"\b(Großbritannien|London|UK|Vereinigtes Königreich)\b",
    "Italien": r"\b(Italien|Rom|Meloni|Tajani)\b",
    "Türkei": r"\b(Türkei|Ankara|Erdogan|Fidan)\b",
    "Iran": r"\b(Iran|Teheran)\b",

    # Multilaterale Formate & Allianzen
    "EU": r"\b(EU|Europäische Union|Brüssel|Borrell|Kallas)\b",
    "NATO": r"\b(NATO|Nordatlantikpakt|Rutte|Stoltenberg)\b",
    "G7": r"\b(G7|Gruppe der Sieben)\b",
    "UN": r"\b(UN|Vereinte Nationen|UN-Sicherheitsrat|Guterres|UNMISS)\b",
    "Weimarer Dreieck": r"\b(Weimarer Dreieck|Weimar Triangle)\b"
}

def extract_entities(text):
    if not isinstance(text, str):
        return []
    found = []
    for entity, pattern in ENTITY_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(entity)
    return sorted(list(set(found)))

# Volltext + Schlagzeile zusammenführen
df["full_content"] = df["headline"].fillna("") + " " + df["text"].fillna("")
df["entities"] = df["full_content"].apply(extract_entities)

# 3. Kookkurrenz-Graph erstellen
G = nx.Graph()

for entities in df["entities"]:
    if len(entities) > 1:
        # Alle 2er-Kombinationen in derselben Mitteilung verknüpfen
        for u, v in itertools.combinations(entities, 2):
            if G.has_edge(u, v):
                G[u][v]["weight"] += 1
            else:
                G.add_edge(u, v, weight=1)

print(f"\nNetzwerk-Metriken berechnet:")
print(f"- Akteure / Knoten: {G.number_of_nodes()}")
print(f"- Diplomatische Kanten: {G.number_of_edges()}")

# 4. Zentralitätsmaße (Centrality Ranking)
degree_cent = nx.degree_centrality(G)
betweenness_cent = nx.betweenness_centrality(G, weight="weight")
closeness_cent = nx.closeness_centrality(G)

metrics_df = pd.DataFrame({
    "Degree_Centrality": degree_cent,
    "Betweenness_Centrality": betweenness_cent,
    "Closeness_Centrality": closeness_cent
}).sort_values(by="Degree_Centrality", ascending=False)

print("\n--- TOP 10 AKTEURE NACH CENTRALITY ---")
print(metrics_df.head(10).round(4).to_string())

# 5. Top-Beziehungen (stärkste Kanten nach Gewicht)
edges_data = []
for u, v, data in G.edges(data=True):
    edges_data.append({"Knoten_A": u, "Knoten_B": v, "Gewicht": data["weight"]})

edges_df = pd.DataFrame(edges_data).sort_values(by="Gewicht", ascending=False)

print("\n--- TOP 10 STÄRKSTE DIPLOMATISCHE ACHSEN ---")
print(edges_df.head(10).to_string(index=False))

# 6. Ergebnisse exportieren
metrics_df.to_csv(os.path.join(DATA_DIR, "network_centrality_results.csv"), encoding="utf-8")
edges_df.to_csv(os.path.join(DATA_DIR, "network_edges_results.csv"), index=False, encoding="utf-8")
print(f"\nErgebnisse gespeichert in 'network_centrality_results.csv' und 'network_edges_results.csv'.")
'@