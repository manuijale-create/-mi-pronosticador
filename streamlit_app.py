import streamlit as st, requests, pandas as pd
import itertools

API_KEY = "1e4ee6fc60b847f30afc0d2f6fac4118"
HEAD = {"x-apisports-key": API_KEY}

st.set_page_config(page_title="Analisis de Partidos V1", page_icon="⚽", layout="wide")
st.markdown("<h1 style='text-align:center; color:#0f172a'>⚽ ANALISIS DE PARTIDOS V1</h1>", unsafe_allow_html=True)
st.caption("FIX error + Tabla LIVE en tiempo real")

def get_team_stats(nombre):
    try:
        r=requests.get(f"https://v3.football.api-sports.io/teams?search={nombre.split()[0]}", headers=HEAD, timeout=8).json()
        if not r['response']: return None
        tid=r['response'][0]['team']['id']
        f=requests.get(f"https://v3.football.api-sports.io/fixtures?team={tid}&last=5", headers=HEAD, timeout=8).json()['response']
        wins=sum(1 for x in f if (x['teams']['home']['id']==tid and x['teams']['home']['winner']) or (x['teams']['away']['id']==tid and x['teams']['away']['winner']))
        gf=sum((x['goals']['home'] if x['teams']['home']['id']==tid else x['goals']['away']) or 0 for x in f)
        boost=1.0 + (wins*0.15) + (0.1 if gf>6 else 0) - (0.2 if wins<=1 else 0)
        racha="".join(["V" if ((x['teams']['home']['id']==tid and x['teams']['home']['winner']) or (x['teams']['away']['id']==tid and x['teams']['away']['winner'])) else "E" if x['goals']['home']==x['goals']['away'] else "D" for x in f])
        return {"wins":wins,"gf":gf,"boost":round(max(0.6,min(boost,1.7)),2),"racha":racha}
    except: return None

def tabla(league, season=2024):
    try:
        r=requests.get(f"https://v3.football.api-sports.io/standings?league={league}&season={season}", headers=HEAD, timeout=10).json()
        d=r['response'][0]['league']['standings'][0]
        return pd.DataFrame([{"#":t['rank'],"Equipo":t['team']['name'],"Pts":t['points'],"PJ":t['all']['played'],"G":t['all']['win'],"E":t['all']['draw'],"P":t['all']['lose']} for t in d])
    except: return None

def partidos_live(league):
    try:
        r=requests.get(f"https://v3.football.api-sports.io/fixtures?league={league}&season=2024&live=all", headers=HEAD, timeout=8).json()
        return r['response']
    except: return []

# --- 1. PARTIDOS ---
st.subheader("1. Tus 6 Partidos")
partidos=[]
for i in range(6):
    with st.container(border=True):
        c1,c2,c3,c4,c5=st.columns([2,2,1,1,1])
        with c1: e1=st.text_input(f"Local {i+1}", ["Frankfurt","Roma","Union","Instituto","Gimnasia Mza","Stuttgart"][i], key=f"e1{i}")
        with c2: e2=st.text_input(f"Visita {i+1}", ["Friburgo","Inter","Independiente","Talleres","Riestra","Dortmund"][i], key=f"e2{i}")
        with c3: q1=st.number_input(f"1 {e1}", value=2.5, key=f"q1{i}", step=0.05)
        with c4: qx=st.number_input(f"X", value=3.3, key=f"qx{i}", step=0.05)
        with c5: q2=st.number_input(f"2 {e2}", value=2.8, key=f"q2{i}", step=0.05)

        col_a,col_b=st.columns(2)
        with col_a:
            st1=get_team_stats(e1)
            if st1: st.success(f"{e1}: {st1['racha']} | {st1['wins']}V | GF:{st1['gf']} | Boost {st1['boost']}")
        with col_b:
            st2=get_team_stats(e2)
            if st2: st.info(f"{e2}: {st2['racha']} | {st2['wins']}V | GF:{st2['gf']} | Boost {st2['boost']}")

        partidos.append((e1,e2,[q1,qx,q2],[st1['boost']*1.15 if st1 else 1.1, 0.85, st2['boost'] if st2 else 1.0]))

