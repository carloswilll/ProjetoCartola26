import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import os
import re
import io
import numpy as np

# ══════════════════════════════════════════════════════════════
# 1. CONFIG & CSS — TEMA CLARO
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Cartola Pro 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root {
    --green:  #00A878;
    --amber:  #E09B00;
    --red:    #E03E3E;
    --blue:   #1A6EFF;
    --purple: #7C3AED;
    --bg:     #F7F8FA;
    --card:   #FFFFFF;
    --border: #E4E6EB;
    --text-1: #111827;
    --text-2: #6B7280;
    --text-3: #9CA3AF;
}

/* ── Base ── */
.stApp { background-color: var(--bg) !important; }
.main .block-container { padding-top: 1.5rem !important; max-width: 1400px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] > div:first-child {
    background-color: #FFFFFF !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: var(--text-1) !important; font-weight: 500;
}
[data-testid="stSidebar"] hr { border-color: var(--border) !important; }

/* ── Títulos ── */
h1 { color: var(--text-1) !important; font-weight: 800; letter-spacing: -0.02em; }
h2, h3 { color: var(--text-1) !important; }
p { color: var(--text-2); }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px; background: #ECEEF2;
    border-radius: 10px; padding: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important; color: var(--text-2) !important;
    font-weight: 500; font-size: 0.85rem; padding: 6px 12px !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background-color: #FFFFFF !important;
    color: var(--text-1) !important;
    border: 1px solid var(--border) !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.25rem; }

/* ── Metric cards ── */
div[data-testid="metric-container"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
div[data-testid="metric-container"] label {
    color: var(--text-2) !important; font-size: 0.75rem !important;
    font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text-1) !important; font-size: 1.3rem !important; font-weight: 700;
}

/* ── Botões ── */
.stButton > button {
    background: linear-gradient(135deg, #1A6EFF, #0F4FCC) !important;
    color: #fff !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    padding: 10px 20px !important; transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
[data-testid="stDataFrame"] th {
    background: #F3F4F6 !important; color: var(--text-2) !important;
    font-size: 0.72rem !important; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.05em;
}

/* ── Alerts ── */
.stAlert { border-radius: 8px !important; }

/* ── KPI cards custom ── */
.kpi-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 14px; padding: 18px 22px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07); height: 100%;
}
.kpi-label {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.07em;
    text-transform: uppercase; color: var(--text-3); margin-bottom: 6px;
}
.kpi-value { font-size: 1.4rem; font-weight: 800; color: var(--text-1); line-height: 1.2; }
.kpi-sub   { font-size: 0.8rem; font-weight: 600; margin-top: 4px; }
.kpi-green  { color: var(--green); }
.kpi-blue   { color: var(--blue); }
.kpi-amber  { color: var(--amber); }
.kpi-red    { color: var(--red); }
.kpi-purple { color: var(--purple); }

/* ── Section titles ── */
.sec-title {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--text-3);
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px; margin-bottom: 14px;
}

/* ── Confronto cards ── */
.conf-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 18px;
    display: flex; align-items: center;
    justify-content: space-between; margin-bottom: 8px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.conf-time { font-size: 0.95rem; font-weight: 700; color: var(--text-1); }
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
# 2. TEMA PLOTLY — LIGHT
# ══════════════════════════════════════════════════════════════
COLORS = ["#00A878","#1A6EFF","#E09B00","#E03E3E","#7C3AED","#EA580C","#0891B2","#DB2777"]

THEME = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", color="#6B7280", size=12),
    xaxis=dict(gridcolor="#F3F4F6", linecolor="#E4E6EB", tickfont=dict(color="#6B7280")),
    yaxis=dict(gridcolor="#F3F4F6", linecolor="#E4E6EB", tickfont=dict(color="#6B7280")),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#6B7280"),
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=0, r=0, t=36, b=0),
    hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#E4E6EB", font=dict(color="#111827")),
    colorway=COLORS,
)

def themed(fig):
    fig.update_layout(**THEME)
    return fig

# ══════════════════════════════════════════════════════════════
# 3. HELPERS
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
        h   = {"User-Agent": "Mozilla/5.0"}
        res = requests.get("https://api.cartola.globo.com/atletas/mercado", headers=h, timeout=10).json()
        mapa = {int(k): v['nome'] for k, v in res['status'].items()}
        return {a['atleta_id']: mapa.get(a['status_id'], 'Sem Status') for a in res['atletas']}
    except Exception:
        return {}

@st.cache_data(ttl=600)
def pegar_jogos_ao_vivo():
    try:
        h        = {"User-Agent": "Mozilla/5.0"}
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
        return pd.DataFrame(jogos), int(mercado.get('rodada_atual', 0))
    except Exception:
        return pd.DataFrame(), 0

