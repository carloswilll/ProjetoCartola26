import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import re
import io
import numpy as np
from supabase import create_client, Client

# ─────────────────────────────────────────────────────────────
# 1. CONFIGURAÇÕES VISUAIS
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cartola Pro 2026",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1rem; font-weight: 600;
    }
    div[data-testid="metric-container"] {
        background-color: #1E1E2E;
        border: 0.5px solid #333;
        padding: 12px 16px;
        border-radius: 10px;
    }
    @media (max-width: 640px) {
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
        .stPlotlyChart { height: 280px !important; }
        [data-testid="stDataFrame"] { font-size: 12px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 2. CONEXÃO SUPABASE
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def conectar_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = conectar_supabase()

@st.cache_data(ttl=300)
def carregar_historico() -> pd.DataFrame:
    try:
        resposta = supabase.table("historico_cartola").select("*").execute()
        if resposta.data:
            return pd.DataFrame(resposta.data)
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar histórico: {e}")
    return pd.DataFrame()

def salvar_novas_rodadas(novos: list):
    if not novos:
        return
    try:
        for i in range(0, len(novos), 500):
            supabase.table("historico_cartola").insert(novos[i:i+500]).execute()
    except Exception as e:
        st.error(f"❌ Erro ao salvar no Supabase: {e}")

# ─────────────────────────────────────────────────────────────
# 3. FUNÇÕES DE API
# ─────────────────────────────────────────────────────────────
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
            "Accept":     "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        res    = requests.get(url, headers=headers, timeout=15)
        dfs    = pd.read_html(io.StringIO(res.text))
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

# ─────────────────────────────────────────────────────────────
# 4. BANCO DE DADOS
# ─────────────────────────────────────────────────────────────
def gerenciar_banco_dados() -> pd.DataFrame:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        status        = requests.get("https://api.cartola.globo.com/mercado/status", headers=headers, timeout=10).json()
        rodada_atual  = status['rodada_atual']
        ultima_rodada = rodada_atual - 1 if status['status_mercado'] == 1 else rodada_atual
    except Exception as e:
        st.warning(f"⚠️ Não foi possível checar a rodada atual: {e}")
        return pd.DataFrame()

    df              = carregar_historico()
    ultima_no_banco = int(df['rodada_id'].max()) if not df.empty else 0

    if ultima_rodada <= ultima_no_banco:
        return df

    container = st.empty()
    container.info(f"🔄 Baixando rodadas {ultima_no_banco+1} a {ultima_rodada}...")
    novos = []

    try:
        mercado       = requests.get("https://api.cartola.globo.com/atletas/mercado", headers=headers, timeout=15).json()
        dict_clubes   = {int(k): v['nome'] for k, v in mercado['clubes'].items()}
        dict_posicoes = {int(k): v['nome'] for k, v in mercado['posicoes'].items()}
        precos_atuais = {a['atleta_id']: a['preco_num'] for a in mercado['atletas']}
    except Exception as e:
        st.warning(f"⚠️ Erro ao buscar dicionários: {e}")
        dict_clubes, dict_posicoes, precos_atuais = {}, {}, {}

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
                    mapa_jogos[cid] = {'mando': 'CASA', 'adversario': dict_clubes.get(vid, 'Visitante'), 'local': local, 'data': dt}
                    mapa_jogos[vid] = {'mando': 'FORA', 'adversario': dict_clubes.get(cid, 'Mandante'),  'local': local, 'data': dt}
            if pontuados and 'atletas' in pontuados:
                for pid, dados in pontuados['atletas'].items():
                    pid   = int(pid)
                    cid   = dados['clube_id']
                    jogo  = mapa_jogos.get(cid, {'mando': '-', 'adversario': '-', 'local': '-', 'data': '-'})
                    preco = dados.get('preco_num') or dados.get('preco') or precos_atuais.get(pid, 0)
                    linha = {
                        'rodada_id':    r,    'atleta_id':    pid,
                        'apelido':      dados.get('apelido', f'Jog {pid}'),
                        'foto':         dados.get('foto', '').replace('FORMATO', '140x140'),
                        'clube_nome':   dict_clubes.get(cid, 'Outro'),
                        'posicao_nome': dict_posicoes.get(dados['posicao_id'], 'Outro'),
                        'pontos':       dados.get('pontuacao', 0),
                        'preco':        preco,
                        'media':        dados.get('media', 0),
                        'mando':        jogo['mando'],   'adversario': jogo['adversario'],
                        'estadio':      jogo['local'],   'data_jogo':  jogo['data'],
                    }
                    linha.update(dados.get('scout') or {})
                    novos.append(linha)
        except Exception as e:
            st.toast(f"⚠️ Erro na rodada {r}: {e}", icon="⚠️")
            continue

    if novos:
        df_novo = pd.DataFrame(novos).fillna(0)
        salvar_novas_rodadas(df_novo.to_dict('records'))
        carregar_historico.clear()
        container.empty()
        return pd.concat([df, df_novo], ignore_index=True)

    container.empty()
    return df

# ─────────────────────────────────────────────────────────────
# 5. PROCESSAMENTO PRINCIPAL
# ─────────────────────────────────────────────────────────────
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
    (df['DS']*1.5) + (df['FS']*0.5) + (df['FF']*0.8) + (df['FD']*1.2) +
    (df['FT']*3.0) + (df['DE']*1.0) + (df['PS']*1.0) +
    (df['FC']*-0.3) + (df['PC']*-1.0) + (df['CA']*-1.0) +
    (df['CV']*-3.0) + (df['GS']*-1.0) + (df['I']*-0.1)
)
df['participacao_gol'] = df['G'] + df['A']
df['finalizacoes']     = df['FD'] + df['FF'] + df['FT']

# ── SIDEBAR ──────────────────────────────────────────────────
st.sidebar.title("⚙️ Painel de Controle")
contagem_jogos = df.groupby('atleta_id')['rodada_id'].nunique()
max_jogos      = int(contagem_jogos.max()) if not contagem_jogos.empty else 1
min_jogos      = st.sidebar.slider("Mínimo de Jogos Disputados:", 1, max_jogos, 1)
st.sidebar.divider()

lista_clubes   = sorted(df['clube_nome'].astype(str).unique())
lista_posicoes = sorted(df['posicao_nome'].astype(str).unique())
sel_clube      = st.sidebar.multiselect("Filtrar Clube",   lista_clubes,   default=lista_clubes)
sel_posicao    = st.sidebar.multiselect("Filtrar Posição", lista_posicoes, default=lista_posicoes)

df_filtrado = df[
    (df['clube_nome'].isin(sel_clube)) &
    (df['posicao_nome'].isin(sel_posicao))
]

agg_rules = {
    'rodada_id':'count', 'pontos':'mean', 'pontuacao_basica':'mean',
    'preco':'last', 'clube_nome':'last', 'posicao_nome':'last',
    'foto':'last', 'participacao_gol':'sum', 'finalizacoes':'sum', 'apelido':'last',
}
for s in scouts_cols:
    agg_rules[s] = 'sum'

df_agrupado = df_filtrado.groupby('atleta_id').agg(agg_rules).reset_index()
df_agrupado.rename(columns={
    'pontos':'media_geral', 'pontuacao_basica':'media_basica', 'rodada_id':'jogos_disputados'
}, inplace=True)
df_agrupado = df_agrupado[df_agrupado['jogos_disputados'] >= min_jogos]

status_dict              = pegar_status_atletas()
df_agrupado['status_txt'] = df_agrupado['atleta_id'].map(status_dict).fillna('Sem Status')

def formatar_status(s):
    mapa = {'Provável':'✅ Provável','Dúvida':'❓ Dúvida',
            'Suspenso':'🟥 Suspenso','Contundido':'🚑 Contundido','Nulo':'❌ Nulo'}
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

media_cedida_adv     = df.groupby(['adversario',  'posicao_nome'])['pontos'].mean().to_dict()
media_feita_time     = df.groupby(['clube_nome',  'posicao_nome'])['pontos'].mean().to_dict()
media_posicao_global = df.groupby('posicao_nome')['pontos'].mean().to_dict()

def calcular_indice_pro(row):
    clube = row['clube_nome']
    pos   = row['posicao_nome']
    if not mapa_confrontos or clube not in mapa_confrontos:
        return row['media_geral'] * 0.1
    info         = mapa_confrontos[clube]
    fator_mando  = 1.15 if info['mando'] == 'CASA' else 0.85
    adv          = info['adv']
    pts_cedidos  = media_cedida_adv.get((adv, pos),   media_posicao_global.get(pos, 0))
    pts_feitos   = media_feita_time.get((clube, pos), media_posicao_global.get(pos, 0))
    forca_tatica = (pts_cedidos + pts_feitos) / 2
    pos_meu      = obter_pos_tabela(clube)
    pos_adv      = obter_pos_tabela(adv)
    fator_fav    = 1 + ((pos_adv - pos_meu) * 0.008)
    base_score   = (row['media_geral']*0.4) + (row['media_basica']*0.3) + (forca_tatica*0.3)
    return base_score * fator_mando * fator_fav

df_agrupado['indice_pro']      = df_agrupado.apply(calcular_indice_pro, axis=1)
df_agrupado['custo_beneficio'] = df_agrupado.apply(
    lambda r: r['indice_pro'] / r['preco'] if r['preco'] > 0 else 0, axis=1
)

# ── KPIs ─────────────────────────────────────────────────────
st.title("⚽ Cartola Pro 2026 — Dashboard Analítico")
k1, k2, k3, k4 = st.columns(4)
if not df_agrupado.empty:
    top_pro    = df_agrupado.sort_values('indice_pro',       ascending=False).iloc[0]
    top_reg    = df_agrupado.sort_values('media_basica',     ascending=False).iloc[0]
    artilheiro = df_agrupado.sort_values('participacao_gol', ascending=False).iloc[0]
    ladrao     = df_agrupado.sort_values('DS',               ascending=False).iloc[0]
    k1.metric("🤖 Top Índice PRO",   top_pro['apelido'],    f"Score: {top_pro['indice_pro']:.2f}")
    k2.metric("💎 Rei Regularidade", top_reg['apelido'],    f"Básica: {top_reg['media_basica']:.1f} pts")
    k3.metric("🔥 Mais Decisivo",    artilheiro['apelido'], f"{int(artilheiro['participacao_gol'])} G+A")
    k4.metric("🛑 Ladrão de Bolas",  ladrao['apelido'],     f"{int(ladrao['DS'])} Desarmes")

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📅 Jogos", "🤖 Robô", "📊 Tática", "📈 Mercado", "🏆 Destaques",
    "💹 Valorização", "🎯 Capitão", "🔬 Raio-X", "🔮 Projeção", "🧬 ML & Otimizador",
])

