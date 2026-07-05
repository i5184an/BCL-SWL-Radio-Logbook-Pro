# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import re
import math
import requests
from datetime import datetime

# 1. Inizializzazione sessione
if 'last_values' not in st.session_state:
    st.session_state.last_values = {"SFI": "-", "SN": "-", "A": "-", "K": "-", "Date": ""}

# 2. Funzione dati solari (Testata e funzionante)
def fetch_solar_data():
    # PROPAGATION INDEX
    # A index = low is good
    # 1-6 is best, 7-9 is ok, 11+ is bad
    # SFI index = high is good (70 not good, 80 good, 90 better, 100+ best)
    # K index = low is good (0-1 best, 2 ok, 3+ bad, 5 very bad)
    try:
        url = "https://www.hamqsl.com/solarxml.php"
        response = requests.get(url, timeout=10)
        text = response.text
        
        # Dizionario per mappare i tag che sappiamo essere usati in quel sito
        tags_to_find = {
            "SFI": ["sfi", "solarflux"], 
            "SN": ["sunspots", "sn"], 
            "A": ["solarAindex", "aindex"], 
            "K": ["solarKindex", "kindex"]
        }
        
        results = {}
        for key, possible_tags in tags_to_find.items():
            found = False
            for tag in possible_tags:
                match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.IGNORECASE | re.DOTALL)
                if match:
                    results[key] = match.group(1).strip()
                    found = True
                    break
            if not found:
                results[key] = "-"
        
        return results
    except Exception:
        return {"SFI": "-", "SN": "-", "A": "-", "K": "-"}

def get_stato_propagazione_level(sfi, a, k):
    try:
        sfi_val = int(float(sfi)) if str(sfi).replace('.','',1).replace('-','').isdigit() else 0
        a_val = int(float(a)) if str(a).replace('.','',1).replace('-','').isdigit() else 100
        k_val = int(float(k)) if str(k).replace('.','',1).replace('-','').isdigit() else 5
    except:
        return "neutral"

    if sfi_val >= 90 and a_val <= 6 and k_val <= 1:
        return "green"
    elif sfi_val >= 80 and a_val <= 9 and k_val <= 2:
        return "yellow"
    else:
        return "red"  

    # Logica basata sulle tue regole
    # Verde: SFI > 90, A <= 6, K <= 1
    # Giallo: Condizioni intermedie
    # Rosso: SFI < 80, A >= 11, K >= 3
    if sfi_val >= 90 and a_val <= 6 and k_val <= 1:
        return "🟢", "Ottimo! Propagazione eccellente."
    elif sfi_val >= 80 and a_val <= 9 and k_val <= 2:
        return "🟡", "Discreta, condizioni medie."
    else:
        return "🔴", "Bassa, meglio fare altro!"

# 3. Funzione calcolo distanza
def calcola_distanza(lat1, lon1, lat2, lon2):
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None: return 0
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return int(R * c)

st.set_page_config(page_title="Radio Logbook Pro", layout="wide")

# CSS Globale
st.markdown("""
<style>
    .stApp { background-color: #0B0E14; }
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    [data-testid="stForm"] { background-color: #1C2128; border: 1px solid #30363D; border-radius: 10px; padding: 20px; }
    h1, h2, h3 { color: #E6EDF3 !important; }
</style>
""", unsafe_allow_html=True)

# 4. Configurazione File
FILE_LOG = r"C:\Users\SERVER-MUS\Desktop\LogbookRadio\my_logbook.csv"
COLS = ["Date", "Rig - Ant", "SFI", "SN", "A", "K", "Time (UTC)", "Freq (khz)", "Mode", "Power (kW)", "Station", "SINPO", "Language", "RST", "QTH", "Remark", "QSL Sent", "QSL Recv", "Latitudine", "Longitudine"]

def load_data():
    if not os.path.exists(FILE_LOG):
        pd.DataFrame(columns=COLS).to_csv(FILE_LOG, sep=';', index=False, encoding='utf-8-sig')
    df = pd.read_csv(FILE_LOG, sep=';', encoding='utf-8-sig')
    df.columns = [col.strip() for col in df.columns]
    return df

def pulizia_coordinate(val):
    try:
        val = str(val).upper()
        num = float(re.sub(r'[^\d.]', '', val))
        return -num if ('S' in val or 'W' in val) else num
    except: return None

def load_data():
    if not os.path.exists(FILE_LOG):
        pd.DataFrame(columns=COLS).to_csv(FILE_LOG, sep=';', index=False, encoding='utf-8-sig')
    df = pd.read_csv(FILE_LOG, sep=';', encoding='utf-8-sig')
    df.columns = [col.strip() for col in df.columns] # Normalizzazione colonne
    return df

