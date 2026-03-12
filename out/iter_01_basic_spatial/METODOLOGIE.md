# Iterace 01: Základní Prostorová Analýza - METODOLOGIE

## 📍 O Datech

Tato analýza pracuje s **daty z BTS stanic** (Base Transceiver Stations - mobilní věže v Estonsku).

- **BTS (mobilní věže):** Detekuje polohu mobilního zařízení přes síťu
- **Přesnost:** Přibližně 2-5 km (horší než GPS)
- **Výhoda:** Funguje uvnitř budov, není závislá na viditelnosti satelitů
- **Zdroj dat:** Každý signál do BTS stanice zaznamenává čas a ID stanice

---

## 🔍 Postup Analýzy

### Fáze 1: Načtení Dat z GDB

```
cvic04.gdb (ESRI File Geodatabase)
    ├─ mobile_data_user_a     [54,154 bodů BTS]
    ├─ mobile_data_user_b     [42,909 bodů BTS]
    ├─ gps_data               [221,293 bodů GPS - referenční]
    ├─ bts_locations          [1,117 BTS stanic - infrastruktura]
    ├─ lau1_maakond           [15 krajů]
    └─ lau2_omavalitsus       [79 municipalit]
```

**Jak se načítá:**
- GDB je speciální ESRI formát (databáze)
- Používáme `geopandas.read_file()` pro čtení
- Každá vrstva = GeoDataFrame (geografické + tabulkové données)
- Zachováme geometrii (body v EPSG:3301 - estonský souřadnicový systém)

### Fáze 2: Příprava Dat - Extrakce Временних Vlastností

```python
# Každý bod obsahuje timestamp - čas detekce signálu
gdf['pos_time'] = pd.to_datetime(gdf['pos_time'])

# Extrahujeme:
gdf['year']    = 2008-2011 (roky v datech)
gdf['month']   = 1-12       (měsíc)
gdf['day']     = 1-31       (den v měsíci)
gdf['weekday'] = 0-6        (den v týdnu: 0=Pondělí)
gdf['hour']    = 0-23       (hodina dne)
```

**Proč:**
- Chceme pochopit KDYŽ se uživatel pohybuje
- Chceme separovat pracovní dobu od noci
- Potřebujeme pro domovskou lokaci (night points = noc)

### Fáze 3: Sázení Noční Filtrace - Odhad Domovské Lokace

```
ALGORITMUS:
1. Vezmi všechny body mezi 00:00-06:00 (spánek)
2. Vypočítej centroid (průměrnou polohu)
3. Výsledek = domácí adresa uživatele
```

**Proč tohle funguje:**
- Lidé tráví noc doma
- BTS detekce během noci = blízko domu
- Centroid těchto bodů = odhad domácí adresy

**Výsledky:**
```
User A: 14 nočních bodů → 1 domovská lokace (Tallinn)
User B: 181 nočních bodů → 1 domovská lokace (severní Estonie)
```

### Fáze 4: Tvorba Trajektorií - Posloupnost Pohybů

```
ALGORITMUS:
1. Seřaď body chronologicky (podle pos_time)
2. Vytvořit LineString geometrii (linieconnektující body)
3. Zobrazit jako cestu na mapě
```

**Co se zvídáme:**
```
User A:
├─ Počet bodů: 54,154
├─ Časový rozsah: 2008-2011 (3 roky)
├─ Hlavní oblast: Tallinn (hlavní město)
└─ Typ pohybu: Sedentární (stále na místě)

User B:
├─ Počet bodů: 42,909
├─ Časový rozsah: 2008-2011
├─ Hlavní zóna: Severní Estonie (rozprostřená pohybu)
└─ Typ pohybu: Mobilní (cestování)
```

### Fáze 5: Vytváření Vizualizací - Mapy

#### Mapa 1: Individuální Trajektorie

```
user_a_trajectory.png
├─ Levá mapa: Trajektorie User A (modrá linie)
├─ Středová mapa: Trajektorie User B (červená linie)
└─ Pravá mapa: Kombinovaná (oba uživatelé)

Co vidíme:
├─ User A = koncentrovaná aktivita v Tallinnu
└─ User B = rozprostřená po několika městech
```

#### Mapa 2: BTS Stanice a Hranice

```
bts_and_boundaries.png
├─ Do pozadí vložíme:
│  ├─ Hranice krajů (lau1_maakond)
│  ├─ Hranice municipalit (lau2_omavalitsus)
│  └─ BTS stanice (tečky - infrastruktura)
├─ Přes to vložíme trajektorie obou uživatelů
└─ Barvou rozlišujeme województwa
```

#### Mapa 3: Domovské Lokace

```
home_locations.geojson
├─ Zobrazuje odhadnuté domácí adresy
├─ User A: 1 bod v Tallinnu
└─ User B: 1 bod v severní Estonii
```

### Fáze 6: Export do GeoJSON

