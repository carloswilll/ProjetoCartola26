import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import os
import re
import io

# ══════════════════════════════════════════════════════════════
# 1. CONFIG & CSS
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Cartola Pro 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Tokens ── */
:root {
    --bg-base:    #0D0D14;
    --bg-surface: #14141F;
    --bg-card:    #1A1A28;
    --border:     rgba(255,255,255,0.07);
    --green:      #00C48C;
    --amber:      #F5A623;
    --red:        #FF5C5C;
    --blue:       #4A9EFF;
    --text-1:     #EEEDF0;
    --text-2:     #9998A8;
    --text-3:     #5A5A72;
}

/* ── Base ── */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-base) !important;
}
.main .block-container {
    padding-top: 1.5rem !important;
    max-width: 1400px;
}

/* ── Sidebar — força dark mode completo ── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div,
section[data-testid="stSidebar"] > div {
    background-color: #14141F !important;
    border-right: 1px solid var(--border);
}
/* Labels e texto da sidebar */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
    color: var(--text-2) !important;
}
/* Inputs da sidebar */
[data-testid="stSidebar"] .stMultiSelect > div > div,
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stNumberInput > div > div,
[data-testid="stSidebar"] input {
    background-color: #1A1A28 !important;
    border-color: var(--border) !important;
    color: var(--text-1) !important;
}
/* Tags do multiselect */
[data-testid="stSidebar"] span[data-baseweb="tag"] {
    background-color: #2A2A3C !important;
    color: var(--text-1) !important;
}
/* Slider */
[data-testid="stSidebar"] [data-testid="stSlider"] div[role="slider"] {
    background-color: var(--green) !important;
}
/* Divider */
[data-testid="stSidebar"] hr { border-color: var(--border) !important; }

/* ── Área principal inputs ── */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stNumberInput > div > div,
.stTextInput > div > div {
    background-color: var(--bg-card) !important;
    border-color: var(--border) !important;
    color: var(--text-1) !important;
    border-radius: 8px !important;
}
span[data-baseweb="tag"] {
    background-color: #2A2A3C !important;
    color: var(--text-1) !important;
}
/* Dropdown popup */
[data-baseweb="popover"] [data-baseweb="menu"],
[data-baseweb="select"] [data-baseweb="popover"] {
    background-color: #1A1A28 !important;
    border: 1px solid var(--border) !important;
}
[data-baseweb="option"] { color: var(--text-1) !important; }
[data-baseweb="option"]:hover { background-color: #2A2A3C !important; }

/* ── Título e texto ── */
h1, h2, h3 { color: var(--text-1) !important; }
p, li { color: var(--text-2); }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--bg-surface);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    color: var(--text-2) !important;
    font-weight: 500;
    font-size: 0.875rem;
    padding: 6px 14px !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background-color: var(--bg-card) !important;
    color: var(--text-1) !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.25rem; }

/* ── Metric cards ── */
div[data-testid="metric-container"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px !important;
}
div[data-testid="metric-container"] label {
    color: var(--text-2) !important;
    font-size: 0.75rem !important;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text-1) !important;
    font-size: 1.3rem !important;
    font-weight: 700;
}

/* ── Botões ── */
.stButton > button {
    background: linear-gradient(135deg, #1A6EFF, #0F4FCC) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden;
}
[data-testid="stDataFrame"] th {
    background: var(--bg-surface) !important;
    color: var(--text-2) !important;
    font-size: 0.72rem !important;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stDataFrame"] td {
    color: var(--text-1) !important;
    font-size: 0.875rem;
}

/* ── Alerts ── */
.stAlert { border-radius: 8px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: #2A2A3C; border-radius: 3px; }

/* ── KPI custom cards ── */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 22px;
    height: 100%;
}
.kpi-label {
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.07em; text-transform: uppercase;
    color: var(--text-3); margin-bottom: 6px;
}
.kpi-value { font-size: 1.4rem; font-weight: 700; color: var(--text-1); line-height: 1.2; }
.kpi-sub   { font-size: 0.8rem; font-weight: 600; margin-top: 4px; }
.kpi-green { color: var(--green); }
.kpi-blue  { color: var(--blue); }
.kpi-amber { color: var(--amber); }
.kpi-red   { color: var(--red); }

/* ── Section titles ── */
.sec-title {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--text-3);
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px; margin-bottom: 14px;
}

/* ── Confronto cards ── */
.conf-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 18px;
    display: flex; align-items: center;
    justify-content: space-between; margin-bottom: 8px;
}
.conf-time { font-size: 0.95rem; font-weight: 600; color: var(--text-1); }
.conf-vs   { font-size: 0.7rem; color: var(--text-3); font-weight: 700; letter-spacing: 0.08em; }
.conf-info { font-size: 0.72rem; color: var(--text-2); text-align: right; }

