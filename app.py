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

def local_css():
    st.markdown("""
    <style>
    /* ── Tokens de cor ── */
    :root {
        --bg-base:       #0D0D14;
        --bg-surface:    #14141F;
        --bg-card:       #1A1A28;
        --bg-card-hover: #1F1F30;
        --border:        rgba(255,255,255,0.07);
        --green:         #00C48C;
        --green-dim:     rgba(0,196,140,0.12);
        --amber:         #F5A623;
        --amber-dim:     rgba(245,166,35,0.12);
        --red:           #FF5C5C;
        --red-dim:       rgba(255,92,92,0.12);
        --blue:          #4A9EFF;
        --blue-dim:      rgba(74,158,255,0.12);
        --text-primary:  #EEEDF0;
        --text-secondary:#9998A8;
        --text-muted:    #5A5A72;
    }

    /* ── Reset global ── */
    .stApp { background-color: var(--bg-base); }
    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: var(--bg-surface) !important;
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--text-primary);
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSlider label { color: var(--text-secondary) !important; }

    /* ── Título principal ── */
    h1 { color: var(--text-primary) !important; letter-spacing: -0.02em; }
    h2, h3 { color: var(--text-primary) !important; }

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
        color: var(--text-secondary) !important;
        font-weight: 500;
        font-size: 0.875rem;
        padding: 6px 14px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
    }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 1.25rem; }

    /* ── st.metric cards ── */
    div[data-testid="metric-container"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px 20px !important;
        transition: border-color 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        border-color: rgba(255,255,255,0.14);
    }
    div[data-testid="metric-container"] label {
        color: var(--text-secondary) !important;
        font-size: 0.78rem !important;
        font-weight: 500;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-size: 1.35rem !important;
        font-weight: 600;
    }
    /* delta verde */
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] svg { display: none; }
    div[data-testid="stMetricDelta"] > div { font-size: 0.8rem !important; font-weight: 500; }

    /* ── Botões ── */
    .stButton > button {
        background: linear-gradient(135deg, #1A6EFF 0%, #0F4FCC 100%);
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        transition: opacity 0.2s, transform 0.1s;
    }
    .stButton > button:hover { opacity: 0.88; transform: translateY(-1px); }
    .stButton > button:active { transform: translateY(0); }

    /* ── Inputs / selects ── */
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stNumberInput > div > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }
    .stRadio > div { gap: 6px; }
    .stRadio label { color: var(--text-secondary) !important; }

    /* ── DataFrames ── */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        overflow: hidden;
    }
    [data-testid="stDataFrame"] th {
        background: var(--bg-surface) !important;
        color: var(--text-secondary) !important;
        font-size: 0.75rem !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stDataFrame"] td { color: var(--text-primary) !important; font-size: 0.875rem; }

    /* ── Divider ── */
    hr { border-color: var(--border) !important; margin: 1rem 0; }

    /* ── Alerts ── */
    .stAlert { border-radius: 8px !important; border: 1px solid var(--border) !important; }

    /* ── Caption / small text ── */
    .stCaptionContainer p, small { color: var(--text-muted) !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: #2A2A3C; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #3A3A50; }

    /* ── Mobile ── */
    @media (max-width: 640px) {
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
        .stPlotlyChart { height: 260px !important; }
        [data-testid="stDataFrame"] td { font-size: 0.75rem !important; }
        .main .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    }

    /* ── KPI badge custom ── */
    .kpi-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px 22px;
        display: flex;
        flex-direction: column;
        gap: 6px;
        transition: border-color 0.2s, transform 0.15s;
    }
    .kpi-card:hover { border-color: rgba(255,255,255,0.15); transform: translateY(-2px); }
    .kpi-label { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-muted); }
    .kpi-value { font-size: 1.45rem; font-weight: 700; color: var(--text-primary); line-height: 1.2; }
    .kpi-sub   { font-size: 0.8rem; font-weight: 500; margin-top: 2px; }
    .kpi-green { color: var(--green); }
    .kpi-red   { color: var(--red); }
    .kpi-amber { color: var(--amber); }
    .kpi-blue  { color: var(--blue); }

    /* ── Section header ── */
    .section-title {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.75rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid var(--border);
    }

    /* ── Player leader card ── */
    .leader-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 14px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 10px;
        transition: border-color 0.2s;
    }
    .leader-card:hover { border-color: rgba(255,255,255,0.15); }
    .leader-rank { font-size: 1.5rem; min-width: 32px; text-align: center; }
    .leader-name { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); }
    .leader-meta { font-size: 0.78rem; color: var(--text-secondary); margin-top: 1px; }
    .leader-score { font-size: 1.2rem; font-weight: 700; margin-left: auto; }

    /* ── Confronto card ── */
    .confronto-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    .confronto-time { font-size: 0.9rem; font-weight: 600; color: var(--text-primary); }
    .confronto-vs   { font-size: 0.75rem; color: var(--text-muted); font-weight: 500; letter-spacing: 0.06em; }
    .confronto-info { font-size: 0.75rem; color: var(--text-secondary); text-align: right; }

    /* ── Status badges ── */
    .badge {
        display: inline-block;
        padding: 2px 9px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .badge-green { background: var(--green-dim);  color: var(--green); }
    .badge-amber { background: var(--amber-dim);  color: var(--amber); }
    .badge-red   { background: var(--red-dim);    color: var(--red); }
    .badge-gray  { background: rgba(255,255,255,0.05); color: var(--text-muted); }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ══════════════════════════════════════════════════════════════
# 2. TEMA PLOTLY CUSTOMIZADO
# ══════════════════════════════════════════════════════════════
CARTOLA_COLORS = ["#00C48C","#4A9EFF","#F5A623","#FF5C5C","#B57BFF","#FF8A65","#26C6DA","#F06292"]

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", color="#9998A8", size=12),
    title_font=dict(color="#EEEDF0", size=15, family="Inter, system-ui, sans-serif"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)", tickfont=dict(color="#9998A8")),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)", tickfont=dict(color="#9998A8")),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.07)", borderwidth=1,
                font=dict(color="#9998A8"), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=0, r=0, t=36, b=0),
    hoverlabel=dict(bgcolor="#1A1A28", bordercolor="rgba(255,255,255,0.1)", font=dict(color="#EEEDF0")),
    colorway=CARTOLA_COLORS,
)

def apply_theme(fig, title=""):
    fig.update_layout(**PLOTLY_LAYOUT)
    if title:
        fig.update_layout(title_text=title)
    return fig

# ══════════════════════════════════════════════════════════════
# 3. COMPONENTES HTML REUTILIZÁVEIS
# ══════════════════════════════════════════════════════════════
def kpi_card(label: str, value: str, sub: str, color: str = "green") -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub kpi-{color}">{sub}</div>
    </div>
    """

def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)

