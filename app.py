import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import os
import io
import logging
import numpy as np
from datetime import datetime

# ══════════════════════════════════════════════════════════════
# 0. LOGGING ESTRUTURADO
# ══════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s",
)
log = logging.getLogger("cartola_pro")

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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

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
.stApp { background-color: var(--bg) !important; font-family: 'DM Sans', system-ui, sans-serif; }
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
h1 { color: var(--text-1) !important; font-weight: 800; letter-spacing: -0.02em; font-family: 'DM Sans', sans-serif; }
h2, h3 { color: var(--text-1) !important; font-family: 'DM Sans', sans-serif; }
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

/* ── Status badge ── */
.badge {
    display: inline-block; padding: 2px 8px; border-radius: 99px;
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.04em;
}
.badge-green  { background:#D1FAE5; color:#065F46; }
.badge-amber  { background:#FEF3C7; color:#92400E; }
.badge-red    { background:#FEE2E2; color:#991B1B; }
.badge-gray   { background:#F3F4F6; color:#374151; }

/* ── Price trend chip ── */
.trend-up   { color: var(--green); font-weight: 700; }
.trend-down { color: var(--red);   font-weight: 700; }

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
    font=dict(family="DM Sans, system-ui, sans-serif", color="#6B7280", size=12),
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

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CartolaPro/2026)"}

def _get_json(url: str, timeout: int = 10) -> dict | None:
    """GET com tratamento de erro estruturado. Retorna None em falha."""
    try:
        res = requests.get(url, headers=_HEADERS, timeout=timeout)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.Timeout:
        log.warning("Timeout ao acessar %s", url)
    except requests.exceptions.HTTPError as e:
        log.warning("HTTP %s ao acessar %s", e.response.status_code, url)
    except requests.exceptions.ConnectionError:
        log.warning("Falha de conexão ao acessar %s", url)
    except Exception as e:
        log.error("Erro inesperado ao acessar %s: %s", url, e)
    return None

# ══════════════════════════════════════════════════════════════
# 4. SUPABASE — INTEGRAÇÃO OPCIONAL
# ══════════════════════════════════════════════════════════════
USAR_SUPABASE = bool(
    st.secrets.get("SUPABASE_URL") and st.secrets.get("SUPABASE_KEY")
    if hasattr(st, "secrets") else False
)

@st.cache_resource
def conectar_supabase():
    """Conecta ao Supabase se credenciais disponíveis. Retorna None caso contrário."""
    if not USAR_SUPABASE:
        return None
    try:
        from supabase import create_client
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        cliente = create_client(url, key)
        log.info("Supabase conectado com sucesso.")
        return cliente
    except ImportError:
        log.warning("Biblioteca 'supabase' não instalada. Usando CSV local.")
    except Exception as e:
        log.error("Falha ao conectar Supabase: %s", e)
    return None

def _carregar_historico_supabase(cliente, ultima_rodada_banco: int) -> pd.DataFrame:
    """
    Carrega histórico completo do Supabase com paginação automática.
    O free tier retorna no máximo 1000 linhas por request — sem paginação
    o app pensa que rodadas já salvas estão faltando e tenta reinserí-las (erro 409).
    """
    try:
        todos = []
        tamanho_pagina = 1000
        offset = 0
        while True:
            res = (
                cliente.table("historico_cartola")
                .select("*")
                .order("rodada_id")
                .range(offset, offset + tamanho_pagina - 1)
                .execute()
            )
            if not res.data:
                break
            todos.extend(res.data)
            log.info("Supabase: página offset=%d → %d registros.", offset, len(res.data))
            if len(res.data) < tamanho_pagina:
                break  # última página
            offset += tamanho_pagina
        if todos:
            df = pd.DataFrame(todos)
            log.info("Supabase: %d registros totais carregados (até rodada %d).",
                     len(df), df["rodada_id"].max())
            return df
    except Exception as e:
        log.error("Erro ao carregar histórico do Supabase: %s", e)
    return pd.DataFrame()

def _salvar_novas_rodadas_supabase(cliente, df_novo: pd.DataFrame) -> bool:
    """Insere novas linhas no Supabase em lotes de 500."""
    if df_novo.empty:
        return True
    try:
        registros = df_novo.replace({np.nan: None}).to_dict(orient="records")
        # Converte int64 para int nativo
        for rec in registros:
            for k, v in rec.items():
                if isinstance(v, (np.integer,)):
                    rec[k] = int(v)
                elif isinstance(v, (np.floating,)):
                    rec[k] = float(v)
        tamanho_lote = 500
        for i in range(0, len(registros), tamanho_lote):
            lote = registros[i:i + tamanho_lote]
            cliente.table("historico_cartola").upsert(lote).execute()
        log.info("Supabase: %d registros salvos.", len(registros))
        return True
    except Exception as e:
        log.error("Erro ao salvar no Supabase: %s", e)
        return False

# ══════════════════════════════════════════════════════════════
# 5. FUNÇÕES DE DADOS — API CARTOLA
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def pegar_status_atletas() -> dict:
    dados = _get_json("https://api.cartola.globo.com/atletas/mercado")
    if not dados:
        return {}
    try:
        mapa = {int(k): v["nome"] for k, v in dados["status"].items()}
        return {a["atleta_id"]: mapa.get(a["status_id"], "Sem Status") for a in dados["atletas"]}
    except (KeyError, TypeError) as e:
        log.error("Estrutura inesperada em pegar_status_atletas: %s", e)
        return {}

@st.cache_data(ttl=600)
def pegar_jogos_ao_vivo() -> tuple[pd.DataFrame, int]:
    mercado  = _get_json("https://api.cartola.globo.com/mercado/status")
    partidas = _get_json("https://api.cartola.globo.com/partidas")
    clubes   = _get_json("https://api.cartola.globo.com/clubes")

    if not mercado:
        return pd.DataFrame(), 0

    rodada_atual = int(mercado.get("rodada_atual", 0))

    # Monta dicionário de clubes
    dc: dict[int, str] = {}
    if clubes:
        dc = {int(k): v["nome"] for k, v in clubes.items()}
    if not dc:
        mf = _get_json("https://api.cartola.globo.com/atletas/mercado")
        if mf:
            dc = {int(k): v["nome"] for k, v in mf.get("clubes", {}).items()}

    jogos = []
    if partidas and "partidas" in partidas:
        for p in partidas["partidas"]:
            try:
                jogos.append({
                    "Mandante":  dc.get(p["clube_casa_id"], "Casa"),
                    "Visitante": dc.get(p["clube_visitante_id"], "Fora"),
                    "Local":     p.get("local", "-"),
                    "Data":      f"{p.get('partida_data','')} {p.get('partida_hora','')}".strip(),
                })
            except KeyError as e:
                log.warning("Campo ausente em partida: %s", e)

    return pd.DataFrame(jogos), rodada_atual

@st.cache_data(ttl=3600)
def pegar_tabela_brasileirao_api() -> pd.DataFrame:
    """
    Tenta buscar classificação do Brasileirão via API football-data.org (free tier).
    Requer FOOTBALL_DATA_KEY no st.secrets para funcionar.
    Retorna DataFrame vazio se não disponível.
    """
    try:
        api_key = st.secrets.get("FOOTBALL_DATA_KEY", "") if hasattr(st, "secrets") else ""
        if not api_key:
            return pd.DataFrame()
        h = {**_HEADERS, "X-Auth-Token": api_key}
        res = requests.get(
            "https://api.football-data.org/v4/competitions/BSA/standings",
            headers=h, timeout=10
        )
        res.raise_for_status()
        dados = res.json()
        tabela = dados["standings"][0]["table"]
        return pd.DataFrame([{
            "Pos":   t["position"],
            "Clube": t["team"]["name"],
            "PJ":    t["playedGames"],
            "Pts":   t["points"],
            "V":     t["won"],
            "E":     t["draw"],
            "D":     t["lost"],
            "GP":    t["goalsFor"],
            "GC":    t["goalsAgainst"],
            "SG":    t["goalDifference"],
        } for t in tabela])
    except Exception as e:
        log.info("API football-data indisponível: %s. Usando fallback interno.", e)
        return pd.DataFrame()

def montar_tabela_interna(df_hist: pd.DataFrame) -> pd.DataFrame:
    """Classificação aproximada a partir do histórico local de scouts."""
    if df_hist.empty or "adversario" not in df_hist.columns:
        return pd.DataFrame()
    try:
        resumo = (
            df_hist.groupby("clube_nome")
            .agg(Jogos=("rodada_id", "nunique"), MediaPts=("pontos", "mean"))
            .reset_index()
            .rename(columns={"clube_nome": "Clube"})
            .sort_values("MediaPts", ascending=False)
            .reset_index(drop=True)
        )
        resumo["Pos"]      = resumo.index + 1
        resumo["Pts"]      = (resumo["MediaPts"] * 3).astype(int)
        resumo["MediaPts"] = resumo["MediaPts"].round(2)
        return resumo[["Pos", "Clube", "Jogos", "Pts", "MediaPts"]]
    except Exception as e:
        log.error("Erro em montar_tabela_interna: %s", e)
        return pd.DataFrame()

# ══════════════════════════════════════════════════════════════
# 6. GERENCIAMENTO DO BANCO DE DADOS (CSV + SUPABASE)
# ══════════════════════════════════════════════════════════════
NOME_CSV = "banco_de_dados_historico.csv"

def _buscar_rodadas_api(de: int, ate: int, clubes: dict, posicoes: dict, precos_atuais: dict) -> list[dict]:
    """Baixa rodadas [de, ate] da API do Cartola. Retorna lista de registros."""
    novos = []
    for r in range(de, ate + 1):
        try:
            pontuados = _get_json(f"https://api.cartola.globo.com/atletas/pontuados/{r}", timeout=15)
            partidas  = _get_json(f"https://api.cartola.globo.com/partidas/{r}", timeout=15)

            if not pontuados or "atletas" not in pontuados:
                log.warning("Rodada %d: sem dados de pontuados.", r)
                continue

            mapa_jogos: dict[int, dict] = {}
            if partidas and "partidas" in partidas:
                for p in partidas["partidas"]:
                    cid, vid = p["clube_casa_id"], p["clube_visitante_id"]
                    local    = p.get("local", "-")
                    dt       = f"{p.get('partida_data','')} {p.get('partida_hora','')}".strip()
                    mapa_jogos[cid] = {"mando": "CASA", "adversario": clubes.get(vid, "Visitante"), "local": local, "data": dt}
                    mapa_jogos[vid] = {"mando": "FORA", "adversario": clubes.get(cid, "Mandante"),  "local": local, "data": dt}

            for pid_str, dados in pontuados["atletas"].items():
                pid  = int(pid_str)
                cid  = dados.get("clube_id", 0)
                jogo = mapa_jogos.get(cid, {"mando": "-", "adversario": "-", "local": "-", "data": "-"})
                preco = dados.get("preco_num") or dados.get("preco") or precos_atuais.get(pid, 0)
                row   = {
                    "rodada_id":    r,
                    "atleta_id":    pid,
                    "apelido":      dados.get("apelido", f"Jog {pid}"),
                    "foto":         dados.get("foto", "").replace("FORMATO", "140x140"),
                    "clube_nome":   clubes.get(cid, "Outro"),
                    "posicao_nome": posicoes.get(dados.get("posicao_id", 0), "Outro"),
                    "pontos":       dados.get("pontuacao", 0),
                    "preco":        preco,
                    "media":        dados.get("media", 0),
                    "mando":        jogo["mando"],
                    "adversario":   jogo["adversario"],
                    "estadio":      jogo["local"],
                    "data_jogo":    jogo["data"],
                }
                row.update(dados.get("scout") or {})
                novos.append(row)

            log.info("Rodada %d: %d atletas processados.", r, len(pontuados["atletas"]))

        except Exception as e:
            log.error("Erro inesperado na rodada %d: %s", r, e)
            st.toast(f"⚠️ Erro na rodada {r}: {e}", icon="⚠️")

    return novos

def gerenciar_banco_dados() -> pd.DataFrame:
    """
    Gerencia o banco de dados de histórico.
    - Se Supabase disponível: usa como fonte primária.
    - Caso contrário: CSV local (efêmero no Streamlit Cloud).
    """
    supabase = conectar_supabase()

    # ── 1. Status da API ──────────────────────────────────────
    status = _get_json("https://api.cartola.globo.com/mercado/status")
    if not status:
        st.warning("⚠️ API do Cartola indisponível. Carregando dados locais se existentes.")
        if os.path.exists(NOME_CSV):
            try:
                return pd.read_csv(NOME_CSV, sep=";", encoding="utf-8-sig")
            except Exception as e:
                log.error("Erro ao ler CSV de fallback: %s", e)
        return pd.DataFrame()

    rodada_atual  = int(status.get("rodada_atual", 0))
    mercado_aberto = status.get("status_mercado") == 1  # 1 = fechado, 4 = aberto (verificar)
    ultima_rodada = rodada_atual - 1 if mercado_aberto else rodada_atual

    # ── 2. Carregar banco existente ───────────────────────────
    if supabase:
        df = _carregar_historico_supabase(supabase, 0)
    elif os.path.exists(NOME_CSV):
        try:
            df = pd.read_csv(NOME_CSV, sep=";", encoding="utf-8-sig")
        except Exception as e:
            log.error("Erro ao ler CSV: %s", e)
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    ultima_no_banco = int(df["rodada_id"].max()) if not df.empty else 0

    if ultima_rodada <= ultima_no_banco:
        log.info("Banco atualizado (rodada %d). Nada a baixar.", ultima_no_banco)
        return df

    # ── 3. Baixar novas rodadas ───────────────────────────────
    container = st.empty()
    container.info(f"🔄 Baixando rodadas {ultima_no_banco + 1} → {ultima_rodada}...")

    mercado_dados = _get_json("https://api.cartola.globo.com/atletas/mercado", timeout=15)
    clubes, posicoes, precos_atuais = {}, {}, {}
    if mercado_dados:
        try:
            clubes        = {int(k): v["nome"] for k, v in mercado_dados.get("clubes", {}).items()}
            posicoes      = {int(k): v["nome"] for k, v in mercado_dados.get("posicoes", {}).items()}
            precos_atuais = {a["atleta_id"]: a["preco_num"] for a in mercado_dados.get("atletas", [])}
        except (KeyError, TypeError) as e:
            log.warning("Estrutura inesperada no mercado: %s", e)

    novos = _buscar_rodadas_api(ultima_no_banco + 1, ultima_rodada, clubes, posicoes, precos_atuais)

    if novos:
        df_novo  = pd.DataFrame(novos).fillna(0)
        df_final = pd.concat([df, df_novo], ignore_index=True)

        if supabase:
            _salvar_novas_rodadas_supabase(supabase, df_novo)
        else:
            try:
                df_final.to_csv(NOME_CSV, index=False, sep=";", encoding="utf-8-sig")
                log.info("CSV salvo com %d registros.", len(df_final))
            except Exception as e:
                log.error("Erro ao salvar CSV: %s", e)

        container.empty()
        return df_final

    container.empty()
    return df

# ══════════════════════════════════════════════════════════════
# 7. PROCESSAMENTO PRINCIPAL
# ══════════════════════════════════════════════════════════════
df = gerenciar_banco_dados()

if df.empty:
    st.title("⚽ Cartola Pro 2026")
    st.warning("Aguardando dados da primeira rodada ou API indisponível.")
    st.stop()

# ── Garantir colunas ──────────────────────────────────────────
for col in ["estadio", "data_jogo", "mando", "adversario", "foto", "apelido", "clube_nome", "posicao_nome"]:
    if col not in df.columns:
        df[col] = "-"

SCOUTS = ["G","A","FT","FD","FF","FS","PS","I","PP","DS","SG","DE","DP","GS","FC","PC","CA","CV","GC"]
for c in SCOUTS:
    if c not in df.columns:
        df[c] = 0
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

# ── Colunas derivadas (vetorizadas) ───────────────────────────
df["pontuacao_basica"] = (
    df["DS"]*1.5 + df["FS"]*0.5 + df["FF"]*0.8 + df["FD"]*1.2 + df["FT"]*3.0
    + df["DE"]*1.0 + df["PS"]*1.0 + df["FC"]*-0.3 + df["PC"]*-1.0
    + df["CA"]*-1.0 + df["CV"]*-3.0 + df["GS"]*-1.0 + df["I"]*-0.1
)
df["participacao_gol"] = df["G"] + df["A"]
df["finalizacoes"]     = df["FD"] + df["FF"] + df["FT"]

# ══════════════════════════════════════════════════════════════
# 8. SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚽ Cartola Pro 2026")
    st.caption(f"🔄 Fonte: {'☁️ Supabase' if USAR_SUPABASE else '📄 CSV local'}")
    sec("⚙️ Filtros Globais")
    contagem_jogos = df.groupby("atleta_id")["rodada_id"].nunique()
    max_jogos      = int(contagem_jogos.max()) if not contagem_jogos.empty else 1
    min_jogos      = st.slider("🎮 Mínimo de jogos:", 1, max_jogos, 1)
    st.divider()
    sec("🔍 Segmentação")
    lista_clubes   = sorted(df["clube_nome"].astype(str).unique())
    lista_posicoes = sorted(df["posicao_nome"].astype(str).unique())
    sel_clube      = st.multiselect("🏟️ Clube",   lista_clubes,   default=lista_clubes)
    sel_posicao    = st.multiselect("👕 Posição", lista_posicoes, default=lista_posicoes)
    st.divider()
    rodadas_disp    = sorted(df["rodada_id"].unique())
    n_rodadas_total = len(rodadas_disp)
    st.caption(f"📊 {n_rodadas_total} rodadas · {rodadas_disp[0]}→{rodadas_disp[-1]}")

# ══════════════════════════════════════════════════════════════
# 9. PROCESSAMENTO AGREGADO + ÍNDICE PRO (VETORIZADO)
# ══════════════════════════════════════════════════════════════
df_filtrado = df[
    df["clube_nome"].isin(sel_clube) &
    df["posicao_nome"].isin(sel_posicao)
]

agg_rules = {
    "rodada_id": "count", "pontos": "mean", "pontuacao_basica": "mean", "preco": "last",
    "clube_nome": "last", "posicao_nome": "last", "foto": "last",
    "participacao_gol": "sum", "finalizacoes": "sum", "apelido": "last",
}
for s in SCOUTS:
    agg_rules[s] = "sum"

df_agrupado = df_filtrado.groupby("atleta_id").agg(agg_rules).reset_index()
df_agrupado.rename(columns={
    "pontos": "media_geral", "pontuacao_basica": "media_basica", "rodada_id": "jogos_disputados"
}, inplace=True)
df_agrupado = df_agrupado[df_agrupado["jogos_disputados"] >= min_jogos].copy()

# ── Status ────────────────────────────────────────────────────
status_dict               = pegar_status_atletas()
df_agrupado["status_txt"] = df_agrupado["atleta_id"].map(status_dict).fillna("Sem Status")
STATUS_MAP = {
    "Provável": "✅ Provável", "Dúvida": "❓ Dúvida",
    "Suspenso": "🟥 Suspenso", "Contundido": "🚑 Contundido", "Nulo": "❌ Nulo",
}
df_agrupado["status"] = df_agrupado["status_txt"].apply(lambda s: STATUS_MAP.get(s, f"⚪ {s}"))

# ── Contexto tático ───────────────────────────────────────────
df_proximos, _ = pegar_jogos_ao_vivo()
df_tabela      = pegar_tabela_brasileirao_api()
if df_tabela.empty:
    df_tabela = montar_tabela_interna(df)

mapa_confrontos: dict[str, dict] = {}
if not df_proximos.empty:
    for _, row in df_proximos.iterrows():
        mapa_confrontos[row["Mandante"]]  = {"mando": "CASA", "adv": row["Visitante"]}
        mapa_confrontos[row["Visitante"]] = {"mando": "FORA", "adv": row["Mandante"]}

mapa_pos_br: dict[str, int] = {}
if not df_tabela.empty and "Clube" in df_tabela.columns and "Pos" in df_tabela.columns:
    for _, row in df_tabela.iterrows():
        mapa_pos_br[str(row["Clube"]).lower()] = int(row["Pos"])

def _pos_tabela(nome_clube: str) -> int:
    if not mapa_pos_br:
        return 10
    cl = nome_clube.lower().strip()
    for nome, pos in mapa_pos_br.items():
        if cl in nome or nome in cl:
            return pos
    return 10

# ── Mando do próximo jogo ─────────────────────────────────────
df_agrupado["mando"] = df_agrupado["clube_nome"].apply(
    lambda c: mapa_confrontos[c]["mando"] if c in mapa_confrontos else "Sem Jogo"
)
df_agrupado["adversario_prox"] = df_agrupado["clube_nome"].apply(
    lambda c: mapa_confrontos[c]["adv"] if c in mapa_confrontos else "-"
)

# ── Índice PRO VETORIZADO ─────────────────────────────────────
media_cedida_adv     = df.groupby(["adversario", "posicao_nome"])["pontos"].mean()
media_feita_time     = df.groupby(["clube_nome", "posicao_nome"])["pontos"].mean()
media_posicao_global = df.groupby("posicao_nome")["pontos"].mean()

def _calcular_indice_pro_vetorizado(df_ag: pd.DataFrame) -> pd.Series:
    """
    Calcula o Índice PRO para todas as linhas de uma vez.
    Evita o lento .apply(axis=1).
    """
    n     = len(df_ag)
    fator_mando = np.where(df_ag["mando"] == "CASA", 1.15,
                  np.where(df_ag["mando"] == "FORA", 0.85, 1.0))

    pts_cedidos = np.array([
        media_cedida_adv.get(
            (row["adversario_prox"], row["posicao_nome"]),
            media_posicao_global.get(row["posicao_nome"], 0)
        )
        for _, row in df_ag.iterrows()
    ])
    pts_feitos = np.array([
        media_feita_time.get(
            (row["clube_nome"], row["posicao_nome"]),
            media_posicao_global.get(row["posicao_nome"], 0)
        )
        for _, row in df_ag.iterrows()
    ])

    forca      = (pts_cedidos + pts_feitos) / 2
    pos_adv    = np.array([_pos_tabela(adv) for adv in df_ag["adversario_prox"]])
    pos_clube  = np.array([_pos_tabela(c)   for c   in df_ag["clube_nome"]])
    fator_fav  = 1 + (pos_adv - pos_clube) * 0.008

    sem_jogo   = df_ag["mando"] == "Sem Jogo"
    base       = (df_ag["media_geral"].values * 0.4 +
                  df_ag["media_basica"].values * 0.3 +
                  forca * 0.3)
    indice     = base * fator_mando * fator_fav
    indice[sem_jogo] = df_ag.loc[sem_jogo, "media_geral"].values * 0.1
    return pd.Series(indice, index=df_ag.index)

df_agrupado["indice_pro"]      = _calcular_indice_pro_vetorizado(df_agrupado)
df_agrupado["custo_beneficio"] = np.where(
    df_agrupado["preco"] > 0,
    df_agrupado["indice_pro"] / df_agrupado["preco"],
    0.0
)

# ── Tendência de preço ────────────────────────────────────────
# Usa apenas preços > 0 para evitar distorção com dados ausentes da API
rodadas_ord = sorted(df["rodada_id"].unique())
df_preco_valido = df[df["preco"] > 0][["atleta_id","rodada_id","preco"]].copy()

if len(rodadas_ord) >= 2 and not df_preco_valido.empty:
    # Último preço válido por atleta
    df_preco_sorted = df_preco_valido.sort_values(["atleta_id","rodada_id"])
    df_preco_last   = df_preco_sorted.groupby("atleta_id").last().reset_index()[["atleta_id","preco"]].rename(columns={"preco":"preco_ult"})
    # Penúltimo preço válido por atleta
    def _penultimo(g):
        g2 = g.sort_values("rodada_id")
        return g2.iloc[-2]["preco"] if len(g2) >= 2 else g2.iloc[-1]["preco"]
    df_preco_pen = df_preco_sorted.groupby("atleta_id").apply(_penultimo).reset_index()
    df_preco_pen.columns = ["atleta_id","preco_pen"]

    df_delta = df_preco_last.merge(df_preco_pen, on="atleta_id", how="left")
    df_delta["delta_preco_real"] = df_delta["preco_ult"] - df_delta["preco_pen"].fillna(df_delta["preco_ult"])
    df_agrupado = df_agrupado.merge(df_delta[["atleta_id","delta_preco_real"]], on="atleta_id", how="left")
    df_agrupado["delta_preco_real"] = df_agrupado["delta_preco_real"].fillna(0.0)
else:
    df_agrupado["delta_preco_real"] = 0.0

# ══════════════════════════════════════════════════════════════
# 10. HEADER & KPI CARDS
# ══════════════════════════════════════════════════════════════
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("# ⚽ Cartola Pro 2026")
    st.markdown(
        '<p style="color:#6B7280;margin-top:-10px;font-size:0.9rem;">'
        "Dashboard de Inteligência Esportiva · Temporada 2026</p>",
        unsafe_allow_html=True,
    )
with col_h2:
    lbl = f"Rodadas {rodadas_disp[0]}–{rodadas_disp[-1]}" if rodadas_disp else "–"
    st.markdown(
        f'<div style="text-align:right;padding-top:20px;color:#9CA3AF;font-size:0.82rem;">{lbl}</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div style="height:3px;background:linear-gradient(90deg,#00A878,#1A6EFF,#E09B00);'
    'border-radius:2px;margin:6px 0 20px 0;"></div>',
    unsafe_allow_html=True,
)

if not df_agrupado.empty:
    top_pro    = df_agrupado.sort_values("indice_pro",       ascending=False).iloc[0]
    top_reg    = df_agrupado.sort_values("media_basica",     ascending=False).iloc[0]
    artilheiro = df_agrupado.sort_values("participacao_gol", ascending=False).iloc[0]
    ladrao     = df_agrupado.sort_values("DS",               ascending=False).iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(kpi("🤖 Top Índice PRO",   top_pro["apelido"],    f"Score: {top_pro['indice_pro']:.2f}",        "green"),  unsafe_allow_html=True)
    k2.markdown(kpi("💎 Rei Regularidade", top_reg["apelido"],    f"Básica: {top_reg['media_basica']:.1f} pts", "blue"),   unsafe_allow_html=True)
    k3.markdown(kpi("🔥 Mais Decisivo",    artilheiro["apelido"], f"{int(artilheiro['participacao_gol'])} G+A", "amber"),  unsafe_allow_html=True)
    k4.markdown(kpi("🛑 Ladrão de Bolas",  ladrao["apelido"],     f"{int(ladrao['DS'])} Desarmes",              "red"),    unsafe_allow_html=True)

st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 11. TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📅 Confrontos", "⚙️ Otimizador", "📊 Tática", "📈 Mercado", "🏆 Destaques",
    "🎯 Capitão", "🔮 Projeção", "💹 Valorização", "🧬 ML",
])

# ──────────────────────────────────────────────────────────────
# TAB 1 — CONFRONTOS DA RODADA (análise completa)
# ──────────────────────────────────────────────────────────────

# ── Helpers de análise de confrontos ─────────────────────────
def _media_ataque_clube(clube: str) -> float:
    """Média de pontos gerados pelos atacantes/meias do clube."""
    sub = df[df["clube_nome"] == clube]
    return float(sub[sub["posicao_nome"].isin(["Atacante","Meia"])]["pontos"].mean()) if not sub.empty else 0.0

def _media_defesa_clube(clube: str) -> float:
    """Quanto o clube cede de pontos para adversários (todos os jogadores contra ele)."""
    cedido = df[df["adversario"] == clube]["pontos"].mean()
    return float(cedido) if not np.isnan(cedido) else 0.0

def _top_atletas_confronto(clube: str, adv: str, n: int = 3) -> pd.DataFrame:
    """Top N atletas do clube considerando histórico contra o adversário + média geral."""
    pool = df_agrupado[
        (df_agrupado["clube_nome"] == clube) &
        (df_agrupado["mando"] != "Sem Jogo") &
        (~df_agrupado["status_txt"].isin(["Suspenso","Contundido","Nulo"]))
    ].copy()
    if pool.empty:
        pool = df_agrupado[df_agrupado["clube_nome"] == clube].copy()

    # Bônus: média específica contra o adversário, se houver histórico
    def _score_vs(row):
        hist = df[(df["atleta_id"] == row["atleta_id"]) & (df["adversario"] == adv)]
        if len(hist) >= 1:
            return hist["pontos"].mean() * 0.5 + row["indice_pro"] * 0.5
        return row["indice_pro"]

    pool["score_conf"] = pool.apply(_score_vs, axis=1)
    return pool.sort_values("score_conf", ascending=False).head(n)

def _narrativa_confronto(time_a: str, time_b: str, atq_a: float, def_b: float,
                          atq_b: float, def_a: float, mando_a: str) -> tuple[str, str]:
    """
    Retorna (favorito, texto de análise) baseado nas estatísticas históricas.
    """
    score_a = atq_a / max(def_a, 0.01) * (1.15 if mando_a == "CASA" else 0.85)
    score_b = atq_b / max(def_b, 0.01) * (0.85 if mando_a == "CASA" else 1.15)

    diff     = abs(score_a - score_b)
    fav      = time_a if score_a >= score_b else time_b
    underdog = time_b if fav == time_a else time_a

    # Texto de análise ataque
    if atq_a > atq_b * 1.2:
        txt_atq = f"**{time_a}** tem o ataque mais poderoso do confronto (média {atq_a:.1f} pts vs {atq_b:.1f})."
    elif atq_b > atq_a * 1.2:
        txt_atq = f"**{time_b}** tem o ataque mais poderoso do confronto (média {atq_b:.1f} pts vs {atq_a:.1f})."
    else:
        txt_atq = f"Ataque equilibrado: {time_a} ({atq_a:.1f}) vs {time_b} ({atq_b:.1f})."

    # Texto de análise defesa
    if def_b > def_a * 1.15:
        txt_def = f"**{time_b}** tem a defesa mais vulnerável — cede em média {def_b:.1f} pts/rodada contra {def_a:.1f} do {time_a}."
    elif def_a > def_b * 1.15:
        txt_def = f"**{time_a}** tem a defesa mais vulnerável — cede em média {def_a:.1f} pts/rodada contra {def_b:.1f} do {time_b}."
    else:
        txt_def = f"Defesas similares: {time_a} cede {def_a:.1f} pts e {time_b} cede {def_b:.1f} pts por rodada."

    # Veredito
    if diff < 0.05:
        veredito = f"⚖️ **Jogo equilibrado.** Pequena vantagem para **{fav}** pelo histórico."
    elif diff < 0.15:
        veredito = f"🟡 **Leve favoritismo de {fav}.** {underdog} pode surpreender."
    else:
        veredito = f"🟢 **{fav} é o favorito claro** com base no histórico desta temporada."

    analise = f"{txt_atq} {txt_def} {veredito}"
    return fav, analise

with tab1:
    sec("CONFRONTOS DA RODADA — ANÁLISE INTELIGENTE")
    if df_proximos.empty:
        st.warning("Mercado fechado ou sem jogos previstos para esta rodada.")
    else:
        for _, jogo in df_proximos.iterrows():
            time_a = jogo["Mandante"]
            time_b = jogo["Visitante"]

            atq_a  = _media_ataque_clube(time_a)
            atq_b  = _media_ataque_clube(time_b)
            def_a  = _media_defesa_clube(time_a)
            def_b  = _media_defesa_clube(time_b)
            fav, analise = _narrativa_confronto(time_a, time_b, atq_a, def_b, atq_b, def_a, "CASA")

            top_a = _top_atletas_confronto(time_a, time_b)
            top_b = _top_atletas_confronto(time_b, time_a)

            # ── Card do confronto ──────────────────────────────
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #E4E6EB;border-radius:14px;
                        padding:20px 24px;margin-bottom:20px;
                        box-shadow:0 1px 4px rgba(0,0,0,0.07);">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
                    <span style="font-size:1.15rem;font-weight:800;color:#111827;">{time_a}</span>
                    <span style="font-size:0.7rem;font-weight:700;color:#9CA3AF;letter-spacing:0.1em;background:#F3F4F6;
                                 padding:3px 10px;border-radius:99px;">🏠 MANDANTE vs VISITANTE ✈️</span>
                    <span style="font-size:1.15rem;font-weight:800;color:#111827;">{time_b}</span>
                </div>
                <div style="font-size:0.78rem;color:#9CA3AF;text-align:center;margin-bottom:14px;">
                    📍 {jogo.get('Local','-')} &nbsp;·&nbsp; 🕐 {jogo.get('Data','')}
                </div>
                <div style="background:#F7F8FA;border-radius:10px;padding:12px 16px;
                            font-size:0.85rem;color:#374151;line-height:1.6;">
                    {analise}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Métricas comparativas ──────────────────────────
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(f"⚔️ Ataque {time_a}",  f"{atq_a:.1f} pts",  help="Média de pontos gerados por atacantes/meias")
            m2.metric(f"🛡️ Defesa {time_a}",  f"{def_a:.1f} ced.", help="Média de pontos cedidos por rodada", delta=f"{'vuln.' if def_a > def_b else 'sólida'}", delta_color="inverse")
            m3.metric(f"⚔️ Ataque {time_b}",  f"{atq_b:.1f} pts")
            m4.metric(f"🛡️ Defesa {time_b}",  f"{def_b:.1f} ced.", delta=f"{'vuln.' if def_b > def_a else 'sólida'}", delta_color="inverse")

            # ── Top 3 indicações por time ──────────────────────
            st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

            def _render_indicacoes(top_df: pd.DataFrame, adv_clube: str, cor_pro: str):
                """Renderiza cards + tabela comparativa de scouts dos indicados."""
                for rank, (_, at) in enumerate(top_df.iterrows()):
                    medal = ["🥇","🥈","🥉"][rank] if rank < 3 else f"#{rank+1}"
                    # Média específica vs adversário — calculada fora da f-string
                    hist_vs  = df[(df["atleta_id"] == at["atleta_id"]) & (df["adversario"] == adv_clube)]
                    media_vs = float(hist_vs["pontos"].mean()) if not hist_vs.empty else None
                    if media_vs and not np.isnan(media_vs):
                        vs_html = (
                            f'<div style="font-size:0.7rem;color:#E09B00;margin-top:2px;">'
                            f'⚡ {media_vs:.1f} pts vs {adv_clube}</div>'
                        )
                    else:
                        vs_html = ""
                    apelido_safe  = str(at["apelido"])
                    posicao_safe  = str(at["posicao_nome"])
                    status_safe   = str(at["status"])
                    indice_fmt    = f"{float(at['indice_pro']):.1f}"
                    media_fmt     = f"{float(at['media_geral']):.1f}"
                    preco_fmt     = f"{float(at['preco']):.1f}"
                    card_html = (
                        f'<div style="display:flex;align-items:flex-start;gap:10px;'
                        f'padding:10px 0;border-bottom:1px solid #F3F4F6;">'
                        f'<span style="font-size:1.1rem;min-width:28px;">{medal}</span>'
                        f'<div style="flex:1;">'
                        f'<div style="font-size:0.9rem;font-weight:700;color:#111827;">{apelido_safe}</div>'
                        f'<div style="font-size:0.72rem;color:#6B7280;">{posicao_safe} · {status_safe}</div>'
                        f'{vs_html}'
                        f'</div>'
                        f'<div style="text-align:right;">'
                        f'<div style="font-size:0.85rem;font-weight:700;color:{cor_pro};">PRO {indice_fmt}</div>'
                        f'<div style="font-size:0.72rem;color:#6B7280;">Média {media_fmt} · C$ {preco_fmt}</div>'
                        f'</div>'
                        f'</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

                # Tabela comparativa de scouts dos indicados
                if not top_df.empty:
                    scouts_exibir = ["G","A","FT","DS","FS","FC","CA","DE","SG"]
                    cols_existem  = [s for s in scouts_exibir if s in top_df.columns]
                    df_sc = top_df[["apelido","media_geral","indice_pro","preco"] + cols_existem].copy()
                    df_sc = df_sc.rename(columns={"apelido":"Atleta","media_geral":"Média","indice_pro":"PRO","preco":"C$"})
                    st.dataframe(
                        df_sc,
                        column_config={
                            "Atleta": st.column_config.TextColumn(width="medium"),
                            "Média":  st.column_config.NumberColumn(format="%.1f"),
                            "PRO":    st.column_config.NumberColumn(format="%.1f"),
                            "C$":     st.column_config.NumberColumn(format="%.2f"),
                            **{s: st.column_config.NumberColumn(format="%d") for s in cols_existem},
                        },
                        hide_index=True, width="stretch",
                    )

            col_a, col_sep, col_b = st.columns([5, 1, 5])
            with col_a:
                st.markdown(f"**🎯 Indicações — {time_a}**")
                _render_indicacoes(top_a, time_b, "#00A878")
            with col_sep:
                st.markdown('<div style="border-left:1px solid #E4E6EB;height:160px;margin:8px auto;width:1px;"></div>', unsafe_allow_html=True)
            with col_b:
                st.markdown(f"**🎯 Indicações — {time_b}**")
                _render_indicacoes(top_b, time_a, "#1A6EFF")

            st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TAB 2 — OTIMIZADOR PuLP + COMPARADOR
# ──────────────────────────────────────────────────────────────
with tab2:
    st_opt, st_vs = st.tabs(["⚙️ Otimizador de Escalação", "⚔️ Mano a Mano"])

    with st_opt:
        st.markdown("### ⚙️ Otimizador de Escalação")
        st.caption("Programação Linear (PuLP) — garante a escalação com **máximo Índice PRO global**, respeitando orçamento, esquema e restrições por clube.")
        try:
            import pulp
            co1, co2 = st.columns([1, 2])
            with co1:
                sec("PARÂMETROS")
                orc_opt     = st.number_input("💰 Orçamento (C$)", value=100.0, key="opt_orc")
                esq_opt     = st.selectbox("📐 Esquema", ["4-3-3","3-4-3","3-5-2"], key="opt_esq")
                status_opt  = st.multiselect("✅ Status aceitos:", ["Provável","Dúvida","Sem Status"],
                                             default=["Provável"], key="opt_st")
                max_time    = st.number_input("🏟️ Máx. por clube", min_value=1, max_value=5, value=5, key="opt_mt")
                so_jogo_opt = st.checkbox("Somente atletas com jogo", value=True, key="opt_jogo")
                criterio_opt = st.radio("🎯 Maximizar por:", ["Índice PRO ✨","Média Geral","Pontuação Básica"], key="opt_crit")
                col_opt = {"Índice PRO ✨":"indice_pro","Média Geral":"media_geral","Pontuação Básica":"media_basica"}[criterio_opt]
                btn_opt = st.button("🚀 Otimizar Escalação", width="stretch")

            with co2:
                if btn_opt:
                    ESQUEMAS_OPT = {
                        "4-3-3": {"Goleiro":1,"Lateral":2,"Zagueiro":2,"Meia":3,"Atacante":3,"Técnico":1},
                        "3-5-2": {"Goleiro":1,"Lateral":0,"Zagueiro":3,"Meia":5,"Atacante":2,"Técnico":1},
                        "3-4-3": {"Goleiro":1,"Lateral":0,"Zagueiro":3,"Meia":4,"Atacante":3,"Técnico":1},
                    }
                    meta_opt = ESQUEMAS_OPT.get(esq_opt, ESQUEMAS_OPT["4-3-3"])
                    pool = df_agrupado[df_agrupado["status_txt"].isin(status_opt)].copy()
                    if so_jogo_opt:
                        pool = pool[pool["mando"] != "Sem Jogo"]
                    pool = pool.reset_index(drop=True)

                    if pool.empty:
                        st.warning("Nenhum atleta disponível com os parâmetros selecionados.")
                    else:
                        with st.spinner("Resolvendo o problema de otimização..."):
                            prob  = pulp.LpProblem("cartola", pulp.LpMaximize)
                            n     = len(pool)
                            ids   = list(range(n))
                            x     = pulp.LpVariable.dicts("x", ids, cat="Binary")
                            # Objetivo
                            prob += pulp.lpSum(pool.iloc[i][col_opt] * x[i] for i in ids)
                            # Orçamento
                            prob += pulp.lpSum(pool.iloc[i]["preco"] * x[i] for i in ids) <= orc_opt
                            # Restrição por posição
                            for pos, qtd in meta_opt.items():
                                ip = [i for i in ids if pool.iloc[i]["posicao_nome"] == pos]
                                prob += pulp.lpSum(x[i] for i in ip) == qtd
                            # Restrição por clube
                            for tm in pool["clube_nome"].unique():
                                it = [i for i in ids if pool.iloc[i]["clube_nome"] == tm]
                                prob += pulp.lpSum(x[i] for i in it) <= max_time
                            prob.solve(pulp.PULP_CBC_CMD(msg=0))

                        if pulp.LpStatus[prob.status] == "Optimal":
                            esc    = [i for i in ids if pulp.value(x[i]) == 1]
                            df_opt = pool.iloc[esc].copy()
                            ordem  = ["Goleiro","Lateral","Zagueiro","Meia","Atacante","Técnico"]
                            df_opt["posicao_nome"] = pd.Categorical(df_opt["posicao_nome"], categories=ordem, ordered=True)
                            df_opt = df_opt.sort_values("posicao_nome")
                            custo  = df_opt["preco"].sum()
                            score  = df_opt[col_opt].sum()

                            # KPIs do resultado
                            r1, r2, r3, r4 = st.columns(4)
                            r1.metric("✅ Score Total",    f"{score:.2f}")
                            r2.metric("💰 Custo",          f"C$ {custo:.2f}")
                            r3.metric("💵 Saldo",          f"C$ {orc_opt - custo:.2f}")
                            r4.metric("👥 Atletas",        f"{len(df_opt)}")

                            st.dataframe(
                                df_opt[["foto","status","posicao_nome","apelido","clube_nome",
                                        "mando","adversario_prox","preco","indice_pro","media_geral","media_basica"]],
                                column_config={
                                    "foto":           st.column_config.ImageColumn("Perfil"),
                                    "status":         "Status",
                                    "posicao_nome":   "Posição",
                                    "apelido":        "Jogador",
                                    "clube_nome":     "Clube",
                                    "mando":          "Mando",
                                    "adversario_prox":"Adv.",
                                    "preco":          st.column_config.NumberColumn("C$",           format="%.2f"),
                                    "indice_pro":     st.column_config.NumberColumn("Índice PRO ✨", format="%.2f"),
                                    "media_geral":    st.column_config.NumberColumn("Média",        format="%.2f"),
                                    "media_basica":   st.column_config.NumberColumn("Básica",       format="%.2f"),
                                },
                                hide_index=True, width="stretch",
                            )

                            # Gráfico de composição por posição
                            fig_pos = px.bar(
                                df_opt.groupby("posicao_nome")[col_opt].sum().reset_index(),
                                x="posicao_nome", y=col_opt, color="posicao_nome",
                                labels={"posicao_nome":"Posição", col_opt:"Score Contribuído"},
                                color_discrete_sequence=COLORS, text_auto=".1f",
                            )
                            themed(fig_pos)
                            fig_pos.update_traces(textposition="outside")
                            st.plotly_chart(fig_pos, width="stretch")
                            st.info("💡 PuLP (CBC) garante o **ótimo global** — nenhuma outra combinação dentro do orçamento gera score maior.")
                        else:
                            st.error("❌ Sem solução viável. Tente aumentar o orçamento, aceitar mais status ou reduzir o máximo por clube.")
        except ImportError:
            st.error("❌ `pulp` não instalado. Adicione ao `requirements.txt` e faça o redeploy.")

    with st_vs:
        sec("COMPARATIVO MANO A MANO")
        jogadores = sorted(df_agrupado["apelido"].unique())
        c1, c2    = st.columns(2)
        p1 = c1.selectbox("Jogador 1", jogadores, index=0)
        p2 = c2.selectbox("Jogador 2", jogadores, index=1 if len(jogadores) > 1 else 0)
        if p1 and p2:
            d1   = df_agrupado[df_agrupado["apelido"] == p1].iloc[0]
            d2   = df_agrupado[df_agrupado["apelido"] == p2].iloc[0]
            cats = ["Índice PRO","Pont. Básica","Gols","Finalizações","Desarmes","Part. Gol"]
            v1   = [d1["indice_pro"], d1["media_basica"], d1["G"], d1["finalizacoes"], d1["DS"], d1["participacao_gol"]]
            v2   = [d2["indice_pro"], d2["media_basica"], d2["G"], d2["finalizacoes"], d2["DS"], d2["participacao_gol"]]
            fig  = go.Figure()
            fig.add_trace(go.Scatterpolar(r=v1+[v1[0]], theta=cats+[cats[0]], fill="toself", name=p1,
                                          line=dict(color="#00A878",width=2), fillcolor="rgba(0,168,120,0.12)"))
            fig.add_trace(go.Scatterpolar(r=v2+[v2[0]], theta=cats+[cats[0]], fill="toself", name=p2,
                                          line=dict(color="#1A6EFF",width=2), fillcolor="rgba(26,110,255,0.12)"))
            fig.update_layout(
                **{k: v for k, v in THEME.items() if k not in ("xaxis","yaxis")},
                polar=dict(bgcolor="rgba(0,0,0,0)",
                           radialaxis=dict(visible=True, gridcolor="#E4E6EB"),
                           angularaxis=dict(gridcolor="#E4E6EB")),
            )
            st.plotly_chart(fig, width="stretch")

            # Tabela comparativa detalhada
            st.divider()
            sec("ESTATÍSTICAS DETALHADAS")
            stats_cols = ["media_geral","media_basica","indice_pro","custo_beneficio","G","A","DS","FS","DE","CA","CV"]
            comp_df = pd.DataFrame({
                "Métrica": ["Média Geral","Pont. Básica","Índice PRO","Custo/Ben.","Gols","Assist.","Desarmes","F.Sofridas","Defesas","Cart. Am.","Cart. Vm."],
                p1: [d1[c] for c in stats_cols],
                p2: [d2[c] for c in stats_cols],
            })
            comp_df["Vantagem"] = comp_df.apply(
                lambda r: f"✅ {p1}" if r[p1] > r[p2] else (f"✅ {p2}" if r[p2] > r[p1] else "—"), axis=1
            )
            st.dataframe(comp_df, hide_index=True, width="stretch")

# ──────────────────────────────────────────────────────────────
# TAB 3 — TÁTICA
# ──────────────────────────────────────────────────────────────
with tab3:
    hm1, hm2, hm3 = st.tabs(["🛡️ Defesa","⚔️ Ataque","🏰 Mando"])
    with hm1:
        sec("FRAGILIDADE DEFENSIVA — PONTOS CEDIDOS POR POSIÇÃO")
        heat = df.groupby(["adversario","posicao_nome"])["pontos"].mean().reset_index()
        if not heat.empty:
            piv = heat.pivot(index="adversario", columns="posicao_nome", values="pontos").fillna(0)
            fig = px.imshow(piv, text_auto=".1f", color_continuous_scale="Reds", aspect="auto")
            themed(fig); st.plotly_chart(fig, width="stretch")
    with hm2:
        sec("PODER OFENSIVO — PONTOS FEITOS POR POSIÇÃO")
        heat2 = df.groupby(["clube_nome","posicao_nome"])["pontos"].mean().reset_index()
        if not heat2.empty:
            piv2 = heat2.pivot(index="clube_nome", columns="posicao_nome", values="pontos").fillna(0)
            fig2 = px.imshow(piv2, text_auto=".1f", color_continuous_scale="Greens", aspect="auto")
            themed(fig2); st.plotly_chart(fig2, width="stretch")
    with hm3:
        sec("DESEMPENHO: CASA × FORA")
        stats_mando = df.groupby(["clube_nome","mando"])["pontos"].mean().reset_index()
        fig_pts = px.bar(stats_mando, x="clube_nome", y="pontos", color="mando", barmode="group",
                         labels={"pontos":"Média","clube_nome":"Time"},
                         color_discrete_map={"CASA":"#00A878","FORA":"#1A6EFF"})
        themed(fig_pts); fig_pts.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_pts, width="stretch")

# ──────────────────────────────────────────────────────────────
# TAB 4 — MERCADO
# ──────────────────────────────────────────────────────────────
with tab4:
    sec("INTELIGÊNCIA DE MERCADO")
    col_sf1, col_sf2, col_sf3 = st.columns([2,2,1])
    with col_sf1:
        busca = st.text_input("🔍 Buscar atleta", placeholder="Nome...", label_visibility="collapsed")
    with col_sf2:
        filtro_st = st.multiselect(
            "Status",
            ["✅ Provável","❓ Dúvida","🚑 Contundido","🟥 Suspenso","⚪ Sem Status"],
            default=["✅ Provável","❓ Dúvida","⚪ Sem Status"],
            label_visibility="collapsed",
        )
    with col_sf3:
        ord_por = st.selectbox("Ordenar", ["Índice PRO","Média","C$","C/B","Δ Preço"], label_visibility="collapsed")

    ord_map = {"Índice PRO":"indice_pro","Média":"media_geral","C$":"preco","C/B":"custo_beneficio","Δ Preço":"delta_preco_real"}
    df_merc = df_agrupado.copy()
    if busca:
        df_merc = df_merc[df_merc["apelido"].str.contains(busca, case=False, na=False)]
    if filtro_st:
        df_merc = df_merc[df_merc["status"].isin(filtro_st)]
    df_merc = df_merc.sort_values(ord_map[ord_por], ascending=(ord_por == "C$"))

    cols_view = ["foto","status","apelido","posicao_nome","clube_nome","adversario_prox","mando",
                 "jogos_disputados","preco","delta_preco_real","indice_pro","custo_beneficio","media_geral","media_basica"] + SCOUTS
    st.dataframe(
        df_merc[cols_view],
        column_config={
            "foto":              st.column_config.ImageColumn("Foto", width="small"),
            "status":            "Status",
            "apelido":           "Atleta",
            "posicao_nome":      "Posição",
            "clube_nome":        "Clube",
            "adversario_prox":   "Adv.",
            "mando":             "Mando",
            "jogos_disputados":  st.column_config.NumberColumn("Jogos",       format="%d"),
            "preco":             st.column_config.NumberColumn("C$",          format="%.2f"),
            "delta_preco_real":  st.column_config.NumberColumn("Δ C$",        format="%+.2f"),
            "indice_pro":        st.column_config.NumberColumn("Índice PRO ✨",format="%.2f"),
            "custo_beneficio":   st.column_config.NumberColumn("C/B ⚡",       format="%.2f"),
            "media_geral":       st.column_config.NumberColumn("Média",       format="%.2f"),
            "media_basica":      st.column_config.ProgressColumn("Básica",    format="%.2f",min_value=-5,max_value=15),
        },
        width="stretch", hide_index=True, height=560,
    )
    st.divider()
    sec("PREÇO × ÍNDICE PRO")
    if not df_merc.empty:
        fig_sc2 = px.scatter(
            df_merc, x="preco", y="indice_pro", color="posicao_nome",
            hover_name="apelido",
            hover_data={"clube_nome":True,"media_geral":":.1f","preco":":.2f","indice_pro":":.2f","delta_preco_real":":.2f"},
            labels={"preco":"Preço (C$)","indice_pro":"Índice PRO","posicao_nome":"Posição"},
            color_discrete_sequence=COLORS,
        )
        themed(fig_sc2)
        fig_sc2.update_traces(marker=dict(size=8, opacity=0.8, line=dict(width=0.5, color="#E4E6EB")))
        st.plotly_chart(fig_sc2, width="stretch")

    # ── Drill-down: clique no nome para ver ficha completa ─────
    st.divider()
    sec("🔍 FICHA DO ATLETA — DRILL-DOWN")
    st.caption("Selecione um atleta da tabela acima para ver sua ficha completa com histórico de scouts.")

    atletas_merc = sorted(df_merc["apelido"].unique()) if not df_merc.empty else []
    if atletas_merc:
        sel_drill = st.selectbox(
            "Selecione o atleta:", atletas_merc,
            index=0, key="drill_mercado",
            placeholder="Escolha um atleta..."
        )
        if sel_drill:
            row_at = df_agrupado[df_agrupado["apelido"] == sel_drill]
            if not row_at.empty:
                row_at = row_at.iloc[0]
                # Header da ficha
                fc1, fc2, fc3 = st.columns([1,3,2])
                with fc1:
                    if row_at["foto"] and str(row_at["foto"]).startswith("http"):
                        st.image(str(row_at["foto"]), width=80)
                with fc2:
                    st.markdown(
                        f'<div style="font-size:1.1rem;font-weight:800;color:#111827;">{sel_drill}</div>'
                        f'<div style="font-size:0.82rem;color:#6B7280;">'
                        f'{row_at["posicao_nome"]} · {row_at["clube_nome"]} · {row_at["status"]}</div>',
                        unsafe_allow_html=True
                    )
                with fc3:
                    st.metric("Índice PRO", f"{row_at['indice_pro']:.2f}")

                # KPIs rápidos
                dk1, dk2, dk3, dk4, dk5 = st.columns(5)
                dk1.metric("Média Geral",  f"{row_at['media_geral']:.1f} pts")
                dk2.metric("C$ Atual",     f"C$ {row_at['preco']:.2f}")
                dk3.metric("Δ C$ Últ.",    f"{row_at['delta_preco_real']:+.2f}")
                dk4.metric("C/B",          f"{row_at['custo_beneficio']:.2f}")
                dk5.metric("Jogos",        f"{int(row_at['jogos_disputados'])}")

                # Scouts totais na temporada
                scouts_top = ["G","A","FT","DS","FS","FC","CA","DE","SG","CV"]
                sc_vals = {s: int(row_at[s]) for s in scouts_top if s in row_at.index and row_at[s] > 0}
                if sc_vals:
                    sc_df = pd.DataFrame(list(sc_vals.items()), columns=["Scout","Total"])
                    fig_sc_bar = px.bar(sc_df, x="Scout", y="Total", text="Total",
                                        color="Total", color_continuous_scale="Greens",
                                        height=200)
                    _tb = {k: v for k, v in THEME.items() if k != "yaxis"}
                    fig_sc_bar.update_layout(**_tb, showlegend=False,
                                            yaxis=dict(title="", gridcolor="#F3F4F6"),
                                            margin=dict(l=0,r=0,t=20,b=0))
                    fig_sc_bar.update_traces(textposition="outside")
                    st.plotly_chart(fig_sc_bar, width="stretch")

                # Histórico rodada a rodada
                with st.expander("📅 Ver histórico rodada a rodada", expanded=False):
                    atleta_id_sel = int(row_at["atleta_id"])
                    scouts_hist   = [s for s in SCOUTS if s in df.columns]
                    sel_sc_drill  = st.multiselect(
                        "Scouts:", scouts_hist,
                        default=["G","A","DS","FC"],
                        key="sc_drill"
                    )
                    df_drill = df[df["atleta_id"] == atleta_id_sel].sort_values("rodada_id")
                    if not df_drill.empty and sel_sc_drill:
                        fig_drill = go.Figure()
                        for s in sel_sc_drill:
                            if s in df_drill.columns:
                                fig_drill.add_trace(go.Bar(
                                    name=s, x=df_drill["rodada_id"], y=df_drill[s], opacity=0.75
                                ))
                        fig_drill.add_trace(go.Scatter(
                            name="Pontos", x=df_drill["rodada_id"], y=df_drill["pontos"],
                            mode="lines+markers", line=dict(color="#E09B00", width=2.5),
                            marker=dict(size=6), yaxis="y2",
                        ))
                        _td = {k: v for k, v in THEME.items() if k not in ("xaxis","yaxis")}
                        fig_drill.update_layout(
                            **_td, barmode="stack", height=300,
                            xaxis=dict(title="Rodada", tickmode="linear", dtick=1,
                                       gridcolor="#F3F4F6", linecolor="#E4E6EB",
                                       tickfont=dict(color="#6B7280")),
                            yaxis=dict(title="Scouts", gridcolor="#F3F4F6",
                                       linecolor="#E4E6EB", tickfont=dict(color="#6B7280")),
                            yaxis2=dict(title="Pts", overlaying="y", side="right",
                                        showgrid=False, tickfont=dict(color="#E09B00")),
                        )
                        st.plotly_chart(fig_drill, width="stretch")
                        tabela_drill = df_drill[["rodada_id","pontos","adversario","mando","preco"] + sel_sc_drill].copy()
                        tabela_drill = tabela_drill.rename(columns={
                            "rodada_id":"Rodada","pontos":"Pts",
                            "adversario":"Adversário","mando":"Mando","preco":"C$"
                        })
                        st.dataframe(tabela_drill, hide_index=True, width="stretch")

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
            ci.image(lider["foto"], width=64)
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
        fig_box = px.box(df_agrupado, x="posicao_nome", y="media_geral",
                         color="posicao_nome", points="outliers",
                         labels={"posicao_nome":"Posição","media_geral":"Média de Pontos"},
                         color_discrete_sequence=COLORS)
        themed(fig_box); st.plotly_chart(fig_box, width="stretch")

# ──────────────────────────────────────────────────────────────
# TAB 6 — CAPITÃO IDEAL
# ──────────────────────────────────────────────────────────────
with tab6:
    st.markdown("### 🎯 Alerta de Capitão Ideal")
    st.caption("O capitão dobra os pontos. Score = Índice PRO × Fator Mando (Casa +15%, Fora -15%).")

    cap_pool = df_agrupado[df_agrupado["mando"] != "Sem Jogo"].copy()
    if cap_pool.empty:
        st.warning("Nenhum atleta com jogo confirmado.")
    else:
        cap_pool["fator_mando_cap"] = cap_pool["mando"].map({"CASA":1.15,"FORA":0.85}).fillna(1.0)
        cap_pool["score_capitao"]   = cap_pool["indice_pro"] * cap_pool["fator_mando_cap"]

        inc_status = st.multiselect("Incluir status:",
            ["Provável","Dúvida","Sem Status"], default=["Provável"], key="cap_status")
        if inc_status:
            cap_pool = cap_pool[cap_pool["status_txt"].isin(inc_status)]

        top_cap = cap_pool.sort_values("score_capitao", ascending=False).head(10)
        for i, (_, row) in enumerate(top_cap.iterrows()):
            medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"#{i+1}"
            adv   = row["adversario_prox"]
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
# TAB 7 — PROJEÇÃO + FORMA RECENTE (era tab8)
with tab7:
    proj_tab, forma_tab = st.tabs(["🔮 Projeção por Posição","📅 Forma Recente"])

    with proj_tab:
        st.markdown("### 🔮 Projeção de Pontuação")
        st.caption("Todos os atletas com jogo confirmado. Projeção = média ponderada de scouts contra o adversário específico (ou geral, se não houver histórico).")

        PESOS_PROJ = {"G":8.0,"A":5.0,"FT":3.0,"FD":1.2,"FF":0.8,"FS":0.5,"PS":1.0,
                      "DE":1.0,"DS":1.5,"FC":-0.3,"PC":-1.0,"CA":-1.0,"CV":-3.0,"GS":-1.0,"I":-0.1,"SG":5.0}

        # Calcula projeção para TODOS os atletas com jogo
        pool_proj = df_agrupado[df_agrupado["mando"] != "Sem Jogo"].copy()

        if pool_proj.empty:
            st.warning("Nenhum atleta com jogo confirmado nesta rodada.")
        else:
            rows_proj = []
            for _, row_ag in pool_proj.iterrows():
                clube = row_ag["clube_nome"]
                adv   = mapa_confrontos.get(clube, {}).get("adv", None)
                df_at = df[df["atleta_id"] == row_ag["atleta_id"]]
                df_vs = df_at[df_at["adversario"] == adv] if adv else df_at
                if df_vs.empty:
                    df_vs = df_at
                proj = sum(
                    df_vs[s].mean() * p
                    for s, p in PESOS_PROJ.items()
                    if s in df_vs.columns and not np.isnan(df_vs[s].mean())
                )
                rows_proj.append({
                    "atleta_id":  row_ag["atleta_id"],
                    "Atleta":     row_ag["apelido"],
                    "Posição":    row_ag["posicao_nome"],
                    "Clube":      clube,
                    "Adv":        adv or "-",
                    "Mando":      row_ag["mando"],
                    "Status":     row_ag["status_txt"],
                    "C$":         row_ag["preco"],
                    "Índice PRO": round(row_ag["indice_pro"], 2),
                    "C/B":        round(row_ag["custo_beneficio"], 2),
                    "Média Real": round(row_ag["media_geral"], 1),
                    "Proj Min":   round(proj * 0.70, 1),
                    "Proj Med":   round(proj, 1),
                    "Proj Máx":   round(proj * 1.30, 1),
                })

            df_proj_all = pd.DataFrame(rows_proj).sort_values("Proj Med", ascending=False)

            # ── Filtros ──────────────────────────────────────────
            pf1, pf2, pf3, pf4 = st.columns([2, 2, 2, 2])
            with pf1:
                pos_f = st.multiselect(
                    "Posição:", sorted(df_proj_all["Posição"].unique()),
                    default=sorted(df_proj_all["Posição"].unique()), key="pf_pos"
                )
            with pf2:
                time_f = st.multiselect(
                    "Clube:", sorted(df_proj_all["Clube"].unique()),
                    default=sorted(df_proj_all["Clube"].unique()), key="pf_clube"
                )
            with pf3:
                st_f = st.multiselect(
                    "Status:", ["Provável","Dúvida","Sem Status"],
                    default=["Provável","Dúvida"], key="pf_status"
                )
            with pf4:
                ord_proj = st.selectbox(
                    "Ordenar por:", ["Proj Med","Índice PRO","Média Real","C$","C/B"],
                    key="pf_ord"
                )

            df_view = df_proj_all[
                df_proj_all["Posição"].isin(pos_f) &
                df_proj_all["Clube"].isin(time_f) &
                df_proj_all["Status"].isin(st_f)
            ].sort_values(ord_proj, ascending=(ord_proj == "C$"))

            # KPIs rápidos
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Atletas exibidos",  len(df_view))
            k2.metric("Maior projeção",    f"{df_view['Proj Med'].max():.1f} pts" if not df_view.empty else "-")
            k3.metric("Melhor C/B",        f"{df_view['C/B'].max():.2f}"          if not df_view.empty else "-")
            k4.metric("Mais barato top10", f"C$ {df_view.head(10)['C$'].min():.2f}" if len(df_view) >= 1 else "-")

            # Tabela principal
            st.dataframe(
                df_view.drop(columns=["atleta_id"]),
                column_config={
                    "Atleta":     st.column_config.TextColumn(width="medium"),
                    "Posição":    st.column_config.TextColumn(width="small"),
                    "Clube":      st.column_config.TextColumn(width="small"),
                    "Adv":        st.column_config.TextColumn(width="small"),
                    "Mando":      st.column_config.TextColumn(width="small"),
                    "Status":     st.column_config.TextColumn(width="small"),
                    "C$":         st.column_config.NumberColumn(format="%.2f"),
                    "Índice PRO": st.column_config.NumberColumn(format="%.2f"),
                    "C/B":        st.column_config.NumberColumn(format="%.2f"),
                    "Média Real": st.column_config.NumberColumn(format="%.1f"),
                    "Proj Min":   st.column_config.NumberColumn(format="%.1f"),
                    "Proj Med":   st.column_config.ProgressColumn(
                        "Proj Med", format="%.1f",
                        min_value=float(df_view["Proj Med"].min()) if not df_view.empty else 0,
                        max_value=float(df_view["Proj Med"].max()) if not df_view.empty else 1,
                    ),
                    "Proj Máx":   st.column_config.NumberColumn(format="%.1f"),
                },
                hide_index=True, width="stretch", height=520,
            )

            # Gráfico dispersão Projeção × C$ (colorido por posição)
            if not df_view.empty:
                st.divider()
                sec("PROJEÇÃO × PREÇO — MAPA DE VALOR")
                fig_pv = px.scatter(
                    df_view, x="C$", y="Proj Med",
                    color="Posição", hover_name="Atleta",
                    hover_data={"Clube":True,"Adv":True,"Mando":True,"Índice PRO":":.2f",
                                "Média Real":":.1f","C$":":.2f","Proj Med":":.1f"},
                    labels={"C$":"Preço (C$)","Proj Med":"Projeção (pts)"},
                    color_discrete_sequence=COLORS,
                    size_max=12,
                )
                themed(fig_pv)
                fig_pv.update_traces(marker=dict(size=9, opacity=0.85, line=dict(width=0.5, color="#E4E6EB")))
                st.plotly_chart(fig_pv, width="stretch")
            st.caption("Proj Min / Proj Máx = ±30% sobre a projeção central.")

    with forma_tab:
        st.markdown("### 📅 Forma Recente")
        st.caption("Compare a média total com a performance nas últimas N rodadas.")
        n_rec = st.slider("Últimas N rodadas:", 1, max_jogos, min(5, max_jogos))
        rodadas_rec = sorted(df["rodada_id"].unique())[-n_rec:]
        df_rec      = df[df["rodada_id"].isin(rodadas_rec)]
        df_ag_rec   = df_rec.groupby("atleta_id").agg(
            media_rec=("pontos","mean"), jogos_rec=("rodada_id","count"),
            clube_nome=("clube_nome","last"), apelido=("apelido","last"),
        ).reset_index()
        df_forma = df_agrupado[["atleta_id","apelido","clube_nome","media_geral"]].merge(
            df_ag_rec[["atleta_id","media_rec","jogos_rec"]], on="atleta_id", how="inner"
        )
        df_forma["delta"] = df_forma["media_rec"] - df_forma["media_geral"]

        ca, cb = st.columns(2)
        with ca:
            st.markdown(f"#### 🔥 Em alta (últ. {n_rec} rod.)")
            for _, r in df_forma.sort_values("delta", ascending=False).head(8).iterrows():
                st.metric(f"{r['apelido']} — {r['clube_nome']}",
                          f"{r['media_rec']:.1f} pts", f"{r['delta']:+.1f} vs média total")
        with cb:
            st.markdown(f"#### 📉 Em queda (últ. {n_rec} rod.)")
            for _, r in df_forma.sort_values("delta", ascending=True).head(8).iterrows():
                st.metric(f"{r['apelido']} — {r['clube_nome']}",
                          f"{r['media_rec']:.1f} pts", f"{r['delta']:+.1f} vs média total")

        st.divider()
        df_top20  = df_forma.sort_values("media_rec", ascending=False).head(20)
        fig_forma = go.Figure()
        fig_forma.add_trace(go.Bar(name="Média Total", x=df_top20["apelido"],
                                   y=df_top20["media_geral"], marker_color="#E4E6EB"))
        fig_forma.add_trace(go.Bar(name=f"Últ. {n_rec} rod.", x=df_top20["apelido"],
                                   y=df_top20["media_rec"], marker_color="#00A878"))
        fig_forma.update_layout(**THEME, barmode="group", xaxis_tickangle=-45)
        st.plotly_chart(fig_forma, width="stretch")

# ──────────────────────────────────────────────────────────────
# TAB 8 — VALORIZAÇÃO
# ──────────────────────────────────────────────────────────────
with tab8:
    st.markdown("### 💹 Tendência de Valorização")
    st.caption("Análise de valorização/desvalorização de C$ ao longo da temporada.")

    # ── Base de cálculo robusta: só preços > 0 ─────────────────
    df_pv = df[df["preco"] > 0][["atleta_id","rodada_id","apelido","clube_nome","posicao_nome","preco"]].copy()

    if len(rodadas_ord) >= 2 and not df_pv.empty:
        # Primeiro e último preço válido por atleta
        df_pv_sorted = df_pv.sort_values(["atleta_id","rodada_id"])
        df_ini = df_pv_sorted.groupby("atleta_id").first().reset_index()[["atleta_id","preco","rodada_id"]].rename(columns={"preco":"preco_ini","rodada_id":"rodada_ini"})
        df_fim = df_pv_sorted.groupby("atleta_id").last().reset_index()[["atleta_id","preco","rodada_id","apelido","clube_nome","posicao_nome"]].rename(columns={"preco":"preco_fim","rodada_id":"rodada_fim"})
        jogos_count = df.groupby("atleta_id")["rodada_id"].count().reset_index().rename(columns={"rodada_id":"jogos"})

        df_val = df_fim.merge(df_ini, on="atleta_id").merge(jogos_count, on="atleta_id")
        df_val["delta_total"] = df_val["preco_fim"] - df_val["preco_ini"]
        df_val["delta_pct"]   = ((df_val["delta_total"] / df_val["preco_ini"]) * 100).replace([np.inf,-np.inf], 0).fillna(0)
        df_val = df_val[df_val["jogos"] >= 2]  # só atletas com ao menos 2 rodadas
    else:
        df_val = pd.DataFrame()

    val_tab1, val_tab2, val_tab3 = st.tabs([
        "🔥 Ranking de Valorização", "📈 Curva de Preço", "🗺️ Mapa de Calor"
    ])

    with val_tab1:
        if df_val.empty:
            st.info("Necessário pelo menos 2 rodadas com preços válidos.")
        else:
            # ── Filtros ──────────────────────────────────────────
            vf1, vf2, vf3 = st.columns([2,2,2])
            with vf1:
                pos_v = st.multiselect("Posição:", sorted(df_val["posicao_nome"].unique()),
                                       default=sorted(df_val["posicao_nome"].unique()), key="vf_pos")
            with vf2:
                dir_v = st.radio("Direção:", ["🔺 Valorizados","🔻 Desvalorizados"], horizontal=True, key="vf_dir")
            with vf3:
                n_v = st.slider("Top N:", 5, 30, 20, key="vf_n")

            df_vf = df_val[df_val["posicao_nome"].isin(pos_v)].copy()
            ascend = dir_v == "🔻 Desvalorizados"
            df_vf  = df_vf.sort_values("delta_total", ascending=ascend).head(n_v)

            # KPIs rápidos
            kv1, kv2, kv3, kv4 = st.columns(4)
            kv1.metric("Maior valorização", f"+C$ {df_val['delta_total'].max():.2f}")
            kv2.metric("Maior desvalorização", f"C$ {df_val['delta_total'].min():.2f}")
            kv3.metric("Média da temporada", f"C$ {df_val['delta_total'].mean():+.2f}")
            kv4.metric("Atletas estáveis (Δ=0)", int((df_val["delta_total"] == 0).sum()))

            # Gráfico de barras horizontal — mais legível que vertical para nomes
            cor_bars = "#00A878" if not ascend else "#E03E3E"
            fig_rank = px.bar(
                df_vf.sort_values("delta_total", ascending=not ascend),
                y="apelido", x="delta_total",
                color="posicao_nome", orientation="h",
                text=df_vf.sort_values("delta_total", ascending=not ascend)["delta_total"].apply(
                    lambda v: f"{v:+.2f}"
                ),
                hover_data={"clube_nome":True,"preco_ini":":.2f","preco_fim":":.2f","delta_pct":":.1f","jogos":True},
                labels={"apelido":"Atleta","delta_total":"Δ C$","posicao_nome":"Posição"},
                color_discrete_sequence=COLORS,
                height=max(280, n_v * 28),
            )
            themed(fig_rank)
            fig_rank.update_traces(textposition="outside")
            fig_rank.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_rank, width="stretch")

            # Tabela completa com formato rico
            st.dataframe(
                df_vf[["apelido","clube_nome","posicao_nome","preco_ini","preco_fim","delta_total","delta_pct","jogos"]].rename(
                    columns={"apelido":"Atleta","clube_nome":"Clube","posicao_nome":"Posição",
                             "jogos":"Jogos"}
                ),
                column_config={
                    "Atleta":   st.column_config.TextColumn(width="medium"),
                    "preco_ini":st.column_config.NumberColumn("C$ Início", format="%.2f"),
                    "preco_fim":st.column_config.NumberColumn("C$ Atual",  format="%.2f"),
                    "delta_total": st.column_config.NumberColumn("Δ C$",  format="%+.2f"),
                    "delta_pct":   st.column_config.NumberColumn("Δ %",   format="%+.1f%%"),
                    "Jogos":       st.column_config.NumberColumn(format="%d"),
                },
                hide_index=True, width="stretch",
            )

    with val_tab2:
        sec("CURVA DE PREÇO — TOP VALORIZADOS DA TEMPORADA")
        st.caption("Exibe automaticamente os 10 atletas com maior valorização total. Use o filtro para personalizar.")

        if df_val.empty:
            st.info("Necessário pelo menos 2 rodadas com preços válidos.")
        else:
            # Default: top 10 mais valorizados — sem multiselect obrigatório
            cf1, cf2 = st.columns([3,1])
            with cf1:
                auto_top10 = list(df_val.sort_values("delta_total", ascending=False).head(10)["apelido"])
                sel_curva  = st.multiselect(
                    "Personalizar atletas (opcional):", sorted(df_pv["apelido"].unique()),
                    default=[], max_selections=12, key="curva_sel",
                    placeholder="Deixe vazio para ver Top 10 valorizados automaticamente"
                )
            with cf2:
                pos_curva = st.multiselect("Posição:", sorted(df_val["posicao_nome"].unique()),
                                           default=sorted(df_val["posicao_nome"].unique()), key="curva_pos")

            atletas_plot = sel_curva if sel_curva else auto_top10
            # Filtra por posição se necessário
            validos_pos  = df_val[df_val["posicao_nome"].isin(pos_curva)]["apelido"].tolist()
            atletas_plot = [a for a in atletas_plot if a in validos_pos] or auto_top10[:5]

            df_curva = df_pv[df_pv["apelido"].isin(atletas_plot)].copy()
            df_curva = df_curva.groupby(["rodada_id","apelido"])["preco"].last().reset_index()

            fig_curva = px.line(
                df_curva, x="rodada_id", y="preco", color="apelido",
                labels={"rodada_id":"Rodada","preco":"Preço (C$)","apelido":"Atleta"},
                markers=True, color_discrete_sequence=COLORS,
            )
            themed(fig_curva)
            fig_curva.update_traces(line=dict(width=2.5), marker=dict(size=6))
            fig_curva.update_layout(
                xaxis=dict(tickmode="linear", dtick=1, title="Rodada",
                           gridcolor="#F3F4F6", linecolor="#E4E6EB", tickfont=dict(color="#6B7280")),
            )
            st.plotly_chart(fig_curva, width="stretch")

            # Mini tabela de referência ao lado do gráfico
            ref = df_val[df_val["apelido"].isin(atletas_plot)][["apelido","preco_ini","preco_fim","delta_total","delta_pct"]].sort_values("delta_total", ascending=False)
            st.dataframe(ref.rename(columns={"apelido":"Atleta","preco_ini":"C$ Início","preco_fim":"C$ Atual","delta_total":"Δ C$","delta_pct":"Δ %"}),
                column_config={
                    "C$ Início": st.column_config.NumberColumn(format="%.2f"),
                    "C$ Atual":  st.column_config.NumberColumn(format="%.2f"),
                    "Δ C$":      st.column_config.NumberColumn(format="%+.2f"),
                    "Δ %":       st.column_config.NumberColumn(format="%+.1f%%"),
                }, hide_index=True, width="stretch")

    with val_tab3:
        sec("MAPA DE CALOR — ΔPREÇO POR ATLETA × RODADA")
        st.caption("Verde = valorizou, Vermelho = desvalorizou, Cinza = sem dado.")

        if df_val.empty or len(rodadas_ord) < 2:
            st.info("Necessário pelo menos 2 rodadas.")
        else:
            # Calcula delta rodada a rodada para cada atleta
            pos_heat = st.multiselect("Posição:", sorted(df_val["posicao_nome"].unique()),
                                      default=["Atacante","Meia"], key="heat_pos")
            top_n_heat = st.slider("Top N atletas (por média):", 10, 50, 20, key="heat_n")

            atletas_heat = (df_agrupado[df_agrupado["posicao_nome"].isin(pos_heat)]
                            .sort_values("media_geral", ascending=False)
                            .head(top_n_heat)["apelido"].tolist())

            df_ph = df_pv[df_pv["apelido"].isin(atletas_heat)].sort_values(["atleta_id","rodada_id"])
            df_ph["delta_rod"] = df_ph.groupby("atleta_id")["preco"].diff()

            if not df_ph.empty:
                piv_heat = df_ph.pivot_table(index="apelido", columns="rodada_id",
                                             values="delta_rod", aggfunc="mean").fillna(0)
                fig_heat = px.imshow(
                    piv_heat,
                    color_continuous_scale=[[0,"#E03E3E"],[0.5,"#F9FAFB"],[1,"#00A878"]],
                    color_continuous_midpoint=0,
                    text_auto="+.2f",
                    labels={"x":"Rodada","y":"Atleta","color":"Δ C$"},
                    aspect="auto",
                )
                themed(fig_heat)
                fig_heat.update_layout(
                    xaxis=dict(title="Rodada", gridcolor="#F3F4F6"),
                    yaxis=dict(title=""),
                    coloraxis_colorbar=dict(title="Δ C$"),
                )
                st.plotly_chart(fig_heat, width="stretch")
            else:
                st.info("Sem dados suficientes para o mapa de calor com os filtros selecionados.")

