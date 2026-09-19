import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Pronosticador V5 - Inteligente", page_icon="🧠", layout="wide")
st.title("🧠 Pronosticador V5 - Simple y Fundamentado")

api_key = st.text_input("🔑 Tu API Key (queda guardada en esta sesión)", type="password", value=st.session_state.get("key",""))
if api_key: st.session_state["key"] = api_key

def get_stats(team_name, headers):
    try:
        # Busca ID
        r = requests.get(f"https://v3.football.api-sports.io/teams?search={team_name.split()[0]}", headers=headers, timeout=8)
        if not r.json()['response']: return None
        team_id = r.json()['response'][0]['team']['id']
        # Ultimos 5
        r2 = requests.get(f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5", headers=headers, timeout=8)
        fixtures = r2.json()['response']
        wins=0; gf=0; ga=0
        for f in fixtures:
            is_home = f['teams']['home']['id']==team_id
            gfor = f['goals']['home'] if is_home else f['goals']['away']
            gaga = f['goals']['away'] if is_home else f['goals']['home']
            if (is_home and f['teams']['home']['winner']) or (not is_home and f['teams']['away']['winner']): wins+=1
            if gfor: gf+=gfor
            if gaga: ga+=gaga
        boost = min(0.7 + (wins/5)*0.8 + (0.1 if gf>=8 else 0), 1.6)
        stars = "⭐"*wins + "☆"*(5-wins)
        return {"wins":wins, "gf":gf, "ga":ga, "boost":round(boost,2), "stars":stars, "id":team_id}
    except: return None

headers = {"x-apisports-key": api_key} if api_key else None

st.subheader("📝 Tus 6 partidos")
defaults = [
    "Frankfurt vs Friburgo","Roma vs Inter","Union vs Independiente",
    "Instituto vs Talleres","Gimnasia Mza vs Riestra","Stuttgart vs Dortmund"
]
partidos_data = []
for i, def_name in enumerate(defaults):
    c1, c2, c3, c4 = st.columns([3,1,1,1])
    with c1: nombre = st.text_input(f"Partido {i+1}", value=def_name, key=f"v5_nom_{i}", label_visibility="collapsed")
    with c2: q1 = st.number_input("1", value=2.50, key=f"v5_q1_{i}", step=0.05)
    with c3: qx = st.number_input("X", value=3.30, key=f"v5_qx_{i}", step=0.05)
    with c4: q2 = st.number_input("2", value=2.80, key=f"v5_q2_{i}", step=0.05)

    s1 = s2 = None
    if headers and "vs" in nombre:
        t1, t2 = [x.strip() for x in nombre.split("vs")][:2]
        col_a, col_b = st.columns(2)
        with col_a:
            with st.spinner(f"Analizando {t1}..."): s1 = get_stats(t1, headers)
            if s1: st.caption(f"{t1} {s1['stars']} {s1['wins']}V GF:{s1['gf']} - Boost {s1['boost']}")
            else: st.caption(f"{t1} - sin datos")
        with col_b:
            with st.spinner(f"Analizando {t2}..."): s2 = get_stats(t2, headers)
            if s2: st.caption(f"{t2} {s2['stars']} {s2['wins']}V GF:{s2['gf']} - Boost {s2['boost']}")
            else: st.caption(f"{t2} - sin datos")

    # Boosts por defecto si no hay API
    b1 = s1['boost'] if s1 else 1.1
    b2 = s2['boost'] if s2 else 1.1
    if s1 and s1['wins']<=1: st.warning(f"⚠️ OJO: {nombre.split('vs')[0]} viene MAL ({s1['wins']}V)")
    if s2 and s2['wins']<=1: st.warning(f"⚠️ OJO: {nombre.split('vs')[1]} viene MAL ({s2['wins']}V)")

    partidos_data.append((nombre, [q1,qx,q2], [b1, 0.9, b2], s1, s2))

cantidad = st.slider("¿Cuántas jugadas ver?", 10, 100, 36)

if st.button("🚀 CALCULAR V5 FUNDAMENTADA", type="primary", use_container_width=True):
    probs=[]
    for nom, odds, boost, _, _ in partidos_data:
        inv=[1/o for o in odds]; s=sum(inv)
        real=[inv[0]/s*boost[0], inv[1]/s*boost[1], inv[2]/s*boost[2]]
        tot=sum(real); real=[r/tot for r in real]; probs.append(real)

    labels=["1","X","2"]
    combos=[]
    for a in range(3):
     for b in range(3):
      for c in range(3):
       for d in range(3):
        for e in range(3):
         for f in range(3):
            co=(a,b,c,d,e,f)
            if sum(x==1 for x in co)>1: continue
            p=probs[0][a]*probs[1][b]*probs[2][c]*probs[3][d]*probs[4][e]*probs[5][f]
            combos.append((co,p))
    combos=sorted(combos, key=lambda x: x[1], reverse=True)[:cantidad]

    rows=[]
    for idx,(co,p) in enumerate(combos):
        txt="-".join([labels[v] for v in co])
        detalle=[]
        for j,v in enumerate(co):
            tname=partidos_data[j][0]
            if v==0: detalle.append(tname.split("vs")[0].strip())
            elif v==2: detalle.append(tname.split("vs")[1].strip() if "vs" in tname else tname)
            else: detalle.append("EMPATE")
        rows.append({"#":idx+1,"COMBINACION":txt,"QUIEN GANA":" / ".join(detalle),"Prob %":round(p*100,4)})

    df=pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=500)
    st.success(f"🏆 MEJOR: {rows[0]['COMBINACION']} -> {rows[0]['QUIEN GANA']}")

    # Texto para WhatsApp con justificación real
    justif = f"🧠 *Pronóstico Fundamentado V5* - Top {rows[0]['COMBINACION']} ({rows[0]['Prob %']}%)\n\n"
    for j,v in enumerate(combos[0][0]):
        nom,_,_,s1,s2 = partidos_data[j]
        if labels[v]=="1" and s1: justif+=f"✅ {nom.split('vs')[0]} {s1['stars']} viene con {s1['wins']}V en 5, GF {s1['gf']}\n"
        elif labels[v]=="2" and s2: justif+=f"✅ {nom.split('vs')[1]} {s2['stars']} viene con {s2['wins']}V en 5, GF {s2['gf']}\n"
    justif+="\n_Fundamentado con últimos 5 partidos reales vía API_"

    st.text_area("📲 Copiá para WhatsApp:", value=justif, height=200)
    st.download_button("📥 Descargar CSV", df.to_csv(index=False).encode('utf-8'), "v5_fundamentado.csv", "text/csv")
