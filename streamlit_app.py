import streamlit as st
import pandas as pd
import requests

# 🔑 ACA ANCLAMOS TU KEY - Pegala acá una vez y listo
API_KEY_ANCLADA = "1e4ee6fc60b847f30afc0d2f6fac4118" # <-- TU KEY VA ACA

st.set_page_config(page_title="Pronosticador V5.1 Humano", page_icon="⚽", layout="wide")
st.title("⚽ Pronosticador V5.1 - Con Realismo Humano")
st.caption("Ahora analiza como vos: forma, localía, goles y moral")

def get_stats_humano(team_name, headers):
    try:
        r = requests.get(f"https://v3.football.api-sports.io/teams?search={team_name.split()[0]}", headers=headers, timeout=8)
        if not r.json()['response']: return None
        team_data = r.json()['response'][0]
        team_id = team_data['team']['id']
        r2 = requests.get(f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5", headers=headers, timeout=8)
        fixtures = r2.json()['response']
        wins=0; gf=0; ga=0; streak=""
        for f in fixtures:
            is_home = f['teams']['home']['id']==team_id
            gfor = f['goals']['home'] if is_home else f['goals']['away']
            gaga = f['goals']['away'] if is_home else f['goals']['home']
            if gfor is None: gfor=0
            if gaga is None: gaga=0
            gf+=gfor; ga+=gaga
            if (is_home and f['teams']['home']['winner']) or (not is_home and f['teams']['away']['winner']):
                wins+=1; streak+="V"
            elif f['goals']['home']==f['goals']['away']: streak+="E"
            else: streak+="D"

        # ANALISIS HUMANO, NO SOLO MATEMATICA
        boost_base = 1.0
        if wins >=4: boost_base += 0.4 # Encendido
        elif wins==3: boost_base += 0.2
        elif wins<=1: boost_base -= 0.3 # Bajón animico

        if gf >=8: boost_base += 0.15 # Goleador
        if ga >=8: boost_base -= 0.15 # Defensa floja

        texto_humano = ""
        if wins>=4: texto_humano = f"🔥 VIENE ENCENDIDO ({streak}) - mete {gf} goles"
        elif wins<=1: texto_humano = f"😬 VIENE MAL ({streak}) - moral baja"
        else: texto_humano = f"😐 Regular ({streak}) - {gf}GF/{ga}GC"

        return {"wins":wins, "gf":gf, "ga":ga, "boost":round(max(0.6, min(boost_base, 1.8)),2), "texto":texto_humano, "streak":streak, "id":team_id}
    except:
        return None

headers = {"x-apisports-key": API_KEY_ANCLADA}

st.success(f"🔑 Key anclada activa:...{API_KEY_ANCLADA[-6:]} | Modo FUNDAMENTADO HUMANO")

defaults = ["Frankfurt vs Friburgo","Roma vs Inter","Union vs Independiente","Instituto vs Talleres","Gimnasia Mza vs Riestra","Stuttgart vs Dortmund"]
partidos_data = []

for i, def_name in enumerate(defaults):
    st.divider()
    nombre = st.text_input(f"Partido {i+1}", value=def_name, key=f"v51_nom_{i}")
    c1,c2,c3 = st.columns(3)
    with c1: q1 = st.number_input("Local 1", value=2.50, key=f"v51_q1_{i}", step=0.05)
    with c2: qx = st.number_input("Empate X", value=3.30, key=f"v51_qx_{i}", step=0.05)
    with c3: q2 = st.number_input("Visita 2", value=2.80, key=f"v51_q2_{i}", step=0.05)

    s1=s2=None
    if "vs" in nombre:
        t1,t2 = [x.strip() for x in nombre.split("vs")][:2]
        col_a, col_b = st.columns(2)
        with col_a:
            with st.spinner(f"Analizando {t1}..."): s1 = get_stats_humano(t1, headers)
            if s1: st.info(f"**{t1}**: {s1['texto']} | Boost: {s1['boost']}")
        with col_b:
            with st.spinner(f"Analizando {t2}..."): s2 = get_stats_humano(t2, headers)
            if s2: st.info(f"**{t2}**: {s2['texto']} | Boost: {s2['boost']}")

    # Localia humana +15%
    b1 = (s1['boost'] if s1 else 1.1) * 1.15
    b2 = s2['boost'] if s2 else 1.1
    bx = 0.9 # Empate siempre menos probable
    partidos_data.append((nombre, [q1,qx,q2], [b1,bx,b2], s1,s2))

cantidad = st.slider("¿Cuántas jugadas ver?", 10, 100, 36)

if st.button("🚀 CALCULAR CON CRITERIO HUMANO", type="primary", use_container_width=True):
    probs=[]
    for _,odds,boost,_,_ in partidos_data:
        inv=[1/o for o in odds]; s=sum(inv)
        real=[inv[0]/s*boost[0], inv[1]/s*boost[1], inv[2]/s*boost[2]]
        tot=sum(real); probs.append([r/tot for r in real])

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

    for idx,(co,p) in enumerate(combos[:5]):
        txt="-".join([labels[v] for v in co])
        with st.container(border=True):
            st.markdown(f"### #{idx+1} - {txt} ({round(p*100,4)}%)")
            for j,v in enumerate(co):
                nom,_,_,s1,s2 = partidos_data[j]
                if v==0 and s1: st.write(f"👉 **{nom.split('vs')[0]}** -> {s1['texto']}")
                elif v==2 and s2: st.write(f"👉 **{nom.split('vs')[1]}** -> {s2['texto']}")
                elif v==1: st.write(f"👉 **Empate en {nom}**")

    # Guardar para descarga
    rows=[{"COMBINACION":"-".join([labels[v] for v in co]), "Prob %":round(p*100,4)} for co,p in combos]
    st.download_button("📥 Descargar CSV", pd.DataFrame(rows).to_csv(index=False).encode('utf-8'), "v51_humano.csv")