# ─────────────────────────────────────────────────────────────
# TAB 1 — JOGOS
# ─────────────────────────────────────────────────────────────
with tab1:
    aba_conf, aba_tab = st.tabs(["⚽ Próximos Confrontos", "🏆 Tabela Brasileirão"])
    with aba_conf:
        st.subheader("🔮 Próximos Confrontos")
        if not df_proximos.empty:
            st.dataframe(df_proximos, hide_index=True, use_container_width=True)
        else:
            st.warning("Mercado fechado ou sem jogos previstos.")
    with aba_tab:
        st.subheader("🏆 Classificação Atualizada")
        if not df_tabela.empty:
            max_pts = df_tabela['Pts'].max() or 100
            st.dataframe(
                df_tabela,
                column_config={
                    "Pos": st.column_config.NumberColumn("Pos", width="small"),
                    "Pts": st.column_config.ProgressColumn("Pontos", format="%d", min_value=0, max_value=max_pts),
                },
                hide_index=True, use_container_width=True, height=750,
            )
        else:
            st.warning("Tabela indisponível no momento.")

# ─────────────────────────────────────────────────────────────
# TAB 2 — ROBÔ & COMPARADOR
# ─────────────────────────────────────────────────────────────
with tab2:
    st_robo, st_vs = st.tabs(["🤖 Robô Otimizador", "⚔️ Mano a Mano"])

    with st_robo:
        col_in, col_res = st.columns([1, 3])
        with col_in:
            st.markdown("### Configurações")
            orc      = st.number_input("Orçamento (C$)", value=100.0, key="robo_orc")
            esq      = st.selectbox("Esquema", ["4-3-3","3-4-3","3-5-2"], key="robo_esq")
            criterio = st.radio("Critério:", ["Índice PRO ✨","Média Geral","Pontuação Básica"])
            col_crit = 'indice_pro'
            if "Média Geral" in criterio:  col_crit = 'media_geral'
            elif "Pontuação" in criterio:  col_crit = 'media_basica'
            gerar = st.button("Gerar Time", use_container_width=True)

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
                        st.error("Não foi possível montar um time dentro do orçamento.")
                    else:
                        st.success(f"Custo: C$ {custo_total:.2f} | Score: {df_time[col_crit].sum():.1f}")
                        st.dataframe(
                            df_time[['foto','status','posicao_nome','apelido','clube_nome','mando','preco','indice_pro','media_geral','media_basica']],
                            column_config={
                                "foto":         st.column_config.ImageColumn("Perfil"),
                                "status":       "Status",
                                "posicao_nome": "Posição",
                                "apelido":      "Jogador",
                                "clube_nome":   "Clube",
                                "mando":        "Mando",
                                "preco":        st.column_config.NumberColumn("C$",          format="%.2f"),
                                "indice_pro":   st.column_config.NumberColumn("Índice PRO ✨",format="%.2f"),
                                "media_geral":  st.column_config.NumberColumn("Média Geral", format="%.2f"),
                                "media_basica": st.column_config.NumberColumn("Pont. Básica",format="%.2f"),
                            },
                            hide_index=True, use_container_width=True,
                        )

    with st_vs:
        st.markdown("#### Comparador Mano a Mano")
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
            fig.add_trace(go.Scatterpolar(r=v1, theta=cats, fill='toself', name=f"{p1} ({d1['status_txt']})"))
            fig.add_trace(go.Scatterpolar(r=v2, theta=cats, fill='toself', name=f"{p2} ({d2['status_txt']})"))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 3 — TÁTICA
