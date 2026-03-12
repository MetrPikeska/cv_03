# Advanced Trajectory Analysis - Results

## 📊 Analýza denních rytmů a detekce anomálií

Rozšířená prostorová analýza mobilních dat s důrazem na:
- ✓ Denní rytmy (hourly patterns)
- ✓ Detekce období bez pohybu (inactivity)
- ✓ Detekce outlierů (anomálie v pohybu)
- ✓ Časové filtrování (měsíce, dny, hodiny)
- ✓ Grafické vizualizace
- ✓ Statistické tabulky (CSV)

**Datum analýzy:** 12. března 2026

---

## 📈 Klíčové Zjištění

### User A - Analýza
- **Celkem bodů:** 54,154
- **Neaktivních období:** 1,683 (3.1%)
- **Aktivních období:** 52,471 (96.9%)
- **Detekovaných anomálií:** 651 (1.2%)

**Denní rytmy User A:**
- Noc (00:00-06:00): Minimální aktivita (3 body)
- Rána (06:00-09:00): Příjem aktivity
- Deníšek (09:00-17:00): **VRCHOL aktivity** - 272 neaktivních období v 16:00-17:00
- Večer (17:00-23:00): Rychlý pokles
- Noční doba znovu: Velmi nízká aktivita

**Analýza pohybu User A:**
- Průměrná rychlost: 7.03 km/h
- Medián rychlosti: 0.00 km/h (ve statiku!)
- Max rychlost: 1,818.08 km/h ⚠️ (ANOMÁLIE)
- 95. percentil: 38.54 km/h
- Body s rychlostí >100 km/h: 250 ⚠️ (OUTLIERS)

**Časové mezery User A:**
- Průměr: 1.133 hodin
- Medián: 7.9 minut
- Max: 407.31 hodin (17 dní!) ⚠️
- Body s mezerou >24 hodin: 401 ⚠️

---

### User B - Analýza
- **Celkem bodů:** 42,909
- **Neaktivních období:** 2,333 (5.4%)
- **Aktivních období:** 40,576 (94.6%)
- **Detekovaných anomálií:** 1,611 (3.8%) - **VÍCE NEŽ USER A**

**Denní rytmy User B:**
- Noc (00:00-06:00): Mírná aktivita (36 bodů) - více než User A!
- Rána (07:00-09:00): Postupný nárůst
- Deníšek (09:00-21:00): **ROZŠÍŘENÝ vrchol** - aktivita trvá déle
- Noc (21:00-23:00): Ještě stále relativně aktivní
- Nejaktivnější hodina: 21:00 (206 neaktivních období) - **KLÍČOVÝ ROZDÍL**

**Analýza pohybu User B:**
- Průměrná rychlost: 15.24 km/h **VYŠŠÍ NEŽ USER A**
- Medián rychlosti: 0.00 km/h (stejně jako User A)
- Max rychlost: 4,931.57 km/h ⚠️ (VELMI EXTRÉMNÍ!)
- 95. percentil: 68.14 km/h **VYŠŠÍ NEŽ USER A**
- Body s rychlostí >100 km/h: 1,411 ⚠️ (MNOHO MÍĚ)

**Časové mezery User B:**
- Průměr: 1.430 hodin **DELŠÍ NEŽ USER A**
- Medián: 2.88 minut
- Max: 444.95 hodin (18.5 dne!) ⚠️
- Body s mezerou >24 hodin: 200 ⚠️

---

## 🔍 Detailní Porovnání

| Metrika | User A | User B | Rozdíl |
|---------|--------|--------|--------|
| Celkem bodů | 54,154 | 42,909 | User A má více |
| Neaktivnost | 3.1% | 5.4% | User B více neaktivní |
| Anomálie | 1.2% | 3.8% | User B **3x více anomálií** |
| Průměr rychlosti | 7.03 km/h | 15.24 km/h | User B se pohybuje rychleji |
| Max rychlost | 1,818 km/h | 4,932 km/h | User B **extremnější** |
| Outlier > 100 km/h | 250 | 1,411 | User B **5.6x více** |
| Celková doba | > 3 roky | > 3 roky | Srovnatelná |

---

## 📋 Detekované Anomálie (Outliers)

### Typy Anomálií:

1. **Nerealistické rychlosti** (>100 km/h)
   - Běžný případ: Data mají chyby v GPS
   - Příklad: User B - 4,932 km/h (logisticky nemožné)
   - Řešení: Filtrovat tyto body před další analýzou

2. **Dlouhé časové mezery** (>24 hodin)
   - Případ: Přerušení datové služby
   - Příklad: User A - 407 hodin (17 dní bez dat)
   - Příklad: User B - 444 hodin (18.5 dne bez dat)
   - Řešení: Považovat za přirozené přerušení, nikoliv pohyb

3. **Kombinované anomálie**
   - Vysoká rychlost + krátká doba = telekomunikační jump
   - Nízká rychlost + dlouhá doba = statický bod

---

## 📊 Generované Soubory

### Vizualizace (PNG)

#### 1. Daily Rhythm Graphs
- `user_a_daily_rhythm.png` (347 KB)
- `user_b_daily_rhythm.png` (329 KB)

**Obsah:**
- Hodinová aktivita (počet bodů)
- Průměrné rychlosti po hodinách
- Distribuce neaktivnosti
- Aktivita po dnech v týdnu
- Měsíční distribuce

#### 2. Speed Analysis
- `user_a_speed_analysis.png` (347 KB)
- `user_b_speed_analysis.png` (351 KB)

