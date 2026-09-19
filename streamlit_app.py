import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pronosticador PRO V3.1", page_icon="🏆", layout="wide")
st.title("🏆 Pronosticador PRO V3.1 - Equipos Editables")

# Base con 6 partidos, ahora editables
partidos_base = [
    {"nombre": "Frankfurt vs Friburgo", "info": "Friburgo líder invicto", "c1": 2.37, "cx": 3.85, "c2": 2.70, "boost": [0.9, 0.7, 1.5]},
    {"nombre": "Roma vs Inter", "info": "Roma 0 goles en contra", "c1": 2.62, "cx": 3.50, "c2": 2.60, "boost": [1.2, 0.7, 1.0]},
    {"nombre": "Union vs Independiente", "info": "Duelo parejo", "c1": 2.47, "cx": 3.05, "c2": 3.15, "boost": [1.1, 1.0, 1.0]},
    {"nombre": "Instituto vs Talleres", "info": "Instituto LÍDER", "c1": 2.00, "cx": 3.30, "c2": 4.60, "boost": [1.4, 1.0, 0.8]},
    {"nombre": "Gimnasia Mza vs Riestra", "info": "Gimnasia fuerte local", "c1": 2.20, "cx": 2.92, "c2": 3.95, "boost": [1.3, 1.0, 0.7]},
    {"nombre": "Stuttgart vs Dortmund", "info": "Dortmund 2° invicto", "c1": 2.40, "cx": 3.75, "c2": 2.72, "boost": [0.8, 1.0, 1.4]},
]

st.subheader("📝 1. Editá EQUIPOS y cuotas")

nuevos = []
for i, p in enumerate(partidos_base):
    st.markdown(f"--- \n **PARTIDO {i+1}**")
    col1, col2 = st.columns([2, 1])
    with col1:
        nombre = st.text_input(f"Equipos (Partido {i+1})", value=p['nombre'], key=f"nom_{i}")
        info = st.text_input(f"Info / Nota", value=p['info'], key=f"info_{i}")
    with col2:
        c1 = st.number_input(f"Cuota 1", value=p['c1'], key=f"c1_{i}", step=0.05)
        cx = st.number_input(f"Cuota X", value=p['cx'], key=f"cx_{i}", step=0.05)
        c2 = st.number_input(f"Cuota 2", value=p['c2'], key=f"c2_{i}", step=0.05)

    nuevos.append((nombre, [c1,cx,c2], p['boost'], info))

cantidad = st.slider("¿Cuántas combinaciones?", 10, 100, 36)

if st.button(f"🚀 CALCULAR TOP {cantidad}", type="primary", use_container_width=True):
    probs = []
    for (nom, odds, boost, info) in nuevos:
        inv = [1/odds[0], 1/odds[1], 1/odds[2]]
        s = sum(inv)
        real = [inv[0]/s*boost[0], inv[1]/s*boost[1], inv[2]/s*boost[2]]
        total = sum(real)
        real = [r/total for r in real]
        probs.append(real)

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

    combos = sorted(combos, key=lambda x: x[1], reverse=True)[:cantidad]
    rows=[]
    for idx, (combo, p) in enumerate(combos):
        txt = f"{labels[combo[0]]}-{labels[combo[1]]}-{labels[combo[2]]}-{labels[combo[3]]}-{labels[combo[4]]}-{labels[combo[5]]}"
        detalle = []
        for j, val in enumerate(combo):
            res = labels[val]
            if res == "1": equipo = nuevos[j][0].split(" vs ")[0].split(" ")[0]
            elif res == "2": equipo = nuevos[j][0].split(" vs ")[-1].split(" ")[0] if "vs" in nuevos[j][0] else nuevos[j][0]
            else: equipo = "EMPATE"
            detalle.append(equipo)
        rows.append({"#": idx+1, "COMBINACION": txt, "DETALLE": " / ".join(detalle), "X": sum(x==1 for x in combo), "Prob %": round(p*100, 4)})

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=500)
    st.success(f"🏆 MEJOR: {rows[0]['COMBINACION']} - {rows[0]['DETALLE']} ({rows[0]['Prob %']}%)")
    st.download_button("📥 Descargar CSV", df.to_csv(index=False).encode('utf-8'), "pronostico.csv", "text/csv")
