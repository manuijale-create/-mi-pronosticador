import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pronosticador PRO V3", page_icon="🏆", layout="wide")

st.markdown("""
<style>
.metric {background: #f8f9fa; padding:15px; border-radius:10px; border-left:5px solid #ff4b4b;}
.combo-top {background: linear-gradient(90deg, #d4edda, #fff); padding:10px; border-radius:10px; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

st.title("🏆 Pronosticador PRO V3 - 10% Empates")

partidos_base = [
    {"nombre": "Frankfurt 🆚 Friburgo", "info": "Friburgo líder invicto", "c1": 2.37, "cx": 3.85, "c2": 2.70, "boost": [0.9, 0.7, 1.5]},
    {"nombre": "Roma 🆚 Inter", "info": "Roma 0 goles en contra de local", "c1": 2.62, "cx": 3.50, "c2": 2.60, "boost": [1.2, 0.7, 1.0]},
    {"nombre": "Unión 🆚 Independiente", "info": "Duelo parejo, local levemente fav", "c1": 2.47, "cx": 3.05, "c2": 3.15, "boost": [1.1, 1.0, 1.0]},
    {"nombre": "Instituto 🆚 Talleres", "info": "Instituto LÍDER 4V-1E", "c1": 2.00, "cx": 3.30, "c2": 4.60, "boost": [1.4, 1.0, 0.8]},
    {"nombre": "Gimnasia Mza 🆚 Riestra", "info": "Gimnasia fuerte en Mendoza", "c1": 2.20, "cx": 2.92, "c2": 3.95, "boost": [1.3, 1.0, 0.7]},
    {"nombre": "Stuttgart 🆚 Dortmund", "info": "Dortmund 2° invicto Bundesliga", "c1": 2.40, "cx": 3.75, "c2": 2.72, "boost": [0.8, 1.0, 1.4]},
]

st.subheader("📝 1. Revisá las cuotas (podés editarlas)")

cols = st.columns(3)
nuevos = []
for i, p in enumerate(partidos_base):
    with cols[i % 3]:
        st.markdown(f"**{p['nombre']}**")
        st.caption(f"ℹ️ {p['info']}")
        c1 = st.number_input(f"1 ({p['nombre'][:10]})", value=p['c1'], key=f"c1v3_{i}", step=0.05)
        cx = st.number_input(f"X", value=p['cx'], key=f"cxv3_{i}", step=0.05)
        c2 = st.number_input(f"2", value=p['c2'], key=f"c2v3_{i}", step=0.05)
        nuevos.append((p['nombre'], [c1,cx,c2], p['boost'], p['info']))
        st.divider()

st.subheader("🎯 2. Calculá tu jugada maestra")
cantidad = st.slider("¿Cuántas combinaciones querés ver?", 10, 100, 36)

if st.button(f"🚀 CALCULAR TOP {cantidad}", type="primary", use_container_width=True):
    probs = []
    for (nom, odds, boost, info) in nuevos:
        inv = [1/odds[0], 1/odds[1], 1/odds[2]]
        s = sum(inv)
        # Probabilidad real con forma
        real = [inv[0]/s*boost[0], inv[1]/s*boost[1], inv[2]/s*boost[2]]
        # Normalizar de nuevo a 100%
        total = sum(real)
        real = [r/total for r in real]
        probs.append(real)

    # Mostrar probabilidades por partido
    st.write("### 📊 Probabilidades reales estimadas:")
    p_cols = st.columns(3)
    for i, (nom, odds, boost, info) in enumerate(nuevos):
        with p_cols[i % 3]:
            st.markdown(f'<div class="metric"><b>{nom}</b><br>🏠 Local: {probs[i][0]*100:.1f}%<br>🤝 Empate: {probs[i][1]*100:.1f}%<br>✈️ Visit: {probs[i][2]*100:.1f}%</div>', unsafe_allow_html=True)

    labels = ["1","X","2"]
    combos = []
    for a in range(3):
     for b in range(3):
      for c in range(3):
       for d in range(3):
        for e in range(3):
         for f in range(3):
            combo = (a,b,c,d,e,f)
            if sum(x==1 for x in combo) > 1: continue # FILTRO 10% EMPATES
            prob = probs[0][a]*probs[1][b]*probs[2][c]*probs[3][d]*probs[4][e]*probs[5][f]
            combos.append((combo, prob))

    combos = sorted(combos, key=lambda x: x[1], reverse=True)[:cantidad]

    st.write(f"### 🔥 TOP {cantidad} combinaciones (filtradas de 729 -> {len(combos)} con 0 o 1 empate)")
    rows=[]
    for idx, (combo, p) in enumerate(combos):
        txt = f"{labels[combo[0]]}-{labels[combo[1]]}-{labels[combo[2]]}-{labels[combo[3]]}-{labels[combo[4]]}-{labels[combo[5]]}"
        rows.append({"#": idx+1, "COMBINACION": txt, "X": sum(x==1 for x in combo), "Prob %": round(p*100, 4), "Texto WhatsApp": txt})

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=500)

    top1 = rows[0]['COMBINACION']
    st.markdown(f'<div class="combo-top">🏆 MEJOR JUGADA HOY: {top1} con {rows[0]["Prob %"]}% de probabilidad total</div>', unsafe_allow_html=True)

    # Botón para copiar
    texto_wsp = "\n".join([f"{r['#']}. {r['COMBINACION']} ({r['Prob %']}%)" for r in rows[:5]])
    st.code(texto_wsp, language="text")
    st.caption("☝️ Copiá ese texto y pegalo directo en WhatsApp")

    st.download_button("📥 Descargar CSV completo", df.to_csv(index=False).encode('utf-8'), "top_combinaciones.csv", "text/csv")
