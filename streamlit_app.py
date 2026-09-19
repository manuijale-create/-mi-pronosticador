import streamlit as st, requests, pandas as pd

API_KEY = "1e4ee6fc60b847f30afc0d2f6fac4118"
HEAD = {"x-apisports-key": API_KEY}

st.set_page_config(page_title="Analisis de Partidos V1", page_icon="⚽", layout="wide")
st.markdown("""
<style>
.titulo{font-size:34px;font-weight:800;color:#0f172a;text-align:center}
.caja{background:#f1f5ff;border-radius:10px;padding:10px;border-left:5px solid #2563eb}
</style>
<div class="titulo">⚽ ANALISIS DE PARTIDOS V1</div>
""", unsafe_allow_html=True)

def get_team_stats(nombre):
    try:
        r=requests.get(f"https://v3.football.api-sports.io/teams?search={nombre.split()[0]}", headers=HEAD, timeout=8).json()
        if not r['response']: return None
        tid=r['response'][0]['team']['id']
        f=requests.get(f"https://v3.football.api-sports.io/fixtures?team={tid}&last=5", headers=HEAD, timeout=8).json()['response']
        wins=sum(1 for x in f if (x['teams']['home']['id']==tid and x['teams']['home']['winner']) or (x['teams']['away']['id']==tid and x['teams']['away']['winner']))
        gf=sum((x['goals']['home'] if x['teams']['home']['id']==tid else x['goals']['away']) or 0 for x in f)
        boost=1.0 + (wins*0.15) + (0.1 if gf>6 else 0) - (0.2 if wins<=1 else 0)
        return {"wins":wins,"gf":gf,"boost":round(max(0.6,min(boost,1.7)),2),"racha":"".join(["V" if ((x['teams']['home']['id']==tid and x['teams']['home']['winner']) or (x['teams']['away']['id']==tid and x['teams']['away']['winner'])) else "E" if x['goals']['home']==x['goals']['away'] else "D" for x in f])}
    except: return None

def tabla(league, season=2024):
    try:
        r=requests.get(f"https://v3.football.api-sports.io/standings?league={league}&season={season}", headers=HEAD, timeout=8).json()
        d=r['response'][0]['league']['standings'][0]
        return pd.DataFrame([{"#":t['rank'],"Equipo":t['team']['name'],"Pts":t['points'],"PJ":t['all']['played']} for t in d])
    except: return None

# --- PARTIDOS ---
st.subheader("1. Escribí los equipos y lo que paga")
partidos=[]
for i in range(6):
    with st.container(border=True):
        c1,c2,c3,c4,c5=st.columns([2,2,1,1,1])
        with c1: e1=st.text_input(f"Local {i+1}", ["Frankfurt","Roma","Union","Instituto","Gimnasia Mza","Stuttgart"][i], key=f"e1{i}", label_visibility="collapsed", placeholder="Local")
        with c2: e2=st.text_input(f"Visita {i+1}", ["Friburgo","Inter","Independiente","Talleres","Riestra","Dortmund"][i], key=f"e2{i}", label_visibility="collapsed", placeholder="Visita")
        with c3: q1=st.number_input("1", value=2.5, key=f"q1{i}", step=0.05, label_visibility="collapsed")
        with c4: qx=st.number_input("X", value=3.3, key=f"qx{i}", step=0.05, label_visibility="collapsed")
        with c5: q2=st.number_input("2", value=2.8, key=f"q2{i}", step=0.05, label_visibility="collapsed")
        st.caption(f"{e1} ({q1}) - Empate ({qx}) - {e2} ({q2})")
        st1=get_team_stats(e1); st2=get_team_stats(e2)
        if st1: st.markdown(f"<span style='color:green'>**{e1}**: {st1['racha']} {st1['wins']}V GF:{st1['gf']} Boost {st1['boost']}</span>", unsafe_allow_html=True)
        if st2: st.markdown(f"<span style='color:blue'>**{e2}**: {st2['racha']} {st2['wins']}V GF:{st2['gf']} Boost {st2['boost']}</span>", unsafe_allow_html=True)
        partidos.append((e1,e2,[q1,qx,q2],[st1['boost']*1.15 if st1 else 1.1, 0.85, st2['boost'] if st2 else 1.0]))

st.divider()
st.subheader("2. Tablas de Posiciones")
t1,t2=st.tabs(["EUROPA 🌍","SUDAMERICA 🌎"])
with t1:
    a,b=st.columns(2)
    with a:
        st.markdown("**🇪🇸 La Liga**"); df=tabla(140)
        if df is not None: st.dataframe(df.head(10), use_container_width=True, hide_index=True)
    with b:
        st.markdown("**🏴󐁧󐁢󐁥󐁮󐁧󐁿 Premier**"); df=tabla(39)
        if df is not None: st.dataframe(df.head(10), use_container_width=True, hide_index=True)
with t2:
    a,b=st.columns(2)
    with a:
        st.markdown("**🇦🇷 Argentina LPF**"); df=tabla(128)
        if df is not None: st.dataframe(df.head(12).style.applymap(lambda v: 'background-color: #bbf7d0' if isinstance(v,int) and v<=4 else '', subset=['#']), use_container_width=True, hide_index=True)
    with b:
        st.markdown("**🇧🇷 Brasileirao**"); df=tabla(71)
        if df is not None: st.dataframe(df.head(10), use_container_width=True, hide_index=True)

st.divider()
st.subheader("3. Noticias de Hoy")
st.link_button("📰 Ver ESPN Fútbol - En vivo", "https://www.espn.com.ar/futbol/")
st.link_button("📰 Ver TyC Sports", "https://www.tycsports.com/")
st.link_button("📰 Ver Marca - Europa", "https://www.marca.com/futbol.html")

st.divider()
if st.button("🚀 CALCULAR MEJOR COMBINADA", type="primary", use_container_width=True):
    import itertools
    probs=[]
    for _,_,odds,boost in partidos:
        inv=[1/o for o in odds]; s=sum(inv); real=[inv[0]/s*boost[0], inv[1]/s*boost[1], inv[2]/s*boost[2]]; tot=sum(real)
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
    st.dataframe(df.style.applymap(lambda v: 'background-color: #22c55e; color:white; font-weight:bold' if v==df.iloc[0]['COMBINACION'] else '', subset=['COMBINACION']), use_container_width=True, height=500)
    st.success(f"🏆 JUGÁ ESTA: {rows[0]['COMBINACION']} - {rows[0]['PROB %']}%")
    st.balloons()