# ─────────────────────────────────────────────────────────────
with tab3:
    hm1, hm2, hm3 = st.tabs(["🛡️ Defesa","⚔️ Ataque","🏰 Mando"])
    with hm1:
        st.markdown("**Fragilidade Defensiva:** Times que mais cedem pontos por posição.")
        heat = df.groupby(['adversario','posicao_nome'])['pontos'].mean().reset_index()
        if not heat.empty:
            piv = heat.pivot(index='adversario', columns='posicao_nome', values='pontos').fillna(0)
            st.plotly_chart(px.imshow(piv, text_auto=".1f", color_continuous_scale="Reds", aspect="auto"), use_container_width=True)
    with hm2:
        st.markdown("**Poder Ofensivo:** Posições que mais pontuam por time.")
        heat_atk = df.groupby(['clube_nome','posicao_nome'])['pontos'].mean().reset_index()
        if not heat_atk.empty:
            piv2 = heat_atk.pivot(index='clube_nome', columns='posicao_nome', values='pontos').fillna(0)
            st.plotly_chart(px.imshow(piv2, text_auto=".1f", color_continuous_scale="Greens", aspect="auto"), use_container_width=True)
    with hm3:
        st.subheader("📊 Casa x Fora")
        stats_mando = df.groupby(['clube_nome','mando'])['pontos'].mean().reset_index()
        fig_pts = px.bar(stats_mando, x='clube_nome', y='pontos', color='mando', barmode='group',
                         labels={'pontos':'Média de Pontos','clube_nome':'Time'},
                         color_discrete_map={'CASA':'#FFD700','FORA':'#696969'})
        fig_pts.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_pts, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 4 — MERCADO
# ─────────────────────────────────────────────────────────────
with tab4:
    st.markdown("### 📋 Tabela Completa do Mercado")
    cols_view = ['foto','status','apelido','posicao_nome','clube_nome','jogos_disputados',
                 'preco','indice_pro','custo_beneficio','media_geral','media_basica'] + scouts_cols
    st.dataframe(
        df_agrupado[cols_view].sort_values('indice_pro', ascending=False),
        column_config={
            "foto":            st.column_config.ImageColumn("Foto", width="small"),
            "status":          "Status",
            "jogos_disputados":st.column_config.NumberColumn("Jogos",       format="%d"),
            "preco":           st.column_config.NumberColumn("C$",          format="%.2f"),
            "indice_pro":      st.column_config.NumberColumn("Índice PRO ✨",format="%.2f"),
            "custo_beneficio": st.column_config.NumberColumn("C/B ⚡",       format="%.2f"),
            "media_geral":     st.column_config.NumberColumn("Média Tot",    format="%.2f"),
            "media_basica":    st.column_config.ProgressColumn("Pont. Básica", format="%.2f", min_value=-5, max_value=15),
        },
        use_container_width=True, hide_index=True, height=600,
    )