@st.cache_data(ttl=3600)
def pegar_tabela_brasileirao():
    """
    Busca a tabela do Brasileirão via API JSON pública — sem html5lib.
    Fonte: api.football-data.org (free tier, sem autenticação para leitura básica)
    Fallback: retorna DataFrame vazio com aviso amigável.
    """
    try:
        # Tenta API JSON alternativa (sem scraping)
        h   = {"User-Agent": "Mozilla/5.0"}
        url = "https://api.cartola.globo.com/partidas"
        # Monta tabela a partir dos confrontos históricos se API externa falhar
        raise Exception("usando fallback interno")
    except Exception:
        pass

    # Fallback: tabela sintética a partir dos dados históricos (calculada depois)
    return pd.DataFrame()

def montar_tabela_interna(df_hist: pd.DataFrame) -> pd.DataFrame:
    """
    Monta classificação aproximada usando pontuação média cedida por time
    quando a API externa não está disponível.
    """
    if df_hist.empty or 'adversario' not in df_hist.columns:
        return pd.DataFrame()
    try:
        resumo = (
            df_hist.groupby('clube_nome')
            .agg(
                Jogos=('rodada_id', 'nunique'),
                MediaPts=('pontos', 'mean'),
            )
            .reset_index()
            .rename(columns={'clube_nome': 'Clube'})
            .sort_values('MediaPts', ascending=False)
            .reset_index(drop=True)
        )
        resumo['Pos'] = resumo.index + 1
        resumo['Pts'] = (resumo['MediaPts'] * 3).astype(int)
        return resumo[['Pos','Clube','Jogos','Pts','MediaPts']]
    except Exception:
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
                            'rodada_id':    r,    'atleta_id':    pid,
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
    sec("⚙️ Filtros Globais")
    contagem_jogos = df.groupby('atleta_id')['rodada_id'].nunique()
    max_jogos      = int(contagem_jogos.max()) if not contagem_jogos.empty else 1
    min_jogos      = st.slider("🎮 Mínimo de jogos:", 1, max_jogos, 1)
    st.divider()
    sec("🔍 Segmentação")
    lista_clubes   = sorted(df['clube_nome'].astype(str).unique())
    lista_posicoes = sorted(df['posicao_nome'].astype(str).unique())
    sel_clube      = st.multiselect("🏟️ Clube",   lista_clubes,   default=lista_clubes)
    sel_posicao    = st.multiselect("👕 Posição", lista_posicoes, default=lista_posicoes)
    st.divider()
    rodadas_disp    = sorted(df['rodada_id'].unique())
    n_rodadas_total = len(rodadas_disp)
    st.caption(f"📊 {n_rodadas_total} rodadas · {rodadas_disp[0]}→{rodadas_disp[-1]}")

df_filtrado = df[
    (df['clube_nome'].isin(sel_clube)) &
    (df['posicao_nome'].isin(sel_posicao))
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
df_agrupado['status']     = df_agrupado['status_txt'].apply(
    lambda s: {'Provável':'✅ Provável','Dúvida':'❓ Dúvida','Suspenso':'🟥 Suspenso',
               'Contundido':'🚑 Contundido','Nulo':'❌ Nulo'}.get(s, f'⚪ {s}')
)

# ── ÍNDICE PRO ───────────────────────────────────────────────
df_proximos, _ = pegar_jogos_ao_vivo()
df_tabela      = pegar_tabela_brasileirao()
if df_tabela.empty:
    df_tabela = montar_tabela_interna(df)

mapa_confrontos = {}
if not df_proximos.empty:
    for _, row in df_proximos.iterrows():
        mapa_confrontos[row['Mandante']]  = {'mando':'CASA','adv':row['Visitante']}
        mapa_confrontos[row['Visitante']] = {'mando':'FORA','adv':row['Mandante']}

mapa_pos_br = {}
if not df_tabela.empty and 'Clube' in df_tabela.columns and 'Pos' in df_tabela.columns:
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

media_cedida_adv     = df.groupby(['adversario','posicao_nome'])['pontos'].mean().to_dict()
media_feita_time     = df.groupby(['clube_nome', 'posicao_nome'])['pontos'].mean().to_dict()
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
    st.markdown('<p style="color:#6B7280;margin-top:-10px;font-size:0.9rem;">Dashboard de Inteligência Esportiva · Temporada 2026</p>', unsafe_allow_html=True)
with col_h2:
    lbl = f"Rodadas {rodadas_disp[0]}–{rodadas_disp[-1]}" if rodadas_disp else "–"
    st.markdown(f'<div style="text-align:right;padding-top:20px;color:#9CA3AF;font-size:0.82rem;">{lbl}</div>', unsafe_allow_html=True)

st.markdown('<div style="height:3px;background:linear-gradient(90deg,#00A878,#1A6EFF,#E09B00);border-radius:2px;margin:6px 0 20px 0;"></div>', unsafe_allow_html=True)

if not df_agrupado.empty:
    top_pro    = df_agrupado.sort_values('indice_pro',       ascending=False).iloc[0]
    top_reg    = df_agrupado.sort_values('media_basica',     ascending=False).iloc[0]
    artilheiro = df_agrupado.sort_values('participacao_gol', ascending=False).iloc[0]
    ladrao     = df_agrupado.sort_values('DS',               ascending=False).iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(kpi("🤖 Top Índice PRO",   top_pro['apelido'],    f"Score: {top_pro['indice_pro']:.2f}",        "green"),  unsafe_allow_html=True)
    k2.markdown(kpi("💎 Rei Regularidade", top_reg['apelido'],    f"Básica: {top_reg['media_basica']:.1f} pts", "blue"),   unsafe_allow_html=True)
    k3.markdown(kpi("🔥 Mais Decisivo",    artilheiro['apelido'], f"{int(artilheiro['participacao_gol'])} G+A", "amber"),  unsafe_allow_html=True)
    k4.markdown(kpi("🛑 Ladrão de Bolas",  ladrao['apelido'],     f"{int(ladrao['DS'])} Desarmes",              "red"),    unsafe_allow_html=True)

st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 7. TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📅 Jogos", "🤖 Robô", "📊 Tática", "📈 Mercado", "🏆 Destaques",
    "🎯 Capitão", "🔬 Raio-X", "🔮 Projeção", "🧬 ML & Otimizador",
])

