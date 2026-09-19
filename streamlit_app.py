import streamlit as st, requests, pandas as pd
import itertools

API_KEY = "1e4ee6fc60b847f30afc0d2f6fac4118"
HEAD = {"x-apisports-key": API_KEY}

st.set_page_config(page_title="Analisis de Partidos V1 - LIVE", page_icon="⚽", layout="wide")
st.markdown("<h1 style='text-align:center'>⚽ ANALISIS DE PARTIDOS V1 - TABLAS EN VIVO</h1>", unsafe_allow_html=True)

# Auto refresco cada 60 seg para el vivo
st.markdown("🔴 **LIVE**: La página se actualiza cada 60 segundos sola")

def get_tabla_base(league):
    try:
        r=requests.get(f"https://v3.football.api-sports.io/standings?league={league}&season=2024", headers=HEAD, timeout=10).json()
        return r['response'][0]['league']['standings'][0]
    except: return None

def get_live_fixtures(league):
    try:
        r=requests.get(f"https://v3.football.api-sports.io/fixtures?league={league}&season=2024&live=all", headers=HEAD, timeout=10).json()
        return r['response']
    except: return []

def tabla_live(league, nombre_liga):
    base_raw = get_tabla_base(league)
    lives = get_live_fixtures(league)
    if not base_raw: return None, []

    # DataFrame base
    df = pd.DataFrame([{
        "#":t['rank'], "Equipo":t['team']['name'], "Pts":t['points'],
        "PJ":t['all']['played'], "id":t['team']['id']
    } for t in base_raw])

    # Si hay partidos en vivo, ajustamos puntos en tiempo real
    if lives:
        df_live = df.copy()
        for lv in lives:
            hg = lv['goals']['home'] or 0
            ag = lv['goals']['away'] or 0
            hid = lv['teams']['home']['id']
            aid = lv['teams']['away']['id']

            # Sumamos puntos LIVE
            if hg > ag: # local gana
                df_live.loc[df_live['id']==hid, 'Pts'] += 3
            elif ag > hg: # visita gana
                df_live.loc[df_live['id']==aid, 'Pts'] += 3
            else: # empate
                df_live.loc[df_live['id'].isin([hid,aid]), 'Pts'] += 1

            # Marca LIVE
            df_live.loc[df_live['id']==hid, 'Equipo'] = df_live.loc[df_live['id']==hid, 'Equipo'] + f" 🔴 {hg}-{ag} ({lv['fixture']['status']['elapsed']}')"
            df_live.loc[df_live['id']==aid, 'Equipo'] = df_live.loc[df_live['id']==aid, 'Equipo'] + f" 🔴 {ag}-{hg} ({lv['fixture']['status']['elapsed']}')"

        # Reordenar por puntos LIVE
        df_live = df_live.sort_values(by="Pts", ascending=False).reset_index(drop=True)
        df_live['#'] = df_live.index + 1
        return df_live[['#','Equipo','Pts','PJ']], lives
    else:
        return df[['#','Equipo','Pts','PJ']], []

def get_team_stats(nombre):
    try:
        r=requests.get(f"https://v3.football.api-sports.io/teams?search={nombre.split()[0]}", headers=HEAD, timeout=8).json()
        if not r['response']: return None
        tid=r['response'][0]['team']['id']
        f=requests.get(f"https://v3.football.api-sports.io/fixtures?team={tid}&last=5", headers=HEAD, timeout=8).json()['response']
        wins=sum(1 for x in f if (x['teams']['home']['id']==tid and x['teams']['home']['winner']) or (x['teams']['away']['id']==tid and x['teams']['away']['winner']))
        return {"wins":wins, "boost": round(1.0 + wins*0.15 - (0.2 if wins<=1 else 0),2)}
    except: return None

# --- 1. TUS PARTIDOS ---
st.subheader("1. Tus Partidos")
partidos=[]
cols = st.columns(2)
for i in range(6):
    with cols[i%2]:
        with st.container(border=True):
            c1,c2=st.columns(2)
            with c1: e1=st.text_input(f"Local {i+1}", ["Frankfurt","Roma","Union","Instituto","Gimnasia Mza","Stuttgart"][i], key=f"e1{i}")
            with c2: e2=st.text_input(f"Visita {i+1}", ["Friburgo","Inter","Independiente","Talleres","Riestra","Dortmund"][i], key=f"e2{i}")
            q1,qx,q2=st.columns(3)
            with q1: p1=st.number_input(f"1", 2.5, key=f"p1{i}", step=0.05)
            with qx: px=st.number_input(f"X", 3.3, key=f"px{i}", step=0.05)
            with q2: p2=st.number_input(f"2", 2.8, key=f"p2{i}", step=0.05)
            s1=get_team_stats(e1); s2=get_team_stats(e2)
            partidos.append((e1,e2,[p1,px,p2],[s1['boost']*1.15 if s1 else 1.1, 0.85, s2['boost'] if s2 else 1.0]))

