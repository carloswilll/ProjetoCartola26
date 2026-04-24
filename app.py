import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import re
import io
import numpy as np
from supabase import create_client, Client

# ══════════════════════════════════════════════════════════════
# 1. CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Cartola Pro 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# 2. CSS — design system com alto contraste
# ══════════════════════════════════════════════════════════════
def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg:        #0A0A12;
        --surface:   #111119;
        --card:      #16161F;
        --card2:     #1C1C27;
        --border:    #2A2A3A;
        --border2:   #333344;
        --green:     #22D17A;
        --green-bg:  #0D2B1E;
        --amber:     #F7B731;
        --amber-bg:  #2A2000;
        --red:       #FF6B6B;
        --red-bg:    #2A1010;
        --blue:      #5BA4FF;
        --blue-bg:   #0D1E38;
        --purple:    #A78BFF;
        --t1:        #F0EFF5;
        --t2:        #B0AEBF;
        --t3:        #6B6980;
    }

    * { font-family: 'Inter', system-ui, sans-serif; box-sizing: border-box; }

    /* ── App background ── */
    .stApp, .main { background: var(--bg) !important; }
    .main .block-container {
        padding: 1.25rem 2rem 2rem 2rem !important;
        max-width: 1440px !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] * { color: var(--t2) !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: var(--t1) !important; }
    [data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] { color: var(--green) !important; }

    /* ── Inputs ── */
    .stSelectbox > div > div, .stMultiSelect > div > div,
    .stNumberInput > div > div, .stTextInput > div > div {
        background: var(--card2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--t1) !important;
    }
    input, textarea { color: var(--t1) !important; }
    .stRadio label, .stCheckbox label { color: var(--t2) !important; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px;
        padding: 3px;
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        color: var(--t3) !important;
        font-weight: 500;
        font-size: 0.82rem;
        padding: 6px 12px !important;
        border: 1px solid transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--card2) !important;
        color: var(--t1) !important;
        border-color: var(--border2) !important;
    }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 1.25rem !important; }

    /* ── st.metric ── */
    div[data-testid="metric-container"] {
        background: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 16px 18px !important;
    }
    div[data-testid="metric-container"] label {
        color: var(--t3) !important;
        font-size: 0.7rem !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    [data-testid="stMetricValue"] { color: var(--t1) !important; font-size: 1.3rem !important; font-weight: 700 !important; }
    [data-testid="stMetricDelta"] > div { font-size: 0.78rem !important; font-weight: 500 !important; }

    /* ── Botões ── */
    .stButton > button {
        background: linear-gradient(135deg, #22D17A 0%, #16A85E 100%) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        padding: 10px 20px !important;
        transition: opacity .18s, transform .12s;
    }
    .stButton > button:hover { opacity: 0.85; transform: translateY(-1px); }

    /* ── DataFrames ── */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        overflow: hidden;
    }
    [data-testid="stDataFrame"] th {
        background: var(--surface) !important;
        color: var(--t3) !important;
        font-size: 0.7rem !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        border-bottom: 1px solid var(--border) !important;
    }
    [data-testid="stDataFrame"] td { color: var(--t2) !important; font-size: 0.85rem; }

    /* ── Markdown ── */
    p, li { color: var(--t2) !important; }
    h1 { color: var(--t1) !important; letter-spacing: -0.03em; font-weight: 700; }
    h2, h3, h4 { color: var(--t1) !important; font-weight: 600; }
    .stCaption p { color: var(--t3) !important; }
    hr { border-color: var(--border) !important; margin: 1rem 0; }

    /* ── Alerts ── */
    .stAlert { border-radius: 10px !important; border: 1px solid var(--border2) !important; }
    div[data-testid="stNotification"] p { color: var(--t1) !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

    /* ── KPI card ── */
    .kpi {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px 20px;
        display: flex; flex-direction: column; gap: 5px;
        transition: border-color .2s, transform .15s;
        height: 100%;
    }
    .kpi:hover { border-color: var(--border2); transform: translateY(-2px); }
    .kpi-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--t3); }
    .kpi-value { font-size: 1.4rem; font-weight: 700; color: var(--t1); line-height: 1.15; }
    .kpi-sub   { font-size: 0.78rem; font-weight: 600; }
    .c-green  { color: var(--green); }
    .c-amber  { color: var(--amber); }
    .c-red    { color: var(--red); }
    .c-blue   { color: var(--blue); }
    .c-purple { color: var(--purple); }

    /* ── Section label ── */
    .slabel {
        font-size: 0.62rem; font-weight: 700; letter-spacing: 0.12em;
        text-transform: uppercase; color: var(--t3);
        padding-bottom: 6px; margin-bottom: 10px;
        border-bottom: 1px solid var(--border);
    }

    /* ── Confronto card ── */
    .jogo-card {
        background: var(--card); border: 1px solid var(--border);
        border-radius: 10px; padding: 14px 18px;
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 7px; transition: border-color .2s;
    }
    .jogo-card:hover { border-color: var(--border2); }
    .jogo-time { font-size: 0.95rem; font-weight: 600; color: var(--t1); }
    .jogo-vs   { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; color: var(--t3); padding: 0 12px; }
    .jogo-info { font-size: 0.72rem; color: var(--t2); text-align: right; line-height: 1.5; }

    /* ── Cap candidate ── */
    .cap-card {
        background: var(--card); border: 1px solid var(--border);
        border-radius: 12px; padding: 14px 18px;
        display: flex; align-items: center; gap: 14px;
        margin-bottom: 8px; transition: border-color .2s;
    }
    .cap-card:hover { border-color: var(--border2); }
    .cap-rank  { font-size: 1.4rem; min-width: 30px; text-align: center; }
    .cap-name  { font-size: 0.95rem; font-weight: 600; color: var(--t1); }
    .cap-meta  { font-size: 0.75rem; color: var(--t3); margin-top: 2px; }
    .cap-score { font-size: 1.1rem; font-weight: 700; color: var(--green); margin-left: auto; }
    .cap-just  { font-size: 0.72rem; color: var(--t2); }

    /* ── Leader card ── */
    .leader {
        background: var(--card); border: 1px solid var(--border);
        border-radius: 12px; padding: 14px 16px; margin-bottom: 8px;
    }
    .leader-pos  { font-size: 0.62rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
    .leader-name { font-size: 1rem; font-weight: 700; color: var(--t1); margin: 2px 0; }
    .leader-club { font-size: 0.75rem; color: var(--t3); }
    .leader-val  { font-size: 1.5rem; font-weight: 700; }

    /* ── Mobile ── */
    @media (max-width: 640px) {
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
        .main .block-container { padding: 1rem !important; }
        .stPlotlyChart { height: 260px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ══════════════════════════════════════════════════════════════
# 3. HELPERS VISUAIS
# ══════════════════════════════════════════════════════════════
COLORS = ["#22D17A","#5BA4FF","#F7B731","#FF6B6B","#A78BFF","#FF9F43","#26D4D4","#F368E0"]

PLOT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui", color="#6B6980", size=11),
    title_font=dict(color="#F0EFF5", size=14),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="#2A2A3A", tickfont=dict(color="#6B6980")),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="#2A2A3A", tickfont=dict(color="#6B6980")),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#2A2A3A", borderwidth=1,
                font=dict(color="#B0AEBF"), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=0, r=0, t=36, b=0),
    hoverlabel=dict(bgcolor="#1C1C27", bordercolor="#333344", font=dict(color="#F0EFF5", size=12)),
    colorway=COLORS,
)