def pulizia_coordinate(val):
    try:
        val = str(val).upper()
        num = float(re.sub(r'[^\d.]', '', val))
        return -num if ('S' in val or 'W' in val) else num
    except: return None

df = load_data()

# Inizializza la memoria per l'inserimento rapido
if 'last_values' not in st.session_state:
    st.session_state.last_values = {"SFI": "", "SN": "", "A": "", "K": "", "Date": ""}

# --- TITOLO E SIDEBAR (Propagazione iniziale) ---
st.title("📻 Radio Logbook Pro - IN3032SWL")
st.sidebar.subheader("📡 Propagazione (NOAA)")

# Usiamo una chiave unica per il bottone della sidebar principale
if st.sidebar.button("🔄 Aggiorna Dati Solari", key="btn_main_solar"):
    nuovi_dati = fetch_solar_data()
    if nuovi_dati:
        st.session_state.last_values.update(nuovi_dati)
        st.sidebar.success("Aggiornato!")
    else:
        st.sidebar.error("Errore.")

# 1. Visualizzazione metriche esistenti (lasciale come sono)
col1, col2 = st.sidebar.columns(2)
col1.metric("SFI", st.session_state.last_values.get("SFI", "-"))
col2.metric("SN", st.session_state.last_values.get("SN", "-"))
col1.metric("A", st.session_state.last_values.get("A", "-"))
col2.metric("K", st.session_state.last_values.get("K", "-"))

# 2. INSERISCI QUESTO CODICE ESATTO (Sostituisce il precedente tentativo del semaforo)
st.sidebar.markdown("---")
st.sidebar.subheader("🚦 Stato Propagazione")

# Definiamo la logica qui al volo per semplicità
sfi = st.session_state.last_values.get("SFI", "-")
a = st.session_state.last_values.get("A", "-")
k = st.session_state.last_values.get("K", "-")

# Convertiamo in numeri sicuri
try:
    sfi_v = int(float(sfi)) if str(sfi).replace('.','').isdigit() else 0
    a_v = int(float(a)) if str(a).replace('.','').isdigit() else 100
    k_v = int(float(k)) if str(k).replace('.','').isdigit() else 5
except:
    sfi_v, a_v, k_v = 0, 100, 5

# Mostriamo il box colorato nativo di Streamlit
if sfi_v >= 90 and a_v <= 6 and k_v <= 1:
    st.sidebar.success("Ottimo! Propagazione eccellente.")
elif sfi_v >= 80 and a_v <= 9 and k_v <= 2:
    st.sidebar.warning("Discreta, condizioni medie.")
else:
    st.sidebar.error("Bassa, meglio fare altro!")
# --- 1. SIDEBAR: DEFINIZIONE CONTROLLI ---
st.sidebar.header("⚙️ Filtri e Ordine")
col_filtro = st.sidebar.selectbox("Filtra per:", options=df.columns.tolist())
valore_filtro = st.sidebar.text_input(f"Cerca in {col_filtro}:")

st.sidebar.subheader("📅 Filtro Data")
usa_filtro_data = st.sidebar.checkbox("Filtra per data specifica")

# Inizializziamo filtro_data per evitare errori
filtro_data = "Tutte" 

if usa_filtro_data:
    data_sel = st.sidebar.date_input("Seleziona data:", value=datetime.now())
    filtro_data = data_sel.strftime("%d/%m/%Y")

ordina_distanza = st.sidebar.checkbox("Ordina per Distanza (più lontano prima)")

# Logica di filtraggio
df_filtered = df.copy()
if valore_filtro:
    df_filtered = df_filtered[df_filtered[col_filtro].astype(str).str.contains(valore_filtro, case=False, na=False)]
if filtro_data != "Tutte":
    df_filtered = df_filtered[df_filtered['Date'] == filtro_data]

# --- DEFINIZIONE TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["Analisi e Dati", "Inserimento Dati", "Mappa FT8 Style", "Generatore QSL"])