# ─────────────────────────────────────────────────────────────
# TAB 5 — DESTAQUES
# ─────────────────────────────────────────────────────────────
with tab5:
    st.subheader("🏆 Líderes por Fundamento")

    def render_leader_card(titulo, col_sort, col_container, sufixo=""):
        df_valid = df_agrupado[df_agrupado[col_sort] > 0]
        if df_valid.empty:
            return
        lider = df_valid.sort_values(col_sort, ascending=False).iloc[0]
        with col_container:
            c_img, c_txt = st.columns([1, 2])
            c_img.image(lider['foto'], width=70)
            c_txt.caption(titulo)
            c_txt.markdown(f"**{lider['apelido']}**")
            c_txt.markdown(f"### {int(lider[col_sort])} {sufixo}")
            st.divider()

    r1, r2, r3, r4 = st.columns(4)
    render_leader_card("Participação (G+A)", "participacao_gol", r1)
    render_leader_card("Artilheiro",         "G",                r2, "Gols")
    render_leader_card("Garçom",             "A",                r3, "Assis")
    render_leader_card("Finalizações",       "finalizacoes",     r4, "Chutes")
    r5, r6, r7, r8 = st.columns(4)
    render_leader_card("Desarmes",        "DS", r5)
    render_leader_card("Faltas Sofridas", "FS", r6)
    render_leader_card("Defesas (Gol)",   "DE", r7)
    render_leader_card("Paredão (SG)",    "SG", r8, "Jgs")

# ─────────────────────────────────────────────────────────────
# TAB 6 — TENDÊNCIA DE VALORIZAÇÃO
# ─────────────────────────────────────────────────────────────
with tab6:
    st.markdown("### 💹 Tendência de Valorização (C$)")
    st.caption("Acompanhe como o preço dos atletas evolui rodada a rodada.")

    col_busca, col_pos_val, col_minj = st.columns([2, 1, 1])
    with col_busca:
        busca_nome = st.text_input("🔍 Buscar atleta", placeholder="Ex: Gabigol, Veiga...", label_visibility="collapsed")
    with col_pos_val:
        todas_pos  = ["Todas"] + sorted(df['posicao_nome'].astype(str).unique())
        filtro_pos = st.selectbox("Posição", todas_pos, label_visibility="collapsed", key="val_pos")
    with col_minj:
        min_j_val  = st.number_input("Mín. jogos", min_value=1, max_value=10, value=3, key="val_minj")

    st.divider()

    df_preco = (
        df.groupby(['atleta_id','rodada_id'])
        .agg(apelido=('apelido','last'), posicao_nome=('posicao_nome','last'),
             clube_nome=('clube_nome','last'), preco=('preco','last'))
        .reset_index()
    )
    atletas_validos_v = df_preco.groupby('atleta_id')['rodada_id'].nunique()
    atletas_validos_v = atletas_validos_v[atletas_validos_v >= min_j_val].index
    df_preco = df_preco[df_preco['atleta_id'].isin(atletas_validos_v)]
    if filtro_pos != "Todas":
        df_preco = df_preco[df_preco['posicao_nome'] == filtro_pos]
    if busca_nome:
        df_preco = df_preco[df_preco['apelido'].str.contains(busca_nome, case=False, na=False)]

    if df_preco.empty:
        st.warning("Nenhum atleta encontrado.")
    else:
        resumo_val = []
        for atleta_id, grupo in df_preco.groupby('atleta_id'):
            g         = grupo.sort_values('rodada_id')
            p_ini     = g.iloc[0]['preco']
            p_fim     = g.iloc[-1]['preco']
            delta_abs = p_fim - p_ini
            delta_pct = ((p_fim - p_ini) / p_ini * 100) if p_ini > 0 else 0
            resumo_val.append({
                'atleta_id':    atleta_id,
                'apelido':      g.iloc[-1]['apelido'],
                'posicao_nome': g.iloc[-1]['posicao_nome'],
                'clube_nome':   g.iloc[-1]['clube_nome'],
                'preco_atual':  p_fim,
                'preco_ini':    p_ini,
                'delta_abs':    delta_abs,
                'delta_pct':    delta_pct,
                'n_rodadas':    len(g),
            })
        df_resumo_val = pd.DataFrame(resumo_val)

        col_top, col_bot = st.columns(2)
        with col_top:
            st.markdown("#### 🚀 Maiores valorizações")
            for _, row in df_resumo_val.sort_values('delta_pct', ascending=False).head(5).iterrows():
                st.metric(
                    label=f"{row['apelido']} — {row['clube_nome']}",
                    value=f"C$ {row['preco_atual']:.2f}",
                    delta=f"+C$ {row['delta_abs']:.2f} ({row['delta_pct']:+.1f}%)",
                )
        with col_bot:
            st.markdown("#### 📉 Maiores desvalorizações")
            for _, row in df_resumo_val.sort_values('delta_pct', ascending=True).head(5).iterrows():
                st.metric(
                    label=f"{row['apelido']} — {row['clube_nome']}",
                    value=f"C$ {row['preco_atual']:.2f}",
                    delta=f"C$ {row['delta_abs']:.2f} ({row['delta_pct']:+.1f}%)",
                )

        st.divider()
        st.markdown("#### 📊 Evolução do preço (até 5 atletas)")
        lista_at_val     = sorted(df_preco['apelido'].unique())
        selecionados_val = st.multiselect(
            "Selecione atletas:", lista_at_val,
            default=lista_at_val[:3] if len(lista_at_val) >= 3 else lista_at_val,
            max_selections=5, key="val_sel",
        )
        if selecionados_val:
            df_graf = df_preco[df_preco['apelido'].isin(selecionados_val)].sort_values('rodada_id')
            fig_val = px.line(df_graf, x='rodada_id', y='preco', color='apelido', markers=True,
                              labels={'rodada_id':'Rodada','preco':'Preço (C$)','apelido':'Atleta'},
                              color_discrete_sequence=px.colors.qualitative.Safe)
            fig_val.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(tickmode='linear', dtick=1, gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                hovermode='x unified', legend=dict(orientation='h', y=1.02, x=1, xanchor='right'),
            )
            st.plotly_chart(fig_val, use_container_width=True)

        st.divider()
        st.dataframe(
            df_resumo_val[['apelido','posicao_nome','clube_nome','preco_ini','preco_atual','delta_abs','delta_pct','n_rodadas']]
            .sort_values('delta_pct', ascending=False),
            column_config={
                "apelido":      "Atleta",      "posicao_nome": "Posição",  "clube_nome": "Clube",
                "preco_ini":    st.column_config.NumberColumn("C$ Inicial", format="%.2f"),
                "preco_atual":  st.column_config.NumberColumn("C$ Atual",   format="%.2f"),
                "delta_abs":    st.column_config.NumberColumn("Δ C$",       format="%+.2f"),
                "delta_pct":    st.column_config.NumberColumn("Δ %",        format="%+.1f%%"),
                "n_rodadas":    st.column_config.NumberColumn("Rodadas",    format="%d"),
            },
            hide_index=True, use_container_width=True, height=450,
        )