def ptheme(fig, title=""):
    fig.update_layout(**PLOT)
    if title: fig.update_layout(title_text=title)
    return fig

def kpi(label, value, sub, c="green"):
    return f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-sub c-{c}">{sub}</div></div>'

def slabel(txt):
    st.markdown(f'<div class="slabel">{txt}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 4. SUPABASE
# ══════════════════════════════════════════════════════════════
@st.cache_resource
def conectar_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = conectar_supabase()

@st.cache_data(ttl=300)
def carregar_historico() -> pd.DataFrame:
    try:
        r = supabase.table("historico_cartola").select("*").execute()
        if r.data: return pd.DataFrame(r.data)
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar histórico: {e}")
    return pd.DataFrame()

def salvar_novas_rodadas(novos):
    if not novos: return
    try:
        for i in range(0, len(novos), 500):
            supabase.table("historico_cartola").insert(novos[i:i+500]).execute()
    except Exception as e:
        st.error(f"❌ Erro ao salvar: {e}")

# ══════════════════════════════════════════════════════════════
# 5. FUNÇÕES DE API
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def pegar_status_atletas():
    try:
        H   = {"User-Agent": "Mozilla/5.0"}
        res = requests.get("https://api.cartola.globo.com/atletas/mercado", headers=H, timeout=10).json()
        ms  = {int(k): v['nome'] for k, v in res['status'].items()}
        return {a['atleta_id']: ms.get(a['status_id'], 'Sem Status') for a in res['atletas']}
    except: return {}

@st.cache_data(ttl=600)
def pegar_jogos_ao_vivo():
    try:
        H  = {"User-Agent": "Mozilla/5.0"}
        mk = requests.get("https://api.cartola.globo.com/mercado/status", headers=H, timeout=10).json()
        pt = requests.get("https://api.cartola.globo.com/partidas",       headers=H, timeout=10).json()
        cl = requests.get("https://api.cartola.globo.com/clubes",         headers=H, timeout=10).json()
        dc = {int(k): v['nome'] for k, v in cl.items()}
        if not dc:
            mf = requests.get("https://api.cartola.globo.com/atletas/mercado", headers=H, timeout=10).json()
            dc = {int(k): v['nome'] for k, v in mf['clubes'].items()}
        jogos = []
        for p in pt.get('partidas', []):
            jogos.append({
                'Mandante':  dc.get(p['clube_casa_id'],      'Casa'),
                'Visitante': dc.get(p['clube_visitante_id'], 'Fora'),
                'Local':     p.get('local', '-'),
                'Data':      f"{p.get('partida_data','')} {p.get('partida_hora','')}",
            })
        return pd.DataFrame(jogos), mk['rodada_atual']
    except: return pd.DataFrame(), 0

@st.cache_data(ttl=3600)
def pegar_tabela_brasileirao():
    try:
        H   = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
               "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"}
        res = requests.get("https://www.espn.com.br/futebol/classificacao/_/liga/BRA.1/brazilian-serie-a", headers=H, timeout=15)
        dfs = pd.read_html(io.StringIO(res.text))
        if len(dfs) >= 2:
            df_c = pd.concat([dfs[0], dfs[1]], axis=1)
            df_c['Clube_Limpo'] = df_c[dfs[0].columns[0]].astype(str).apply(lambda x: re.sub(r'^\d+[A-Z]{3}', '', x))
            rows = []
            for i, row in df_c.iterrows():
                rows.append({'Pos': i+1, 'Clube': row['Clube_Limpo'],
                             'Pts': row.get('PTS',0), 'J': row.get('J',0),
                             'V':   row.get('V',0),   'E': row.get('E',0),
                             'D':   row.get('D',0),   'SG': row.get('SG',0)})
            return pd.DataFrame(rows)
    except Exception as e:
        st.warning(f"⚠️ Tabela ESPN indisponível: {e}")
    return pd.DataFrame()

# ══════════════════════════════════════════════════════════════
# 6. BANCO DE DADOS
# ══════════════════════════════════════════════════════════════
def gerenciar_banco_dados() -> pd.DataFrame:
    H = {"User-Agent": "Mozilla/5.0"}
    try:
        st_api        = requests.get("https://api.cartola.globo.com/mercado/status", headers=H, timeout=10).json()
        rodada_atual  = st_api['rodada_atual']
        ultima_rodada = rodada_atual - 1 if st_api['status_mercado'] == 1 else rodada_atual
    except Exception as e:
        st.warning(f"⚠️ {e}"); return pd.DataFrame()

    df              = carregar_historico()
    ultima_no_banco = int(df['rodada_id'].max()) if not df.empty else 0
    if ultima_rodada <= ultima_no_banco: return df

    box = st.empty()
    box.info(f"🔄 Baixando rodadas {ultima_no_banco+1}–{ultima_rodada}...")
    novos = []
    try:
        mk  = requests.get("https://api.cartola.globo.com/atletas/mercado", headers=H, timeout=15).json()
        dcl = {int(k): v['nome'] for k, v in mk['clubes'].items()}
        dpo = {int(k): v['nome'] for k, v in mk['posicoes'].items()}
        dpr = {a['atleta_id']: a['preco_num'] for a in mk['atletas']}
    except: dcl, dpo, dpr = {}, {}, {}

    for r in range(ultima_no_banco+1, ultima_rodada+1):
        try:
            pon = requests.get(f"https://api.cartola.globo.com/atletas/pontuados/{r}", headers=H, timeout=15).json()
            par = requests.get(f"https://api.cartola.globo.com/partidas/{r}",          headers=H, timeout=15).json()
            mj  = {}
            for p in par.get('partidas', []):
                cid, vid = p['clube_casa_id'], p['clube_visitante_id']
                loc = p.get('local','-'); dt = f"{p.get('partida_data','')} {p.get('partida_hora','')}"
                mj[cid] = {'mando':'CASA','adversario':dcl.get(vid,'Vis'),'local':loc,'data':dt}
                mj[vid] = {'mando':'FORA','adversario':dcl.get(cid,'Man'),'local':loc,'data':dt}
            for pid, d in pon.get('atletas', {}).items():
                pid  = int(pid); cid = d['clube_id']
                jogo = mj.get(cid, {'mando':'-','adversario':'-','local':'-','data':'-'})
                lin  = {
                    'rodada_id':r, 'atleta_id':pid,
                    'apelido':      d.get('apelido',f'Jog {pid}'),
                    'foto':         d.get('foto','').replace('FORMATO','140x140'),
                    'clube_nome':   dcl.get(cid,'Outro'),
                    'posicao_nome': dpo.get(d['posicao_id'],'Outro'),
                    'pontos':       d.get('pontuacao',0),
                    'preco':        d.get('preco_num') or d.get('preco') or dpr.get(pid,0),
                    'media':        d.get('media',0),
                    'mando':        jogo['mando'], 'adversario':jogo['adversario'],
                    'estadio':      jogo['local'], 'data_jogo':jogo['data'],
                }
                lin.update(d.get('scout') or {}); novos.append(lin)
        except Exception as e:
            st.toast(f"⚠️ Rodada {r}: {e}", icon="⚠️"); continue

    if novos:
        df_n = pd.DataFrame(novos).fillna(0)
        salvar_novas_rodadas(df_n.to_dict('records'))
        carregar_historico.clear(); box.empty()
        return pd.concat([df, df_n], ignore_index=True)
    box.empty(); return df