# --- 2. TABLAS REALES + LIVE ---
st.divider()
st.subheader("2. Tablas de Posiciones REALES - Se actualizan solas")

st.markdown("🔴 **MODO LIVE ACTIVO** - Si hay partidos jugandose ahora, la tabla cambia en tiempo real")

tab_eu, tab_sud = st.tabs(["EUROPA 🌍", "SUDAMERICA 🌎"])

with tab_eu:
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**🇪🇸 La Liga España**")
        lives=partidos_live(140)
        if lives:
            st.error(f"🔴 {len(lives)} partidos EN VIVO ahora")
            for lv in lives[:3]:
                st.write(f"⚽ {lv['teams']['home']['name']} {lv['goals']['home']}-{lv['goals']['away']} {lv['teams']['away']['name']} ({lv['fixture']['status']['elapsed']}')")
        df=tabla(140)
        if df is not None: st.dataframe(df.head(15), use_container_width=True, hide_index=True)
    with c2:
        st.markdown("**🏴󐁧󐁢󐁥󐁮󐁧󐁿 Premier League**")
        lives=partidos_live(39)
        if lives: st.error(f"🔴 {len(lives)} partidos EN VIVO")
        df=tabla(39)
        if df is not None: st.dataframe(df.head(15), use_container_width=True, hide_index=True)

with tab_sud:
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**🇦🇷 Liga Profesional Argentina**")
        lives=partidos_live(128)
        if lives:
            st.error(f"🔴 LIVE: {len(lives)} partidos ahora")
            for lv in lives:
                st.write(f"🔴 {lv['teams']['home']['name']} {lv['goals']['home']}-{lv['goals']['away']} {lv['teams']['away']['name']} - {lv['fixture']['status']['elapsed']}'")
        df=tabla(128)
        if df is not None: st.dataframe(df.head(15), use_container_width=True, hide_index=True)
        else: st.warning("Tabla no disponible - limite diario, vuelve mañana")
    with c2:
        st.markdown("**🇧🇷 Brasileirao**")
        df=tabla(71)
        if df is not None: st.dataframe(df.head(15), use_container_width=True, hide_index=True)

# --- 3. NOTICIAS ---
st.divider()
st.subheader("3. Noticias del Día")
st.link_button("📰 ESPN - Fútbol al instante", "https://www.espn.com.ar/futbol/")
st.link_button("📰 TyC Sports - Argentina", "https://www.tycsports.com/")
st.link_button("📰 Marca - Europa LIVE", "https://www.marca.com/futbol.html?intcmp=MENUMIGA&s_kw=futbol")

# --- 4. CALCULO (SIN ERROR) ---
st.divider()
if st.button("🚀 CALCULAR MEJOR COMBINADA", type="primary", use_container_width=True):
    probs=[]
    for _,_,odds,boost in partidos:
        inv=[1/o for o in odds]; s=sum(inv)
        real=[inv[0]/s*boost[0], inv[1]/s*boost[1], inv[2]/s*boost[2]]
        tot=sum(real)
        probs.append([r/tot for r in real])

    combos=[]
    for comb in itertools.product([0,1,2], repeat=6):
        if sum(c==1 for c in comb)>1: continue
        p=1
        for j,c in enumerate(comb): p*=probs[j][c]
        combos.append((comb,p))

    combos=sorted(combos, key=lambda x:x[1], reverse=True)[:36]

    rows=[]
    for idx,(comb,p) in enumerate(combos):
        txt="-".join(["1" if x==0 else "X" if x==1 else "2" for x in comb])
        rows.append({"#":idx+1,"COMBINACION":txt,"PROB %":round(p*100,4)})

    df=pd.DataFrame(rows)
    # TABLA SIN ERROR DE COLORES - simple
    st.dataframe(df, use_container_width=True, height=500)

    st.success(f"🏆 MEJOR JUGADA: {rows[0]['COMBINACION']} - {rows[0]['PROB %']}% de prob")
    st.balloons()