# --- 2. TABLAS EN VIVO ---
st.divider()
st.subheader("2. Tablas EN VIVO - Se mueven mientras se juega")

tab_eu, tab_sud = st.tabs(["🌍 LIGA EUROPEA EN VIVO", "🌎 SUDAMERICANA EN VIVO"])

with tab_eu:
    st.info("Tablas Europeas - Si hay un partido jugándose, la tabla ya suma los puntos LIVE")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("### 🇪🇸 La Liga - LIVE")
        df, lives = tabla_live(140, "La Liga")
        if lives:
            for lv in lives: st.error(f"🔴 EN VIVO: {lv['teams']['home']['name']} {lv['goals']['home']}-{lv['goals']['away']} {lv['teams']['away']['name']} {lv['fixture']['status']['elapsed']}'")
        if df is not None: st.dataframe(df.head(15), use_container_width=True, hide_index=True)
        else: st.warning("Sin datos - limite 100/día")

    with c2:
        st.markdown("### 🏴󐁧󐁢󐁥󐁮󐁧󐁿 Premier League - LIVE")
        df, lives = tabla_live(39, "Premier")
        if lives:
            for lv in lives: st.error(f"🔴 EN VIVO: {lv['teams']['home']['name']} {lv['goals']['home']}-{lv['goals']['away']} {lv['teams']['away']['name']}")
        if df is not None: st.dataframe(df.head(15), use_container_width=True, hide_index=True)

    c3,c4=st.columns(2)
    with c3:
        st.markdown("### 🇮🇹 Serie A - LIVE")
        df, lives = tabla_live(135, "Serie A")
        if df is not None: st.dataframe(df.head(15), use_container_width=True, hide_index=True)
    with c4:
        st.markdown("### 🇩🇪 Bundesliga - LIVE")
        df, lives = tabla_live(78, "Bundesliga")
        if df is not None: st.dataframe(df.head(15), use_container_width=True, hide_index=True)

with tab_sud:
    st.success("Tablas Sudamericanas - Actualización en tiempo real")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("### 🇦🇷 Liga Profesional Argentina - LIVE")
        df, lives = tabla_live(128, "LPF")
        if lives:
            st.error(f"🔴 HAY {len(lives)} PARTIDOS EN VIVO AHORA")
            for lv in lives:
                st.markdown(f"**🔴 {lv['teams']['home']['name']} {lv['goals']['home']} - {lv['goals']['away']} {lv['teams']['away']['name']} ({lv['fixture']['status']['elapsed']}')**")
        else:
            st.caption("No hay partidos en vivo ahora. La tabla es la oficial actualizada.")
        if df is not None: st.dataframe(df.head(15), use_container_width=True, hide_index=True)
    with c2:
        st.markdown("### 🇧🇷 Brasileirao - LIVE")
        df, lives = tabla_live(71, "Brasileirao")
        if lives:
            for lv in lives: st.error(f"🔴 LIVE: {lv['teams']['home']['name']} {lv['goals']['home']}-{lv['goals']['away']} {lv['teams']['away']['name']}")
        if df is not None: st.dataframe(df.head(15), use_container_width=True, hide_index=True)

# --- CALCULO ---
st.divider()
if st.button("🚀 CALCULAR MEJOR COMBINADA", type="primary", use_container_width=True):
    probs=[]
    for _,_,odds,boost in partidos:
        inv=[1/o for o in odds]; s=sum(inv)
        real=[inv[0]/s*boost[0], inv[1]/s*boost[1], inv[2]/s*boost[2]]
        probs.append([r/sum(real) for r in real])
    combos=[(c, __import__('math').prod(probs[j][c[j]] for j in range(6))) for c in itertools.product([0,1,2], repeat=6) if sum(x==1 for x in c)<=1]
    combos=sorted(combos, key=lambda x:x[1], reverse=True)[:36]
    df=pd.DataFrame([{"#":i+1,"COMBINACION":"-".join(["1" if x==0 else "X" if x==1 else "2" for x in c]), "PROB %":round(p*100,4)} for i,(c,p) in enumerate(combos)])
    st.dataframe(df, use_container_width=True, height=400)
    st.success(f"🏆 JUGÁ: {df.iloc[0]['COMBINACION']}")
    st.balloons()