# ══════════════════════════════════════════════════════════════
# 7. PROCESSAMENTO
# ══════════════════════════════════════════════════════════════
df = gerenciar_banco_dados()

if df.empty:
    st.title("⚽ Cartola Pro 2026")
    st.warning("Aguardando dados da primeira rodada..."); st.stop()

for col in ['estadio','data_jogo','mando','adversario','foto','apelido','clube_nome','posicao_nome']:
    if col not in df.columns: df[col] = '-'

SC = ['G','A','FT','FD','FF','FS','PS','I','PP','DS','SG','DE','DP','GS','FC','PC','CA','CV','GC']
for c in SC:
    if c not in df.columns: df[c] = 0
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

df['pontuacao_basica']  = ((df['DS']*1.5)+(df['FS']*0.5)+(df['FF']*0.8)+(df['FD']*1.2)+(df['FT']*3.0)
                           +(df['DE']*1.0)+(df['PS']*1.0)+(df['FC']*-.3)+(df['PC']*-1)
                           +(df['CA']*-1)+(df['CV']*-3)+(df['GS']*-1)+(df['I']*-.1))
df['participacao_gol']  = df['G'] + df['A']
df['finalizacoes']      = df['FD'] + df['FF'] + df['FT']

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ Cartola Pro 2026")
    st.markdown('<div class="slabel">⚙️ Filtros Globais</div>', unsafe_allow_html=True)
    cj      = df.groupby('atleta_id')['rodada_id'].nunique()
    max_j   = int(cj.max()) if not cj.empty else 1
    min_j   = st.slider("🎮 Mínimo de jogos:", 1, max_j, 1)
    st.divider()
    st.markdown('<div class="slabel">🔍 Segmentação</div>', unsafe_allow_html=True)
    lcl     = sorted(df['clube_nome'].astype(str).unique())
    lpo     = sorted(df['posicao_nome'].astype(str).unique())
    sel_cl  = st.multiselect("🏟️ Clube",   lcl, default=lcl)
    sel_po  = st.multiselect("👕 Posição", lpo, default=lpo)
    st.divider()
    rods    = sorted(df['rodada_id'].unique())
    st.markdown(f'<div class="slabel">📊 {len(rods)} rodadas · R{rods[0]}–R{rods[-1]}</div>', unsafe_allow_html=True)

df_f = df[(df['clube_nome'].isin(sel_cl)) & (df['posicao_nome'].isin(sel_po))]

agg = {'rodada_id':'count','pontos':'mean','pontuacao_basica':'mean','preco':'last',
       'clube_nome':'last','posicao_nome':'last','foto':'last',
       'participacao_gol':'sum','finalizacoes':'sum','apelido':'last'}
for s in SC: agg[s] = 'sum'

dfa = df_f.groupby('atleta_id').agg(agg).reset_index()
dfa.rename(columns={'pontos':'media_geral','pontuacao_basica':'media_basica','rodada_id':'jogos_disputados'}, inplace=True)
dfa = dfa[dfa['jogos_disputados'] >= min_j]

sd = pegar_status_atletas()
dfa['status_txt'] = dfa['atleta_id'].map(sd).fillna('Sem Status')
dfa['status']     = dfa['status_txt'].map(
    {'Provável':'✅ Provável','Dúvida':'❓ Dúvida','Suspenso':'🟥 Suspenso',
     'Contundido':'🚑 Contundido','Nulo':'❌ Nulo'}
).fillna(dfa['status_txt'].apply(lambda s: f'⚪ {s}'))

# ── ÍNDICE PRO ───────────────────────────────────────────────
dfp, _  = pegar_jogos_ao_vivo()
dft     = pegar_tabela_brasileirao()
mc      = {}
if not dfp.empty:
    for _, r in dfp.iterrows():
        mc[r['Mandante']]  = {'mando':'CASA','adv':r['Visitante']}
        mc[r['Visitante']] = {'mando':'FORA','adv':r['Mandante']}

mpb = {}
if not dft.empty:
    for _, r in dft.iterrows(): mpb[r['Clube'].lower()] = r['Pos']

def pos_tab(c):
    cl = c.lower().strip()
    for k, v in mpb.items():
        if cl in k or k in cl: return v
    return 10

dfa['mando'] = dfa['clube_nome'].apply(lambda c: mc[c]['mando'] if c in mc else 'Sem Jogo')

mca = df.groupby(['adversario','posicao_nome'])['pontos'].mean().to_dict()
mct = df.groupby(['clube_nome', 'posicao_nome'])['pontos'].mean().to_dict()
mpg = df.groupby('posicao_nome')['pontos'].mean().to_dict()

def calc_pro(row):
    c, p = row['clube_nome'], row['posicao_nome']
    if not mc or c not in mc: return row['media_geral'] * 0.1
    info = mc[c]; fm = 1.15 if info['mando']=='CASA' else 0.85; adv = info['adv']
    pc   = mca.get((adv,p), mpg.get(p,0))
    pf   = mct.get((c,p),   mpg.get(p,0))
    ff   = 1 + ((pos_tab(adv) - pos_tab(c)) * 0.008)
    base = row['media_geral']*0.4 + row['media_basica']*0.3 + ((pc+pf)/2)*0.3
    return base * fm * ff

dfa['indice_pro']      = dfa.apply(calc_pro, axis=1)
dfa['custo_beneficio'] = dfa.apply(lambda r: r['indice_pro']/r['preco'] if r['preco']>0 else 0, axis=1)

# ══════════════════════════════════════════════════════════════
# 8. HEADER
# ══════════════════════════════════════════════════════════════
c1, c2 = st.columns([3,1])
c1.markdown("# ⚽ Cartola Pro 2026")
c1.markdown('<p style="color:#6B6980;margin-top:-10px;font-size:0.875rem;">Dashboard de Inteligência Esportiva · Temporada 2026</p>', unsafe_allow_html=True)
c2.markdown(f'<div style="text-align:right;padding-top:20px;font-size:0.8rem;color:#6B6980;">Rodadas {rods[0]}–{rods[-1]}</div>', unsafe_allow_html=True)
st.markdown('<div style="height:3px;background:linear-gradient(90deg,#22D17A 0%,#5BA4FF 50%,#F7B731 100%);border-radius:2px;margin:6px 0 18px 0;"></div>', unsafe_allow_html=True)

if not dfa.empty:
    tp = dfa.sort_values('indice_pro',       ascending=False).iloc[0]
    tr = dfa.sort_values('media_basica',     ascending=False).iloc[0]
    ta = dfa.sort_values('participacao_gol', ascending=False).iloc[0]
    tl = dfa.sort_values('DS',               ascending=False).iloc[0]
    k1,k2,k3,k4 = st.columns(4)
    k1.markdown(kpi("🤖 Top Índice PRO",   tp['apelido'], f"Score {tp['indice_pro']:.2f}",         "green"),  unsafe_allow_html=True)
    k2.markdown(kpi("💎 Rei Regularidade", tr['apelido'], f"Básica {tr['media_basica']:.1f} pts",   "blue"),   unsafe_allow_html=True)
    k3.markdown(kpi("🔥 Mais Decisivo",    ta['apelido'], f"{int(ta['participacao_gol'])} G+A",      "amber"),  unsafe_allow_html=True)
    k4.markdown(kpi("🛑 Ladrão de Bolas",  tl['apelido'], f"{int(tl['DS'])} Desarmes",               "red"),    unsafe_allow_html=True)