GeoJSON = otevřený formát pro geografická data

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [25.12, 59.43]  // Longitude, Latitude
  },
  "properties": {
    "user": "User A",
    "hour": 14,
    "weekday": "Monday"
  }
}
```

**Výhody:**
- Kompatibilní s GIS (QGIS, ArcGIS)
- Lze importovat do webových map
- Otevřený standard

---

## 📊 Výstupy ITER 01

### PNG Mapy (vizualizace)
```
user_a_trajectory.png          - Trasa User A
user_b_trajectory.png          - Trasa User B  
combined_analysis.png          - Kombinovaná analýza
bts_and_boundaries.png         - S BTS a hranicemi
```

### GeoJSON Soubory (data)
```
user_a_trajectory.geojson      - LineString trajektorie User A
user_b_trajectory.geojson      - LineString trajektorie User B
user_a_points.geojson          - Všechny body User A (54k bodů)
user_b_points.geojson          - Všechny body User B (43k bodů)
home_locations.geojson         - Odhadnuté domovy
```

---

## 🎯 Jaké Otázky Tento Krok Odpovídá?

✓ **Kde se uživatelé pohybují?**
  - Mapa trajektorií ukazuje geografickou zónu

✓ **Kde bydlí?**
  - Odhad domovské lokace z nočních bodů

✓ **Jaký typ uživatele vidíme?**
  - User A: Sedentární (koncentriovaý pohyb)
  - User B: Mobilní (rozptýlený pohyb)

✓ **Jak dlouho máme data?**
  - Časový rozsah 2008-2011

---

## ⚙️ Technické V detaily

### Souřadnicový Systém (CRS)

**EPSG:3301 - Estonský Koordinátor Grid**
- Projektovaný souřadnicový systém
- Para meter: Pro Estonsko (místní optimalizace)
- Jednotka: Metry

**EPSG:4326 - WGS84 (zeměpisné)**
- Zeměpisné souřadnice (Lon, Lat)
- Globální standard
- Používáno pro webové mapy

### Transformace: EPSG:3301 → EPSG:4326

```python
gdf = gdf.to_crs('EPSG:4326')  # Pro vizualizaci
```

Proč: Webové mapovací knihovny (matplotlib, folium) očekávají WGS84.

---

## 📈 Interpretace Výsledků

### User A Profil
```
Charakteristika:     Sedentární pracovník (pravděpodobně v kanceláři)
Hlavní lokace:       Tallinn, severní okrajový čtvrť
Mobilita:            Nízká - drží se v jedné zóně
Závěr:               Stejné pracovní místo, pravidelný mode
```

### User B Profil
```
Charakteristika:     Mobilní profesionál (prodejce, taxidlák, atd.)
Hlavní zóny:         Několik měst v severní Estonii
Mobilita:            Vysoká - cestuje mezi místy
Závěr:               Práce vyžadující cestování
```

---

## 🔧 Softwarová Architektura

### Hlavní Funkce

```python
def load_layer(gdb_path, layer_name):
    """Načte vrstvu z GDB"""
    
def extract_temporal_features(gdf):
    """Extrahuje čas, měsíc, den, hodinu"""
    
def filter_night_points(gdf):
    """Filtruje body z noci (00:00-06:00)"""
    
def compute_home_location(gdf):
    """Centroid nočních bodů"""
    
def create_trajectory(gdf):
    """Vytvoří LineString z seřazených bodů"""
    
def plot_user_trajectory(gdf):
    """Vykreslí mapu trajektorie"""
    
def export_to_geojson(gdf, filename):
    """Exportuje do GeoJSON"""
```

### Tok Dat

```
GDB (na disku)
    ↓ gpd.read_file()
GeoDataFrame (geopandas)
    ↓ Feature extraction
Obohacená data (se časy)
    ↓ Filtrování & Výpočty
Metriky (domova, trajektorie)
    ↓ Vizualizace & Export
PNG mapy + GeoJSON soubory (v out/)
```

---

## 💾 Datové Charakteristiky

### User A Data
```
Celkem bodů:         54,154
Nočních bodů:        14
Domácí lokace:       Tallin (25.1147°E, 59.4238°N)
Náladavy čas:        2008-2011
Průměr bodů/den:     ~45
```

### User B Data
```
Celkem bodů:         42,909
Nočních bodů:        181
Domácí lokace:       Severní Estonie (~58°N, 26°E)
Náladavy čas:        2008-2011
Průměr bodů/den:     ~35
```

### BTS Stanice
```
Celkem: 1,117 BTS stanic v datech
Funkce: Referenční vrstva infrastruktury
```

---

## ✅ Ověření Kvality

- ✓ Všechny body mají geometrii
- ✓ Časy jsou validní (2008-2011)
- ✓ Domácí lokace má smysl (fyzicky na Estonsku)
- ✓ Trajektorie jsou logické (bez nereálných skoků)
- ✓ GeoJSON exporty jsou validní

---

## 📚 Zdroje a Reference

- **EPSG:3301**: https://epsg.io/3301 (Estonský grid)
- **GeoJSON**: https://geojson.org/ (Otevřený standard)
- **GeoDataFrame**: https://geopandas.org/ (Python knihovna)
- **BTS Data**: Opole anonymizované signály z mobilní sítě

---

**Status:** ✅ Iterace 1 Kompletní  
**Počet Výstupů:** 9 souborů (4 PNG + 5 GeoJSON)  
**Další Krok:** Iterace 2 - Časová Analýza a Detekce Vzorů