# ─────────────────────────────────────────────────────────────
# TAB 7 — ALERTA DE CAPITÃO IDEAL
# ─────────────────────────────────────────────────────────────
with tab7:
    st.markdown("### 🎯 Alerta de Capitão Ideal")
    st.caption("O capitão dobra os pontos. Aqui estão os melhores candidatos com justificativa completa.")

    cap_pool = df_agrupado[
        (df_agrupado['status_txt'] == 'Provável') &
        (df_agrupado['mando'] != 'Sem Jogo')
    ].copy()

    if cap_pool.empty:
        st.warning("Nenhum atleta Provável com jogo confirmado. Exibindo todos os atletas com jogo.")
        cap_pool = df_agrupado[df_agrupado['mando'] != 'Sem Jogo'].copy()

    if not cap_pool.empty:
        cap_pool['fator_mando_cap'] = cap_pool['mando'].map({'CASA':1.15,'FORA':0.85}).fillna(1.0)
        cap_pool['score_capitao']   = cap_pool['indice_pro'] * cap_pool['fator_mando_cap']
        top_cap = cap_pool.sort_values('score_capitao', ascending=False).head(10)

        for i, (_, row) in enumerate(top_cap.iterrows()):
            cor = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
            adv = mapa_confrontos.get(row['clube_nome'], {}).get('adv', '-')
            c1, c2, c3, c4, c5 = st.columns([0.5, 2, 1.5, 1.5, 2])
            c1.markdown(f"### {cor}")
            c2.markdown(f"**{row['apelido']}**")
            c2.caption(f"{row['posicao_nome']} · {row['clube_nome']}")
            c3.metric("Score Capitão", f"{row['score_capitao']:.2f}")
            c4.metric("Mando", row['mando'])
            c5.caption(
                f"Índice PRO {row['indice_pro']:.2f} | Média {row['media_geral']:.1f} pts | "
                f"{'🏠 CASA +15%' if row['mando']=='CASA' else '✈️ FORA -15%'} | Adv: {adv}"
            )
            st.divider()

        st.info(
            "💡 Score Capitão = Índice PRO × Fator Mando. "
            "Casa: +15% | Fora: -15%. Prefira Prováveis contra defesas fracas."
        )

