# Opět Vzdálené Struktury Repository

## Co Se Změnilo

### Staré Umístění
```
cv_03/
├── analysis_results/        → 9 souborů
├── analysis_advanced/       → 16 souborů  
├── analysis_filtered/       → 8 souborů
└── *.py skripty
```

### Nové Umístění
```
cv_03/
├── out/
│   ├── iter_01_basic_spatial/        (9 souborů)
│   ├── iter_02_advanced_temporal/    (16 souborů)
│   ├── iter_03_interactive_filtering/ (8 souborů)
│   └── README.md                      (dokumentace struktury)
├── *.py skripty (s aktualizovanými OUTPUT_DIR)
└── *.md dokumentace
```

## Aktualizované Skripty

### 1. gdb_spatial_analysis.py
```python
OUTPUT_DIR = "out/iter_01_basic_spatial"
```
**Generuje:**
- Mapy trajektorií (PNG)
- GeoJSON soubory (trajektorie, body, domovská místa)

### 2. trajectory_analysis_advanced.py
```python
OUTPUT_DIR = "out/iter_02_advanced_temporal"
```
**Generuje:**
- Grafy denních rytmů (PNG)
- Analýzu rychlosti (PNG)
- Teplotní mapy (PNG)
- Statistické tabulky (CSV)

### 3. filtering_tool.py
```python
OUTPUT_DIR = "out/iter_03_interactive_filtering"
```
**Generuje:**
- Srovnávací mapy filtrů (PNG)
- Statistiky filtrů

## Jak Pokračovat v Iteracích

### Přidání Nové Iterace (Fáze 4)

1. **Vytvoř nový adresář:**
```powershell
mkdir "out/iter_04_clustering"
```

2. **Vytvoř nový Python skript** (např. `clustering_analysis.py`):
```python
OUTPUT_DIR = "out/iter_04_clustering"
```

3. **Spusť skript:**
```bash
python clustering_analysis.py
# Výstupy se automaticky uloží do out/iter_04_clustering/
```

## Výhody Neue Struktury

✅ **Organizace** - Každá iterace má svou složku  
✅ **Verzování** - Porovnání mezi iteracemi  
✅ **Čistota** - Žádné chaotické soubory v kořeni  
✅ **Škálovatelnost** - Lehké přidávání nových analýz  
✅ **Dokumentace** - README popisuje obsahy  

## Přehled Obsahu

### ITER 01: Základní Prostorová Analýza
```
9 souborů:
- 4× PNG mapy
- 5× GeoJSON vektory
```

**Příklad:**
```
user_a_trajectory.png          - Trasa User A
user_b_points.geojson          - Body User B (import do QGIS)
home_locations.geojson         - Odhadnutá domovská místa
```

### ITER 02: Pokročilá Časová Analýza
```
16 souborů (8 pro User A, 8 pro User B):
- 3× PNG vizualizace (rhythm, speed, heatmap)
- 5× CSV statistiky (hourly, daily, monthly, inactivity, outliers)
```

**Beispiele:**
```
user_a_daily_rhythm.png        - 5-panelová analýza denního rytmu
user_a_outlier_points.csv      - 651 detekovaných anomálií
user_b_inactivity_periods.csv  - 2,333 period nečinnosti
```

### ITER 03: Interaktivní Filtrování
```
8 souborů (4 pro User A, 4 pro User B):
- PNG mapy se srovnáním original vs. filtr
```

**Příklady:**
```
user_a_summer.png              - Letní měsíce (jun-srp) vs. všechny data
user_b_working_hours.png       - Pracovní doba (9-17) vs. všechny data
user_a_weekends.png            - Víkendy vs. všechny data
user_b_night.png               - Noc (21-6) vs. všechny data
```

## Spuštění Všech Iterací Najednou

```bash
python gdb_spatial_analysis.py
python trajectory_analysis_advanced.py
python filtering_tool.py
```

Posloupně se vygenerují výstupy do:
- `out/iter_01_basic_spatial/`
- `out/iter_02_advanced_temporal/`
- `out/iter_03_interactive_filtering/`

## Poznámky

- ✅ Staré složky (analysis_results, analysis_advanced, analysis_filtered) byly smazány
- ✅ Všechny soubory jsou zachovány v nové struktuře
- ✅ Skripty byly aktualizovány na nové OUTPUT_DIR cesty
- ✅ Struktura je připravena pro rozšíření (iter_04, iter_05, ...)

---
Datum reorganizace: 12.03.2026
Status: ✅ HOTOVO