with tab1:
    df_dist = df_filtered.copy()
    df_dist['Dist (km)'] = df_dist.apply(lambda row: calcola_distanza(45.88, 10.84, pulizia_coordinate(row['Latitudine']), pulizia_coordinate(row['Longitudine'])), axis=1)
    
    if ordina_distanza:
        df_dist = df_dist.sort_values(by='Dist (km)', ascending=False)
        
    st.subheader("📊 Analisi Pareto")
    if 'Station' in df_filtered.columns:
        fig = px.bar(df_filtered['Station'].value_counts().head(20), template="plotly_dark")
        fig.update_traces(marker_color='#39ff14')
        st.plotly_chart(fig, use_container_width=True)
        
    # --- INTEGRAZIONE EDITOR ---
    st.subheader("📋 Logbook Editor")
    st.info("💡 Suggerimento: Modifica le celle direttamente qui sotto e premi Salva.")
    
    edited_df = st.data_editor(df_dist, use_container_width=True, num_rows="fixed")
    
    if st.button("💾 Salva modifiche al Logbook"):
        df_originale = pd.read_csv(FILE_LOG, sep=';', encoding='utf-8-sig')
        dati_modificati = edited_df.drop(columns=['Dist (km)'])
        df_originale.update(dati_modificati)
        df_originale.to_csv(FILE_LOG, sep=';', index=False, encoding='utf-8-sig')
        st.success("Logbook aggiornato!")
        st.rerun() 

    # ---------------------------
    
    # Esportazione ADIF
    if st.button("Esporta in ADIF"):
        adif_content = "Generated by Radio Logbook Pro\n<EOH>\n"
        for _, row in df_filtered.iterrows():
            adif_content += f"<CALL:{len(str(row['Station']))}>{row['Station']} "
            adif_content += f"<BAND:{len(str(row['Freq (khz)']))}>{row['Freq (khz)']} "
            adif_content += f"<MODE:{len(str(row['Mode']))}>{row['Mode']} "
            adif_content += f"<QSO_DATE:{len(str(row['Date']))}>{row['Date']} "
            adif_content += "<EOR>\n"
        st.download_button("Scarica file .adi", adif_content, file_name="my_logbook.adi", mime="text/plain")

with tab2:
    st.header("📝 Inserimento Nuovi Dati")
    
    with st.form("form_inserimento"):
        # Raggruppiamo i dati solari (che si ripetono) in una riga sola
        st.subheader("Dati Solari (Automatici)")
        col_sol1, col_sol2, col_sol3, col_sol4, col_sol5 = st.columns(5)
        Date = col_sol1.text_input("Data", value=st.session_state.last_values["Date"])
        SFI = col_sol2.text_input("SFI", value=st.session_state.last_values["SFI"])
        SN = col_sol3.text_input("SN", value=st.session_state.last_values["SN"])
        A = col_sol4.text_input("A", value=st.session_state.last_values["A"])
        K = col_sol5.text_input("K", value=st.session_state.last_values["K"])

        # Dati Stazione e QSO
        st.subheader("Dati Stazione e QSO")
        col_st1, col_st2, col_st3 = st.columns(3)
        Rig_Ant = col_st1.text_input("Rig - Ant")
        Time_UTC = col_st2.text_input("Time (UTC)")
        Freq_khz = col_st3.text_input("Freq (khz)")
        
        col_st4, col_st5, col_st6 = st.columns(3)
        Mode = col_st4.text_input("Mode")
        Power_kw = col_st5.text_input("Power (kw)")
        Station = col_st6.text_input("Station")

        # Dati Ricezione e QTH
        st.subheader("Dati Ricezione")
        col_rec1, col_rec2, col_rec3 = st.columns(3)
        SINPO = col_rec1.text_input("SINPO")
        Language = col_rec2.text_input("Language")
        RST = col_rec3.text_input("RST")
        
        QTH = st.text_input("QTH")
        Remark = st.text_area("Remark") # text_area per più spazio

        # QSL e Coordinate
        col_qsl1, col_qsl2, col_qsl3, col_qsl4 = st.columns(4)
        QSL_Sent = col_qsl1.text_input("QSL Sent")
        QSL_Recv = col_qsl2.text_input("QSL Recv")
        Latitudine = col_qsl3.text_input("Latitudine")
        Longitudine = col_qsl4.text_input("Longitudine")
        
        submitted = st.form_submit_button("SALVA LOG", use_container_width=True)           