st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 9. TABS
# ══════════════════════════════════════════════════════════════
tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9,tab10 = st.tabs([
    "📅 Jogos","🤖 Robô","📊 Tática","📈 Mercado","🏆 Destaques",
    "💹 Valorização","🎯 Capitão","🔬 Raio-X","🔮 Projeção","🧬 ML & Otimizador",
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — JOGOS
# ══════════════════════════════════════════════════════════════
with tab1:
    a1, a2 = st.tabs(["⚽ Confrontos","🏆 Brasileirão"])
    with a1:
        slabel("CONFRONTOS DA RODADA")
        if not dfp.empty:
            for _, r in dfp.iterrows():
                st.markdown(f"""
                <div class="jogo-card">
                    <div class="jogo-time">{r['Mandante']}</div>
                    <div class="jogo-vs">VS</div>
                    <div class="jogo-time">{r['Visitante']}</div>
                    <div class="jogo-info">{r.get('Local','-')}<br><span style="color:#3A3A50;">{r.get('Data','')}</span></div>
                </div>""", unsafe_allow_html=True)
        else:
            st.warning("Mercado fechado ou sem jogos previstos.")
    with a2:
        slabel("CLASSIFICAÇÃO SÉRIE A")
        if not dft.empty:
            mp = dft['Pts'].max() or 100
            st.dataframe(dft, column_config={
                "Pos": st.column_config.NumberColumn("Pos", width="small"),
                "Pts": st.column_config.ProgressColumn("Pontos", format="%d", min_value=0, max_value=mp),
            }, hide_index=True, use_container_width=True, height=750)
        else:
            st.warning("Tabela indisponível.")

# ══════════════════════════════════════════════════════════════
# TAB 2 — ROBÔ
# ══════════════════════════════════════════════════════════════
with tab2:
    r1, r2 = st.tabs(["🤖 Robô Otimizador","⚔️ Mano a Mano"])

    with r1:
        ci, cr = st.columns([1,3])
        with ci:
            slabel("PARÂMETROS")
            orc  = st.number_input("💰 Orçamento (C$)", value=100.0)
            esq  = st.selectbox("📐 Esquema", ["4-3-3","3-4-3","3-5-2"])
            crit = st.radio("🎯 Critério:", ["Índice PRO ✨","Média Geral","Pont. Básica"])
            cc   = 'indice_pro' if "PRO" in crit else ('media_geral' if "Geral" in crit else 'media_basica')
            gerar = st.button("⚡ Gerar Time", use_container_width=True)

        with cr:
            if gerar:
                meta = {"4-3-3":{'Goleiro':1,'Lateral':2,'Zagueiro':2,'Meia':3,'Atacante':3,'Técnico':1},
                        "3-5-2":{'Goleiro':1,'Lateral':0,'Zagueiro':3,'Meia':5,'Atacante':2,'Técnico':1},
                        "3-4-3":{'Goleiro':1,'Lateral':0,'Zagueiro':3,'Meia':4,'Atacante':3,'Técnico':1}}.get(esq)
                pool = dfa[dfa['status_txt']=='Provável'].sort_values(cc, ascending=False)
                if pool.empty: pool = dfa.sort_values(cc, ascending=False)
                tf = []
                for pos, qtd in meta.items():
                    if qtd > 0: tf.append(pool[pool['posicao_nome']==pos].head(qtd))
                if tf:
                    dt2  = pd.concat(tf); ct = dt2['preco'].sum(); lp = 0
                    while ct > orc and lp < 100:
                        dt2 = dt2.sort_values('preco', ascending=False); ok = False
                        for idx, jc in dt2.iterrows():
                            cand = pool[(pool['posicao_nome']==jc['posicao_nome'])&
                                        (pool['preco']<jc['preco'])&
                                        (~pool['atleta_id'].isin(dt2['atleta_id']))]
                            if not cand.empty:
                                sub = cand.iloc[0]; dt2 = dt2.drop(idx)
                                dt2 = pd.concat([dt2, sub.to_frame().T]); ct = dt2['preco'].sum(); ok=True; break
                        if not ok: break
                        lp += 1
                    ord_t = ['Goleiro','Lateral','Zagueiro','Meia','Atacante','Técnico']
                    dt2['posicao_nome'] = pd.Categorical(dt2['posicao_nome'], categories=ord_t, ordered=True)
                    dt2 = dt2.sort_values('posicao_nome')
                    if ct > orc:
                        st.error("❌ Não foi possível montar dentro do orçamento.")
                    else:
                        m1,m2,m3 = st.columns(3)
                        m1.metric("Score", f"{dt2[cc].sum():.1f}")
                        m2.metric("Custo", f"C$ {ct:.2f}", f"Saldo C$ {orc-ct:.2f}")
                        m3.metric("Atletas", len(dt2))
                        st.dataframe(dt2[['foto','status','posicao_nome','apelido','clube_nome','mando','preco','indice_pro','media_geral','media_basica']],
                            column_config={
                                "foto":         st.column_config.ImageColumn("Foto"),
                                "preco":        st.column_config.NumberColumn("C$",    format="%.2f"),
                                "indice_pro":   st.column_config.NumberColumn("PRO ✨", format="%.2f"),
                                "media_geral":  st.column_config.NumberColumn("Média", format="%.2f"),
                                "media_basica": st.column_config.NumberColumn("Básica",format="%.2f"),
                            }, hide_index=True, use_container_width=True)

    with r2:
        slabel("COMPARATIVO MANO A MANO")
        jg = sorted(dfa['apelido'].unique())
        ca, cb = st.columns(2)
        p1 = ca.selectbox("Jogador 1", jg, 0)
        p2 = cb.selectbox("Jogador 2", jg, 1 if len(jg)>1 else 0)
        if p1 and p2:
            d1 = dfa[dfa['apelido']==p1].iloc[0]; d2 = dfa[dfa['apelido']==p2].iloc[0]
            cats = ['Índice PRO','Pont. Básica','Gols','Finalizações','Desarmes','Part. Gol']
            v1   = [d1['indice_pro'],d1['media_basica'],d1['G'],d1['finalizacoes'],d1['DS'],d1['participacao_gol']]
            v2   = [d2['indice_pro'],d2['media_basica'],d2['G'],d2['finalizacoes'],d2['DS'],d2['participacao_gol']]
            fig  = go.Figure()
            fig.add_trace(go.Scatterpolar(r=v1+[v1[0]],theta=cats+[cats[0]],fill='toself',name=p1,
                line=dict(color="#22D17A",width=2),fillcolor="rgba(34,209,122,0.12)"))
            fig.add_trace(go.Scatterpolar(r=v2+[v2[0]],theta=cats+[cats[0]],fill='toself',name=p2,
                line=dict(color="#5BA4FF",width=2),fillcolor="rgba(91,164,255,0.12)"))
            fig.update_layout(**{k:v for k,v in PLOT.items() if k not in('xaxis','yaxis')},
                polar=dict(bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True,gridcolor="rgba(255,255,255,0.05)",tickfont=dict(color="#3A3A50")),
                    angularaxis=dict(gridcolor="rgba(255,255,255,0.05)",tickfont=dict(color="#6B6980"))))
            st.plotly_chart(fig, use_container_width=True)
            cx1, cx2 = st.columns(2)
            for d, col, cor in [(d1,cx1,"#22D17A"),(d2,cx2,"#5BA4FF")]:
                col.markdown(f"""<div class="leader">
                    <div class="leader-pos" style="color:{cor};">{d['posicao_nome']} · {d['clube_nome']}</div>
                    <div class="leader-name">{d['apelido']}</div>
                    <div class="leader-val" style="color:{cor};">{d['indice_pro']:.2f} <span style="font-size:.8rem;color:#6B6980;">PRO</span></div>
                    <div class="leader-club">Média {d['media_geral']:.1f} pts · C$ {d['preco']:.2f}</div>
                </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 — TÁTICA
# ══════════════════════════════════════════════════════════════
with tab3:
    h1,h2,h3 = st.tabs(["🛡️ Defesa","⚔️ Ataque","🏰 Mando"])
    with h1:
        slabel("FRAGILIDADE DEFENSIVA — PONTOS CEDIDOS POR POSIÇÃO")
        heat = df.groupby(['adversario','posicao_nome'])['pontos'].mean().reset_index()
        if not heat.empty:
            piv = heat.pivot(index='adversario',columns='posicao_nome',values='pontos').fillna(0)
            fig = px.imshow(piv, text_auto=".1f", color_continuous_scale=[[0,"#0A0A12"],[0.5,"#7B2D8B"],[1,"#FF6B6B"]], aspect="auto")
            ptheme(fig); st.plotly_chart(fig, use_container_width=True)
    with h2:
        slabel("PODER OFENSIVO — PONTOS FEITOS POR POSIÇÃO")
        hak = df.groupby(['clube_nome','posicao_nome'])['pontos'].mean().reset_index()
        if not hak.empty:
            pv2 = hak.pivot(index='clube_nome',columns='posicao_nome',values='pontos').fillna(0)
            fg2 = px.imshow(pv2, text_auto=".1f", color_continuous_scale=[[0,"#0A0A12"],[0.5,"#0D5C2B"],[1,"#22D17A"]], aspect="auto")
            ptheme(fg2); st.plotly_chart(fg2, use_container_width=True)
    with h3:
        slabel("DESEMPENHO CASA × FORA")
        sm = df.groupby(['clube_nome','mando'])['pontos'].mean().reset_index()
        fg3 = px.bar(sm, x='clube_nome', y='pontos', color='mando', barmode='group',
                     labels={'pontos':'Média pts','clube_nome':'Time'},
                     color_discrete_map={'CASA':'#22D17A','FORA':'#5BA4FF'})
        ptheme(fg3); fg3.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fg3, use_container_width=True)
        st.divider()
        sc_sel = st.selectbox("Scout:", ["Gols (G)","Desarmes (DS)","Finalizações"])
        sc_col = {"Gols (G)":"G","Desarmes (DS)":"DS","Finalizações":"finalizacoes"}[sc_sel]
        ss = df.groupby(['clube_nome','mando'])[sc_col].sum().reset_index()
        fg4 = px.bar(ss, x='clube_nome', y=sc_col, color='mando', barmode='group',
                     color_discrete_map={'CASA':'#F7B731','FORA':'#A78BFF'})
        ptheme(fg4); fg4.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fg4, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 4 — MERCADO
# ══════════════════════════════════════════════════════════════
with tab4:
    slabel("INTELIGÊNCIA DE MERCADO")
    sf1, sf2, sf3 = st.columns([2,2,1])
    bm  = sf1.text_input("🔍 Buscar atleta", placeholder="Nome...", label_visibility="collapsed")
    fsm = sf2.multiselect("Status", ['✅ Provável','❓ Dúvida','🚑 Contundido','🟥 Suspenso','⚪ Sem Status'],
                          default=['✅ Provável','❓ Dúvida','⚪ Sem Status'], label_visibility="collapsed")
    ord_sel = sf3.selectbox("Ordenar",["Índice PRO","Média","C$","C/B"], label_visibility="collapsed")
    ord_map = {"Índice PRO":"indice_pro","Média":"media_geral","C$":"preco","C/B":"custo_beneficio"}
    dm = dfa.copy()
    if bm:  dm = dm[dm['apelido'].str.contains(bm, case=False, na=False)]
    if fsm: dm = dm[dm['status'].isin(fsm)]
    dm = dm.sort_values(ord_map[ord_sel], ascending=False)
    cv = ['foto','status','apelido','posicao_nome','clube_nome','jogos_disputados','preco','indice_pro','custo_beneficio','media_geral','media_basica']+SC
    st.dataframe(dm[cv], column_config={
        "foto":            st.column_config.ImageColumn("Foto", width="small"),
        "jogos_disputados":st.column_config.NumberColumn("Jogos",  format="%d"),
        "preco":           st.column_config.NumberColumn("C$",     format="%.2f"),
        "indice_pro":      st.column_config.NumberColumn("PRO ✨",  format="%.2f"),
        "custo_beneficio": st.column_config.NumberColumn("C/B ⚡",  format="%.2f"),
        "media_geral":     st.column_config.NumberColumn("Média",   format="%.2f"),
        "media_basica":    st.column_config.ProgressColumn("Básica",format="%.2f", min_value=-5, max_value=15),
    }, use_container_width=True, hide_index=True, height=550)
    st.divider()
    slabel("PREÇO × ÍNDICE PRO")
    if not dm.empty:
        fg5 = px.scatter(dm, x='preco', y='indice_pro', color='posicao_nome', size='media_geral',
                         hover_name='apelido', hover_data={'clube_nome':True,'media_geral':':.1f'},
                         labels={'preco':'Preço (C$)','indice_pro':'Índice PRO'},
                         color_discrete_sequence=COLORS)
        ptheme(fg5); fg5.update_traces(marker=dict(opacity=0.85,line=dict(width=0)))
        st.plotly_chart(fg5, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 5 — DESTAQUES
# ══════════════════════════════════════════════════════════════
with tab5:
    slabel("LÍDERES POR FUNDAMENTO")
    def lcard(titulo, col_s, container, suf="", cor="#22D17A"):
        dv = dfa[dfa[col_s]>0]
        if dv.empty: return
        l  = dv.sort_values(col_s, ascending=False).iloc[0]
        with container:
            ci2, ct2 = st.columns([1,2])
            ci2.image(l['foto'], width=64)
            ct2.markdown(f'<div class="leader"><div class="leader-pos" style="color:{cor};">{titulo}</div>'
                         f'<div class="leader-name">{l["apelido"]}</div>'
                         f'<div class="leader-val" style="color:{cor};">{int(l[col_s])} {suf}</div>'
                         f'<div class="leader-club">{l["clube_nome"]} · {l["posicao_nome"]}</div></div>',
                         unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    lcard("Participação G+A", "participacao_gol", c1, cor="#22D17A")
    lcard("Artilheiro",       "G",                c2, "Gols",   "#F7B731")
    lcard("Garçom",           "A",                c3, "Assis",  "#5BA4FF")
    lcard("Finalizações",     "finalizacoes",     c4, "Chutes", "#A78BFF")
    st.divider()
    c5,c6,c7,c8 = st.columns(4)
    lcard("Desarmes",        "DS", c5, cor="#FF6B6B")
    lcard("Faltas Sofridas", "FS", c6, cor="#F7B731")
    lcard("Defesas",         "DE", c7, cor="#5BA4FF")
    lcard("Paredão (SG)",    "SG", c8, "Jgs","#22D17A")
    st.divider()
    slabel("DISTRIBUIÇÃO DE PONTUAÇÃO POR POSIÇÃO")
    if not dfa.empty:
        fbx = px.box(dfa, x='posicao_nome', y='media_geral', color='posicao_nome', points="outliers",
                     labels={'posicao_nome':'Posição','media_geral':'Média'},
                     color_discrete_sequence=COLORS)
        ptheme(fbx); st.plotly_chart(fbx, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 6 — VALORIZAÇÃO
# ══════════════════════════════════════════════════════════════
with tab6:
    slabel("TENDÊNCIA DE VALORIZAÇÃO C$")
    vb, vp, vj = st.columns([2,1,1])
    bnome  = vb.text_input("🔍", placeholder="Buscar...", label_visibility="collapsed", key="vnom")
    fpos   = vp.selectbox("Pos",["Todas"]+lpo, label_visibility="collapsed", key="vpos")
    minjv  = vj.number_input("Mín.",1,10,3, key="vmin")
    dfpr   = (df.groupby(['atleta_id','rodada_id'])
               .agg(apelido=('apelido','last'),posicao_nome=('posicao_nome','last'),
                    clube_nome=('clube_nome','last'),preco=('preco','last')).reset_index())
    av     = dfpr.groupby('atleta_id')['rodada_id'].nunique()
    dfpr   = dfpr[dfpr['atleta_id'].isin(av[av>=minjv].index)]
    if fpos!="Todas": dfpr = dfpr[dfpr['posicao_nome']==fpos]
    if bnome:         dfpr = dfpr[dfpr['apelido'].str.contains(bnome,case=False,na=False)]
    if dfpr.empty:
        st.warning("Nenhum atleta encontrado.")
    else:
        rv = []
        for aid, g in dfpr.groupby('atleta_id'):
            g=g.sort_values('rodada_id'); pi=g.iloc[0]['preco']; pf=g.iloc[-1]['preco']
            da=pf-pi; dp=((pf-pi)/pi*100) if pi>0 else 0
            rv.append({'atleta_id':aid,'apelido':g.iloc[-1]['apelido'],'posicao_nome':g.iloc[-1]['posicao_nome'],
                       'clube_nome':g.iloc[-1]['clube_nome'],'preco_atual':pf,'preco_ini':pi,
                       'delta_abs':da,'delta_pct':dp,'n_rodadas':len(g)})
        drv = pd.DataFrame(rv)
        va, vb2 = st.columns(2)
        with va:
            slabel("🚀 MAIORES VALORIZAÇÕES")
            for _, r in drv.sort_values('delta_pct',ascending=False).head(5).iterrows():
                st.metric(f"{r['apelido']} — {r['clube_nome']}", f"C$ {r['preco_atual']:.2f}",
                          f"+C$ {r['delta_abs']:.2f} ({r['delta_pct']:+.1f}%)")
        with vb2:
            slabel("📉 MAIORES DESVALORIZAÇÕES")
            for _, r in drv.sort_values('delta_pct',ascending=True).head(5).iterrows():
                st.metric(f"{r['apelido']} — {r['clube_nome']}", f"C$ {r['preco_atual']:.2f}",
                          f"C$ {r['delta_abs']:.2f} ({r['delta_pct']:+.1f}%)")
        st.divider()
        slabel("EVOLUÇÃO DO PREÇO (ATÉ 5 ATLETAS)")
        lat = sorted(dfpr['apelido'].unique())
        sel = st.multiselect("Atletas:",lat,default=lat[:3] if len(lat)>=3 else lat,max_selections=5,key="vsel")
        if sel:
            dg = dfpr[dfpr['apelido'].isin(sel)].sort_values('rodada_id')
            fv = px.line(dg,x='rodada_id',y='preco',color='apelido',markers=True,
                         labels={'rodada_id':'Rodada','preco':'C$'},color_discrete_sequence=COLORS)
            ptheme(fv); fv.update_layout(hovermode='x unified')
            st.plotly_chart(fv, use_container_width=True)
        st.divider()
        st.dataframe(drv[['apelido','posicao_nome','clube_nome','preco_ini','preco_atual','delta_abs','delta_pct','n_rodadas']]
                     .sort_values('delta_pct',ascending=False),
            column_config={"preco_ini":st.column_config.NumberColumn("C$ Ini",format="%.2f"),
                           "preco_atual":st.column_config.NumberColumn("C$ Atual",format="%.2f"),
                           "delta_abs":st.column_config.NumberColumn("Δ C$",format="%+.2f"),
                           "delta_pct":st.column_config.NumberColumn("Δ %",format="%+.1f%%"),
                           "n_rodadas":st.column_config.NumberColumn("Rods",format="%d")},
            hide_index=True, use_container_width=True, height=400)

# ══════════════════════════════════════════════════════════════
# TAB 7 — CAPITÃO
# ══════════════════════════════════════════════════════════════
with tab7:
    slabel("ALERTA DE CAPITÃO IDEAL")
    st.caption("O capitão dobra os pontos. Top candidatos com score e justificativa.")
    cp = dfa[(dfa['status_txt']=='Provável')&(dfa['mando']!='Sem Jogo')].copy()
    if cp.empty: cp = dfa[dfa['mando']!='Sem Jogo'].copy()
    if not cp.empty:
        cp['fm'] = cp['mando'].map({'CASA':1.15,'FORA':0.85}).fillna(1.0)
        cp['sc'] = cp['indice_pro'] * cp['fm']
        for i, (_, r) in enumerate(cp.sort_values('sc',ascending=False).head(10).iterrows()):
            medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"#{i+1}"
            adv   = mc.get(r['clube_nome'],{}).get('adv','-')
            mando_txt = "🏠 CASA +15%" if r['mando']=='CASA' else "✈️ FORA −15%"
            st.markdown(f"""
            <div class="cap-card">
                <div class="cap-rank">{medal}</div>
                <div style="flex:1">
                    <div class="cap-name">{r['apelido']}</div>
                    <div class="cap-meta">{r['posicao_nome']} · {r['clube_nome']} · {mando_txt} · Adv: {adv}</div>
                    <div class="cap-just">PRO {r['indice_pro']:.2f} · Média {r['media_geral']:.1f} pts</div>
                </div>
                <div class="cap-score">{r['sc']:.2f}</div>
            </div>""", unsafe_allow_html=True)
        st.info("💡 Score = Índice PRO × Fator Mando. Casa: +15% | Fora: −15%.")

# ══════════════════════════════════════════════════════════════
# TAB 8 — RAIO-X
# ══════════════════════════════════════════════════════════════
with tab8:
    slabel("RAIO-X DO CONFRONTO")
    times = sorted(df['clube_nome'].astype(str).unique())
    ta2, tb2 = st.columns(2)
    tA = ta2.selectbox("Time A", times, key="rxA")
    tB = tb2.selectbox("Time B", times, index=1 if len(times)>1 else 0, key="rxB")
    if tA==tB:
        st.warning("Selecione times diferentes.")
    else:
        ddir = df[((df['clube_nome']==tA)&(df['adversario']==tB))|((df['clube_nome']==tB)&(df['adversario']==tA))]
        mx1,mx2,mx3 = st.columns(3)
        mx1.metric("Jogos histórico", len(ddir['rodada_id'].unique()) if not ddir.empty else 0)
        if not ddir.empty:
            mx2.metric(f"Média {tA}", f"{ddir[ddir['clube_nome']==tA]['pontos'].mean():.2f}")
            mx3.metric(f"Média {tB}", f"{ddir[ddir['clube_nome']==tB]['pontos'].mean():.2f}")
            st.divider()
            hrx = ddir.groupby(['clube_nome','posicao_nome'])['pontos'].mean().reset_index()
            pvr = hrx.pivot(index='clube_nome',columns='posicao_nome',values='pontos').fillna(0)
            fr  = px.imshow(pvr, text_auto=".1f",
                            color_continuous_scale=[[0,"#0A0A12"],[0.5,"#0D2338"],[1,"#5BA4FF"]], aspect="auto")
            ptheme(fr); st.plotly_chart(fr, use_container_width=True)
            st.divider()
            slabel(f"TOP ATLETAS DE {tA} vs {tB}")
            trx = (ddir[ddir['clube_nome']==tA].groupby('apelido')
                   .agg(media_pts=('pontos','mean'),jogos=('rodada_id','count'))
                   .reset_index().sort_values('media_pts',ascending=False).head(10))
            st.dataframe(trx, column_config={
                "media_pts":st.column_config.NumberColumn("Média pts",format="%.2f"),
                "jogos":    st.column_config.NumberColumn("Jogos",format="%d")},
                hide_index=True, use_container_width=True)
        else:
            st.info("Sem confronto direto no histórico.")
        st.divider()
        slabel(f"FRAGILIDADE DE {tB} POR POSIÇÃO")
        dced = df[df['adversario']==tB].groupby('posicao_nome')['pontos'].mean().reset_index()
        dced.columns = ['Posição','Média cedida']
        fc = px.bar(dced.sort_values('Média cedida',ascending=False), x='Posição', y='Média cedida',
                    color='Média cedida', color_continuous_scale=[[0,"#0A0A12"],[1,"#FF6B6B"]], text_auto='.1f')
        ptheme(fc); st.plotly_chart(fc, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 9 — PROJEÇÃO + FORMA RECENTE
# ══════════════════════════════════════════════════════════════
with tab9:
    pt1, pt2 = st.tabs(["🔮 Projeção por Scout","📅 Forma Recente"])
    with pt1:
        slabel("PROJEÇÃO DE PONTUAÇÃO — PRÓXIMA RODADA")
        st.caption("Estimativa com base nos scouts do atleta contra o adversário específico.")
        pw = {'G':8,'A':5,'FT':3,'FD':1.2,'FF':0.8,'FS':0.5,'PS':1,'DE':1,'DS':1.5,
              'FC':-.3,'PC':-1,'CA':-1,'CV':-3,'GS':-1,'I':-.1,'SG':5}
        acj = dfa[dfa['mando']!='Sem Jogo']['apelido'].unique()
        if len(acj)==0:
            st.warning("Nenhum atleta com jogo confirmado.")
        else:
            selp = st.multiselect("Atletas (máx 10):",sorted(acj),default=list(sorted(acj))[:5],max_selections=10,key="ps")
            if selp:
                rp = []
                for ap in selp:
                    ra = dfa[dfa['apelido']==ap].iloc[0]; cl = ra['clube_nome']
                    adv = mc.get(cl,{}).get('adv',None); da = df[df['apelido']==ap]
                    dvs = da[da['adversario']==adv] if adv else da; fo = f"vs {adv}" if adv else "geral"
                    if dvs.empty: dvs=da; fo="geral"
                    proj = sum(dvs[s].mean()*p for s,p in pw.items() if s in dvs.columns)
                    rp.append({'Atleta':ap,'Clube':cl,'Adv':adv or '-','Mando':ra['mando'],
                               'Base':fo,'Min':proj*.7,'Med':proj,'Max':proj*1.3})
                drp = pd.DataFrame(rp).sort_values('Med',ascending=False)
                st.dataframe(drp, column_config={
                    "Min":st.column_config.NumberColumn(format="%.1f"),
                    "Med":st.column_config.NumberColumn(format="%.1f"),
                    "Max":st.column_config.NumberColumn(format="%.1f")},
                    hide_index=True, use_container_width=True)
                fp = px.bar(drp, x='Atleta', y='Med',
                            error_y=drp['Max']-drp['Med'], error_y_minus=drp['Med']-drp['Min'],
                            color='Mando', color_discrete_map={'CASA':'#22D17A','FORA':'#5BA4FF','Sem Jogo':'#3A3A50'},
                            text_auto='.1f')
                ptheme(fp); st.plotly_chart(fp, use_container_width=True)

    with pt2:
        slabel("ANÁLISE DE FORMA RECENTE")
        nrf = st.slider("Últimas N rodadas:", 1, max_j, min(5,max_j))
        rre = sorted(df['rodada_id'].unique())[-nrf:]
        dre = df[df['rodada_id'].isin(rre)]
        ag2 = {'pontos':'mean','pontuacao_basica':'mean','preco':'last',
               'clube_nome':'last','posicao_nome':'last','apelido':'last','rodada_id':'count'}
        for s in SC: ag2[s]='sum'
        dar = dre.groupby('atleta_id').agg(ag2).reset_index()
        dar.rename(columns={'pontos':'media_rec','pontuacao_basica':'basica_rec','rodada_id':'jogos_rec'},inplace=True)
        dfo = dfa[['atleta_id','apelido','clube_nome','posicao_nome','media_geral','indice_pro']].merge(
            dar[['atleta_id','media_rec','jogos_rec']],on='atleta_id',how='inner')
        dfo['delta'] = dfo['media_rec'] - dfo['media_geral']
        fa2, fb2 = st.columns(2)
        with fa2:
            slabel(f"🔥 EM ALTA — ÚLTIMAS {nrf} RODADAS")
            for _, r in dfo.sort_values('delta',ascending=False).head(8).iterrows():
                st.metric(f"{r['apelido']} — {r['clube_nome']}",f"{r['media_rec']:.1f} pts",f"{r['delta']:+.1f} vs total")
        with fb2:
            slabel(f"📉 EM QUEDA — ÚLTIMAS {nrf} RODADAS")
            for _, r in dfo.sort_values('delta',ascending=True).head(8).iterrows():
                st.metric(f"{r['apelido']} — {r['clube_nome']}",f"{r['media_rec']:.1f} pts",f"{r['delta']:+.1f} vs total")
        st.divider()
        df20 = dfo.sort_values('media_rec',ascending=False).head(20)
        ffm  = go.Figure()
        ffm.add_trace(go.Bar(name='Média Total',x=df20['apelido'],y=df20['media_geral'],marker_color='#2A2A3A',opacity=0.9))
        ffm.add_trace(go.Bar(name=f'Últ. {nrf} rod.',x=df20['apelido'],y=df20['media_rec'],marker_color='#22D17A'))
        ffm.update_layout(**PLOT, barmode='group', xaxis_tickangle=-45)
        st.plotly_chart(ffm, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 10 — ML & OTIMIZADOR
# ══════════════════════════════════════════════════════════════
with tab10:
    ml1, ml2 = st.tabs(["🧬 Predição ML","⚙️ Otimizador PuLP"])

    with ml1:
        slabel("PREDIÇÃO DE VALORIZAÇÃO — RIDGE REGRESSION")
        st.caption("Modelo treinado com scouts e preço histórico para estimar variação de C$ na próxima rodada.")
        try:
            from sklearn.linear_model import Ridge
            from sklearn.preprocessing import StandardScaler
            from sklearn.pipeline import Pipeline
            fm  = ['pontos','G','A','FT','DS','FS','FC','CA','GS','DE','SG','preco']
            for f in fm:
                if f not in df.columns: df[f]=0
            dm2 = df.sort_values(['atleta_id','rodada_id']).copy()
            dm2['preco_prox']  = dm2.groupby('atleta_id')['preco'].shift(-1)
            dm2['delta_preco'] = dm2['preco_prox'] - dm2['preco']
            dm2 = dm2.dropna(subset=['delta_preco']+fm)
            X   = dm2[fm].values; y = dm2['delta_preco'].values
            if len(X)<30:
                st.warning("Dados insuficientes. Aguarde mais rodadas.")
            else:
                mod = Pipeline([('sc',StandardScaler()),('r',Ridge(alpha=1.0))])
                mod.fit(X,y)
                Xp  = np.column_stack([dfa[f].values if f in dfa.columns else np.zeros(len(dfa)) for f in fm])
                dfa['delta_pred'] = mod.predict(Xp)
                cf  = pd.DataFrame({'Feature':fm,'Peso':np.abs(mod.named_steps['r'].coef_)}).sort_values('Peso',ascending=True)
                cp2, ci2 = st.columns([3,2])
                with cp2:
                    slabel("TOP VALORIZAÇÕES PREVISTAS")
                    tp2 = dfa[['apelido','clube_nome','posicao_nome','preco','status_txt','delta_pred']].sort_values('delta_pred',ascending=False).head(15)
                    st.dataframe(tp2, column_config={
                        "preco":     st.column_config.NumberColumn("C$ Atual",  format="%.2f"),
                        "delta_pred":st.column_config.NumberColumn("Δ C$ Prev.",format="%+.2f")},
                        hide_index=True, use_container_width=True)
                with ci2:
                    slabel("FATORES MAIS RELEVANTES")
                    fi2 = px.bar(cf, x='Peso', y='Feature', orientation='h',
                                 color='Peso', color_continuous_scale=[[0,"#0A0A12"],[1,"#22D17A"]])
                    ptheme(fi2); fi2.update_layout(showlegend=False,yaxis_title='')
                    st.plotly_chart(fi2, use_container_width=True)
                st.info("⚠️ Estimativa histórica. Use como sinal complementar.")
        except ImportError:
            st.error("❌ Adicione `scikit-learn` no requirements.txt e faça redeploy.")

    with ml2:
        slabel("OTIMIZADOR DE ESCALAÇÃO — PROGRAMAÇÃO LINEAR")
        st.caption("PuLP: encontra matematicamente a escalação que maximiza o Índice PRO dentro do orçamento.")
        try:
            import pulp
            oc1, oc2 = st.columns([1,2])
            with oc1:
                opo  = st.number_input("💰 Orçamento (C$)", value=100.0, key="opo")
                oes  = st.selectbox("📐 Esquema",["4-3-3","3-4-3","3-5-2"], key="oes")
                ost  = st.multiselect("Status:",['Provável','Dúvida','Sem Status'],default=['Provável'],key="ost")
                omt  = st.number_input("Máx. mesmo time", 1, 5, 5, key="omt")
                obt  = st.button("🚀 Otimizar", use_container_width=True, key="obt")
            with oc2:
                if obt:
                    meta2 = {"4-3-3":{'Goleiro':1,'Lateral':2,'Zagueiro':2,'Meia':3,'Atacante':3,'Técnico':1},
                             "3-5-2":{'Goleiro':1,'Lateral':0,'Zagueiro':3,'Meia':5,'Atacante':2,'Técnico':1},
                             "3-4-3":{'Goleiro':1,'Lateral':0,'Zagueiro':3,'Meia':4,'Atacante':3,'Técnico':1}}.get(oes)
                    pool2 = dfa[dfa['status_txt'].isin(ost)].copy().reset_index(drop=True)
                    if pool2.empty:
                        st.warning("Nenhum atleta disponível.")
                    else:
                        prob = pulp.LpProblem("cartola", pulp.LpMaximize)
                        n2   = len(pool2); il = list(range(n2))
                        x2   = pulp.LpVariable.dicts("x",il,cat='Binary')
                        prob += pulp.lpSum(pool2.iloc[i]['indice_pro']*x2[i] for i in il)
                        prob += pulp.lpSum(pool2.iloc[i]['preco']*x2[i] for i in il) <= opo
                        for pos,qtd in meta2.items():
                            ip = [i for i in il if pool2.iloc[i]['posicao_nome']==pos]
                            prob += pulp.lpSum(x2[i] for i in ip) == qtd
                        for tm in pool2['clube_nome'].unique():
                            it = [i for i in il if pool2.iloc[i]['clube_nome']==tm]
                            prob += pulp.lpSum(x2[i] for i in it) <= omt
                        prob.solve(pulp.PULP_CBC_CMD(msg=0))
                        if pulp.LpStatus[prob.status]=='Optimal':
                            esc = [i for i in il if pulp.value(x2[i])==1]
                            dop = pool2.iloc[esc].copy()
                            ort = ['Goleiro','Lateral','Zagueiro','Meia','Atacante','Técnico']
                            dop['posicao_nome'] = pd.Categorical(dop['posicao_nome'],categories=ort,ordered=True)
                            dop = dop.sort_values('posicao_nome')
                            st.success(f"✅ Custo: C$ {dop['preco'].sum():.2f} · PRO Total: {dop['indice_pro'].sum():.2f}")
                            st.dataframe(dop[['foto','status','posicao_nome','apelido','clube_nome','mando','preco','indice_pro','media_geral']],
                                column_config={
                                    "foto":       st.column_config.ImageColumn("Foto"),
                                    "preco":      st.column_config.NumberColumn("C$",   format="%.2f"),
                                    "indice_pro": st.column_config.NumberColumn("PRO ✨",format="%.2f"),
                                    "media_geral":st.column_config.NumberColumn("Média",format="%.2f")},
                                hide_index=True, use_container_width=True)
                            st.info("💡 Diferença do Robô Greedy: avalia todas as combinações e garante o ótimo global.")
                        else:
                            st.error("❌ Inviável. Aumente o orçamento ou aceite mais status.")
        except ImportError:
            st.error("❌ Adicione `pulp` no requirements.txt e faça redeploy.")
