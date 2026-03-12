# Výstupy Analýzy Mobilních Dat - Struktura Iterací

Organizace výstupů podle jednotlivých iterací vývoje.

## Adresářová Struktura

```
out/
├── iter_01_basic_spatial/        # Základní prostorová analýza
│   ├── *.png                     # Mapy trajektorií, BTS, hranic
│   └── *.geojson                 # Trajektorie, body, domovská místa
│
├── iter_02_advanced_temporal/    # Pokročilá časová analýza
│   ├── *_daily_rhythm.png        # 5-panelové grafy (aktivita, rychlost, inaktivita, den, měsíc)
│   ├── *_speed_analysis.png      # Analýza rychlosti (histogram, box plot, trend)
│   ├── *_heatmap.png             # Teplotní mapa (den x hodina)
│   ├── *_hourly_stats.csv        # Agregace po hodinách (0-23)
│   ├── *_daily_stats.csv         # Agregace po dnech
│   ├── *_monthly_stats.csv       # Agregace po měsících
│   ├── *_inactivity_periods.csv  # Periody nečinnosti (<50m, 1+ hodina)
│   └── *_outlier_points.csv      # Detekované anomálie
│
└── iter_03_interactive_filtering/ # Interaktivní filtrování
    ├── user_a_summer.png         # Letní analýza (červen-srpen)
    ├── user_a_working_hours.png  # Pracovní doba (9:00-17:00)
    ├── user_a_weekends.png       # Víkendy (sobota-neděle)
    ├── user_a_night.png          # Noc (21:00-06:00)
    └── user_b_*.png              # A stejné pro User B
```

## Příklady Výstupů

### Iterace 1: Základní Prostorová Analýza
**Soubor:** `gdb_spatial_analysis.py`

Generuje:
- **Mapy trajektorií** - PNG vizualizace tras obou uživatelů
- **Geografická data** - GeoJSON soubory pro import do GIS
- **Domovská místa** - Estimace domů z nočních bodů

### Iterace 2: Pokročilá Časová Analýza
**Soubor:** `trajectory_analysis_advanced.py`

Generuje:
- **Denní rytmy** - Jak se aktivita mění během dne/týdne/měsíce
- **Analýza rychlosti** - Detekce anomálií (1,818 km/h pro User A, 4,932 km/h pro User B)
- **Inaktivita** - User A 3.1%, User B 5.4%
- **Statistické tabulky** - CSV pro další zpracování

### Iterace 3: Interaktivní Filtrování
**Soubor:** `filtering_tool.py`

Generuje:
- **Sezónní analýzy** - Léto (27-28% dat)
- **Časové filtrování** - Pracovní doba vs. noc
- **Porovnávací mapy** - Original vs. filtrované data
- **Srovnávací statistiky** - Tabulky se klíčovými metrikami

## Jak Spustit Jednotlivé Iterace

### Iterace 1: Základní Analýza
```bash
python gdb_spatial_analysis.py
# Výstupy → out/iter_01_basic_spatial/
```

### Iterace 2: Pokročilá Analýza
```bash
python trajectory_analysis_advanced.py
# Výstupy → out/iter_02_advanced_temporal/
```

### Iterace 3: Filtrování
```bash
python filtering_tool.py
# Výstupy → out/iter_03_interactive_filtering/
```

## Interpretace Výsledků

### User A Profil
- **Typ:** Sedentární pracovník
- **Mobilita:** 96.9% nízké pohybu, 3.1% nečinnosti
- **Pracovní doba:** Dominantní 9-17:00 (87.4% bodů)
- **Víkendy:** Minimální aktivita (1.5% bodů)
- **Anomálie:** Nízké (1.2%), max rychlost 1,818 km/h

### User B Profil
- **Typ:** Mobilní profesionál
- **Mobilita:** 94.6% aktivní, 5.4% nečinnosti
- **Pracovní doba:** Rozšířené 7-23:00 (70.4% bodů)
- **Víkendy:** Vysoká aktivita (20% bodů)
- **Anomálie:** Vysoké (3.8%), max rychlost 4,932 km/h (5.6x více anomálií)

## Filtrování - Příklady Použití

### Vytvoření Vlastního Filtru
```python
from filtering_tool import *

# Načtení dat
user_a = load_and_prepare_data("cvic04.gdb", "mobile_data_user_a")

# Filtrování
winter = filter_by_months(user_a, [12, 1, 2])           # Zimní měsíce
mornings = filter_by_hours(user_a, list(range(6, 12)))   # Ráno
mondays = filter_by_weekdays(user_a, ['Monday'])         # Pondělky

# Kombinace
winter_mornings = filter_by_months(winter, [12, 1, 2])
winter_mornings = filter_by_hours(winter_mornings, list(range(6, 12)))

# Výpočet metrik
winter_mornings = calculate_metrics(winter_mornings)

# Statistiky
stats = get_summary_stats(winter_mornings, "Zimní ráno")
print(stats)
```

## Navrhované Další Analýzy

### Fáze 4: Detekce Lokací a Shluků
- DBSCAN clustering na prostorové datech
- Identifikace pravidelných míst (práce, dům, restaurace)
- Doba strávená na každém místě (dwell time)

### Fáze 5: Komparativní Analýza
- Společná místa obou uživatelů (setkání)
- Srovnání profilu během pracovního týdne vs. víkend  
- Sezónní trendy

### Fáze 6: Prediktivní Modely
- Odhad lokace na základě času
- Klasifikace aktivit (práce, cestování, odpočinek)
- Anomalie detekce v reálném čase

## Technické Poznámky

- **Souřadnicový systém:** EPSG:3301 (Estonská státní síť)
- **Data:** 2008-2011, ~97k bodů pro oba uživatele
- **Časové rozlišení:** Minuta až hodina
- **Počítaná metriky:** Vzdálenost (m), čas (h), rychlost (km/h)

## Archivace

Staré výstupy jsou automaticky archivovány v:
- `analysis_results/` → `out/iter_01_basic_spatial/`
- `analysis_advanced/` → `out/iter_02_advanced_temporal/`
- `analysis_filtered/` → `out/iter_03_interactive_filtering/`

Původní složky lze bezpečně smazat.