def status_badge(status_txt: str) -> str:
    mapa = {
        "Provável":   ("badge-green", "✓ Provável"),
        "Dúvida":     ("badge-amber", "? Dúvida"),
        "Suspenso":   ("badge-red",   "✕ Suspenso"),
        "Contundido": ("badge-red",   "✕ Contundido"),
        "Nulo":       ("badge-red",   "✕ Nulo"),
    }
    cls, txt = mapa.get(status_txt, ("badge-gray", f"○ {status_txt}"))
    return f'<span class="badge {cls}">{txt}</span>'

# ══════════════════════════════════════════════════════════════
# 4. FUNÇÕES DE DADOS
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def pegar_status_atletas():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get("https://api.cartola.globo.com/atletas/mercado", headers=headers, timeout=10).json()
        mapa_status = {int(k): v['nome'] for k, v in res['status'].items()}
        return {a['atleta_id']: mapa_status.get(a['status_id'], 'Sem Status') for a in res['atletas']}
    except Exception:
        return {}

@st.cache_data(ttl=600)
def pegar_jogos_ao_vivo():
    try:
        headers     = {"User-Agent": "Mozilla/5.0"}
        mercado     = requests.get("https://api.cartola.globo.com/mercado/status", headers=headers, timeout=10).json()
        rodada_atual = mercado['rodada_atual']
        partidas    = requests.get("https://api.cartola.globo.com/partidas",  headers=headers, timeout=10).json()
        clubes      = requests.get("https://api.cartola.globo.com/clubes",    headers=headers, timeout=10).json()
        dict_clubes = {int(k): v['nome'] for k, v in clubes.items()}
        if not dict_clubes:
            mf = requests.get("https://api.cartola.globo.com/atletas/mercado", headers=headers, timeout=10).json()
            dict_clubes = {int(k): v['nome'] for k, v in mf['clubes'].items()}
        lista_jogos = []
        if 'partidas' in partidas:
            for p in partidas['partidas']:
                lista_jogos.append({
                    'Mandante':  dict_clubes.get(p['clube_casa_id'],      'Casa'),
                    'Visitante': dict_clubes.get(p['clube_visitante_id'], 'Fora'),
                    'Local':     p.get('local', '-'),
                    'Data':      f"{p.get('partida_data','')} {p.get('partida_hora','')}",
                })
        return pd.DataFrame(lista_jogos), rodada_atual
    except Exception:
        return pd.DataFrame(), 0