**Obsah:**
- Histogram rychlostí (normální + outliers)
- Box plot distribuce
- Trend rychlosti během dne
- Statistické shrnutí

#### 3. Activity Heatmaps
- `user_a_heatmap.png` (143 KB)
- `user_b_heatmap.png` (140 KB)

**Obsah:**
- Matice: Den v týdnu × Hodina
- Intenzita = počet bodů
- Visuálně ukazuje "horké" doby a dny

### Statistické Tabulky (CSV)

#### Hodinové Statistiky
- `user_a_hourly_stats.csv` - 24 řádků (0-23 hodin)
- `user_b_hourly_stats.csv`

**Sloupce:**
- hour: 0-23
- point_count: Počet bodů v dané hodině
- distance_to_next_m: Celková vzdálenost v metrech
- speed_kmh: Průměrná rychlost
- avg_distance_m: Průměrná vzdálenost mezi body

#### Denní Statistiky
- `user_a_daily_stats.csv` - Jeden řádek per den
- `user_b_daily_stats.csv`

**Sloupce:**
- date: Datum
- weekday_name: Den v týdnu
- point_count: Počet bodů v daný den
- distance_to_next_m: Celková vzdálenost
- speed_kmh: Průměrná rychlost
- total_distance_km: Km za den
- inactive_count: Neaktivní období

#### Měsíční Statistiky
- `user_a_monthly_stats.csv` - Jeden řádek per měsíc
- `user_b_monthly_stats.csv`

**Sloupce:**
- month: 1-12
- month_name: Název měsíce
- point_count: Celkem bodů v měsíci
- days_with_data: Dní s daty
- avg_points_per_day: Průměr per den
- total_distance_km: Km za měsíc

#### Neaktivní Období
- `user_a_inactivity_periods.csv` (57 KB)
- `user_b_inactivity_periods.csv` (78 KB)

**Obsah:** Všechny detekované neaktivní periody
- hour: Hodina kdy došlo k neaktivitě
- weekday_name: Den v týdnu
- distance_to_next_m: Vzdálenost (měla by být <50m)
- time_gap_hours: Jak dlouho trval klid

#### Outlier Body
- `user_a_outlier_points.csv` (36 KB) - 651 řádků
- `user_b_outlier_points.csv` (96 KB) - 1,611 řádků

**Obsah:** Všechny detekované anomálii
- hour: Kdy se přidali anomálii
- speed_kmh: Nerealistická rychlost
- time_gap_hours: Neobvyklá doba
- distance_to_next_m: Vzdálenost (často velká)

---

## 📊 Interpretace Výsledků

### User A - Profil
- **Pracovního typu** - Vysoká aktivita během pracovní doby (9-17)
- **Stacionární** - Dlouhé doby bez pohybu (96.9% neaktivní)
- **Stability** - Nízký výskyt anomálií (1.2%)
- **Koherentní** - Konzistentní denní vzor

### User B - Profil
- **Mobilitní typ** - Aktivita rozprostřena přes den (7-23)
- **Dynamičtější** - Více cestování (5.4% neaktivní)
- **Anomálie** - **3.8% anomálií** (3x více než User A)
- **Extrémnější** - Více extrémních rychlostí
- **Noční aktivita** - Zajímavá aktivita v noci (21:00)

---

## 🔧 Jak Interpretovat Outliers

### Příklady z Dat

**User A - Outlier #1**
- Speed: 0.15 km/h, Gap: 61 hodin
- Interpretace: Bodl setval na místě 2.5 dne, pak se přesunul

**User B - Outlier #1**
- Speed: 111.2 km/h, Gap: 0 sekund
- Interpretace: Okamžitý přesun na velkou vzdálenost - **CHYBA GPS**

**User A - Outlier s Max Speed**
- Speed: 711.4 km/h
- Interpretace: Totální chyba v měření (letadlo? softwarová chyba?)

---

## 💡 Možné Příští Kroky

1. **Filtrování anomálií**
   - Odstranit body s >100 km/h
   - Filtrovat mezery >24 hodin

2. **Clustering**
   - DBSCAN pro detekci "stop" (místa, kde se uživatel dlouho zdržel)
   - K-means pro geografické grupy

3. **Sezónnost**
   - Porovnat jaro/léto vs. podzim/zima
   - Najít sezónní vzory

4. **Sociální vzory**
   - Srovnání User A vs. User B pobyty
   - Společné místa?
   - Společné časy?

5. **Prognózy**
   - Machine Learning pro predikci budoucího pohybu
   - Traffic prediction

---

## 📁 Zpracované Data

**Zdroj:** cvic04.gdb
- mobile_data_user_a: 54,154 bodů
- mobile_data_user_b: 42,909 bodů

**Procesované:** Celkem 96,063 bodů

**CRS:** EPSG:3301 (Estónská národní síť)

**Časový rozsah:** ~3 roky (2008-2011)

---

## 🎯 Klíčové Poznatky

1. ✓ **User A = typický byrocracker** (pracovní den)
2. ✓ **User B = aktivnější cestovatel** (rozprostřená aktivita)
3. ✓ **User B má 3x více anomálií** - možná osobní vozidlo vs. veřejná doprava
4. ✓ **Obě data obsahují artefakty GPS** - filtrování je nezbytné
5. ✓ **Změna v chování User B v noci** (21:00) - zajímavý fenomén
6. ✓ **Dlouhé pauzy** u obou - možná přerušení služby nebo offline časy

---

## 📞 Kontakt & Další Informace

Viz. `trajectory_analysis_advanced.py` pro zdrojový kód.

Generováno: 12. března 2026