# ─────────────────────────────────────────────────────────────
# TAB 8 — RAIO-X DO CONFRONTO
# ─────────────────────────────────────────────────────────────
with tab8:
    st.markdown("### 🔬 Raio-X do Confronto")
    st.caption("Analise o histórico completo de um confronto específico.")

    times_disp = sorted(df['clube_nome'].astype(str).unique())
    col_t1, col_t2 = st.columns(2)
    time_a = col_t1.selectbox("Time A (mandante)", times_disp, key="rx_a")
    time_b = col_t2.selectbox("Time B (visitante)", times_disp, index=1 if len(times_disp) > 1 else 0, key="rx_b")

    if time_a == time_b:
        st.warning("Selecione times diferentes.")
    else:
        df_direto = df[
            ((df['clube_nome'] == time_a) & (df['adversario'] == time_b)) |
            ((df['clube_nome'] == time_b) & (df['adversario'] == time_a))
        ]

        col_r1, col_r2, col_r3 = st.columns(3)
        n_jogos_direto = len(df_direto['rodada_id'].unique()) if not df_direto.empty else 0
        col_r1.metric("Jogos no histórico", n_jogos_direto)

        if not df_direto.empty:
            media_a = df_direto[df_direto['clube_nome'] == time_a]['pontos'].mean()
            media_b = df_direto[df_direto['clube_nome'] == time_b]['pontos'].mean()
            col_r2.metric(f"Média pontos {time_a}", f"{media_a:.2f}")
            col_r3.metric(f"Média pontos {time_b}", f"{media_b:.2f}")

            st.divider()
            heat_rx = df_direto.groupby(['clube_nome','posicao_nome'])['pontos'].mean().reset_index()
            piv_rx  = heat_rx.pivot(index='clube_nome', columns='posicao_nome', values='pontos').fillna(0)
            st.markdown(f"#### Pontuação por posição: {time_a} vs {time_b}")
            st.plotly_chart(
                px.imshow(piv_rx, text_auto=".1f", color_continuous_scale="Blues", aspect="auto"),
                use_container_width=True,
            )

            st.divider()
            st.markdown(f"#### Top atletas de {time_a} contra {time_b}")
            top_rx = (
                df_direto[df_direto['clube_nome'] == time_a]
                .groupby('apelido')
                .agg(media_pts=('pontos','mean'), jogos=('rodada_id','count'))
                .reset_index().sort_values('media_pts', ascending=False).head(10)
            )
            st.dataframe(
                top_rx,
                column_config={
                    "apelido":   "Atleta",
                    "media_pts": st.column_config.NumberColumn("Média pts", format="%.2f"),
                    "jogos":     st.column_config.NumberColumn("Jogos",     format="%d"),
                },
                hide_index=True, use_container_width=True,
            )
        else:
            st.info("Nenhum confronto direto entre esses times no histórico atual.")

        st.divider()
        st.markdown(f"#### Fragilidade defensiva — o que {time_b} cede por posição")
        df_cedido = df[df['adversario'] == time_b].groupby('posicao_nome')['pontos'].mean().reset_index()
        df_cedido.columns = ['Posição','Média cedida']
        df_cedido = df_cedido.sort_values('Média cedida', ascending=False)
        fig_ced   = px.bar(df_cedido, x='Posição', y='Média cedida',
                           color='Média cedida', color_continuous_scale='Reds', text_auto='.1f')
        fig_ced.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_ced, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 9 — PROJEÇÃO + FORMA RECENTE