@st.cache_data(ttl=3600)
def pegar_tabela_brasileirao():
    try:
        url     = "https://www.espn.com.br/futebol/classificacao/_/liga/BRA.1/brazilian-serie-a"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept":     "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        res  = requests.get(url, headers=headers, timeout=15)
        dfs  = pd.read_html(io.StringIO(res.text))
        if len(dfs) >= 2:
            df_c     = pd.concat([dfs[0], dfs[1]], axis=1)
            col_nome = dfs[0].columns[0]
            df_c['Clube_Limpo'] = df_c[col_nome].astype(str).apply(lambda x: re.sub(r'^\d+[A-Z]{3}', '', x))
            tabela = []
            for idx, row in df_c.iterrows():
                tabela.append({
                    'Pos':       idx + 1,
                    'Clube':     row['Clube_Limpo'],
                    'Pts':       row.get('PTS', 0),
                    'J':         row.get('J',   0),
                    'V':         row.get('V',   0),
                    'E':         row.get('E',   0),
                    'D':         row.get('D',   0),
                    'SG':        row.get('SG',  0),
                    'Últimos 5': '-',
                })
            return pd.DataFrame(tabela)
    except Exception as e:
        st.warning(f"⚠️ Tabela ESPN indisponível: {e}")
    return pd.DataFrame()

