import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mi Pronosticador 10% Empates", page_icon="⚽", layout="wide")
st.title("⚽ Mi Pronosticador - Filtro 10% Empates")
st.write("Versión sin Key - con datos reales de hoy 19/09")

# --- TUS 6 PARTIDOS - ACÁ LOS CAMBIÁS CADA FECHA ---
partidos = [
    {"nombre": "Frankfurt vs Friburgo", "1": 2.37, "X": 3.85, "2": 2.70, "boost": [0.9, 0.7, 1.5]},
    {"nombre": "Roma vs Inter", "1": 2.62, "X": 3.50, "2": 2.60, "boost": [1.2, 0.7, 1.0]},
    {"nombre": "Union vs Independiente", "1": 2.47, "X": 3.05, "2": 3.15, "boost": [1.1, 1.0, 1.0]},
    {"nombre": "Instituto vs Talleres", "1": 2.00, "X": 3.30, "2": 4.60, "boost": [1.4, 1.0, 0.8]},
    {"nombre": "Gimnasia Mza vs Riestra", "1": 2.20, "X": 2.92, "2": 3.95, "boost": [1.3, 1.0, 0.7]},
    {"nombre": "Stuttgart vs Dortmund", "1": 2.40, "X": 3.75, "2": 2.72, "boost": [0.8, 1.0, 1.4]},
]

st.sidebar.header("Cambiá cuotas acá")
nuevos_partidos = []
for i, p in enumerate(partidos):
    with st.sidebar.expander(f"{i+1}. {p['nombre']}", expanded=True):
        nom = st.text_input("Nombre", p['nombre'], key=f"n{i}")
        c1 = st.number_input("Cuota 1", value=float(p['1']), key=f"c1_{i}")
        cx = st.number_input("Cuota X", value=float(p['X']), key=f"cx_{i}")
        c2 = st.number_input("Cuota 2", value=float(p['2']), key=f"c2_{i}")
        nuevos_partidos.append((nom, [c1,cx,c2], p['boost']))

if st.button("CALCULAR AHORA - TOP 36", type="primary", use_container_width=True):
    probs = []
    for (nom, odds, boost) in nuevos_partidos:
        inv = [1/odds[0], 1/odds[1], 1/odds[2]]
        s = sum(inv)
        probs.append([inv[0]/s*boost[0], inv[1]/s*boost[1], inv[2]/s*boost[2]])

    labels = ["1","X","2"]
    combos = []
    for a in range(3):
     for b in range(3):
      for c in range(3):
       for d in range(3):
        for e in range(3):
         for f in range(3):
            combo = (a,b,c,d,e,f)
            if sum(x==1 for x in combo) > 1: continue
            prob = probs[0][a]*probs[1][b]*probs[2][c]*probs[3][d]*probs[4][e]*probs[5][f]
            combos.append((combo, prob))

    combos = sorted(combos, key=lambda x: x[1], reverse=True)[:36]

    rows=[]
    for idx, (combo, p) in enumerate(combos):
        rows.append({
            "#": idx+1,
            "COMBINACION": f"{labels[combo[0]]}-{labels[combo[1]]}-{labels[combo[2]]}-{labels[combo[3]]}-{labels[combo[4]]}-{labels[combo[5]]}",
            "Cant X": sum(x==1 for x in combo),
            "Prob %": round(p*100, 4)
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)
    st.success(f"MEJOR JUGADA HOY: {rows[0]['COMBINACION']} con {rows[0]['Prob %']}%")
    st.download_button("Descargar CSV", df.to_csv(index=False).encode('utf-8'), "pronostico.csv", "text/csv")

st.info("💡 Tip: Los 'boost' ya están puestos con datos de hoy: Friburgo líder, Instituto líder, Dortmund 2do. Vos solo cambiá las cuotas.")