# ─────────────────────────────────────────────────────────────
with tab9:
    proj_tab, forma_tab = st.tabs(["🔮 Projeção por Scout","📅 Forma Recente"])

    with proj_tab:
        st.markdown("### 🔮 Projeção de Pontuação por Scout")
        st.caption("Estima a pontuação esperada para a próxima rodada com base na média de scouts contra o adversário.")

        pesos_scouts = {
            'G':8.0,'A':5.0,'FT':3.0,'FD':1.2,'FF':0.8,'FS':0.5,
            'PS':1.0,'DE':1.0,'DS':1.5,'FC':-0.3,'PC':-1.0,
            'CA':-1.0,'CV':-3.0,'GS':-1.0,'I':-0.1,'SG':5.0,
        }

        atletas_com_jogo = df_agrupado[df_agrupado['mando'] != 'Sem Jogo']['apelido'].unique()
        if len(atletas_com_jogo) == 0:
            st.warning("Nenhum atleta com jogo confirmado para projeção.")
        else:
            sel_proj = st.multiselect(
                "Selecione atletas (máx. 10):",
                sorted(atletas_com_jogo), max_selections=10,
                default=list(sorted(atletas_com_jogo))[:5], key="proj_sel",
            )
            if sel_proj:
                rows_proj = []
                for apelido in sel_proj:
                    row_ag = df_agrupado[df_agrupado['apelido'] == apelido].iloc[0]
                    clube  = row_ag['clube_nome']
                    adv    = mapa_confrontos.get(clube, {}).get('adv', None)
                    df_at  = df[df['apelido'] == apelido]
                    if adv:
                        df_vs = df_at[df_at['adversario'] == adv]
                        fonte = f"vs {adv}"
                    else:
                        df_vs = df_at
                        fonte = "histórico geral"
                    if df_vs.empty:
                        df_vs = df_at
                        fonte = "histórico geral (sem dados vs adversário)"

                    projecao = sum(
                        df_vs[s].mean() * peso
                        for s, peso in pesos_scouts.items()
                        if s in df_vs.columns
                    )
                    rows_proj.append({
                        'Atleta':     apelido,
                        'Clube':      clube,
                        'Adversário': adv or '-',
                        'Mando':      row_ag['mando'],
                        'Base':       fonte,
                        'Proj. Mín':  projecao * 0.70,
                        'Proj. Med':  projecao,
                        'Proj. Máx':  projecao * 1.30,
                    })

                df_proj = pd.DataFrame(rows_proj).sort_values('Proj. Med', ascending=False)
                st.dataframe(
                    df_proj,
                    column_config={
                        "Proj. Mín": st.column_config.NumberColumn(format="%.1f"),
                        "Proj. Med": st.column_config.NumberColumn(format="%.1f"),
                        "Proj. Máx": st.column_config.NumberColumn(format="%.1f"),
                    },
                    hide_index=True, use_container_width=True,
                )
                fig_proj = px.bar(
                    df_proj, x='Atleta', y='Proj. Med',
                    error_y=df_proj['Proj. Máx'] - df_proj['Proj. Med'],
                    error_y_minus=df_proj['Proj. Med'] - df_proj['Proj. Mín'],
                    color='Mando', color_discrete_map={'CASA':'#1D9E75','FORA':'#185FA5','Sem Jogo':'#888'},
                    text_auto='.1f',
                )
                fig_proj.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_proj, use_container_width=True)
                st.caption("Barras de erro = ±30% sobre a projeção central.")

    with forma_tab:
        st.markdown("### 📅 Análise de Forma Recente")
        st.caption("Compare a média total com a performance nas últimas N rodadas.")

        n_rodadas_forma  = st.slider("Últimas N rodadas:", 1, max_jogos, min(5, max_jogos))
        rodadas_recentes = sorted(df['rodada_id'].unique())[-n_rodadas_forma:]
        df_recente       = df[df['rodada_id'].isin(rodadas_recentes)]

        agg_rec = {'pontos':'mean','pontuacao_basica':'mean','preco':'last',
                   'clube_nome':'last','posicao_nome':'last','apelido':'last',
                   'foto':'last','rodada_id':'count'}
        for s in scouts_cols:
            agg_rec[s] = 'sum'

        df_ag_rec = df_recente.groupby('atleta_id').agg(agg_rec).reset_index()
        df_ag_rec.rename(columns={'pontos':'media_rec','pontuacao_basica':'basica_rec','rodada_id':'jogos_rec'}, inplace=True)

        df_forma = df_agrupado[['atleta_id','apelido','clube_nome','posicao_nome','preco','media_geral','indice_pro','status_txt']].merge(
            df_ag_rec[['atleta_id','media_rec','basica_rec','jogos_rec']], on='atleta_id', how='inner'
        )
        df_forma['delta_forma'] = df_forma['media_rec'] - df_forma['media_geral']

        col_alta, col_baixa = st.columns(2)
        with col_alta:
            st.markdown(f"#### 🔥 Em alta (últimas {n_rodadas_forma} rodadas)")
            for _, r in df_forma.sort_values('delta_forma', ascending=False).head(8).iterrows():
                st.metric(
                    label=f"{r['apelido']} — {r['clube_nome']}",
                    value=f"{r['media_rec']:.1f} pts",
                    delta=f"{r['delta_forma']:+.1f} vs média total",
                )
        with col_baixa:
            st.markdown(f"#### 📉 Em queda (últimas {n_rodadas_forma} rodadas)")
            for _, r in df_forma.sort_values('delta_forma', ascending=True).head(8).iterrows():
                st.metric(
                    label=f"{r['apelido']} — {r['clube_nome']}",
                    value=f"{r['media_rec']:.1f} pts",
                    delta=f"{r['delta_forma']:+.1f} vs média total",
                )

        st.divider()
        df_forma_top = df_forma.sort_values('media_rec', ascending=False).head(20)
        fig_forma = go.Figure()
        fig_forma.add_trace(go.Bar(name='Média Total',          x=df_forma_top['apelido'], y=df_forma_top['media_geral'], marker_color='#444', opacity=0.7))
        fig_forma.add_trace(go.Bar(name=f'Últimas {n_rodadas_forma} rod.', x=df_forma_top['apelido'], y=df_forma_top['media_rec'],   marker_color='#1D9E75'))
        fig_forma.update_layout(
            barmode='group', xaxis_tickangle=-45,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation='h', y=1.02),
        )
        st.plotly_chart(fig_forma, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 10 — ML & OTIMIZADOR LINEAR
# ─────────────────────────────────────────────────────────────
with tab10:
    ml_tab, opt_tab = st.tabs(["🧬 Predição ML","⚙️ Otimizador PuLP"])

    # ── ML ───────────────────────────────────────────────────
    with ml_tab:
        st.markdown("### 🧬 Predição de Valorização com ML")
        st.caption("Ridge Regression treinada com scouts e preço histórico para estimar variação de C$ na próxima rodada.")

        try:
            from sklearn.linear_model import Ridge
            from sklearn.preprocessing import StandardScaler
            from sklearn.pipeline import Pipeline

            features_ml = ['pontos','G','A','FT','DS','FS','FC','CA','GS','DE','SG','preco']
            for f in features_ml:
                if f not in df.columns:
                    df[f] = 0

            df_ml           = df.sort_values(['atleta_id','rodada_id']).copy()
            df_ml['preco_prox']   = df_ml.groupby('atleta_id')['preco'].shift(-1)
            df_ml['delta_preco']  = df_ml['preco_prox'] - df_ml['preco']
            df_ml = df_ml.dropna(subset=['delta_preco'] + features_ml)

            X = df_ml[features_ml].values
            y = df_ml['delta_preco'].values

            if len(X) < 30:
                st.warning("Dados insuficientes para treinar o modelo. Aguarde mais rodadas.")
            else:
                modelo = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])
                modelo.fit(X, y)

                X_pred = np.column_stack([
                    df_agrupado[f].values if f in df_agrupado.columns else np.zeros(len(df_agrupado))
                    for f in features_ml
                ])
                df_agrupado['delta_pred'] = modelo.predict(X_pred)

                coef    = modelo.named_steps['ridge'].coef_
                df_coef = pd.DataFrame({'Feature': features_ml, 'Importância': np.abs(coef)}).sort_values('Importância', ascending=True)

                col_pred, col_imp = st.columns([3, 2])
                with col_pred:
                    st.markdown("#### Top valorizações previstas")
                    top_pred = df_agrupado[['apelido','clube_nome','posicao_nome','preco','status_txt','delta_pred']]\
                        .sort_values('delta_pred', ascending=False).head(15)
                    st.dataframe(
                        top_pred,
                        column_config={
                            "apelido":     "Atleta",    "clube_nome":  "Clube",
                            "posicao_nome":"Posição",   "status_txt":  "Status",
                            "preco":       st.column_config.NumberColumn("C$ Atual",   format="%.2f"),
                            "delta_pred":  st.column_config.NumberColumn("Δ C$ Prev.", format="%+.2f"),
                        },
                        hide_index=True, use_container_width=True,
                    )
                with col_imp:
                    st.markdown("#### Fatores mais relevantes")
                    fig_imp = px.bar(df_coef, x='Importância', y='Feature', orientation='h',
                                     color='Importância', color_continuous_scale='Teal')
                    fig_imp.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                          showlegend=False, yaxis_title='')
                    st.plotly_chart(fig_imp, use_container_width=True)

                st.info("⚠️ Estimativa baseada em padrões históricos. Use como sinal complementar, não como verdade absoluta.")

        except ImportError:
            st.error("❌ **scikit-learn não instalado.** Adicione `scikit-learn` no `requirements.txt` e faça o redeploy.")

    # ── OTIMIZADOR PuLP ──────────────────────────────────────
    with opt_tab:
        st.markdown("### ⚙️ Otimizador de Escalação com Programação Linear")
        st.caption("Maximiza o Índice PRO matematicamente, respeitando orçamento, posições e restrições do esquema.")

        try:
            import pulp

            col_opt1, col_opt2 = st.columns([1, 2])
            with col_opt1:
                orc_opt    = st.number_input("Orçamento (C$)", value=100.0, key="opt_orc")
                esq_opt    = st.selectbox("Esquema", ["4-3-3","3-4-3","3-5-2"], key="opt_esq")
                status_opt = st.multiselect("Status aceitos:", ['Provável','Dúvida','Sem Status'], default=['Provável'], key="opt_status")
                max_time   = st.number_input("Máx. atletas do mesmo time", min_value=1, max_value=5, value=5, key="opt_maxtm")
                otimizar   = st.button("🚀 Otimizar Escalação", use_container_width=True, key="opt_btn")

            with col_opt2:
                if otimizar:
                    meta_opt = {
                        "4-3-3": {'Goleiro':1,'Lateral':2,'Zagueiro':2,'Meia':3,'Atacante':3,'Técnico':1},
                        "3-5-2": {'Goleiro':1,'Lateral':0,'Zagueiro':3,'Meia':5,'Atacante':2,'Técnico':1},
                        "3-4-3": {'Goleiro':1,'Lateral':0,'Zagueiro':3,'Meia':4,'Atacante':3,'Técnico':1},
                    }.get(esq_opt)

                    pool_opt = df_agrupado[df_agrupado['status_txt'].isin(status_opt)].copy().reset_index(drop=True)

                    if pool_opt.empty:
                        st.warning("Nenhum atleta disponível com os status selecionados.")
                    else:
                        prob     = pulp.LpProblem("cartola_otimizador", pulp.LpMaximize)
                        n        = len(pool_opt)
                        idx_list = list(range(n))
                        x        = pulp.LpVariable.dicts("x", idx_list, cat='Binary')

                        # Objetivo: maximizar Índice PRO total
                        prob += pulp.lpSum(pool_opt.iloc[i]['indice_pro'] * x[i] for i in idx_list)

                        # Orçamento
                        prob += pulp.lpSum(pool_opt.iloc[i]['preco'] * x[i] for i in idx_list) <= orc_opt

                        # Posições
                        for pos, qtd in meta_opt.items():
                            indices_pos = [i for i in idx_list if pool_opt.iloc[i]['posicao_nome'] == pos]
                            prob += pulp.lpSum(x[i] for i in indices_pos) == qtd

                        # Máximo por time
                        for time_nome in pool_opt['clube_nome'].unique():
                            indices_time = [i for i in idx_list if pool_opt.iloc[i]['clube_nome'] == time_nome]
                            prob += pulp.lpSum(x[i] for i in indices_time) <= max_time

                        prob.solve(pulp.PULP_CBC_CMD(msg=0))

                        if pulp.LpStatus[prob.status] == 'Optimal':
                            escalados  = [i for i in idx_list if pulp.value(x[i]) == 1]
                            df_opt     = pool_opt.iloc[escalados].copy()
                            ordem_tat  = ['Goleiro','Lateral','Zagueiro','Meia','Atacante','Técnico']
                            df_opt['posicao_nome'] = pd.Categorical(df_opt['posicao_nome'], categories=ordem_tat, ordered=True)
                            df_opt     = df_opt.sort_values('posicao_nome')
                            custo_opt  = df_opt['preco'].sum()
                            score_opt  = df_opt['indice_pro'].sum()

                            st.success(f"✅ Escalação ótima! Custo: C$ {custo_opt:.2f} | Score PRO: {score_opt:.2f}")
                            st.dataframe(
                                df_opt[['foto','status','posicao_nome','apelido','clube_nome','mando','preco','indice_pro','media_geral']],
                                column_config={
                                    "foto":         st.column_config.ImageColumn("Perfil"),
                                    "status":       "Status",
                                    "posicao_nome": "Posição",
                                    "apelido":      "Jogador",
                                    "clube_nome":   "Clube",
                                    "mando":        "Mando",
                                    "preco":        st.column_config.NumberColumn("C$",          format="%.2f"),
                                    "indice_pro":   st.column_config.NumberColumn("Índice PRO ✨",format="%.2f"),
                                    "media_geral":  st.column_config.NumberColumn("Média",       format="%.2f"),
                                },
                                hide_index=True, use_container_width=True,
                            )
                            st.info(
                                "💡 **Diferença para o Robô Greedy:** O otimizador avalia todas as combinações "
                                "simultaneamente e garante o máximo global. O Robô faz substituições uma a uma "
                                "e pode ficar preso em ótimos locais."
                            )
                        else:
                            st.error("❌ Solução inviável. Tente aumentar o orçamento ou aceitar mais status.")

        except ImportError:
            st.error("❌ **PuLP não instalado.** Adicione `pulp` no `requirements.txt` e faça o redeploy.")