def gerenciar_banco_dados() -> pd.DataFrame:
    nome_arquivo = "banco_de_dados_historico.csv"
    headers      = {"User-Agent": "Mozilla/5.0"}
    try:
        status        = requests.get("https://api.cartola.globo.com/mercado/status", headers=headers, timeout=10).json()
        rodada_atual  = status['rodada_atual']
        ultima_rodada = rodada_atual - 1 if status['status_mercado'] == 1 else rodada_atual
    except Exception as e:
        st.warning(f"⚠️ Não foi possível checar a rodada atual: {e}")
        return pd.DataFrame()

    if os.path.exists(nome_arquivo):
        try:
            df              = pd.read_csv(nome_arquivo, sep=';')
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
            mercado       = requests.get("https://api.cartola.globo.com/atletas/mercado", headers=headers, timeout=15).json()
            clubes        = {int(k): v['nome'] for k, v in mercado['clubes'].items()}
            posicoes      = {int(k): v['nome'] for k, v in mercado['posicoes'].items()}
            precos_atuais = {a['atleta_id']: a['preco_num'] for a in mercado['atletas']}
        except Exception:
            clubes, posicoes, precos_atuais = {}, {}, {}

        for r in range(ultima_no_banco + 1, ultima_rodada + 1):
            try:
                pontuados = requests.get(f"https://api.cartola.globo.com/atletas/pontuados/{r}", headers=headers, timeout=15).json()
                partidas  = requests.get(f"https://api.cartola.globo.com/partidas/{r}",          headers=headers, timeout=15).json()
                mapa_jogos = {}
                if partidas and 'partidas' in partidas:
                    for p in partidas['partidas']:
                        cid, vid = p['clube_casa_id'], p['clube_visitante_id']
                        local    = p.get('local', '-')
                        dt       = f"{p.get('partida_data','')} {p.get('partida_hora','')}"
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
                            'foto':         dados.get('foto','').replace('FORMATO','140x140'),
                            'clube_nome':   clubes.get(cid,'Outro'),
                            'posicao_nome': posicoes.get(dados['posicao_id'],'Outro'),
                            'pontos':       dados.get('pontuacao',0),
                            'preco':        preco,
                            'media':        dados.get('media',0),
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
    if c not in df.columns:
        df[c] = 0
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
    st.markdown('<div class="section-title">⚙️ Filtros Globais</div>', unsafe_allow_html=True)

    contagem_jogos = df.groupby('atleta_id')['rodada_id'].nunique()
    max_jogos      = int(contagem_jogos.max()) if not contagem_jogos.empty else 1
    min_jogos      = st.slider("🎮 Mínimo de jogos:", 1, max_jogos, 1)
    st.divider()

    st.markdown('<div class="section-title">🔍 Segmentação</div>', unsafe_allow_html=True)
    lista_clubes   = sorted(df['clube_nome'].astype(str).unique())
    lista_posicoes = sorted(df['posicao_nome'].astype(str).unique())
    sel_clube      = st.multiselect("🏟️ Clube", lista_clubes,   default=lista_clubes)
    sel_posicao    = st.multiselect("👕 Posição", lista_posicoes, default=lista_posicoes)
    st.divider()

    rodadas_disponiveis = sorted(df['rodada_id'].unique())
    n_rodadas_total     = len(rodadas_disponiveis)
    st.markdown(f'<div class="section-title">📊 {n_rodadas_total} Rodadas no banco</div>', unsafe_allow_html=True)
    st.caption(f"Rodadas: {rodadas_disponiveis[0]} a {rodadas_disponiveis[-1]}")

df_filtrado = df[(df['clube_nome'].isin(sel_clube)) & (df['posicao_nome'].isin(sel_posicao))]