/* ── Mobile ── */
@media (max-width: 640px) {
    [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
    .stPlotlyChart { height: 260px !important; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 2. TEMA PLOTLY
# ══════════════════════════════════════════════════════════════
COLORS = ["#00C48C","#4A9EFF","#F5A623","#FF5C5C","#B57BFF","#FF8A65","#26C6DA","#F06292"]

THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", color="#9998A8", size=12),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.05)"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#9998A8"),
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=0, r=0, t=36, b=0),
    hoverlabel=dict(bgcolor="#1A1A28", bordercolor="rgba(255,255,255,0.1)",
                    font=dict(color="#EEEDF0")),
    colorway=COLORS,
)

def themed(fig):
    fig.update_layout(**THEME)
    return fig

# ══════════════════════════════════════════════════════════════
# 3. HELPERS HTML
# ══════════════════════════════════════════════════════════════
def kpi(label, value, sub, color="green"):
    return f"""<div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub kpi-{color}">{sub}</div>
    </div>"""

def sec(text):
    st.markdown(f'<div class="sec-title">{text}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 4. FUNÇÕES DE DADOS
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def pegar_status_atletas():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get("https://api.cartola.globo.com/atletas/mercado",
                           headers=headers, timeout=10).json()
        mapa = {int(k): v['nome'] for k, v in res['status'].items()}
        return {a['atleta_id']: mapa.get(a['status_id'], 'Sem Status') for a in res['atletas']}
    except Exception:
        return {}

@st.cache_data(ttl=600)
def pegar_jogos_ao_vivo():
    try:
        h = {"User-Agent": "Mozilla/5.0"}
        mercado  = requests.get("https://api.cartola.globo.com/mercado/status", headers=h, timeout=10).json()
        partidas = requests.get("https://api.cartola.globo.com/partidas",        headers=h, timeout=10).json()
        clubes   = requests.get("https://api.cartola.globo.com/clubes",          headers=h, timeout=10).json()
        dc = {int(k): v['nome'] for k, v in clubes.items()}
        if not dc:
            mf = requests.get("https://api.cartola.globo.com/atletas/mercado", headers=h, timeout=10).json()
            dc = {int(k): v['nome'] for k, v in mf['clubes'].items()}
        jogos = []
        if 'partidas' in partidas:
            for p in partidas['partidas']:
                jogos.append({
                    'Mandante':  dc.get(p['clube_casa_id'],      'Casa'),
                    'Visitante': dc.get(p['clube_visitante_id'], 'Fora'),
                    'Local':     p.get('local', '-'),
                    'Data':      f"{p.get('partida_data','')} {p.get('partida_hora','')}",
                })
        return pd.DataFrame(jogos), int(mercado['rodada_atual'])
    except Exception:
        return pd.DataFrame(), 0

@st.cache_data(ttl=3600)
def pegar_tabela_brasileirao():
    try:
        url = "https://www.espn.com.br/futebol/classificacao/_/liga/BRA.1/brazilian-serie-a"
        h   = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
        res = requests.get(url, headers=h, timeout=15)
        dfs = pd.read_html(io.StringIO(res.text))
        if len(dfs) >= 2:
            df_c = pd.concat([dfs[0], dfs[1]], axis=1)
            df_c['Clube_Limpo'] = df_c[dfs[0].columns[0]].astype(str).apply(
                lambda x: re.sub(r'^\d+[A-Z]{3}', '', x))
            tabela = []
            for idx, row in df_c.iterrows():
                tabela.append({
                    'Pos':       int(idx + 1),
                    'Clube':     str(row['Clube_Limpo']),
                    # ✅ int() evita numpy.int64 → erro de serialização JSON
                    'Pts': int(row['PTS']) if 'PTS' in df_c.columns else 0,
                    'J':   int(row['J'])   if 'J'   in df_c.columns else 0,
                    'V':   int(row['V'])   if 'V'   in df_c.columns else 0,
                    'E':   int(row['E'])   if 'E'   in df_c.columns else 0,
                    'D':   int(row['D'])   if 'D'   in df_c.columns else 0,
                    'SG':  int(row['SG'])  if 'SG'  in df_c.columns else 0,
                    'Últimos 5': '-',
                })
            return pd.DataFrame(tabela)
    except Exception as e:
        st.warning(f"⚠️ Tabela ESPN indisponível: {e}")
    return pd.DataFrame()

def gerenciar_banco_dados() -> pd.DataFrame:
    nome_arquivo = "banco_de_dados_historico.csv"
    h = {"User-Agent": "Mozilla/5.0"}
    try:
        status        = requests.get("https://api.cartola.globo.com/mercado/status", headers=h, timeout=10).json()
        rodada_atual  = status['rodada_atual']
        ultima_rodada = rodada_atual - 1 if status['status_mercado'] == 1 else rodada_atual
    except Exception as e:
        st.warning(f"⚠️ API indisponível: {e}")
        return pd.DataFrame()

    if os.path.exists(nome_arquivo):
        try:
            df = pd.read_csv(nome_arquivo, sep=';')
            ultima_no_banco = df['rodada_id'].max() if not df.empty else 0
        except Exception:
            df = pd.DataFrame(); ultima_no_banco = 0
    else:
        df = pd.DataFrame(); ultima_no_banco = 0

    if ultima_rodada > ultima_no_banco:
        container = st.empty()
        container.info(f"🔄 Baixando rodadas {ultima_no_banco+1} a {ultima_rodada}...")
        novos = []
        try:
            mercado       = requests.get("https://api.cartola.globo.com/atletas/mercado", headers=h, timeout=15).json()
            clubes        = {int(k): v['nome'] for k, v in mercado['clubes'].items()}
            posicoes      = {int(k): v['nome'] for k, v in mercado['posicoes'].items()}
            precos_atuais = {a['atleta_id']: a['preco_num'] for a in mercado['atletas']}
        except Exception:
            clubes, posicoes, precos_atuais = {}, {}, {}

        for r in range(ultima_no_banco + 1, ultima_rodada + 1):
            try:
                pontuados = requests.get(f"https://api.cartola.globo.com/atletas/pontuados/{r}", headers=h, timeout=15).json()
                partidas  = requests.get(f"https://api.cartola.globo.com/partidas/{r}",          headers=h, timeout=15).json()
                mapa_jogos = {}
                if partidas and 'partidas' in partidas:
                    for p in partidas['partidas']:
                        cid, vid = p['clube_casa_id'], p['clube_visitante_id']
                        local = p.get('local', '-')
                        dt    = f"{p.get('partida_data','')} {p.get('partida_hora','')}"
                        mapa_jogos[cid] = {'mando':'CASA','adversario':clubes.get(vid,'Visitante'),'local':local,'data':dt}
                        mapa_jogos[vid] = {'mando':'FORA','adversario':clubes.get(cid,'Mandante'), 'local':local,'data':dt}
                if pontuados and 'atletas' in pontuados:
                    for pid, dados in pontuados['atletas'].items():
                        pid   = int(pid)
                        cid   = dados['clube_id']
                        jogo  = mapa_jogos.get(cid, {'mando':'-','adversario':'-','local':'-','data':'-'})
                        preco = dados.get('preco_num') or dados.get('preco') or precos_atuais.get(pid, 0)
                        row   = {
                            'rodada_id':    r,      'atleta_id':    pid,
                            'apelido':      dados.get('apelido', f'Jog {pid}'),
                            'foto':         dados.get('foto', '').replace('FORMATO', '140x140'),
                            'clube_nome':   clubes.get(cid, 'Outro'),
                            'posicao_nome': posicoes.get(dados['posicao_id'], 'Outro'),
                            'pontos':       dados.get('pontuacao', 0),
                            'preco':        preco,
                            'media':        dados.get('media', 0),
                            'mando':        jogo['mando'],   'adversario': jogo['adversario'],
                            'estadio':      jogo['local'],   'data_jogo':  jogo['data'],
                        }
                        row.update(dados.get('scout') or {})
                        novos.append(row)
            except Exception as e:
                st.toast(f"⚠️ Erro na rodada {r}: {e}", icon="⚠️")
                continue

        if novos:
            df_novo  = pd.DataFrame(novos).fillna(0)
            df_final = pd.concat([df, df_novo], ignore_index=True)
            df_final.to_csv(nome_arquivo, index=False, sep=';', encoding='utf-8-sig')
            container.empty()
            return df_final

    return df

# ══════════════════════════════════════════════════════════════
# 5. PROCESSAMENTO
# ══════════════════════════════════════════════════════════════
df = gerenciar_banco_dados()

if df.empty:
    st.title("⚽ Cartola Pro 2026")
    st.warning("Aguardando dados da primeira rodada...")
    st.stop()

for col in ['estadio','data_jogo','mando','adversario','foto','apelido','clube_nome','posicao_nome']:
    if col not in df.columns:
        df[col] = '-'

scouts_cols = ['G','A','FT','FD','FF','FS','PS','I','PP','DS','SG','DE','DP','GS','FC','PC','CA','CV','GC']
for c in scouts_cols:
    if c not in df.columns: df[c] = 0
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

df['pontuacao_basica'] = (
    (df['DS']*1.5)+(df['FS']*0.5)+(df['FF']*0.8)+(df['FD']*1.2)+(df['FT']*3.0)+
    (df['DE']*1.0)+(df['PS']*1.0)+(df['FC']*-0.3)+(df['PC']*-1.0)+
    (df['CA']*-1.0)+(df['CV']*-3.0)+(df['GS']*-1.0)+(df['I']*-0.1)
)
df['participacao_gol'] = df['G'] + df['A']
df['finalizacoes']     = df['FD'] + df['FF'] + df['FT']

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ Cartola Pro 2026")
    st.markdown('<div class="sec-title">⚙️ Filtros Globais</div>', unsafe_allow_html=True)

    contagem_jogos = df.groupby('atleta_id')['rodada_id'].nunique()
    max_jogos      = int(contagem_jogos.max()) if not contagem_jogos.empty else 1
    min_jogos      = st.slider("🎮 Mínimo de jogos:", 1, max_jogos, 1)
    st.divider()

    st.markdown('<div class="sec-title">🔍 Segmentação</div>', unsafe_allow_html=True)
    lista_clubes   = sorted(df['clube_nome'].astype(str).unique())
    lista_posicoes = sorted(df['posicao_nome'].astype(str).unique())
    sel_clube      = st.multiselect("🏟️ Clube",   lista_clubes,   default=lista_clubes)
    sel_posicao    = st.multiselect("👕 Posição", lista_posicoes, default=lista_posicoes)
    st.divider()

    rodadas_disp    = sorted(df['rodada_id'].unique())
    n_rodadas_total = len(rodadas_disp)
    st.markdown(f'<div class="sec-title">📊 {n_rodadas_total} rodadas no banco</div>', unsafe_allow_html=True)
    st.caption(f"Rodadas: {rodadas_disp[0]} → {rodadas_disp[-1]}")

df_periodo  = df.copy()
df_filtrado = df_periodo[
    (df_periodo['clube_nome'].isin(sel_clube)) &
    (df_periodo['posicao_nome'].isin(sel_posicao))
]

agg_rules = {
    'rodada_id':'count','pontos':'mean','pontuacao_basica':'mean','preco':'last',
    'clube_nome':'last','posicao_nome':'last','foto':'last',
    'participacao_gol':'sum','finalizacoes':'sum','apelido':'last',
}
for s in scouts_cols:
    agg_rules[s] = 'sum'

df_agrupado = df_filtrado.groupby('atleta_id').agg(agg_rules).reset_index()
df_agrupado.rename(columns={
    'pontos':'media_geral','pontuacao_basica':'media_basica','rodada_id':'jogos_disputados'
}, inplace=True)
df_agrupado = df_agrupado[df_agrupado['jogos_disputados'] >= min_jogos]

status_dict               = pegar_status_atletas()
df_agrupado['status_txt'] = df_agrupado['atleta_id'].map(status_dict).fillna('Sem Status')

def formatar_status(s):
    mapa = {'Provável':'✅ Provável','Dúvida':'❓ Dúvida','Suspenso':'🟥 Suspenso',
            'Contundido':'🚑 Contundido','Nulo':'❌ Nulo'}
    return mapa.get(s, f'⚪ {s}')

df_agrupado['status'] = df_agrupado['status_txt'].apply(formatar_status)

# ── ÍNDICE PRO ───────────────────────────────────────────────
df_proximos, _ = pegar_jogos_ao_vivo()
df_tabela      = pegar_tabela_brasileirao()

mapa_confrontos = {}
if not df_proximos.empty:
    for _, row in df_proximos.iterrows():
        mapa_confrontos[row['Mandante']]  = {'mando':'CASA','adv':row['Visitante']}
        mapa_confrontos[row['Visitante']] = {'mando':'FORA','adv':row['Mandante']}

mapa_pos_br = {}
if not df_tabela.empty:
    for _, row in df_tabela.iterrows():
        mapa_pos_br[str(row['Clube']).lower()] = int(row['Pos'])

def obter_pos_tabela(nome_clube):
    if not mapa_pos_br: return 10
    cl = nome_clube.lower().strip()
    for nome, pos in mapa_pos_br.items():
        if cl in nome or nome in cl: return pos
    return 10

df_agrupado['mando'] = df_agrupado['clube_nome'].apply(
    lambda c: mapa_confrontos[c]['mando'] if c in mapa_confrontos else 'Sem Jogo'
)

media_cedida_adv     = df.groupby(['adversario', 'posicao_nome'])['pontos'].mean().to_dict()
media_feita_time     = df.groupby(['clube_nome',  'posicao_nome'])['pontos'].mean().to_dict()
media_posicao_global = df.groupby('posicao_nome')['pontos'].mean().to_dict()

def calcular_indice_pro(row):
    clube = row['clube_nome']; pos = row['posicao_nome']
    if not mapa_confrontos or clube not in mapa_confrontos:
        return row['media_geral'] * 0.1
    info        = mapa_confrontos[clube]
    fator_mando = 1.15 if info['mando'] == 'CASA' else 0.85
    adv         = info['adv']
    pts_cedidos = media_cedida_adv.get((adv, pos),   media_posicao_global.get(pos, 0))
    pts_feitos  = media_feita_time.get((clube, pos), media_posicao_global.get(pos, 0))
    forca       = (pts_cedidos + pts_feitos) / 2
    fator_fav   = 1 + ((obter_pos_tabela(adv) - obter_pos_tabela(clube)) * 0.008)
    base        = (row['media_geral']*0.4) + (row['media_basica']*0.3) + (forca*0.3)
    return base * fator_mando * fator_fav

df_agrupado['indice_pro']      = df_agrupado.apply(calcular_indice_pro, axis=1)
df_agrupado['custo_beneficio'] = df_agrupado.apply(
    lambda r: r['indice_pro'] / r['preco'] if r['preco'] > 0 else 0, axis=1
)

# ══════════════════════════════════════════════════════════════
# 6. HEADER & KPI CARDS
# ══════════════════════════════════════════════════════════════
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("# ⚽ Cartola Pro 2026")
    st.markdown('<p style="color:#9998A8;margin-top:-10px;font-size:0.9rem;">Dashboard de Inteligência Esportiva · Temporada 2026</p>',
                unsafe_allow_html=True)
with col_h2:
    lbl = f"Rodadas {rodadas_disp[0]}–{rodadas_disp[-1]}" if rodadas_disp else "–"
    st.markdown(f'<div style="text-align:right;padding-top:20px;color:#5A5A72;font-size:0.82rem;">{lbl}</div>',
                unsafe_allow_html=True)

# Faixa gradiente decorativa
st.markdown('<div style="height:3px;background:linear-gradient(90deg,#00C48C,#4A9EFF,#F5A623);'
            'border-radius:2px;margin:6px 0 20px 0;"></div>', unsafe_allow_html=True)

if not df_agrupado.empty:
    top_pro    = df_agrupado.sort_values('indice_pro',       ascending=False).iloc[0]
    top_reg    = df_agrupado.sort_values('media_basica',     ascending=False).iloc[0]
    artilheiro = df_agrupado.sort_values('participacao_gol', ascending=False).iloc[0]
    ladrao     = df_agrupado.sort_values('DS',               ascending=False).iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(kpi("🤖 Top Índice PRO",   top_pro['apelido'],    f"Score: {top_pro['indice_pro']:.2f}",        "green"), unsafe_allow_html=True)
    k2.markdown(kpi("💎 Rei Regularidade", top_reg['apelido'],    f"Básica: {top_reg['media_basica']:.1f} pts", "blue"),  unsafe_allow_html=True)
    k3.markdown(kpi("🔥 Mais Decisivo",    artilheiro['apelido'], f"{int(artilheiro['participacao_gol'])} G+A", "amber"), unsafe_allow_html=True)
    k4.markdown(kpi("🛑 Ladrão de Bolas",  ladrao['apelido'],     f"{int(ladrao['DS'])} Desarmes",              "red"),   unsafe_allow_html=True)

st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 7. TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Próximos Jogos",
    "🤖 Robô & Comparador",
    "📊 Tática",
    "📈 Mercado",
    "🏆 Destaques",
])