# ──────────────────────────────────────────────────────────────
# TAB 9 — ML (era tab10)
# ──────────────────────────────────────────────────────────────
with tab9:
    ml_tab, opt_tab = st.tabs(["🧬 Predição ML","📊 Histórico de Scouts"])

    with ml_tab:
        st.markdown("### 🧬 Predição de Valorização com ML")
        st.caption("Ridge Regression: estima variação de C$ na próxima rodada com base em scouts históricos.")
        try:
            from sklearn.linear_model import Ridge
            from sklearn.preprocessing import StandardScaler
            from sklearn.pipeline import Pipeline

            FEATS_ML = ["pontos","G","A","FT","DS","FS","FC","CA","GS","DE","SG","preco"]
            for f in FEATS_ML:
                if f not in df.columns: df[f] = 0

            df_ml = df[df["preco"] > 0].sort_values(["atleta_id","rodada_id"]).copy()
            df_ml["preco_prox"]  = df_ml.groupby("atleta_id")["preco"].shift(-1)
            df_ml["delta_preco"] = df_ml["preco_prox"] - df_ml["preco"]
            # Treina apenas com variações reais — remove linhas onde delta=0
            # (preço estático não ensina nada ao modelo)
            df_ml = df_ml.dropna(subset=["delta_preco"] + FEATS_ML)
            df_ml_treino = df_ml[df_ml["delta_preco"] != 0].copy()

            X_all = df_ml[FEATS_ML].values
            y_all = df_ml["delta_preco"].values
            X_tr  = df_ml_treino[FEATS_ML].values
            y_tr  = df_ml_treino["delta_preco"].values

            pct_com_variacao = len(df_ml_treino) / max(len(df_ml), 1) * 100

            if len(X_tr) < 20:
                st.warning(
                    f"Poucas variações de preço detectadas ({len(df_ml_treino)} linhas com Δ≠0 "
                    f"de {len(df_ml)} total = {pct_com_variacao:.0f}%). "
                    "O modelo precisa de mais rodadas com preços variando para ser confiável. "
                    "Isso é normal nas primeiras rodadas da temporada."
                )
            else:
                # Treina com linhas que tiveram variação real
                modelo = Pipeline([("sc", StandardScaler()), ("ridge", Ridge(alpha=0.5))])
                modelo.fit(X_tr, y_tr)

                X_pred = np.column_stack([
                    df_agrupado[f].values if f in df_agrupado.columns else np.zeros(len(df_agrupado))
                    for f in FEATS_ML
                ])
                df_agrupado["delta_pred"] = modelo.predict(X_pred)
                coef    = modelo.named_steps["ridge"].coef_
                df_coef = pd.DataFrame({"Feature": FEATS_ML, "Importância": np.abs(coef)}).sort_values("Importância")

                # Métricas de qualidade do modelo
                from sklearn.metrics import mean_absolute_error
                y_hat = modelo.predict(X_tr)
                mae   = mean_absolute_error(y_tr, y_hat)

                m1, m2, m3 = st.columns(3)
                m1.metric("Linhas de treino",    f"{len(df_ml_treino)}")
                m2.metric("MAE do modelo",       f"C$ {mae:.3f}", help="Erro médio absoluto — quanto o modelo erra em média")
                m3.metric("Registros c/ Δ≠0",    f"{pct_com_variacao:.0f}%")

                col_p, col_i = st.columns([3, 2])
                with col_p:
                    st.markdown("#### Top valorizações previstas")
                    top_pred = (
                        df_agrupado[["apelido","clube_nome","posicao_nome","preco","status_txt",
                                     "delta_pred","delta_preco_real"]]
                        .sort_values("delta_pred", ascending=False)
                        .head(15)
                    )
                    st.dataframe(top_pred,
                        column_config={
                            "apelido":          "Atleta",
                            "clube_nome":       "Clube",
                            "posicao_nome":     "Posição",
                            "status_txt":       "Status",
                            "preco":            st.column_config.NumberColumn("C$ Atual",   format="%.2f"),
                            "delta_pred":       st.column_config.NumberColumn("Δ C$ Prev.", format="%+.2f"),
                            "delta_preco_real": st.column_config.NumberColumn("Δ C$ Real",  format="%+.2f"),
                        }, hide_index=True, width="stretch")
                with col_i:
                    st.markdown("#### Fatores mais relevantes")
                    fig_imp = px.bar(df_coef, x="Importância", y="Feature", orientation="h",
                                     color="Importância", color_continuous_scale="Greens")
                    _ti = {k: v for k, v in THEME.items() if k != "yaxis"}
                    fig_imp.update_layout(**_ti, showlegend=False,
                                         yaxis=dict(title="", gridcolor="#F3F4F6"))
                    st.plotly_chart(fig_imp, width="stretch")
                st.info(
                    f"⚠️ Modelo treinado com {len(df_ml_treino)} observações reais de variação de preço. "
                    "Resultados ficam mais precisos conforme mais rodadas são acumuladas. "
                    "Use como sinal complementar, não como verdade absoluta."
                )
        except ImportError:
            st.error("❌ `scikit-learn` não instalado. Adicione ao `requirements.txt` e faça o redeploy.")

    with opt_tab:
        st.markdown("### 📊 Histórico de Scouts por Atleta")
        st.caption("Selecione um atleta e os scouts para ver a evolução rodada a rodada.")

        def _render_scout_history(apelido_sel: str):
            """Renderiza gráfico + tabela de scouts de um atleta."""
            scouts_disp = [s for s in SCOUTS if s in df.columns]
            sel_sc = st.multiselect(
                "Scouts:", scouts_disp,
                default=["G","A","DS","FC","CA"],
                key=f"sc_{apelido_sel}"
            )
            if not sel_sc:
                return
            df_hist = df[df["apelido"] == apelido_sel].sort_values("rodada_id")
            cols_hist = ["rodada_id"] + sel_sc + ["pontos","adversario","mando"]
            df_hist = df_hist[[c for c in cols_hist if c in df_hist.columns]]
            if df_hist.empty:
                st.warning("Sem histórico para este atleta.")
                return
            fig_sc = go.Figure()
            for s in sel_sc:
                if s in df_hist.columns:
                    fig_sc.add_trace(go.Bar(name=s, x=df_hist["rodada_id"], y=df_hist[s], opacity=0.75))
            fig_sc.add_trace(go.Scatter(
                name="Pontos", x=df_hist["rodada_id"], y=df_hist["pontos"],
                mode="lines+markers", line=dict(color="#E09B00", width=2.5),
                marker=dict(size=6), yaxis="y2",
            ))
            _tsc = {k: v for k, v in THEME.items() if k not in ("xaxis","yaxis")}
            fig_sc.update_layout(
                **_tsc, barmode="stack",
                xaxis=dict(title="Rodada", tickmode="linear", dtick=1,
                           gridcolor="#F3F4F6", linecolor="#E4E6EB", tickfont=dict(color="#6B7280")),
                yaxis=dict(title="Scouts", gridcolor="#F3F4F6", linecolor="#E4E6EB",
                           tickfont=dict(color="#6B7280")),
                yaxis2=dict(title="Pontos", overlaying="y", side="right",
                            showgrid=False, tickfont=dict(color="#E09B00")),
                height=340,
            )
            st.plotly_chart(fig_sc, width="stretch")
            st.dataframe(
                df_hist.rename(columns={"rodada_id":"Rodada","pontos":"Pts",
                                        "adversario":"Adversário","mando":"Mando"}),
                hide_index=True, width="stretch",
            )

        atletas_todos = sorted(df_agrupado["apelido"].unique())
        sel_scout_atl = st.selectbox("Atleta:", atletas_todos, key="scout_hist_atl")
        if sel_scout_atl:
            _render_scout_history(sel_scout_atl)