agg_rules = {
    'rodada_id':'count', 'pontos':'mean', 'pontuacao_basica':'mean',
    'preco':'last', 'clube_nome':'last', 'posicao_nome':'last',
    'foto':'last', 'participacao_gol':'sum', 'finalizacoes':'sum', 'apelido':'last',
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
        mapa_confrontos[row['Mandante']]  = {'mando':'CASA', 'adv': row['Visitante']}
        mapa_confrontos[row['Visitante']] = {'mando':'FORA', 'adv': row['Mandante']}

mapa_pos_br = {}
if not df_tabela.empty:
    for _, row in df_tabela.iterrows():
        mapa_pos_br[row['Clube'].lower()] = row['Pos']

def obter_pos_tabela(nome_clube):
    if not mapa_pos_br:
        return 10
    clube_limpo = nome_clube.lower().strip()
    for nome_espn, pos in mapa_pos_br.items():
        if clube_limpo in nome_espn or nome_espn in clube_limpo:
            return pos
    return 10

df_agrupado['mando'] = df_agrupado['clube_nome'].apply(
    lambda c: mapa_confrontos[c]['mando'] if c in mapa_confrontos else 'Sem Jogo'
)

media_cedida_adv     = df.groupby(['adversario', 'posicao_nome'])['pontos'].mean().to_dict()
media_feita_time     = df.groupby(['clube_nome',  'posicao_nome'])['pontos'].mean().to_dict()
media_posicao_global = df.groupby('posicao_nome')['pontos'].mean().to_dict()

def calcular_indice_pro(row):
    clube = row['clube_nome'];  pos = row['posicao_nome']
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
    st.markdown('<p style="color:#9998A8;margin-top:-8px;font-size:0.9rem;">Dashboard de Inteligência Esportiva · Temporada 2026</p>', unsafe_allow_html=True)
with col_h2:
    rodada_label = f"Rodadas 1–{rodadas_disponiveis[-1]}" if rodadas_disponiveis else "–"
    st.markdown(f'<div style="text-align:right;padding-top:18px;color:#9998A8;font-size:0.85rem;">{rodada_label}</div>', unsafe_allow_html=True)

st.markdown('<div style="height:4px;background:linear-gradient(90deg,#00C48C,#4A9EFF,#F5A623);border-radius:2px;margin:8px 0 20px 0;"></div>', unsafe_allow_html=True)

if not df_agrupado.empty:
    top_pro    = df_agrupado.sort_values('indice_pro',       ascending=False).iloc[0]
    top_reg    = df_agrupado.sort_values('media_basica',     ascending=False).iloc[0]
    artilheiro = df_agrupado.sort_values('participacao_gol', ascending=False).iloc[0]
    ladrao     = df_agrupado.sort_values('DS',               ascending=False).iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(kpi_card("🤖 Top Índice PRO",   top_pro['apelido'],    f"Score: {top_pro['indice_pro']:.2f}",         "green"), unsafe_allow_html=True)
    k2.markdown(kpi_card("💎 Rei Regularidade", top_reg['apelido'],    f"Básica: {top_reg['media_basica']:.1f} pts",  "blue"),  unsafe_allow_html=True)
    k3.markdown(kpi_card("🔥 Mais Decisivo",    artilheiro['apelido'], f"{int(artilheiro['participacao_gol'])} G+A",  "amber"), unsafe_allow_html=True)
    k4.markdown(kpi_card("🛑 Ladrão de Bolas",  ladrao['apelido'],     f"{int(ladrao['DS'])} Desarmes",               "red"),   unsafe_allow_html=True)

st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

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
        section_title("CONFRONTOS DA RODADA")
        if not df_proximos.empty:
            for _, row in df_proximos.iterrows():
                st.markdown(f"""
                <div class="confronto-card">
                    <div class="confronto-time">{row['Mandante']}</div>
                    <div class="confronto-vs">VS</div>
                    <div class="confronto-time">{row['Visitante']}</div>
                    <div class="confronto-info">{row.get('Local','-')}<br><span style="color:#5A5A72;">{row.get('Data','')}</span></div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Mercado fechado ou sem jogos previstos.")

    with aba_tab:
        section_title("CLASSIFICAÇÃO SÉRIE A 2026")
        if not df_tabela.empty:
            max_pts = df_tabela['Pts'].max() or 100
            st.dataframe(
                df_tabela,
                column_config={
                    "Pos": st.column_config.NumberColumn("Pos", width="small"),
                    "Pts": st.column_config.ProgressColumn("Pontos", format="%d", min_value=0, max_value=max_pts),
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
            section_title("PARÂMETROS")
            orc      = st.number_input("💰 Orçamento (C$)", value=100.0)
            esq      = st.selectbox("📐 Esquema Tático", ["4-3-3","3-4-3","3-5-2"])
            criterio = st.radio("🎯 Critério de seleção:", ["Índice PRO ✨","Média Geral","Pontuação Básica"])
            col_crit = 'indice_pro'
            if "Média Geral" in criterio:    col_crit = 'media_geral'
            elif "Pontuação Básica" in criterio: col_crit = 'media_basica'
            gerar_botao = st.button("⚡ Gerar Time Inteligente", use_container_width=True)

        with col_res:
            if gerar_botao:
                meta = {
                    "4-3-3": {'Goleiro':1,'Lateral':2,'Zagueiro':2,'Meia':3,'Atacante':3,'Técnico':1},
                    "3-5-2": {'Goleiro':1,'Lateral':0,'Zagueiro':3,'Meia':5,'Atacante':2,'Técnico':1},
                    "3-4-3": {'Goleiro':1,'Lateral':0,'Zagueiro':3,'Meia':4,'Atacante':3,'Técnico':1},
                }.get(esq)

                pool = df_agrupado[df_agrupado['status_txt'] == 'Provável'].sort_values(col_crit, ascending=False)
                if pool.empty:
                    st.warning("⚠️ Nenhum Provável encontrado. Usando todos os atletas.")
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
                                (pool['preco'] < jogador_caro['preco']) &
                                (~pool['atleta_id'].isin(df_time['atleta_id']))
                            ]
                            if not candidatos.empty:
                                substituto  = candidatos.iloc[0]
                                df_time     = df_time.drop(idx)
                                df_time     = pd.concat([df_time, substituto.to_frame().T])
                                custo_total = df_time['preco'].sum()
                                troca_feita = True
                                break
                        if not troca_feita:
                            break
                        loops += 1

                    ordem_tatica = ['Goleiro','Lateral','Zagueiro','Meia','Atacante','Técnico']
                    df_time['posicao_nome'] = pd.Categorical(df_time['posicao_nome'], categories=ordem_tatica, ordered=True)
                    df_time = df_time.sort_values('posicao_nome')

                    if custo_total > orc:
                        st.error("❌ Não foi possível montar um time dentro do orçamento.")
                    else:
                        c_score, c_custo, c_jogos = st.columns(3)
                        c_score.metric("Score Projetado",  f"{df_time[col_crit].sum():.1f}")
                        c_custo.metric("Custo Total",       f"C$ {custo_total:.2f}",  f"Saldo: C$ {orc - custo_total:.2f}")
                        c_jogos.metric("Atletas Escalados", f"{len(df_time)}")
                        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

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

    with st_vs:
        section_title("COMPARATIVO MANO A MANO")
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
                r=v1+[v1[0]], theta=cats+[cats[0]], fill='toself', name=f"{p1}",
                line=dict(color="#00C48C", width=2), fillcolor="rgba(0,196,140,0.15)",
            ))
            fig.add_trace(go.Scatterpolar(
                r=v2+[v2[0]], theta=cats+[cats[0]], fill='toself', name=f"{p2}",
                line=dict(color="#4A9EFF", width=2), fillcolor="rgba(74,158,255,0.15)",
            ))
            fig.update_layout(
                **{k: v for k, v in PLOTLY_LAYOUT.items() if k != 'xaxis' and k != 'yaxis'},
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#5A5A72")),
                    angularaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#9998A8")),
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

            col_s1, col_s2 = st.columns(2)
            for d, col, cor in [(d1, col_s1, "#00C48C"), (d2, col_s2, "#4A9EFF")]:
                with col:
                    st.markdown(f"""
                    <div style="background:#1A1A28;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:16px;">
                        <div style="font-size:0.7rem;color:#5A5A72;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;">{d['posicao_nome']} · {d['clube_nome']}</div>
                        <div style="font-size:1.2rem;font-weight:700;color:#EEEDF0;">{d['apelido']}</div>
                        <div style="font-size:0.8rem;color:{cor};margin-top:4px;">Índice PRO: {d['indice_pro']:.2f}</div>
                        <div style="font-size:0.8rem;color:#9998A8;margin-top:2px;">Média: {d['media_geral']:.1f} pts · C$ {d['preco']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TAB 3 — TÁTICA
# ──────────────────────────────────────────────────────────────
with tab3:
    hm1, hm2, hm3 = st.tabs(["🛡️ Defesa","⚔️ Ataque","🏰 Mando de Campo"])

    with hm1:
        section_title("FRAGILIDADE DEFENSIVA — PONTOS CEDIDOS POR POSIÇÃO")
        heat = df.groupby(['adversario','posicao_nome'])['pontos'].mean().reset_index()
        if not heat.empty:
            piv = heat.pivot(index='adversario', columns='posicao_nome', values='pontos').fillna(0)
            fig = px.imshow(piv, text_auto=".1f", color_continuous_scale="Reds", aspect="auto")
            apply_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

    with hm2:
        section_title("PODER OFENSIVO — PONTOS FEITOS POR POSIÇÃO")
        heat_atk = df.groupby(['clube_nome','posicao_nome'])['pontos'].mean().reset_index()
        if not heat_atk.empty:
            piv2 = heat_atk.pivot(index='clube_nome', columns='posicao_nome', values='pontos').fillna(0)
            fig2 = px.imshow(piv2, text_auto=".1f", color_continuous_scale="Greens", aspect="auto")
            apply_theme(fig2)
            st.plotly_chart(fig2, use_container_width=True)

    with hm3:
        section_title("DESEMPENHO: CASA × FORA")
        stats_mando = df.groupby(['clube_nome','mando'])['pontos'].mean().reset_index()
        fig_pts = px.bar(
            stats_mando, x='clube_nome', y='pontos', color='mando', barmode='group',
            labels={'pontos':'Média de Pontos','clube_nome':'Time'},
            color_discrete_map={'CASA':'#00C48C','FORA':'#4A9EFF'},
        )
        fig_pts.update_layout(**PLOTLY_LAYOUT)
        fig_pts.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_pts, use_container_width=True)

        st.divider()
        col_scout = st.selectbox("Scout para comparar:", ["Gols (G)","Desarmes (DS)","Finalizações (FF+FD)"])
        mapa_sc   = {"Gols (G)":"G","Desarmes (DS)":"DS","Finalizações (FF+FD)":"finalizacoes"}
        sc_col    = mapa_sc[col_scout]
        stats_sc  = df.groupby(['clube_nome','mando'])[sc_col].sum().reset_index()
        fig_sc    = px.bar(
            stats_sc, x='clube_nome', y=sc_col, color='mando', barmode='group',
            labels={sc_col:f'Total {col_scout}','clube_nome':'Time'},
            color_discrete_map={'CASA':'#F5A623','FORA':'#B57BFF'},
        )
        fig_sc.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-45)
        st.plotly_chart(fig_sc, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 4 — MERCADO
# ──────────────────────────────────────────────────────────────
with tab4:
    section_title("INTELIGÊNCIA DE MERCADO")

    # Sub-filtro rápido por status
    col_sf1, col_sf2, col_sf3 = st.columns([2, 2, 1])
    with col_sf1:
        busca_mercado = st.text_input("🔍 Buscar atleta", placeholder="Nome...", label_visibility="collapsed")
    with col_sf2:
        filtro_status_mercado = st.multiselect(
            "Status", options=['✅ Provável','❓ Dúvida','🚑 Contundido','🟥 Suspenso','⚪ Sem Status'],
            default=['✅ Provável','❓ Dúvida','⚪ Sem Status'], label_visibility="collapsed",
        )
    with col_sf3:
        ordenar_por = st.selectbox("Ordenar", ["Índice PRO","Média","C$","C/B"], label_visibility="collapsed")

    mapa_ord = {"Índice PRO":"indice_pro","Média":"media_geral","C$":"preco","C/B":"custo_beneficio"}
    df_merc  = df_agrupado.copy()
    if busca_mercado:
        df_merc = df_merc[df_merc['apelido'].str.contains(busca_mercado, case=False, na=False)]
    if filtro_status_mercado:
        df_merc = df_merc[df_merc['status'].isin(filtro_status_mercado)]

    df_merc = df_merc.sort_values(mapa_ord[ordenar_por], ascending=False)

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
            "media_basica":    st.column_config.ProgressColumn("Pont. Básica", format="%.2f", min_value=-5, max_value=15),
        },
        use_container_width=True, hide_index=True, height=600,
    )

    st.divider()
    section_title("DISTRIBUIÇÃO DE PREÇO VS ÍNDICE PRO")
    if not df_merc.empty:
        fig_sc2 = px.scatter(
            df_merc, x='preco', y='indice_pro', color='posicao_nome',
            size='media_geral', hover_name='apelido',
            hover_data={'clube_nome':True,'media_geral':':.1f','preco':':.2f','indice_pro':':.2f'},
            labels={'preco':'Preço (C$)','indice_pro':'Índice PRO','posicao_nome':'Posição'},
            color_discrete_sequence=CARTOLA_COLORS,
        )
        fig_sc2.update_layout(**PLOTLY_LAYOUT)
        fig_sc2.update_traces(marker=dict(opacity=0.8, line=dict(width=0.5, color='rgba(255,255,255,0.1)')))
        st.plotly_chart(fig_sc2, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 5 — DESTAQUES
# ──────────────────────────────────────────────────────────────
with tab5:
    section_title("LÍDERES POR FUNDAMENTO")

    def render_leader_card(titulo, col_sort, col_container, sufixo="", cor="#00C48C"):
        df_valid = df_agrupado[df_agrupado[col_sort] > 0]
        if df_valid.empty:
            return
        lider = df_valid.sort_values(col_sort, ascending=False).iloc[0]
        val   = int(lider[col_sort])
        with col_container:
            c_img, c_txt = st.columns([1, 2])
            c_img.image(lider['foto'], width=68)
            c_txt.markdown(f'<div style="font-size:0.7rem;color:#5A5A72;text-transform:uppercase;letter-spacing:0.06em;">{titulo}</div>', unsafe_allow_html=True)
            c_txt.markdown(f'<div style="font-size:1rem;font-weight:600;color:#EEEDF0;">{lider["apelido"]}</div>', unsafe_allow_html=True)
            c_txt.markdown(f'<div style="font-size:1.3rem;font-weight:700;color:{cor};">{val} {sufixo}</div>', unsafe_allow_html=True)
            c_txt.caption(f'{lider["clube_nome"]} · {lider["posicao_nome"]}')
            st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    render_leader_card("Participação (G+A)", "participacao_gol", r1, cor="#00C48C")
    render_leader_card("Artilheiro",         "G",                r2, "Gols",   "#F5A623")
    render_leader_card("Garçom",             "A",                r3, "Assis",  "#4A9EFF")
    render_leader_card("Finalizações",       "finalizacoes",     r4, "Chutes", "#B57BFF")

    st.divider()
    r5, r6, r7, r8 = st.columns(4)
    render_leader_card("Desarmes",        "DS", r5, cor="#FF5C5C")
    render_leader_card("Faltas Sofridas", "FS", r6, cor="#F5A623")
    render_leader_card("Defesas (Gol)",   "DE", r7, cor="#4A9EFF")
    render_leader_card("Paredão (SG)",    "SG", r8, "Jgs", "#00C48C")

    st.divider()
    section_title("DISTRIBUIÇÃO DE PONTUAÇÃO POR POSIÇÃO")
    if not df_agrupado.empty:
        fig_box = px.box(
            df_agrupado, x='posicao_nome', y='media_geral',
            color='posicao_nome', points="outliers",
            labels={'posicao_nome':'Posição','media_geral':'Média de Pontos'},
            color_discrete_sequence=CARTOLA_COLORS,
        )
        fig_box.update_layout(**PLOTLY_LAYOUT)
        fig_box.update_traces(marker=dict(opacity=0.7))
        st.plotly_chart(fig_box, use_container_width=True)