if submitted:
            import csv
            import os

            # 1. Raccogliamo tutti i dati della form nell'ordine CORRETTO
            nuovo_dato = {
                "Date": Date,
                "Rig - Ant": Rig_Ant,
                "SFI": SFI,
                "SN": SN,
                "A": A,
                "K": K,
                "Time (UTC)": Time_UTC,
                "Freq (khz)": Freq_khz,
                "Mode": Mode,
                "Power (kw)": Power_kw,
                "Station": Station,
                "SINPO": SINPO,
                "Language": Language,
                "RST": RST,
                "QTH": QTH,
                "Remark": Remark,
                "QSL Sent": QSL_Sent,
                "QSL Recv": QSL_Recv,
                "Latitudine": Latitudine,
                "Longitudine": Longitudine
            }

            # 2. Definisci il nome del file
            file_csv = "my_logbook.csv" 

            # 3. Scrittura fisica sicura
            # Usiamo l'ordine del dizionario così com'è
            with open(file_csv, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(nuovo_dato.values())

            # 4. Aggiorniamo i dati solari nella memoria di sessione
            st.session_state.last_values.update({
                "Date": Date,
                "SFI": SFI,
                "SN": SN,
                "A": A,
                "K": K
            })

            # 5. Avvisiamo l'utente e ricarichiamo l'interfaccia
            st.success("QSO salvato correttamente nel CSV!")
            st.rerun()         

with tab3:
    st.subheader("🗺️ Mappa Collegamenti")
    
    # Condizione: Mostra la mappa solo se NON è "Tutte" OPPURE se c'è un testo nel campo cerca
    # Assumendo che il tuo text_input si chiami 'valore_filtro' e la selectbox 'filtro_data'
    mappa_attiva = (filtro_data != "Tutte") or (col_filtro == "Date" and valore_filtro != "")
    
    if not mappa_attiva:
        st.info("ℹ️ Seleziona una data o cerca una data nella sidebar per visualizzare i collegamenti.")
        fig = go.Figure()
        fig.add_trace(go.Scattergeo(lon=[10.84], lat=[45.88], marker=dict(size=10, color='red'), name="Base"))
    else:
        fig = go.Figure()
        fig.add_trace(go.Scattergeo(lon=[10.84], lat=[45.88], marker=dict(size=10, color='red'), name="Base"))
        
        # 'df_filtered' è già il dataframe filtrato sia dalla selectbox che dal text_input
        for _, row in df_filtered.dropna(subset=['Latitudine', 'Longitudine']).iterrows():
            lat_v, lon_v = pulizia_coordinate(row['Latitudine']), pulizia_coordinate(row['Longitudine'])
            if lat_v is not None and lon_v is not None:
                fig.add_trace(go.Scattergeo(
                    lon=[10.84, lon_v], 
                    lat=[45.88, lat_v], 
                    mode='lines', 
                    line=dict(width=1, color='#39ff14'), 
                    showlegend=False
                ))
    
    fig.update_layout(
        geo=dict(showland=True, landcolor="#1a1d23", showocean=True, oceancolor="#0e1117", showcountries=False), 
        paper_bgcolor='#0e1117', 
        margin={"t":0,"b":0,"l":0,"r":0}, 
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("🖨️ Impostazioni QSL")
    col1, col2 = st.columns(2)
    with col1:
        txt_nom = st.text_input("Nominativo:", "IN3032SWL")
        txt_loc = st.text_input("Locator:", "JN55kv08 - Italy")
    with col2:
        c_nom = st.color_picker("Colore Testo:", "#FF003C")
        bg_url = st.text_input("URL Immagine Sfondo:")
    
    idx = st.number_input("Indice riga:", 0, max(0, len(df)-1))
    
    if st.button("Genera QSL"):
        d = df.iloc[idx]
        st.markdown(f"""
        <div style="border: 4px solid #39ff14; padding: 20px; background-image: url('{bg_url}'); background-size: cover; background-position: center; color: white; width: 750px; font-family: 'Courier New', monospace; box-shadow: 10px 10px 20px #000;">
            <div style="text-align: center; margin-bottom: 15px; color: {c_nom};">
                <h1 style="margin: 0; font-size: 2.5em; text-shadow: 2px 2px 5px #000;">{txt_nom}</h1>
                <h2 style="margin: 0; font-size: 1.5em; text-shadow: 1px 1px 3px #000;">{txt_loc}</h2>
            </div>
            <div style="background: rgba(0,0,0,0.7); padding: 15px; width: fit-content; min-width: 450px; border-radius: 5px; margin: 0 auto;">
                <p style="margin: 3px 0;"><b>Station:</b> {d['Station']} &nbsp;&nbsp; <b>Power:</b> {d['Power (kW)']} kW</p>
                <p style="margin: 3px 0;"><b>Date:</b> {d['Date']} &nbsp;&nbsp; <b>Time:</b> {d['Time (UTC)']}</p>
                <p style="margin: 3px 0;"><b>Freq:</b> {d['Freq (khz)']} kHz &nbsp;&nbsp; <b>Mode:</b> {d['Mode']}</p>
                <p style="margin: 3px 0;"><b>SINPO:</b> {d['SINPO']} &nbsp;&nbsp; <b>RST:</b> {d['RST']}</p>
                <p style="margin: 3px 0;"><b>QTH:</b> {d['QTH']}</p>
                <p style="margin: 8px 0 0 0; border-top: 1px solid white; padding-top: 5px;"><b>Remark:</b> {d['Remark']}</p>
                <p style="margin: 8px 0 0 0; font-size: 0.8em; font-style: italic;">Confirming SWL Report</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.info("Premi CTRL+P per salvare/stampare.")