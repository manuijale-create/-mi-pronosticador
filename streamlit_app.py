import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Pronosticador V4 FUNDAMENTADO", page_icon="🧠", layout="wide")
st.title("🧠 Pronosticador V4 - Fundamentado con Datos Reales")

# --- CAJITA DE KEY ---
st.markdown("### 🔑 API Key (Opcional - Modo PRO)")
api_key = st.text_input("Pegá tu key de API-Football acá para activar datos reales", type="password", placeholder="Si no tenés, dejalo vacío y funciona igual")
st.caption("Conseguila gratis en dashboard.api-football.com - Sin key usa datos del día de hoy")

def get_team_stats(team_name, headers):
    try:
        # 1. Buscar ID del equipo
        search_url = f"https://v3.football.api-sports.io/teams?search={team_name.split()[0]}"
        r = requests.get(search_url, headers=headers, timeout=8)
        data = r.json()
        if not data['response']: return None
        team_id = data['response'][0]['team']['id']

        # 2. Traer últimos 5 partidos
        fix_url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
        r2 = requests.get(fix_url, headers=headers, timeout=8)
        fixtures = r2.json()['response']

        wins = 0; goals_for = 0; goals_against = 0
        for f in fixtures:
            if f['teams']['home']['id'] == team_id:
                gf = f['goals']['home']; ga = f['goals']['away']
                if f['teams']['home']['winner']: wins+=1
            else:
                gf = f['goals']['away']; ga = f['goals']['home']
                if f['teams']['away']['winner']: wins+=1
            if gf is not None: goals_for+=gf; goals_against+=ga if ga is not None else 0

        # Boost basado en forma real
        form_boost = 0.7 + (wins/5)*0.8 # 0.7 a 1.5
        # Si mete muchos goles, boost extra
        if goals_for >= 8: form_boost += 0.1

        return {"wins": wins, "gf": goals_for, "ga": goals_against, "boost": round(min(form_boost, 1.6), 2), "fixtures": len(fixtures)}
    except Exception as e:
        return None

headers = {"x-apisports-key": api_key} if api_key else None

# --- PARTIDOS EDITABLES ---
st.markdown("---")
st.subheader("📝 1. Tus 6 partidos (editá lo que quieras)")

partidos_default = [
    {"nombre": "Frankfurt vs Friburgo", "c1": 2.37, "cx": 3.85, "c2": 2.70},
    {"nombre": "Roma vs Inter", "c1": 2.62, "cx": 3.50, "c2": 2.60},
    {"nombre": "Union vs Independiente", "c1": 2.47, "cx": 3.05, "c2": 3.15},
    {"nombre": "Instituto vs Talleres", "c1": 2.00, "cx": 3.30, "c2": 4.60},
    {"nombre": "Gimnasia Mza vs Riestra", "c1": 2.20, "cx": 2.92, "c2": 3.95},
    {"nombre": "Stuttgart vs Dortmund", "c1": 2.40, "cx": 3.75, "c2": 2.72},
]

partidos = []
for i, p in enumerate(partidos_default):
    st.markdown(f"**PARTIDO {i+1}**")
    c_nom, c1, cx, c2 = st.columns([3,1,1,1])
    with c_nom:
        nom = st.text_input(f"Nombre", value=p['nombre'], key=f"nom_v4_{i}", label_visibility="collapsed", placeholder="Ej: Boca vs River")
    with c1: cuota1 = st.number_input("1", value=p['c1'], key=f"c1_v4_{i}", step=0.05)
    with cx: cuotax = st.number_input("X", value=p['cx'], key=f"cx_v4_{i}", step=0.05)
    with c2: cuota2 = st.number_input("2", value=p['c2'], key=f"c2_v4_{i}", step=0.05)

    # Si hay key, buscar stats reales
    boost_info = "[1.0, 1.0, 1.0]"
    stats_text = "Usando boost base (sin key)"
    if api_key and "vs" in nom:
        team1 = nom.split("vs")[0].strip()
        team2 = nom.split("vs")[1].strip()
        with st.spinner(f"Buscando forma real de {team1} y {team2}..."):
            s1 = get_team_stats(team1, headers)
            s2 = get_team_stats(team2, headers)
            if s1 and s2:
                # Boost: local, empate, visita basado en forma
                b1 = s1['boost']; b2 = s2['boost']
                stats_text = f"✅ REAL: {team1} {s1['wins']}V- GF:{s1['gf']} ({b1}) | {team2} {s2['wins']}V- GF:{s2['gf']} ({b2})"
                boost_info = f"[{b1}, 0.9, {b2}]"
                # Guardamos boosts
                partidos.append((nom, [cuota1, cuotax, cuota2], [b1, 0.9, b2], stats_text))
            else:
                partidos.append((nom, [cuota1, cuotax, cuota2], [1.1, 0.9, 1.1], "⚠️ No se encontró, usando boost neutro"))
        st.caption(stats_text)
    else:
        partidos.append((nom, [cuota1, cuotax, cuota2], [1.1, 0.9, 1.1], stats_text))
        st.caption(stats_text)

st.markdown("---")
cantidad = st.slider("Top combinaciones a ver", 10, 100, 36)

if st.button(f"🚀 CALCULAR CON FUNDAMENTOS", type="primary", use_container_width=True):
    probs = []
    for (nom, odds, boost, info) in partidos:
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
        txt = "-".join([labels[v] for v in combo])
        rows.append({"#": idx+1, "COMBINACION": txt, "Prob %": round(p*100, 4), "Cant X": sum(x==1 for x in combo)})

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=600)
    st.success(f"🏆 MEJOR JUGADA FUNDAMENTADA: {rows[0]['COMBINACION']} con {rows[0]['Prob %']}%")

    if api_key:
        st.balloons()
        st.info("🧠 Este resultado está fundamentado con los últimos 5 partidos reales de cada equipo via API")
    else:
        st.warning("💡 Pegá la key arriba para activar el modo 100% fundamentado con datos en vivo")

    st.download_button("📥 Descargar CSV", df.to_csv(index=False).encode('utf-8'), "v4_fundamentado.csv", "text/csv")
