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
    """Carrega histórico completo do Supabase."""
    try:
        res = (
            cliente.table("historico_cartola")
            .select("*")
            .order("rodada_id")
            .execute()
        )
        if res.data:
            df = pd.DataFrame(res.data)
            log.info("Supabase: %d registros carregados (até rodada %d).",
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
# Calcula delta de preço entre a penúltima e a última rodada disponível
rodadas_ord = sorted(df["rodada_id"].unique())
if len(rodadas_ord) >= 2:
    df_ult  = df[df["rodada_id"] == rodadas_ord[-1]][["atleta_id", "preco"]].rename(columns={"preco": "preco_ult"})
    df_pen  = df[df["rodada_id"] == rodadas_ord[-2]][["atleta_id", "preco"]].rename(columns={"preco": "preco_pen"})
    df_delta = df_ult.merge(df_pen, on="atleta_id", how="left")
    df_delta["delta_preco_real"] = df_delta["preco_ult"] - df_delta["preco_pen"].fillna(df_delta["preco_ult"])
    df_agrupado = df_agrupado.merge(df_delta[["atleta_id", "delta_preco_real"]], on="atleta_id", how="left")
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📅 Jogos", "🤖 Robô", "📊 Tática", "📈 Mercado", "🏆 Destaques",
    "🎯 Capitão", "🔬 Raio-X", "🔮 Projeção", "💹 Valorização", "🧬 ML & Otimizador",
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
        if not df_tabela.empty and "PJ" in df_tabela.columns:
            sec("CLASSIFICAÇÃO — BRASILEIRÃO 2026")
            st.dataframe(df_tabela, hide_index=True, use_container_width=True, height=600)
        elif not df_tabela.empty:
            sec("CLASSIFICAÇÃO — GERADA A PARTIR DO HISTÓRICO")
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
            so_com_jogo = st.checkbox("Somente atletas com jogo", value=True)
            col_crit = "indice_pro"
            if "Média Geral" in criterio:       col_crit = "media_geral"
            elif "Pontuação Básica" in criterio: col_crit = "media_basica"
            gerar = st.button("⚡ Gerar Time", use_container_width=True)

        with col_res:
            if gerar:
                ESQUEMAS = {
                    "4-3-3": {"Goleiro":1,"Lateral":2,"Zagueiro":2,"Meia":3,"Atacante":3,"Técnico":1},
                    "3-5-2": {"Goleiro":1,"Lateral":0,"Zagueiro":3,"Meia":5,"Atacante":2,"Técnico":1},
                    "3-4-3": {"Goleiro":1,"Lateral":0,"Zagueiro":3,"Meia":4,"Atacante":3,"Técnico":1},
                }
                meta = ESQUEMAS.get(esq, ESQUEMAS["4-3-3"])
                pool = df_agrupado[df_agrupado["status_txt"] == "Provável"].sort_values(col_crit, ascending=False)
                if so_com_jogo:
                    pool = pool[pool["mando"] != "Sem Jogo"]
                if pool.empty:
                    pool = df_agrupado.sort_values(col_crit, ascending=False)

                time_final = [
                    pool[pool["posicao_nome"] == pos].head(qtd)
                    for pos, qtd in meta.items() if qtd > 0
                ]
                if time_final:
                    df_time     = pd.concat(time_final)
                    custo_total = df_time["preco"].sum()
                    loops       = 0
                    while custo_total > orc and loops < 100:
                        df_time = df_time.sort_values("preco", ascending=False)
                        troca   = False
                        for idx, jc in df_time.iterrows():
                            cands = pool[
                                (pool["posicao_nome"] == jc["posicao_nome"]) &
                                (pool["preco"] < jc["preco"]) &
                                (~pool["atleta_id"].isin(df_time["atleta_id"]))
                            ]
                            if not cands.empty:
                                df_time     = pd.concat([df_time.drop(idx), cands.iloc[0].to_frame().T])
                                custo_total = df_time["preco"].sum()
                                troca = True; break
                        if not troca: break
                        loops += 1

                    ordem = ["Goleiro","Lateral","Zagueiro","Meia","Atacante","Técnico"]
                    df_time["posicao_nome"] = pd.Categorical(df_time["posicao_nome"], categories=ordem, ordered=True)
                    df_time = df_time.sort_values("posicao_nome")

                    if custo_total > orc:
                        st.error("❌ Não foi possível montar um time dentro do orçamento.")
                    else:
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Score Projetado", f"{df_time[col_crit].sum():.1f}")
                        c2.metric("Custo Total",     f"C$ {custo_total:.2f}", f"Saldo: C$ {orc-custo_total:.2f}")
                        c3.metric("Atletas",         f"{len(df_time)}")
                        st.dataframe(
                            df_time[["foto","status","posicao_nome","apelido","clube_nome",
                                     "mando","adversario_prox","preco","indice_pro","media_geral","media_basica"]],
                            column_config={
                                "foto":           st.column_config.ImageColumn("Perfil"),
                                "status":         "Status",   "posicao_nome":    "Posição",
                                "apelido":        "Jogador",  "clube_nome":      "Clube",
                                "mando":          "Mando",    "adversario_prox": "Adv.",
                                "preco":          st.column_config.NumberColumn("C$",          format="%.2f"),
                                "indice_pro":     st.column_config.NumberColumn("Índice PRO ✨",format="%.2f"),
                                "media_geral":    st.column_config.NumberColumn("Média",       format="%.2f"),
                                "media_basica":   st.column_config.NumberColumn("Básica",      format="%.2f"),
                            },
                            hide_index=True, use_container_width=True,
                        )

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
            st.plotly_chart(fig, use_container_width=True)

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
            st.dataframe(comp_df, hide_index=True, use_container_width=True)

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
            themed(fig); st.plotly_chart(fig, use_container_width=True)
    with hm2:
        sec("PODER OFENSIVO — PONTOS FEITOS POR POSIÇÃO")
        heat2 = df.groupby(["clube_nome","posicao_nome"])["pontos"].mean().reset_index()
        if not heat2.empty:
            piv2 = heat2.pivot(index="clube_nome", columns="posicao_nome", values="pontos").fillna(0)
            fig2 = px.imshow(piv2, text_auto=".1f", color_continuous_scale="Greens", aspect="auto")
            themed(fig2); st.plotly_chart(fig2, use_container_width=True)
    with hm3:
        sec("DESEMPENHO: CASA × FORA")
        stats_mando = df.groupby(["clube_nome","mando"])["pontos"].mean().reset_index()
        fig_pts = px.bar(stats_mando, x="clube_nome", y="pontos", color="mando", barmode="group",
                         labels={"pontos":"Média","clube_nome":"Time"},
                         color_discrete_map={"CASA":"#00A878","FORA":"#1A6EFF"})
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
        use_container_width=True, hide_index=True, height=560,
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
        themed(fig_box); st.plotly_chart(fig_box, use_container_width=True)

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
# TAB 7 — RAIO-X DO CONFRONTO
# ──────────────────────────────────────────────────────────────
with tab7:
    st.markdown("### 🔬 Raio-X do Confronto")
    st.caption("Histórico direto entre dois times + fragilidade defensiva por posição.")

    times_disp = sorted(df["clube_nome"].astype(str).unique())
    c1, c2     = st.columns(2)
    time_a = c1.selectbox("Time A", times_disp, key="rx_a")
    time_b = c2.selectbox("Time B", times_disp, index=1 if len(times_disp)>1 else 0, key="rx_b")

    if time_a == time_b:
        st.warning("Selecione times diferentes.")
    else:
        df_dir = df[
            ((df["clube_nome"]==time_a)&(df["adversario"]==time_b)) |
            ((df["clube_nome"]==time_b)&(df["adversario"]==time_a))
        ]
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Confrontos no histórico", len(df_dir["rodada_id"].unique()) if not df_dir.empty else 0)
        if not df_dir.empty:
            ma = df_dir[df_dir["clube_nome"]==time_a]["pontos"].mean()
            mb = df_dir[df_dir["clube_nome"]==time_b]["pontos"].mean()
            col_r2.metric(f"Média {time_a}", f"{ma:.2f}")
            col_r3.metric(f"Média {time_b}", f"{mb:.2f}")

            st.divider()
            heat_rx = df_dir.groupby(["clube_nome","posicao_nome"])["pontos"].mean().reset_index()
            piv_rx  = heat_rx.pivot(index="clube_nome", columns="posicao_nome", values="pontos").fillna(0)
            fig_rx  = px.imshow(piv_rx, text_auto=".1f", color_continuous_scale="Blues", aspect="auto")
            themed(fig_rx); st.plotly_chart(fig_rx, use_container_width=True)

            st.divider()
            st.markdown(f"**Top atletas de {time_a} contra {time_b}**")
            top_rx = (df_dir[df_dir["clube_nome"]==time_a]
                      .groupby("apelido")
                      .agg(media_pts=("pontos","mean"), jogos=("rodada_id","count"))
                      .reset_index().sort_values("media_pts", ascending=False).head(10))
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
        df_ced = df[df["adversario"]==time_b].groupby("posicao_nome")["pontos"].mean().reset_index()
        df_ced.columns = ["Posição","Média cedida"]
        df_ced = df_ced.sort_values("Média cedida", ascending=False)
        fig_ced = px.bar(df_ced, x="Posição", y="Média cedida",
                         color="Média cedida", color_continuous_scale="Reds", text_auto=".1f")
        themed(fig_ced); st.plotly_chart(fig_ced, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 8 — PROJEÇÃO + FORMA RECENTE
# ──────────────────────────────────────────────────────────────
with tab8:
    proj_tab, forma_tab = st.tabs(["🔮 Projeção por Scout","📅 Forma Recente"])

    with proj_tab:
        st.markdown("### 🔮 Projeção de Pontuação")
        st.caption("Estima pontuação esperada com base na média de scouts contra o adversário.")
        PESOS_PROJ = {"G":8.0,"A":5.0,"FT":3.0,"FD":1.2,"FF":0.8,"FS":0.5,"PS":1.0,
                      "DE":1.0,"DS":1.5,"FC":-0.3,"PC":-1.0,"CA":-1.0,"CV":-3.0,"GS":-1.0,"I":-0.1,"SG":5.0}

        atletas_c_jogo = df_agrupado[df_agrupado["mando"] != "Sem Jogo"]["apelido"].unique()
        if len(atletas_c_jogo) == 0:
            st.warning("Nenhum atleta com jogo confirmado para projeção.")
        else:
            sel_proj = st.multiselect("Atletas (máx. 10):", sorted(atletas_c_jogo),
                                      default=list(sorted(atletas_c_jogo))[:5], max_selections=10)
            if sel_proj:
                rows_proj = []
                for apelido in sel_proj:
                    row_ag = df_agrupado[df_agrupado["apelido"] == apelido].iloc[0]
                    clube  = row_ag["clube_nome"]
                    adv    = mapa_confrontos.get(clube, {}).get("adv", None)
                    df_at  = df[df["apelido"] == apelido]
                    df_vs  = df_at[df_at["adversario"] == adv] if adv else df_at
                    if df_vs.empty: df_vs = df_at
                    proj = sum(df_vs[s].mean()*p for s,p in PESOS_PROJ.items() if s in df_vs.columns)
                    rows_proj.append({
                        "Atleta": apelido, "Clube": clube, "Adv": adv or "-", "Mando": row_ag["mando"],
                        "Proj Min": proj*0.70, "Proj Med": proj, "Proj Máx": proj*1.30,
                    })
                df_proj = pd.DataFrame(rows_proj).sort_values("Proj Med", ascending=False)
                st.dataframe(df_proj,
                    column_config={
                        "Proj Min": st.column_config.NumberColumn(format="%.1f"),
                        "Proj Med": st.column_config.NumberColumn(format="%.1f"),
                        "Proj Máx": st.column_config.NumberColumn(format="%.1f"),
                    }, hide_index=True, use_container_width=True)
                fig_proj = px.bar(df_proj, x="Atleta", y="Proj Med",
                                  error_y=df_proj["Proj Máx"]-df_proj["Proj Med"],
                                  error_y_minus=df_proj["Proj Med"]-df_proj["Proj Min"],
                                  color="Mando", text_auto=".1f",
                                  color_discrete_map={"CASA":"#00A878","FORA":"#1A6EFF","Sem Jogo":"#9CA3AF"})
                themed(fig_proj); st.plotly_chart(fig_proj, use_container_width=True)
                st.caption("Barras de erro = ±30% sobre a projeção central.")

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
        st.plotly_chart(fig_forma, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 9 — VALORIZAÇÃO (NOVA)
# ──────────────────────────────────────────────────────────────
with tab9:
    st.markdown("### 💹 Tendência de Valorização")
    st.caption("Curva de preço C$ ao longo das rodadas por atleta.")

    val_tab1, val_tab2, val_tab3 = st.tabs([
        "📈 Curva de Preço", "🏆 Mais Valorizados", "📉 Mais Desvalorizados"
    ])

    with val_tab1:
        sec("EVOLUÇÃO DE PREÇO — HISTÓRICO POR RODADA")
        atletas_disp = sorted(df_agrupado.sort_values("indice_pro", ascending=False)["apelido"].unique())
        sel_val = st.multiselect(
            "Selecione atletas:", atletas_disp,
            default=list(atletas_disp[:5]), max_selections=8, key="val_sel"
        )
        if sel_val:
            df_curva = df[df["apelido"].isin(sel_val)][["rodada_id","apelido","preco"]].copy()
            df_curva = df_curva.groupby(["rodada_id","apelido"])["preco"].last().reset_index()
            fig_curva = px.line(
                df_curva, x="rodada_id", y="preco", color="apelido",
                labels={"rodada_id":"Rodada","preco":"Preço (C$)","apelido":"Atleta"},
                markers=True, color_discrete_sequence=COLORS,
            )
            themed(fig_curva)
            fig_curva.update_traces(line=dict(width=2))
            st.plotly_chart(fig_curva, use_container_width=True)
        else:
            st.info("Selecione ao menos um atleta.")

    with val_tab2:
        sec("ATLETAS QUE MAIS VALORIZARAM (ΔTOTAL)")
        if len(rodadas_ord) >= 2:
            df_val = df.groupby("atleta_id").agg(
                apelido=("apelido","last"),
                clube_nome=("clube_nome","last"),
                posicao_nome=("posicao_nome","last"),
                preco_ini=("preco","first"),
                preco_fim=("preco","last"),
                jogos=("rodada_id","count"),
            ).reset_index()
            df_val["delta_total"] = df_val["preco_fim"] - df_val["preco_ini"]
            df_val["delta_pct"]   = ((df_val["delta_total"] / df_val["preco_ini"]) * 100).replace([np.inf,-np.inf], 0).fillna(0)
            top_val = df_val.sort_values("delta_total", ascending=False).head(20)
            fig_val = px.bar(
                top_val, x="apelido", y="delta_total", color="posicao_nome",
                text=top_val["delta_total"].apply(lambda v: f"+C${v:.2f}"),
                labels={"apelido":"Atleta","delta_total":"Δ Preço (C$)","posicao_nome":"Posição"},
                color_discrete_sequence=COLORS,
            )
            themed(fig_val); fig_val.update_layout(xaxis_tickangle=-45)
            fig_val.update_traces(textposition="outside")
            st.plotly_chart(fig_val, use_container_width=True)
            st.dataframe(
                top_val[["apelido","clube_nome","posicao_nome","preco_ini","preco_fim","delta_total","delta_pct","jogos"]],
                column_config={
                    "apelido":     "Atleta",
                    "clube_nome":  "Clube",
                    "posicao_nome":"Posição",
                    "preco_ini":   st.column_config.NumberColumn("C$ Início", format="%.2f"),
                    "preco_fim":   st.column_config.NumberColumn("C$ Atual",  format="%.2f"),
                    "delta_total": st.column_config.NumberColumn("Δ Total",   format="%+.2f"),
                    "delta_pct":   st.column_config.NumberColumn("Δ %",       format="%+.1f%%"),
                    "jogos":       st.column_config.NumberColumn("Jogos",     format="%d"),
                },
                hide_index=True, use_container_width=True,
            )
        else:
            st.info("Necessário pelo menos 2 rodadas para calcular valorização.")

    with val_tab3:
        sec("ATLETAS QUE MAIS DESVALORIZARAM (ΔTOTAL)")
        if len(rodadas_ord) >= 2:
            bot_val = df_val.sort_values("delta_total", ascending=True).head(20)
            fig_desval = px.bar(
                bot_val, x="apelido", y="delta_total", color="posicao_nome",
                text=bot_val["delta_total"].apply(lambda v: f"C${v:.2f}"),
                labels={"apelido":"Atleta","delta_total":"Δ Preço (C$)","posicao_nome":"Posição"},
                color_discrete_sequence=COLORS,
            )
            themed(fig_desval); fig_desval.update_layout(xaxis_tickangle=-45)
            fig_desval.update_traces(textposition="outside")
            st.plotly_chart(fig_desval, use_container_width=True)
        else:
            st.info("Necessário pelo menos 2 rodadas para calcular valorização.")

# ──────────────────────────────────────────────────────────────
# TAB 10 — ML & OTIMIZADOR
# ──────────────────────────────────────────────────────────────
with tab10:
    ml_tab, opt_tab = st.tabs(["🧬 Predição ML","⚙️ Otimizador PuLP"])

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

            df_ml = df.sort_values(["atleta_id","rodada_id"]).copy()
            df_ml["preco_prox"]  = df_ml.groupby("atleta_id")["preco"].shift(-1)
            df_ml["delta_preco"] = df_ml["preco_prox"] - df_ml["preco"]
            df_ml = df_ml.dropna(subset=["delta_preco"]+FEATS_ML)

            X = df_ml[FEATS_ML].values
            y = df_ml["delta_preco"].values

            if len(X) < 30:
                st.warning("Dados insuficientes para treinar o modelo. Aguarde mais rodadas.")
            else:
                modelo = Pipeline([("sc", StandardScaler()), ("ridge", Ridge(alpha=1.0))])
                modelo.fit(X, y)
                X_pred = np.column_stack([
                    df_agrupado[f].values if f in df_agrupado.columns else np.zeros(len(df_agrupado))
                    for f in FEATS_ML
                ])
                df_agrupado["delta_pred"] = modelo.predict(X_pred)
                coef    = modelo.named_steps["ridge"].coef_
                df_coef = pd.DataFrame({"Feature":FEATS_ML,"Importância":np.abs(coef)}).sort_values("Importância")

                col_p, col_i = st.columns([3,2])
                with col_p:
                    st.markdown("#### Top valorizações previstas")
                    top_pred = df_agrupado[["apelido","clube_nome","posicao_nome","preco","status_txt","delta_pred",
                                            "delta_preco_real"]]\
                        .sort_values("delta_pred", ascending=False).head(15)
                    st.dataframe(top_pred,
                        column_config={
                            "apelido":          "Atleta",
                            "clube_nome":       "Clube",
                            "posicao_nome":     "Posição",
                            "status_txt":       "Status",
                            "preco":            st.column_config.NumberColumn("C$ Atual",   format="%.2f"),
                            "delta_pred":       st.column_config.NumberColumn("Δ C$ Prev.", format="%+.2f"),
                            "delta_preco_real": st.column_config.NumberColumn("Δ C$ Real",  format="%+.2f"),
                        }, hide_index=True, use_container_width=True)
                with col_i:
                    st.markdown("#### Fatores mais relevantes")
                    fig_imp = px.bar(df_coef, x="Importância", y="Feature", orientation="h",
                                     color="Importância", color_continuous_scale="Greens")
                    themed(fig_imp); fig_imp.update_layout(showlegend=False, yaxis_title="")
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
                status_opt = st.multiselect("Status aceitos:", ["Provável","Dúvida","Sem Status"],
                                            default=["Provável"], key="opt_st")
                max_time   = st.number_input("Máx. por time", min_value=1, max_value=5, value=5, key="opt_mt")
                so_jogo_opt = st.checkbox("Somente com jogo", value=True, key="opt_jogo")
                btn_opt    = st.button("🚀 Otimizar", use_container_width=True)
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
                        st.warning("Nenhum atleta disponível com os status selecionados.")
                    else:
                        prob   = pulp.LpProblem("cartola", pulp.LpMaximize)
                        n      = len(pool)
                        ids    = list(range(n))
                        x      = pulp.LpVariable.dicts("x", ids, cat="Binary")
                        prob  += pulp.lpSum(pool.iloc[i]["indice_pro"]*x[i] for i in ids)
                        prob  += pulp.lpSum(pool.iloc[i]["preco"]*x[i]      for i in ids) <= orc_opt
                        for pos, qtd in meta_opt.items():
                            ip = [i for i in ids if pool.iloc[i]["posicao_nome"] == pos]
                            prob += pulp.lpSum(x[i] for i in ip) == qtd
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
                            score  = df_opt["indice_pro"].sum()
                            st.success(f"✅ Escalação ótima! Custo: C$ {custo:.2f} | Score PRO: {score:.2f}")
                            st.dataframe(
                                df_opt[["foto","status","posicao_nome","apelido","clube_nome",
                                        "mando","adversario_prox","preco","indice_pro","media_geral"]],
                                column_config={
                                    "foto":           st.column_config.ImageColumn("Perfil"),
                                    "status":         "Status",   "posicao_nome":    "Posição",
                                    "apelido":        "Jogador",  "clube_nome":      "Clube",
                                    "mando":          "Mando",    "adversario_prox": "Adv.",
                                    "preco":          st.column_config.NumberColumn("C$",           format="%.2f"),
                                    "indice_pro":     st.column_config.NumberColumn("Índice PRO ✨", format="%.2f"),
                                    "media_geral":    st.column_config.NumberColumn("Média",        format="%.2f"),
                                }, hide_index=True, use_container_width=True)
                            st.info("💡 PuLP avalia todas as combinações e garante o ótimo global.")
                        else:
                            st.error("❌ Sem solução viável. Aumente o orçamento ou aceite mais status.")
        except ImportError:
            st.error("❌ `pulp` não instalado. Adicione ao `requirements.txt` e faça o redeploy.")