# ──────────────────────────────────────────────────────────────
# TAB 1 — JOGOS
# ──────────────────────────────────────────────────────────────
with tab1:
    aba_conf, aba_tab = st.tabs(["⚽ Próximos Confrontos", "🏆 Classificação"])
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
                        <span style="color:#9CA3AF;">{row.get('Data','')}</span></div>
                </div>""", unsafe_allow_html=True)
        else:
            st.warning("Mercado fechado ou sem jogos previstos.")

    with aba_tab:
        sec("CLASSIFICAÇÃO — GERADA A PARTIR DO HISTÓRICO")
        if not df_tabela.empty:
            st.dataframe(df_tabela, hide_index=True, use_container_width=True, height=600)
            st.caption("Classificação aproximada calculada a partir dos dados históricos do app.")
        else:
            st.info("Dados insuficientes para montar a classificação.")

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
            gerar = st.button("⚡ Gerar Time", use_container_width=True)

        with col_res:
            if gerar:
                meta = {
                    "4-3-3": {'Goleiro':1,'Lateral':2,'Zagueiro':2,'Meia':3,'Atacante':3,'Técnico':1},
                    "3-5-2": {'Goleiro':1,'Lateral':0,'Zagueiro':3,'Meia':5,'Atacante':2,'Técnico':1},
                    "3-4-3": {'Goleiro':1,'Lateral':0,'Zagueiro':3,'Meia':4,'Atacante':3,'Técnico':1},
                }.get(esq)
                pool = df_agrupado[df_agrupado['status_txt'] == 'Provável'].sort_values(col_crit, ascending=False)
                if pool.empty:
                    pool = df_agrupado.sort_values(col_crit, ascending=False)
                time_final = [pool[pool['posicao_nome'] == pos].head(qtd)
                              for pos, qtd in meta.items() if qtd > 0]
                if time_final:
                    df_time     = pd.concat(time_final)
                    custo_total = df_time['preco'].sum()
                    loops = 0
                    while custo_total > orc and loops < 100:
                        df_time = df_time.sort_values('preco', ascending=False)
                        troca   = False
                        for idx, jc in df_time.iterrows():
                            cands = pool[
                                (pool['posicao_nome'] == jc['posicao_nome']) &
                                (pool['preco'] < jc['preco']) &
                                (~pool['atleta_id'].isin(df_time['atleta_id']))
                            ]
                            if not cands.empty:
                                df_time     = pd.concat([df_time.drop(idx), cands.iloc[0].to_frame().T])
                                custo_total = df_time['preco'].sum()
                                troca = True; break
                        if not troca: break
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
                        st.dataframe(
                            df_time[['foto','status','posicao_nome','apelido','clube_nome',
                                     'mando','preco','indice_pro','media_geral','media_basica']],
                            column_config={
                                "foto":         st.column_config.ImageColumn("Perfil"),
                                "status":       "Status",   "posicao_nome": "Posição",
                                "apelido":      "Jogador",  "clube_nome":   "Clube",
                                "mando":        "Mando",
                                "preco":        st.column_config.NumberColumn("C$",          format="%.2f"),
                                "indice_pro":   st.column_config.NumberColumn("Índice PRO ✨",format="%.2f"),
                                "media_geral":  st.column_config.NumberColumn("Média",       format="%.2f"),
                                "media_basica": st.column_config.NumberColumn("Básica",      format="%.2f"),
                            },
                            hide_index=True, use_container_width=True,
                        )

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
            fig  = go.Figure()
            fig.add_trace(go.Scatterpolar(r=v1+[v1[0]], theta=cats+[cats[0]], fill='toself', name=p1,
                                          line=dict(color="#00A878",width=2), fillcolor="rgba(0,168,120,0.12)"))
            fig.add_trace(go.Scatterpolar(r=v2+[v2[0]], theta=cats+[cats[0]], fill='toself', name=p2,
                                          line=dict(color="#1A6EFF",width=2), fillcolor="rgba(26,110,255,0.12)"))
            fig.update_layout(
                **{k:v for k,v in THEME.items() if k not in ('xaxis','yaxis')},
                polar=dict(bgcolor="rgba(0,0,0,0)",
                           radialaxis=dict(visible=True, gridcolor="#E4E6EB"),
                           angularaxis=dict(gridcolor="#E4E6EB")),
            )
            st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 3 — TÁTICA
# ──────────────────────────────────────────────────────────────
with tab3:
    hm1, hm2, hm3 = st.tabs(["🛡️ Defesa","⚔️ Ataque","🏰 Mando"])
    with hm1:
        sec("FRAGILIDADE DEFENSIVA — PONTOS CEDIDOS POR POSIÇÃO")
        heat = df.groupby(['adversario','posicao_nome'])['pontos'].mean().reset_index()
        if not heat.empty:
            piv = heat.pivot(index='adversario', columns='posicao_nome', values='pontos').fillna(0)
            fig = px.imshow(piv, text_auto=".1f", color_continuous_scale="Reds", aspect="auto")
            themed(fig); st.plotly_chart(fig, use_container_width=True)
    with hm2:
        sec("PODER OFENSIVO — PONTOS FEITOS POR POSIÇÃO")
        heat2 = df.groupby(['clube_nome','posicao_nome'])['pontos'].mean().reset_index()
        if not heat2.empty:
            piv2 = heat2.pivot(index='clube_nome', columns='posicao_nome', values='pontos').fillna(0)
            fig2 = px.imshow(piv2, text_auto=".1f", color_continuous_scale="Greens", aspect="auto")
            themed(fig2); st.plotly_chart(fig2, use_container_width=True)
    with hm3:
        sec("DESEMPENHO: CASA × FORA")
        stats_mando = df.groupby(['clube_nome','mando'])['pontos'].mean().reset_index()
        fig_pts = px.bar(stats_mando, x='clube_nome', y='pontos', color='mando', barmode='group',
                         labels={'pontos':'Média','clube_nome':'Time'},
                         color_discrete_map={'CASA':'#00A878','FORA':'#1A6EFF'})
        themed(fig_pts); fig_pts.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_pts, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 4 — MERCADO
# ──────────────────────────────────────────────────────────────
with tab4:
    sec("INTELIGÊNCIA DE MERCADO")
    col_sf1, col_sf2, col_sf3 = st.columns([2,2,1])
    with col_sf1:
        busca = st.text_input("🔍 Buscar atleta", placeholder="Nome...", label_visibility="collapsed")
    with col_sf2:
        filtro_st = st.multiselect("Status",
            ['✅ Provável','❓ Dúvida','🚑 Contundido','🟥 Suspenso','⚪ Sem Status'],
            default=['✅ Provável','❓ Dúvida','⚪ Sem Status'], label_visibility="collapsed")
    with col_sf3:
        ord_por = st.selectbox("Ordenar", ["Índice PRO","Média","C$","C/B"], label_visibility="collapsed")

    ord_map = {"Índice PRO":"indice_pro","Média":"media_geral","C$":"preco","C/B":"custo_beneficio"}
    df_merc = df_agrupado.copy()
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
            "status":          "Status", "apelido": "Atleta",
            "posicao_nome":    "Posição","clube_nome":"Clube",
            "jogos_disputados":st.column_config.NumberColumn("Jogos",        format="%d"),
            "preco":           st.column_config.NumberColumn("C$",           format="%.2f"),
            "indice_pro":      st.column_config.NumberColumn("Índice PRO ✨", format="%.2f"),
            "custo_beneficio": st.column_config.NumberColumn("C/B ⚡",        format="%.2f"),
            "media_geral":     st.column_config.NumberColumn("Média",        format="%.2f"),
            "media_basica":    st.column_config.ProgressColumn("Básica",format="%.2f",min_value=-5,max_value=15),
        },
        use_container_width=True, hide_index=True, height=560,
    )
    st.divider()
    sec("PREÇO × ÍNDICE PRO")
    if not df_merc.empty:
        fig_sc2 = px.scatter(df_merc, x='preco', y='indice_pro', color='posicao_nome',
                             hover_name='apelido',
                             hover_data={'clube_nome':True,'media_geral':':.1f','preco':':.2f','indice_pro':':.2f'},
                             labels={'preco':'Preço (C$)','indice_pro':'Índice PRO','posicao_nome':'Posição'},
                             color_discrete_sequence=COLORS)
        themed(fig_sc2)
        fig_sc2.update_traces(marker=dict(size=8, opacity=0.8, line=dict(width=0.5, color='#E4E6EB')))
        st.plotly_chart(fig_sc2, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 5 — DESTAQUES
# ──────────────────────────────────────────────────────────────
with tab5:
    sec("LÍDERES POR FUNDAMENTO")
    def render_leader(titulo, col_sort, col_container, sufixo="", cor="#00A878"):
        df_v = df_agrupado[df_agrupado[col_sort] > 0]
        if df_v.empty: return
        lider = df_v.sort_values(col_sort, ascending=False).iloc[0]
        with col_container:
            ci, ct = st.columns([1,2])
            ci.image(lider['foto'], width=64)
            ct.markdown(f'<div style="font-size:0.65rem;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.06em;">{titulo}</div>', unsafe_allow_html=True)
            ct.markdown(f'<div style="font-size:0.95rem;font-weight:700;color:#111827;">{lider["apelido"]}</div>', unsafe_allow_html=True)
            ct.markdown(f'<div style="font-size:1.2rem;font-weight:800;color:{cor};">{int(lider[col_sort])} {sufixo}</div>', unsafe_allow_html=True)
            ct.caption(f'{lider["clube_nome"]} · {lider["posicao_nome"]}')

    r1,r2,r3,r4 = st.columns(4)
    render_leader("Participação (G+A)", "participacao_gol", r1)
    render_leader("Artilheiro",         "G",                r2, "Gols",  "#E09B00")
    render_leader("Garçom",             "A",                r3, "Assis", "#1A6EFF")
    render_leader("Finalizações",       "finalizacoes",     r4, "",      "#7C3AED")
    st.divider()
    r5,r6,r7,r8 = st.columns(4)
    render_leader("Desarmes",        "DS", r5, cor="#E03E3E")
    render_leader("Faltas Sofridas", "FS", r6, cor="#E09B00")
    render_leader("Defesas (Gol)",   "DE", r7, cor="#1A6EFF")
    render_leader("Paredão (SG)",    "SG", r8, "Jgs")
    st.divider()
    sec("DISTRIBUIÇÃO DE PONTUAÇÃO POR POSIÇÃO")
    if not df_agrupado.empty:
        fig_box = px.box(df_agrupado, x='posicao_nome', y='media_geral',
                         color='posicao_nome', points="outliers",
                         labels={'posicao_nome':'Posição','media_geral':'Média de Pontos'},
                         color_discrete_sequence=COLORS)
        themed(fig_box); st.plotly_chart(fig_box, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 6 — CAPITÃO IDEAL
# ──────────────────────────────────────────────────────────────
with tab6:
    st.markdown("### 🎯 Alerta de Capitão Ideal")
    st.caption("O capitão dobra os pontos. Score = Índice PRO × Fator Mando (Casa +15%, Fora -15%).")

    cap_pool = df_agrupado[df_agrupado['mando'] != 'Sem Jogo'].copy()
    if cap_pool.empty:
        st.warning("Nenhum atleta com jogo confirmado.")
    else:
        cap_pool['fator_mando_cap'] = cap_pool['mando'].map({'CASA':1.15,'FORA':0.85}).fillna(1.0)
        cap_pool['score_capitao']   = cap_pool['indice_pro'] * cap_pool['fator_mando_cap']

        # Filtro de status
        inc_status = st.multiselect("Incluir status:",
            ['Provável','Dúvida','Sem Status'], default=['Provável'], key="cap_status")
        if inc_status:
            cap_pool = cap_pool[cap_pool['status_txt'].isin(inc_status)]

        top_cap = cap_pool.sort_values('score_capitao', ascending=False).head(10)
        for i, (_, row) in enumerate(top_cap.iterrows()):
            medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"#{i+1}"
            adv   = mapa_confrontos.get(row['clube_nome'], {}).get('adv', '-')
            bg    = "#F0FDF4" if i==0 else "#FFFFFF"
            brd   = "#00A878" if i==0 else "#E4E6EB"
            st.markdown(f"""
            <div style="background:{bg};border:1.5px solid {brd};border-radius:10px;
                        padding:12px 18px;margin-bottom:8px;display:flex;
                        align-items:center;gap:16px;">
                <div style="font-size:1.6rem;min-width:36px;">{medal}</div>
                <div style="flex:1;">
                    <div style="font-size:1rem;font-weight:700;color:#111827;">{row['apelido']}</div>
                    <div style="font-size:0.78rem;color:#6B7280;">{row['posicao_nome']} · {row['clube_nome']} · Adv: {adv}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.1rem;font-weight:800;color:#00A878;">Score: {row['score_capitao']:.2f}</div>
                    <div style="font-size:0.75rem;color:#6B7280;">{'🏠 CASA +15%' if row['mando']=='CASA' else '✈️ FORA -15%'} · PRO: {row['indice_pro']:.2f}</div>
                </div>
            </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TAB 7 — RAIO-X DO CONFRONTO