# ──────────────────────────────────────────────────────────────
# TAB 1 — JOGOS
# ──────────────────────────────────────────────────────────────
with tab1:
    aba_conf, aba_tab = st.tabs(["⚽ Próximos Confrontos", "🏆 Tabela Brasileirão"])

    with aba_conf:
        sec("CONFRONTOS DA RODADA")
        if not df_proximos.empty:
            for _, row in df_proximos.iterrows():
                st.markdown(f"""
                <div class="conf-card">
                    <div class="conf-time">{row['Mandante']}</div>
                    <div class="conf-vs">VS</div>
                    <div class="conf-time">{row['Visitante']}</div>
                    <div class="conf-info">{row.get('Local','-')}<br>
                        <span style="color:#5A5A72;">{row.get('Data','')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Mercado fechado ou sem jogos previstos.")

    with aba_tab:
        sec("CLASSIFICAÇÃO SÉRIE A 2026")
        if not df_tabela.empty:
            # ✅ CORREÇÃO: int() explícito para evitar numpy.int64
            max_pts = int(df_tabela['Pts'].max()) if not df_tabela.empty else 100
            dft = df_tabela[['Pos','Clube','Pts','J','V','E','D','SG','Últimos 5']].copy()
            # Garante que todas as colunas numéricas são int Python nativo
            for col_num in ['Pos','Pts','J','V','E','D','SG']:
                dft[col_num] = dft[col_num].astype(int)

            st.dataframe(
                dft,
                column_config={
                    "Pos": st.column_config.NumberColumn("Pos", width="small"),
                    "Pts": st.column_config.ProgressColumn(
                        "Pontos", format="%d",
                        min_value=0,
                        max_value=max_pts,   # ✅ agora é int Python
                    ),
                    "Últimos 5": st.column_config.TextColumn("Fase"),
                },
                hide_index=True, use_container_width=True, height=750,
            )
            st.caption("Fonte: ESPN Brasil")
        else:
            st.warning("Tabela indisponível no momento.")

# ──────────────────────────────────────────────────────────────
# TAB 2 — ROBÔ & COMPARADOR
# ──────────────────────────────────────────────────────────────
with tab2:
    st_robo, st_vs = st.tabs(["🤖 Robô Otimizador", "⚔️ Mano a Mano"])

    with st_robo:
        col_in, col_res = st.columns([1, 3])
        with col_in:
            sec("PARÂMETROS")
            orc      = st.number_input("💰 Orçamento (C$)", value=100.0)
            esq      = st.selectbox("📐 Esquema", ["4-3-3","3-4-3","3-5-2"])
            criterio = st.radio("🎯 Critério:", ["Índice PRO ✨","Média Geral","Pontuação Básica"])
            col_crit = 'indice_pro'
            if "Média Geral"       in criterio: col_crit = 'media_geral'
            elif "Pontuação Básica" in criterio: col_crit = 'media_basica'
            gerar = st.button("⚡ Gerar Time Inteligente", use_container_width=True)

        with col_res:
            if gerar:
                meta = {
                    "4-3-3": {'Goleiro':1,'Lateral':2,'Zagueiro':2,'Meia':3,'Atacante':3,'Técnico':1},
                    "3-5-2": {'Goleiro':1,'Lateral':0,'Zagueiro':3,'Meia':5,'Atacante':2,'Técnico':1},
                    "3-4-3": {'Goleiro':1,'Lateral':0,'Zagueiro':3,'Meia':4,'Atacante':3,'Técnico':1},
                }.get(esq)
                pool = df_agrupado[df_agrupado['status_txt'] == 'Provável'].sort_values(col_crit, ascending=False)
                if pool.empty:
                    st.warning("⚠️ Nenhum Provável. Usando todos os atletas.")
                    pool = df_agrupado.sort_values(col_crit, ascending=False)

                time_final = []
                for pos, qtd in meta.items():
                    if qtd > 0:
                        time_final.append(pool[pool['posicao_nome'] == pos].head(qtd))

                if time_final:
                    df_time     = pd.concat(time_final)
                    custo_total = df_time['preco'].sum()
                    loops = 0
                    while custo_total > orc and loops < 100:
                        df_time     = df_time.sort_values('preco', ascending=False)
                        troca_feita = False
                        for idx, jogador_caro in df_time.iterrows():
                            candidatos = pool[
                                (pool['posicao_nome'] == jogador_caro['posicao_nome']) &
                                (pool['preco']        <  jogador_caro['preco']) &
                                (~pool['atleta_id'].isin(df_time['atleta_id']))
                            ]
                            if not candidatos.empty:
                                sub         = candidatos.iloc[0]
                                df_time     = df_time.drop(idx)
                                df_time     = pd.concat([df_time, sub.to_frame().T])
                                custo_total = df_time['preco'].sum()
                                troca_feita = True
                                break
                        if not troca_feita: break
                        loops += 1

                    ordem = ['Goleiro','Lateral','Zagueiro','Meia','Atacante','Técnico']
                    df_time['posicao_nome'] = pd.Categorical(df_time['posicao_nome'], categories=ordem, ordered=True)
                    df_time = df_time.sort_values('posicao_nome')

                    if custo_total > orc:
                        st.error("❌ Não foi possível montar um time dentro do orçamento.")
                    else:
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Score Projetado", f"{df_time[col_crit].sum():.1f}")
                        c2.metric("Custo Total",     f"C$ {custo_total:.2f}", f"Saldo: C$ {orc-custo_total:.2f}")
                        c3.metric("Atletas",         f"{len(df_time)}")
                        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
                        st.dataframe(
                            df_time[['foto','status','posicao_nome','apelido','clube_nome',
                                     'jogos_disputados','mando','preco','indice_pro','media_geral','media_basica']],
                            column_config={
                                "foto":            st.column_config.ImageColumn("Perfil"),
                                "status":          "Status",
                                "posicao_nome":    "Posição",
                                "apelido":         "Jogador",
                                "clube_nome":      "Clube",
                                "jogos_disputados":st.column_config.NumberColumn("Jogos",       format="%d"),
                                "mando":           "Mando",
                                "preco":           st.column_config.NumberColumn("C$",          format="%.2f"),
                                "indice_pro":      st.column_config.NumberColumn("Índice PRO ✨",format="%.2f"),
                                "media_geral":     st.column_config.NumberColumn("Média Geral", format="%.2f"),
                                "media_basica":    st.column_config.NumberColumn("Pont. Básica",format="%.2f"),
                            },
                            hide_index=True, use_container_width=True,
                        )
                        st.markdown("---")
                        st.info("🧠 Robô escalou apenas **Prováveis ✅** e respeitou o orçamento via substituição greedy.")

    with st_vs:
        sec("COMPARATIVO MANO A MANO")
        jogadores = sorted(df_agrupado['apelido'].unique())
        c1, c2    = st.columns(2)
        p1 = c1.selectbox("Jogador 1", jogadores, index=0)
        p2 = c2.selectbox("Jogador 2", jogadores, index=1 if len(jogadores) > 1 else 0)
        if p1 and p2:
            d1   = df_agrupado[df_agrupado['apelido'] == p1].iloc[0]
            d2   = df_agrupado[df_agrupado['apelido'] == p2].iloc[0]
            cats = ['Índice PRO','Pont. Básica','Gols','Finalizações','Desarmes','Part. Gol']
            v1   = [d1['indice_pro'],d1['media_basica'],d1['G'],d1['finalizacoes'],d1['DS'],d1['participacao_gol']]
            v2   = [d2['indice_pro'],d2['media_basica'],d2['G'],d2['finalizacoes'],d2['DS'],d2['participacao_gol']]

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=v1+[v1[0]], theta=cats+[cats[0]], fill='toself', name=p1,
                line=dict(color="#00C48C",width=2), fillcolor="rgba(0,196,140,0.15)"))
            fig.add_trace(go.Scatterpolar(
                r=v2+[v2[0]], theta=cats+[cats[0]], fill='toself', name=p2,
                line=dict(color="#4A9EFF",width=2), fillcolor="rgba(74,158,255,0.15)"))
            fig.update_layout(
                **{k:v for k,v in THEME.items() if k not in ('xaxis','yaxis')},
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,0.06)",
                                    tickfont=dict(color="#5A5A72")),
                    angularaxis=dict(gridcolor="rgba(255,255,255,0.06)",
                                     tickfont=dict(color="#9998A8")),
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

            cs1, cs2 = st.columns(2)
            for d, col, cor in [(d1, cs1, "#00C48C"), (d2, cs2, "#4A9EFF")]:
                with col:
                    st.markdown(f"""
                    <div style="background:#1A1A28;border:1px solid rgba(255,255,255,0.07);
                         border-radius:10px;padding:16px;">
                        <div style="font-size:0.7rem;color:#5A5A72;text-transform:uppercase;
                             letter-spacing:0.06em;margin-bottom:6px;">
                             {d['posicao_nome']} · {d['clube_nome']}</div>
                        <div style="font-size:1.15rem;font-weight:700;color:#EEEDF0;">{d['apelido']}</div>
                        <div style="font-size:0.82rem;color:{cor};margin-top:4px;">
                             Índice PRO: {d['indice_pro']:.2f}</div>
                        <div style="font-size:0.8rem;color:#9998A8;margin-top:2px;">
                             Média: {d['media_geral']:.1f} pts · C$ {d['preco']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TAB 3 — TÁTICA
# ──────────────────────────────────────────────────────────────
with tab3:
    hm1, hm2, hm3 = st.tabs(["🛡️ Defesa","⚔️ Ataque","🏰 Mando"])

    with hm1:
        sec("FRAGILIDADE DEFENSIVA — PONTOS CEDIDOS POR POSIÇÃO")
        heat = df_periodo.groupby(['adversario','posicao_nome'])['pontos'].mean().reset_index()
        if not heat.empty:
            piv = heat.pivot(index='adversario', columns='posicao_nome', values='pontos').fillna(0)
            fig = px.imshow(piv, text_auto=".1f", color_continuous_scale="Reds", aspect="auto")
            themed(fig)
            st.plotly_chart(fig, use_container_width=True)

    with hm2:
        sec("PODER OFENSIVO — PONTOS FEITOS POR POSIÇÃO")
        heat2 = df_periodo.groupby(['clube_nome','posicao_nome'])['pontos'].mean().reset_index()
        if not heat2.empty:
            piv2 = heat2.pivot(index='clube_nome', columns='posicao_nome', values='pontos').fillna(0)
            fig2 = px.imshow(piv2, text_auto=".1f", color_continuous_scale="Greens", aspect="auto")
            themed(fig2)
            st.plotly_chart(fig2, use_container_width=True)

    with hm3:
        sec("DESEMPENHO: CASA × FORA")
        stats_mando = df_periodo.groupby(['clube_nome','mando'])['pontos'].mean().reset_index()
        fig_pts = px.bar(stats_mando, x='clube_nome', y='pontos', color='mando', barmode='group',
                         labels={'pontos':'Média de Pontos','clube_nome':'Time'},
                         color_discrete_map={'CASA':'#00C48C','FORA':'#4A9EFF'})
        themed(fig_pts)
        fig_pts.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_pts, use_container_width=True)

        st.divider()
        col_scout = st.selectbox("Scout para comparar:", ["Gols (G)","Desarmes (DS)","Finalizações (FF+FD)"])
        sc_map    = {"Gols (G)":"G","Desarmes (DS)":"DS","Finalizações (FF+FD)":"finalizacoes"}
        sc_col    = sc_map[col_scout]
        stats_sc  = df_periodo.groupby(['clube_nome','mando'])[sc_col].sum().reset_index()
        fig_sc    = px.bar(stats_sc, x='clube_nome', y=sc_col, color='mando', barmode='group',
                           labels={sc_col:f'Total {col_scout}','clube_nome':'Time'},
                           color_discrete_map={'CASA':'#F5A623','FORA':'#B57BFF'})
        themed(fig_sc)
        fig_sc.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_sc, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 4 — MERCADO
# ──────────────────────────────────────────────────────────────
with tab4:
    sec("INTELIGÊNCIA DE MERCADO")

    col_sf1, col_sf2, col_sf3 = st.columns([2, 2, 1])
    with col_sf1:
        busca = st.text_input("🔍 Buscar atleta", placeholder="Nome...", label_visibility="collapsed")
    with col_sf2:
        filtro_st = st.multiselect(
            "Status", ['✅ Provável','❓ Dúvida','🚑 Contundido','🟥 Suspenso','⚪ Sem Status'],
            default=['✅ Provável','❓ Dúvida','⚪ Sem Status'], label_visibility="collapsed",
        )
    with col_sf3:
        ord_por = st.selectbox("Ordenar", ["Índice PRO","Média","C$","C/B"], label_visibility="collapsed")

    ord_map  = {"Índice PRO":"indice_pro","Média":"media_geral","C$":"preco","C/B":"custo_beneficio"}
    df_merc  = df_agrupado.copy()
    if busca:
        df_merc = df_merc[df_merc['apelido'].str.contains(busca, case=False, na=False)]
    if filtro_st:
        df_merc = df_merc[df_merc['status'].isin(filtro_st)]
    df_merc = df_merc.sort_values(ord_map[ord_por], ascending=False)

    cols_view = ['foto','status','apelido','posicao_nome','clube_nome','jogos_disputados',
                 'preco','indice_pro','custo_beneficio','media_geral','media_basica'] + scouts_cols

    st.dataframe(
        df_merc[cols_view],
        column_config={
            "foto":            st.column_config.ImageColumn("Foto", width="small"),
            "status":          "Status",
            "apelido":         "Atleta",
            "posicao_nome":    "Posição",
            "clube_nome":      "Clube",
            "jogos_disputados":st.column_config.NumberColumn("Jogos",       format="%d"),
            "preco":           st.column_config.NumberColumn("C$",          format="%.2f"),
            "indice_pro":      st.column_config.NumberColumn("Índice PRO ✨",format="%.2f"),
            "custo_beneficio": st.column_config.NumberColumn("C/B ⚡",       format="%.2f"),
            "media_geral":     st.column_config.NumberColumn("Média Tot",    format="%.2f"),
            "media_basica":    st.column_config.ProgressColumn("Pont. Básica",format="%.2f",min_value=-5,max_value=15),
        },
        use_container_width=True, hide_index=True, height=600,
    )

    st.divider()
    sec("DISTRIBUIÇÃO: PREÇO × ÍNDICE PRO")
    if not df_merc.empty:
        fig_sc2 = px.scatter(
            df_merc, x='preco', y='indice_pro', color='posicao_nome',
            size='media_geral', hover_name='apelido',
            hover_data={'clube_nome':True,'media_geral':':.1f','preco':':.2f','indice_pro':':.2f'},
            labels={'preco':'Preço (C$)','indice_pro':'Índice PRO','posicao_nome':'Posição'},
            color_discrete_sequence=COLORS,
        )
        themed(fig_sc2)
        fig_sc2.update_traces(marker=dict(opacity=0.8, line=dict(width=0.5, color='rgba(255,255,255,0.1)')))
        st.plotly_chart(fig_sc2, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 5 — DESTAQUES
# ──────────────────────────────────────────────────────────────
with tab5:
    sec("LÍDERES POR FUNDAMENTO")

    def render_leader(titulo, col_sort, col_container, sufixo="", cor="#00C48C"):
        df_v = df_agrupado[df_agrupado[col_sort] > 0]
        if df_v.empty: return
        lider = df_v.sort_values(col_sort, ascending=False).iloc[0]
        with col_container:
            ci, ct = st.columns([1, 2])
            ci.image(lider['foto'], width=66)
            ct.markdown(f'<div style="font-size:0.65rem;color:#5A5A72;text-transform:uppercase;'
                        f'letter-spacing:0.06em;">{titulo}</div>', unsafe_allow_html=True)
            ct.markdown(f'<div style="font-size:1rem;font-weight:700;color:#EEEDF0;">'
                        f'{lider["apelido"]}</div>', unsafe_allow_html=True)
            ct.markdown(f'<div style="font-size:1.25rem;font-weight:700;color:{cor};">'
                        f'{int(lider[col_sort])} {sufixo}</div>', unsafe_allow_html=True)
            ct.caption(f'{lider["clube_nome"]} · {lider["posicao_nome"]}')
            st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    render_leader("Participação (G+A)", "participacao_gol", r1, cor="#00C48C")
    render_leader("Artilheiro",         "G",                r2, "Gols",   "#F5A623")
    render_leader("Garçom",             "A",                r3, "Assis",  "#4A9EFF")
    render_leader("Finalizações",       "finalizacoes",     r4, "Chutes", "#B57BFF")

    st.divider()
    r5, r6, r7, r8 = st.columns(4)
    render_leader("Desarmes",        "DS", r5, cor="#FF5C5C")
    render_leader("Faltas Sofridas", "FS", r6, cor="#F5A623")
    render_leader("Defesas (Gol)",   "DE", r7, cor="#4A9EFF")
    render_leader("Paredão (SG)",    "SG", r8, "Jgs", "#00C48C")

    st.divider()
    sec("DISTRIBUIÇÃO DE PONTUAÇÃO POR POSIÇÃO")
    if not df_agrupado.empty:
        fig_box = px.box(
            df_agrupado, x='posicao_nome', y='media_geral',
            color='posicao_nome', points="outliers",
            labels={'posicao_nome':'Posição','media_geral':'Média de Pontos'},
            color_discrete_sequence=COLORS,
        )
        themed(fig_box)
        st.plotly_chart(fig_box, use_container_width=True)