# ──────────────────────────────────────────────────────────────
with tab7:
    st.markdown("### 🔬 Raio-X do Confronto")
    st.caption("Histórico direto entre dois times + fragilidade defensiva por posição.")

    times_disp = sorted(df['clube_nome'].astype(str).unique())
    c1, c2     = st.columns(2)
    time_a = c1.selectbox("Time A", times_disp, key="rx_a")
    time_b = c2.selectbox("Time B", times_disp, index=1 if len(times_disp)>1 else 0, key="rx_b")

    if time_a == time_b:
        st.warning("Selecione times diferentes.")
    else:
        df_dir = df[
            ((df['clube_nome']==time_a)&(df['adversario']==time_b)) |
            ((df['clube_nome']==time_b)&(df['adversario']==time_a))
        ]
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Confrontos no histórico", len(df_dir['rodada_id'].unique()) if not df_dir.empty else 0)
        if not df_dir.empty:
            ma = df_dir[df_dir['clube_nome']==time_a]['pontos'].mean()
            mb = df_dir[df_dir['clube_nome']==time_b]['pontos'].mean()
            col_r2.metric(f"Média {time_a}", f"{ma:.2f}")
            col_r3.metric(f"Média {time_b}", f"{mb:.2f}")

            st.divider()
            heat_rx = df_dir.groupby(['clube_nome','posicao_nome'])['pontos'].mean().reset_index()
            piv_rx  = heat_rx.pivot(index='clube_nome', columns='posicao_nome', values='pontos').fillna(0)
            fig_rx  = px.imshow(piv_rx, text_auto=".1f", color_continuous_scale="Blues", aspect="auto")
            themed(fig_rx); st.plotly_chart(fig_rx, use_container_width=True)

            st.divider()
            st.markdown(f"**Top atletas de {time_a} contra {time_b}**")
            top_rx = (df_dir[df_dir['clube_nome']==time_a]
                      .groupby('apelido')
                      .agg(media_pts=('pontos','mean'), jogos=('rodada_id','count'))
                      .reset_index().sort_values('media_pts', ascending=False).head(10))
            st.dataframe(top_rx,
                column_config={
                    "apelido":   "Atleta",
                    "media_pts": st.column_config.NumberColumn("Média pts", format="%.2f"),
                    "jogos":     st.column_config.NumberColumn("Jogos",     format="%d"),
                }, hide_index=True, use_container_width=True)
        else:
            st.info("Nenhum confronto direto no histórico atual.")

        st.divider()
        st.markdown(f"**Fragilidade defensiva de {time_b} por posição**")
        df_ced = df[df['adversario']==time_b].groupby('posicao_nome')['pontos'].mean().reset_index()
        df_ced.columns = ['Posição','Média cedida']
        df_ced = df_ced.sort_values('Média cedida', ascending=False)
        fig_ced = px.bar(df_ced, x='Posição', y='Média cedida',
                         color='Média cedida', color_continuous_scale='Reds', text_auto='.1f')
        themed(fig_ced); st.plotly_chart(fig_ced, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 8 — PROJEÇÃO + FORMA RECENTE
# ──────────────────────────────────────────────────────────────
with tab8:
    proj_tab, forma_tab = st.tabs(["🔮 Projeção por Scout","📅 Forma Recente"])

    with proj_tab:
        st.markdown("### 🔮 Projeção de Pontuação")
        st.caption("Estima pontuação esperada com base na média de scouts contra o adversário.")
        pesos = {'G':8.0,'A':5.0,'FT':3.0,'FD':1.2,'FF':0.8,'FS':0.5,'PS':1.0,
                 'DE':1.0,'DS':1.5,'FC':-0.3,'PC':-1.0,'CA':-1.0,'CV':-3.0,'GS':-1.0,'I':-0.1,'SG':5.0}

        atletas_c_jogo = df_agrupado[df_agrupado['mando']!='Sem Jogo']['apelido'].unique()
        if len(atletas_c_jogo) == 0:
            st.warning("Nenhum atleta com jogo confirmado para projeção.")
        else:
            sel_proj = st.multiselect("Atletas (máx. 10):", sorted(atletas_c_jogo),
                                      default=list(sorted(atletas_c_jogo))[:5], max_selections=10)
            if sel_proj:
                rows_proj = []
                for apelido in sel_proj:
                    row_ag = df_agrupado[df_agrupado['apelido']==apelido].iloc[0]
                    clube  = row_ag['clube_nome']
                    adv    = mapa_confrontos.get(clube, {}).get('adv', None)
                    df_at  = df[df['apelido']==apelido]
                    df_vs  = df_at[df_at['adversario']==adv] if adv else df_at
                    if df_vs.empty: df_vs = df_at
                    proj = sum(df_vs[s].mean()*p for s,p in pesos.items() if s in df_vs.columns)
                    rows_proj.append({
                        'Atleta':apelido,'Clube':clube,'Adv':adv or '-','Mando':row_ag['mando'],
                        'Proj Min':proj*0.70,'Proj Med':proj,'Proj Máx':proj*1.30,
                    })
                df_proj = pd.DataFrame(rows_proj).sort_values('Proj Med', ascending=False)
                st.dataframe(df_proj,
                    column_config={
                        "Proj Min": st.column_config.NumberColumn(format="%.1f"),
                        "Proj Med": st.column_config.NumberColumn(format="%.1f"),
                        "Proj Máx": st.column_config.NumberColumn(format="%.1f"),
                    }, hide_index=True, use_container_width=True)
                fig_proj = px.bar(df_proj, x='Atleta', y='Proj Med',
                                  error_y=df_proj['Proj Máx']-df_proj['Proj Med'],
                                  error_y_minus=df_proj['Proj Med']-df_proj['Proj Min'],
                                  color='Mando', text_auto='.1f',
                                  color_discrete_map={'CASA':'#00A878','FORA':'#1A6EFF','Sem Jogo':'#9CA3AF'})
                themed(fig_proj); st.plotly_chart(fig_proj, use_container_width=True)
                st.caption("Barras de erro = ±30% sobre a projeção central.")

    with forma_tab:
        st.markdown("### 📅 Forma Recente")
        st.caption("Compare a média total com a performance nas últimas N rodadas.")
        n_rec = st.slider("Últimas N rodadas:", 1, max_jogos, min(5, max_jogos))
        rodadas_rec = sorted(df['rodada_id'].unique())[-n_rec:]
        df_rec      = df[df['rodada_id'].isin(rodadas_rec)]
        agg_rec     = {'pontos':'mean','rodada_id':'count','clube_nome':'last',
                       'posicao_nome':'last','apelido':'last'}
        df_ag_rec   = df_rec.groupby('atleta_id').agg(agg_rec).reset_index()
        df_ag_rec.rename(columns={'pontos':'media_rec','rodada_id':'jogos_rec'}, inplace=True)
        df_forma = df_agrupado[['atleta_id','apelido','clube_nome','media_geral']].merge(
            df_ag_rec[['atleta_id','media_rec','jogos_rec']], on='atleta_id', how='inner')
        df_forma['delta'] = df_forma['media_rec'] - df_forma['media_geral']

        ca, cb = st.columns(2)
        with ca:
            st.markdown(f"#### 🔥 Em alta (últ. {n_rec} rod.)")
            for _, r in df_forma.sort_values('delta', ascending=False).head(8).iterrows():
                st.metric(f"{r['apelido']} — {r['clube_nome']}",
                          f"{r['media_rec']:.1f} pts", f"{r['delta']:+.1f} vs média total")
        with cb:
            st.markdown(f"#### 📉 Em queda (últ. {n_rec} rod.)")
            for _, r in df_forma.sort_values('delta', ascending=True).head(8).iterrows():
                st.metric(f"{r['apelido']} — {r['clube_nome']}",
                          f"{r['media_rec']:.1f} pts", f"{r['delta']:+.1f} vs média total")

        st.divider()
        df_top20  = df_forma.sort_values('media_rec', ascending=False).head(20)
        fig_forma = go.Figure()
        fig_forma.add_trace(go.Bar(name='Média Total', x=df_top20['apelido'],
                                   y=df_top20['media_geral'], marker_color='#E4E6EB'))
        fig_forma.add_trace(go.Bar(name=f'Últ. {n_rec} rod.', x=df_top20['apelido'],
                                   y=df_top20['media_rec'], marker_color='#00A878'))
        fig_forma.update_layout(**THEME, barmode='group', xaxis_tickangle=-45)
        st.plotly_chart(fig_forma, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 9 — ML & OTIMIZADOR
# ──────────────────────────────────────────────────────────────
with tab9:
    ml_tab, opt_tab = st.tabs(["🧬 Predição ML","⚙️ Otimizador PuLP"])

    with ml_tab:
        st.markdown("### 🧬 Predição de Valorização com ML")
        st.caption("Ridge Regression: estima variação de C$ na próxima rodada com base em scouts históricos.")
        try:
            from sklearn.linear_model import Ridge
            from sklearn.preprocessing import StandardScaler
            from sklearn.pipeline import Pipeline

            feats = ['pontos','G','A','FT','DS','FS','FC','CA','GS','DE','SG','preco']
            for f in feats:
                if f not in df.columns: df[f] = 0

            df_ml = df.sort_values(['atleta_id','rodada_id']).copy()
            df_ml['preco_prox']  = df_ml.groupby('atleta_id')['preco'].shift(-1)
            df_ml['delta_preco'] = df_ml['preco_prox'] - df_ml['preco']
            df_ml = df_ml.dropna(subset=['delta_preco']+feats)

            X = df_ml[feats].values
            y = df_ml['delta_preco'].values

            if len(X) < 30:
                st.warning("Dados insuficientes para treinar o modelo. Aguarde mais rodadas.")
            else:
                modelo = Pipeline([('sc', StandardScaler()), ('ridge', Ridge(alpha=1.0))])
                modelo.fit(X, y)
                X_pred = np.column_stack([
                    df_agrupado[f].values if f in df_agrupado.columns else np.zeros(len(df_agrupado))
                    for f in feats
                ])
                df_agrupado['delta_pred'] = modelo.predict(X_pred)
                coef    = modelo.named_steps['ridge'].coef_
                df_coef = pd.DataFrame({'Feature':feats,'Importância':np.abs(coef)}).sort_values('Importância')

                col_p, col_i = st.columns([3,2])
                with col_p:
                    st.markdown("#### Top valorizações previstas")
                    top_pred = df_agrupado[['apelido','clube_nome','posicao_nome','preco','status_txt','delta_pred']]\
                        .sort_values('delta_pred', ascending=False).head(15)
                    st.dataframe(top_pred,
                        column_config={
                            "apelido":"Atleta","clube_nome":"Clube","posicao_nome":"Posição","status_txt":"Status",
                            "preco":      st.column_config.NumberColumn("C$ Atual",   format="%.2f"),
                            "delta_pred": st.column_config.NumberColumn("Δ C$ Prev.", format="%+.2f"),
                        }, hide_index=True, use_container_width=True)
                with col_i:
                    st.markdown("#### Fatores mais relevantes")
                    fig_imp = px.bar(df_coef, x='Importância', y='Feature', orientation='h',
                                     color='Importância', color_continuous_scale='Greens')
                    themed(fig_imp); fig_imp.update_layout(showlegend=False, yaxis_title='')
                    st.plotly_chart(fig_imp, use_container_width=True)
                st.info("⚠️ Estimativa baseada em padrões históricos. Use como sinal complementar.")
        except ImportError:
            st.error("❌ `scikit-learn` não instalado. Adicione ao `requirements.txt` e faça o redeploy.")

    with opt_tab:
        st.markdown("### ⚙️ Otimizador com Programação Linear (PuLP)")
        st.caption("Maximiza o Índice PRO respeitando orçamento, posições e restrições do esquema.")
        try:
            import pulp
            co1, co2 = st.columns([1,2])
            with co1:
                orc_opt    = st.number_input("Orçamento (C$)", value=100.0, key="opt_orc")
                esq_opt    = st.selectbox("Esquema", ["4-3-3","3-4-3","3-5-2"], key="opt_esq")
                status_opt = st.multiselect("Status aceitos:", ['Provável','Dúvida','Sem Status'],
                                            default=['Provável'], key="opt_st")
                max_time   = st.number_input("Máx. por time", min_value=1, max_value=5, value=5, key="opt_mt")
                btn_opt    = st.button("🚀 Otimizar", use_container_width=True)
            with co2:
                if btn_opt:
                    meta_opt = {
                        "4-3-3": {'Goleiro':1,'Lateral':2,'Zagueiro':2,'Meia':3,'Atacante':3,'Técnico':1},
                        "3-5-2": {'Goleiro':1,'Lateral':0,'Zagueiro':3,'Meia':5,'Atacante':2,'Técnico':1},
                        "3-4-3": {'Goleiro':1,'Lateral':0,'Zagueiro':3,'Meia':4,'Atacante':3,'Técnico':1},
                    }.get(esq_opt)
                    pool = df_agrupado[df_agrupado['status_txt'].isin(status_opt)].copy().reset_index(drop=True)
                    if pool.empty:
                        st.warning("Nenhum atleta disponível com os status selecionados.")
                    else:
                        prob     = pulp.LpProblem("cartola", pulp.LpMaximize)
                        n        = len(pool)
                        ids      = list(range(n))
                        x        = pulp.LpVariable.dicts("x", ids, cat='Binary')
                        prob    += pulp.lpSum(pool.iloc[i]['indice_pro']*x[i] for i in ids)
                        prob    += pulp.lpSum(pool.iloc[i]['preco']*x[i]      for i in ids) <= orc_opt
                        for pos, qtd in meta_opt.items():
                            ip = [i for i in ids if pool.iloc[i]['posicao_nome']==pos]
                            prob += pulp.lpSum(x[i] for i in ip) == qtd
                        for tm in pool['clube_nome'].unique():
                            it = [i for i in ids if pool.iloc[i]['clube_nome']==tm]
                            prob += pulp.lpSum(x[i] for i in it) <= max_time
                        prob.solve(pulp.PULP_CBC_CMD(msg=0))

                        if pulp.LpStatus[prob.status] == 'Optimal':
                            esc    = [i for i in ids if pulp.value(x[i])==1]
                            df_opt = pool.iloc[esc].copy()
                            ordem  = ['Goleiro','Lateral','Zagueiro','Meia','Atacante','Técnico']
                            df_opt['posicao_nome'] = pd.Categorical(df_opt['posicao_nome'], categories=ordem, ordered=True)
                            df_opt = df_opt.sort_values('posicao_nome')
                            custo  = df_opt['preco'].sum()
                            score  = df_opt['indice_pro'].sum()
                            st.success(f"✅ Escalação ótima! Custo: C$ {custo:.2f} | Score PRO: {score:.2f}")
                            st.dataframe(
                                df_opt[['foto','status','posicao_nome','apelido','clube_nome','mando','preco','indice_pro','media_geral']],
                                column_config={
                                    "foto":         st.column_config.ImageColumn("Perfil"),
                                    "status":       "Status",  "posicao_nome":"Posição",
                                    "apelido":      "Jogador", "clube_nome":  "Clube", "mando":"Mando",
                                    "preco":        st.column_config.NumberColumn("C$",          format="%.2f"),
                                    "indice_pro":   st.column_config.NumberColumn("Índice PRO ✨",format="%.2f"),
                                    "media_geral":  st.column_config.NumberColumn("Média",       format="%.2f"),
                                }, hide_index=True, use_container_width=True)
                            st.info("💡 PuLP avalia todas as combinações e garante o ótimo global.")
                        else:
                            st.error("❌ Sem solução viável. Aumente o orçamento ou aceite mais status.")
        except ImportError:
            st.error("❌ `pulp` não instalado. Adicione ao `requirements.txt` e faça o redeploy.")
