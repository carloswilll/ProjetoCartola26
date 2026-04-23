import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import re
import io
from supabase import create_client, Client

# --- 1. CONFIGURAÇÕES VISUAIS ---
st.set_page_config(page_title="Cartola Pro 2026", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1rem; font-weight: 600;
    }
    div[data-testid="metric-container"] {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 10px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. FUNÇÕES DE DADOS ---

@st.cache_data(ttl=300)
def pegar_status_atletas():
    """Busca o status atualizado dos jogadores no mercado em tempo real."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get("https://api.cartola.globo.com/atletas/mercado", headers=headers).json()
        mapa_status = {int(k): v['nome'] for k, v in res['status'].items()}
        status_atletas = {a['atleta_id']: mapa_status.get(a['status_id'], 'Sem Status') for a in res['atletas']}
        return status_atletas
    except:
        return {}

@st.cache_data(ttl=600)
def pegar_jogos_ao_vivo():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        mercado = requests.get("https://api.cartola.globo.com/mercado/status", headers=headers).json()
        rodada_atual = mercado['rodada_atual']
        partidas = requests.get("https://api.cartola.globo.com/partidas", headers=headers).json()
        
        clubes = requests.get("https://api.cartola.globo.com/clubes", headers=headers).json()
        dict_clubes = {int(k): v['nome'] for k, v in clubes.items()} 
        if not dict_clubes:
             mercado_full = requests.get("https://api.cartola.globo.com/atletas/mercado", headers=headers).json()
             dict_clubes = {int(k): v['nome'] for k, v in mercado_full['clubes'].items()}

        lista_jogos = []
        if 'partidas' in partidas:
            for p in partidas['partidas']:
                lista_jogos.append({
                    'Mandante': dict_clubes.get(p['clube_casa_id'], 'Casa'),
                    'Visitante': dict_clubes.get(p['clube_visitante_id'], 'Fora'),
                    'Local': p.get('local', '-'),
                    'Data': f"{p.get('partida_data','')} {p.get('partida_hora','')}"
                })
        return pd.DataFrame(lista_jogos), rodada_atual
    except:
        return pd.DataFrame(), 0

@st.cache_data(ttl=3600)
def pegar_tabela_brasileirao():
    try:
        url = "https://www.espn.com.br/futebol/classificacao/_/liga/BRA.1/brazilian-serie-a"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        res = requests.get(url, headers=headers)
        
        dfs = pd.read_html(io.StringIO(res.text))
        
        if len(dfs) >= 2:
            df_times = dfs[0]
            df_stats = dfs[1]
            df_completo = pd.concat([df_times, df_stats], axis=1)
            
            col_nome = df_times.columns[0]
            df_completo['Clube_Limpo'] = df_completo[col_nome].astype(str).apply(
                lambda x: re.sub(r'^\d+[A-Z]{3}', '', x)
            )
            
            tabela = []
            for idx, row in df_completo.iterrows():
                tabela.append({
                    'Pos': idx + 1,
                    'Clube': row['Clube_Limpo'],
                    'Pts': row['PTS'] if 'PTS' in df_completo.columns else 0,
                    'J': row['J'] if 'J' in df_completo.columns else 0,
                    'V': row['V'] if 'V' in df_completo.columns else 0,
                    'E': row['E'] if 'E' in df_completo.columns else 0,
                    'D': row['D'] if 'D' in df_completo.columns else 0,
                    'SG': row['SG'] if 'SG' in df_completo.columns else 0,
                    'Últimos 5': "-" 
                })
            
            return pd.DataFrame(tabela)
            
    except Exception as e:
        print(f"Erro ao extrair Tabela da ESPN: {e}")
        pass
    return pd.DataFrame()

# --- CONEXÃO COM O SUPABASE ---
# @st.cache_resource garante que a conexão é aberta UMA vez só
# e reutilizada em todas as interações do usuário.
@st.cache_resource
def conectar_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = conectar_supabase()

@st.cache_data(ttl=300)
def carregar_historico() -> pd.DataFrame:
    """
    Busca todo o histórico de rodadas salvo no Supabase.
    Equivale ao pd.read_csv() do código original.
    Cache de 5 minutos para não bater no banco a cada clique.
    """
    try:
        resposta = supabase.table("historico_cartola").select("*").execute()
        if resposta.data:
            return pd.DataFrame(resposta.data)
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar histórico: {e}")
    return pd.DataFrame()

def salvar_novas_rodadas(novos: list):
    """
    Insere novas linhas no Supabase em blocos de 500.
    Equivale ao df.to_csv() do código original.
    """
    if not novos:
        return
    try:
        for i in range(0, len(novos), 500):
            supabase.table("historico_cartola").insert(novos[i:i+500]).execute()
    except Exception as e:
        st.error(f"❌ Erro ao salvar no Supabase: {e}")

def gerenciar_banco_dados():
    headers = {"User-Agent": "Mozilla/5.0"}

    # 1. Descobre a rodada atual na API do Cartola
    try:
        status = requests.get(
            "https://api.cartola.globo.com/mercado/status",
            headers=headers, timeout=10
        ).json()
        rodada_atual = status['rodada_atual']
        ultima_rodada = rodada_atual - 1 if status['status_mercado'] == 1 else rodada_atual
    except Exception as e:
        st.warning(f"⚠️ Não foi possível checar a rodada atual: {e}")
        return pd.DataFrame()

    # 2. Carrega o histórico que já temos no Supabase
    df = carregar_historico()
    ultima_no_banco = int(df['rodada_id'].max()) if not df.empty else 0

    # 3. Se não há rodadas novas, retorna o que já temos
    if ultima_rodada <= ultima_no_banco:
        return df

    # 4. Há rodadas novas — vamos baixar
    container = st.empty()
    container.info(f"🔄 Baixando rodadas {ultima_no_banco+1} a {ultima_rodada}...")
    novos = []

    # 5. Busca dicionários de apoio (traduz IDs em nomes)
    try:
        mercado = requests.get(
            "https://api.cartola.globo.com/atletas/mercado",
            headers=headers, timeout=15
        ).json()
        dict_clubes   = {int(k): v['nome'] for k, v in mercado['clubes'].items()}
        dict_posicoes = {int(k): v['nome'] for k, v in mercado['posicoes'].items()}
        precos_atuais = {a['atleta_id']: a['preco_num'] for a in mercado['atletas']}
    except Exception as e:
        st.warning(f"⚠️ Erro ao buscar dicionários do mercado: {e}")
        dict_clubes, dict_posicoes, precos_atuais = {}, {}, {}

    # 6. Loop pelas rodadas novas
    for r in range(ultima_no_banco + 1, ultima_rodada + 1):
        try:
            pontuados = requests.get(
                f"https://api.cartola.globo.com/atletas/pontuados/{r}",
                headers=headers, timeout=15
            ).json()
            partidas = requests.get(
                f"https://api.cartola.globo.com/partidas/{r}",
                headers=headers, timeout=15
            ).json()

            mapa_jogos = {}
            if partidas and 'partidas' in partidas:
                for p in partidas['partidas']:
                    cid, vid = p['clube_casa_id'], p['clube_visitante_id']
                    local = p.get('local', '-')
                    dt = f"{p.get('partida_data','')} {p.get('partida_hora','')}"
                    mapa_jogos[cid] = {'mando': 'CASA', 'adversario': dict_clubes.get(vid, 'Visitante'), 'local': local, 'data': dt}
                    mapa_jogos[vid] = {'mando': 'FORA', 'adversario': dict_clubes.get(cid, 'Mandante'), 'local': local, 'data': dt}

            if pontuados and 'atletas' in pontuados:
                for pid, dados in pontuados['atletas'].items():
                    pid = int(pid)
                    cid = dados['clube_id']
                    jogo = mapa_jogos.get(cid, {'mando': '-', 'adversario': '-', 'local': '-', 'data': '-'})
                    preco = dados.get('preco_num') or dados.get('preco') or precos_atuais.get(pid, 0)

                    linha = {
                        'rodada_id':    r,
                        'atleta_id':    pid,
                        'apelido':      dados.get('apelido', f'Jog {pid}'),
                        'foto':         dados.get('foto', '').replace('FORMATO', '140x140'),
                        'clube_nome':   dict_clubes.get(cid, 'Outro'),
                        'posicao_nome': dict_posicoes.get(dados['posicao_id'], 'Outro'),
                        'pontos':       dados.get('pontuacao', 0),
                        'preco':        preco,
                        'media':        dados.get('media', 0),
                        'mando':        jogo['mando'],
                        'adversario':   jogo['adversario'],
                        'estadio':      jogo['local'],
                        'data_jogo':    jogo['data'],
                    }
                    scouts = dados.get('scout') or {}
                    linha.update(scouts)
                    novos.append(linha)

        except Exception as e:
            st.toast(f"⚠️ Erro na rodada {r}: {e}", icon="⚠️")
            continue

    # 7. Salva as novas rodadas no Supabase
    if novos:
        df_novo = pd.DataFrame(novos).fillna(0)
        salvar_novas_rodadas(df_novo.to_dict('records'))
        carregar_historico.clear()  # invalida o cache para forçar releitura
        container.empty()
        return pd.concat([df, df_novo], ignore_index=True)

    container.empty()
    return df

# --- 3. PROCESSAMENTO DE DADOS ---
df = gerenciar_banco_dados()

if df.empty:
    st.title("⚽ Cartola Pro 2026")
    st.warning("Aguardando dados da primeira rodada...")
else:
    colunas_obrigatorias = ['estadio', 'data_jogo', 'mando', 'adversario', 'foto', 'apelido', 'clube_nome', 'posicao_nome']
    for col in colunas_obrigatorias:
        if col not in df.columns: df[col] = '-' 
            
    scouts_cols = ['G', 'A', 'FT', 'FD', 'FF', 'FS', 'PS', 'I', 'PP', 'DS', 'SG', 'DE', 'DP', 'GS', 'FC', 'PC', 'CA', 'CV', 'GC']
    for c in scouts_cols: 
        if c not in df.columns: df[c] = 0
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    
    df['pontuacao_basica'] = (
        (df['DS'] * 1.5) + (df['FS'] * 0.5) + 
        (df['FF'] * 0.8) + (df['FD'] * 1.2) + (df['FT'] * 3.0) + 
        (df['DE'] * 1.0) + (df['PS'] * 1.0) +
        (df['FC'] * -0.3) + (df['PC'] * -1.0) + 
        (df['CA'] * -1.0) + (df['CV'] * -3.0) + 
        (df['GS'] * -1.0) + (df['I'] * -0.1)
    )
    
    df['participacao_gol'] = df['G'] + df['A']
    df['finalizacoes'] = df['FD'] + df['FF'] + df['FT']

    # --- 4. SIDEBAR & FILTROS GLOBAIS ---
    st.sidebar.title("⚙️ Painel de Controle")
    
    contagem_jogos = df.groupby('atleta_id')['rodada_id'].nunique()
    max_jogos = int(contagem_jogos.max()) if not contagem_jogos.empty else 1
    
    min_jogos = st.sidebar.slider("Mínimo de Jogos Disputados pelo Atleta:", 1, max_jogos, 1)
    
    st.sidebar.divider()
    
    clubes = sorted(df['clube_nome'].astype(str).unique())
    posicoes = sorted(df['posicao_nome'].astype(str).unique())
    
    sel_clube = st.sidebar.multiselect("Filtrar Clube", clubes, default=clubes)
    sel_posicao = st.sidebar.multiselect("Filtrar Posição", posicoes, default=posicoes)
    
    df_periodo = df # Mantém o período para análises de tática (heatmaps e mando)
    df_filtrado = df_periodo[(df_periodo['clube_nome'].isin(sel_clube)) & (df_periodo['posicao_nome'].isin(sel_posicao))]

    agg_rules = {
        'rodada_id': 'count', 
        'pontos': 'mean', 'pontuacao_basica': 'mean', 'preco': 'last', 
        'clube_nome': 'last', 'posicao_nome': 'last', 'foto': 'last',
        'participacao_gol': 'sum', 'finalizacoes': 'sum', 'apelido': 'last'
    }
    for s in scouts_cols: agg_rules[s] = 'sum'
    
    df_agrupado = df_filtrado.groupby('atleta_id').agg(agg_rules).reset_index()
    df_agrupado.rename(columns={'pontos': 'media_geral', 'pontuacao_basica': 'media_basica', 'rodada_id': 'jogos_disputados'}, inplace=True)

    df_agrupado = df_agrupado[df_agrupado['jogos_disputados'] >= min_jogos]

    # --- INSERÇÃO DO STATUS ATUAL (AO VIVO) ---
    status_dict = pegar_status_atletas()
    df_agrupado['status_txt'] = df_agrupado['atleta_id'].map(status_dict).fillna('Sem Status')
    
    def formatar_status(s):
        if s == 'Provável': return '✅ Provável'
        if s == 'Dúvida': return '❓ Dúvida'
        if s == 'Suspenso': return '🟥 Suspenso'
        if s == 'Contundido': return '🚑 Contundido'
        if s == 'Nulo': return '❌ Nulo'
        return f'⚪ {s}'
        
    df_agrupado['status'] = df_agrupado['status_txt'].apply(formatar_status)

    # --- 5. LÓGICA DO ÍNDICE PRO ---
    df_proximos, _ = pegar_jogos_ao_vivo()
    df_tabela = pegar_tabela_brasileirao()
    
    mapa_confrontos = {}
    if not df_proximos.empty:
        for _, row in df_proximos.iterrows():
            mapa_confrontos[row['Mandante']] = {'mando': 'CASA', 'adv': row['Visitante']}
            mapa_confrontos[row['Visitante']] = {'mando': 'FORA', 'adv': row['Mandante']}

    mapa_posicoes_brasileirao = {}
    if not df_tabela.empty:
        for _, row in df_tabela.iterrows():
            mapa_posicoes_brasileirao[row['Clube'].lower()] = row['Pos']

    def obter_posicao_tabela(nome_clube):
        if not mapa_posicoes_brasileirao: return 10
        clube_limpo = nome_clube.lower().strip()
        for nome_espn, pos in mapa_posicoes_brasileirao.items():
            if clube_limpo in nome_espn or nome_espn in clube_limpo:
                return pos
        return 10 

    df_agrupado['mando'] = df_agrupado['clube_nome'].apply(lambda c: mapa_confrontos[c]['mando'] if c in mapa_confrontos else 'Sem Jogo')

    media_cedida_adv = df.groupby(['adversario', 'posicao_nome'])['pontos'].mean().to_dict()
    media_feita_time = df.groupby(['clube_nome', 'posicao_nome'])['pontos'].mean().to_dict()
    media_posicao_global = df.groupby('posicao_nome')['pontos'].mean().to_dict()

    def calcular_indice_pro(row):
        clube = row['clube_nome']
        pos = row['posicao_nome']

        if not mapa_confrontos or clube not in mapa_confrontos:
            return row['media_geral'] * 0.1 

        info = mapa_confrontos[clube]
        mando = info['mando']
        adv = info['adv']

        fator_mando = 1.15 if mando == 'CASA' else 0.85
        pts_cedidos = media_cedida_adv.get((adv, pos), media_posicao_global.get(pos, 0))
        pts_feitos = media_feita_time.get((clube, pos), media_posicao_global.get(pos, 0))
        forca_tatica = (pts_cedidos + pts_feitos) / 2

        pos_meu_time = obter_posicao_tabela(clube)
        pos_time_adv = obter_posicao_tabela(adv)
        fator_favoritismo = 1 + ((pos_time_adv - pos_meu_time) * 0.008)

        base_score = (row['media_geral'] * 0.4) + (row['media_basica'] * 0.3) + (forca_tatica * 0.3)
        return base_score * fator_mando * fator_favoritismo

    df_agrupado['indice_pro'] = df_agrupado.apply(calcular_indice_pro, axis=1)

    # --- 6. INSIGHTS RÁPIDOS ---
    st.title("⚽ Dashboard Analítico 2026")
    
    k1, k2, k3, k4 = st.columns(4)
    if not df_agrupado.empty:
        top_pro = df_agrupado.sort_values('indice_pro', ascending=False).iloc[0]
        k1.metric("🤖 Top Indicação (Índice PRO)", top_pro['apelido'], f"Score: {top_pro['indice_pro']:.2f}")
        
        top_reg = df_agrupado.sort_values('media_basica', ascending=False).iloc[0]
        k2.metric("💎 Rei da Regularidade", top_reg['apelido'], f"Básica: {top_reg['media_basica']:.1f} pts")
        
        artilheiro = df_agrupado.sort_values('participacao_gol', ascending=False).iloc[0]
        k3.metric("🔥 Mais Decisivo", artilheiro['apelido'], f"{int(artilheiro['participacao_gol'])} Gols+Assis")
        
        ladrao = df_agrupado.sort_values('DS', ascending=False).iloc[0]
        k4.metric("🛑 Ladrão de Bolas", ladrao['apelido'], f"{int(ladrao['DS'])} Desarmes")

    # --- 7. TABS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 Próximos Jogos", "🤖 Robô & Comparador", "📊 Tática", "📈 Mercado", "🏆 Destaques"])

    # ABA 1: JOGOS E CLASSIFICAÇÃO
    with tab1:
        aba_confrontos, aba_tabela = st.tabs(["⚽ Próximos Confrontos", "🏆 Tabela Brasileirão"])
        
        with aba_confrontos:
            st.subheader("🔮 Próximos Confrontos (Ao Vivo da API)")
            if not df_proximos.empty:
                st.info("Confrontos da rodada aberta:")
                st.dataframe(df_proximos, hide_index=True, use_container_width=True)
            else:
                st.warning("Mercado fechado ou sem jogos previstos na API.")
                
        with aba_tabela:
            st.subheader("🏆 Classificação Atualizada")
            if not df_tabela.empty:
                max_pts = df_tabela['Pts'].max() if not df_tabela.empty else 100
                st.dataframe(
                    df_tabela,
                    column_config={
                        "Pos": st.column_config.NumberColumn("Pos", width="small"),
                        "Pts": st.column_config.ProgressColumn("Pontos", format="%d", min_value=0, max_value=max_pts),
                        "Últimos 5": st.column_config.TextColumn("Fase (Últimos 5)")
                    },
                    hide_index=True,
                    use_container_width=True,
                    height=750 
                )
                st.caption("Dados sincronizados diretamente da tabela da ESPN.")
            else:
                st.warning("Não foi possível carregar a tabela.")

    # ABA 2: INTELIGÊNCIA
    with tab2:
        st_robo, st_vs = st.tabs(["🤖 Robô Otimizador", "⚔️ Mano a Mano"])
        
        with st_robo:
            col_in, col_res = st.columns([1, 3])
            
            with col_in:
                st.markdown("### Configurações")
                orc = st.number_input("Orçamento (C$)", value=100.0)
                esq = st.selectbox("Esquema", ["4-3-3", "3-4-3", "3-5-2"])
                criterio = st.radio("Critério da IA:", [
                    "Índice PRO ✨", 
                    "Média Geral", 
                    "Pontuação Básica"
                ])
                
                col_crit = 'indice_pro'
                if "Média Geral" in criterio: col_crit = 'media_geral'
                elif "Pontuação Básica" in criterio: col_crit = 'media_basica'
                
                gerar_botao = st.button("Gerar Time Inteligente", use_container_width=True)
                
            with col_res:
                if gerar_botao:
                    meta = {"4-3-3": {'Goleiro':1, 'Lateral':2, 'Zagueiro':2, 'Meia':3, 'Atacante':3, 'Técnico':1},
                            "3-5-2": {'Goleiro':1, 'Lateral':0, 'Zagueiro':3, 'Meia':5, 'Atacante':2, 'Técnico':1},
                            "3-4-3": {'Goleiro':1, 'Lateral':0, 'Zagueiro':3, 'Meia':4, 'Atacante':3, 'Técnico':1}}.get(esq)
                    
                    # FILTRO DE SEGURANÇA: Só aceita jogadores Prováveis
                    pool = df_agrupado[df_agrupado['status_txt'] == 'Provável'].sort_values(col_crit, ascending=False)
                    
                    if pool.empty:
                        st.warning("⚠️ Nenhum jogador marcado como 'Provável' no momento. O Robô tentará escalar com todos os disponíveis.")
                        pool = df_agrupado.sort_values(col_crit, ascending=False)

                    time_final = []
                    for pos, qtd in meta.items():
                        if qtd > 0: time_final.append(pool[pool['posicao_nome'] == pos].head(qtd))
                    
                    if time_final:
                        df_time = pd.concat(time_final)
                        custo_total = df_time['preco'].sum()
                        
                        loops = 0
                        while custo_total > orc and loops < 100:
                            df_time = df_time.sort_values('preco', ascending=False)
                            troca_feita = False
                            
                            for idx, jogador_caro in df_time.iterrows():
                                candidatos = pool[
                                    (pool['posicao_nome'] == jogador_caro['posicao_nome']) & 
                                    (pool['preco'] < jogador_caro['preco']) & 
                                    (~pool['atleta_id'].isin(df_time['atleta_id']))
                                ]
                                
                                if not candidatos.empty:
                                    substituto = candidatos.iloc[0] 
                                    df_time = df_time.drop(idx)
                                    df_time = pd.concat([df_time, substituto.to_frame().T])
                                    custo_total = df_time['preco'].sum()
                                    troca_feita = True
                                    break 
                            
                            if not troca_feita: break 
                            loops += 1

                        ordem_tatica = ['Goleiro', 'Lateral', 'Zagueiro', 'Meia', 'Atacante', 'Técnico']
                        df_time['posicao_nome'] = pd.Categorical(df_time['posicao_nome'], categories=ordem_tatica, ordered=True)
                        df_time = df_time.sort_values('posicao_nome')

                        cor_custo = "green" if custo_total <= orc else "red"
                        
                        if custo_total > orc:
                            st.error("Não foi possível montar um time dentro do orçamento apenas com os Prováveis.")
                        else:
                            st.success(f"**Escalação Concluída!** Custo: C$ {custo_total:.2f} | Score Projetado: {df_time[col_crit].sum():.1f}")
                            
                            st.dataframe(
                                df_time[['foto', 'status', 'posicao_nome', 'apelido', 'clube_nome', 'jogos_disputados', 'mando', 'preco', 'indice_pro', 'media_geral', 'media_basica']],
                                column_config={
                                    "foto": st.column_config.ImageColumn("Perfil"),
                                    "status": "Status",
                                    "posicao_nome": "Posição",
                                    "apelido": "Jogador",
                                    "clube_nome": "Clube",
                                    "jogos_disputados": st.column_config.NumberColumn("Jogos", format="%d"),
                                    "mando": "Mando",
                                    "preco": st.column_config.NumberColumn("C$", format="%.2f"),
                                    "indice_pro": st.column_config.NumberColumn("Índice PRO ✨", format="%.2f"),
                                    "media_geral": st.column_config.NumberColumn("Média Geral", format="%.2f"),
                                    "media_basica": st.column_config.NumberColumn("Pont. Básica", format="%.2f"),
                                },
                                hide_index=True,
                                use_container_width=True
                            )
                            
                            st.markdown("---")
                            st.markdown("### 🧠 Parecer do Robô (Por que escalei esses caras?)")
                            st.info("Escalei **apenas jogadores com status 'Provável' ✅**. Não queremos surpresas de última hora no banco de reservas.")

        with st_vs:
            st.markdown("#### Comparador de Jogadores")
            jogadores = sorted(df_agrupado['apelido'].unique())
            c1, c2 = st.columns(2)
            p1 = c1.selectbox("Jogador 1", jogadores, index=0 if len(jogadores)>0 else None)
            p2 = c2.selectbox("Jogador 2", jogadores, index=1 if len(jogadores)>1 else None)
            
            if p1 and p2:
                d1 = df_agrupado[df_agrupado['apelido'] == p1].iloc[0]
                d2 = df_agrupado[df_agrupado['apelido'] == p2].iloc[0]
                
                categorias = ['Índice PRO', 'Pont. Básica', 'Gols', 'Fin (Chutes)', 'Desarmes', 'Part. Gol']
                val1 = [d1['indice_pro'], d1['media_basica'], d1['G'], d1['finalizacoes'], d1['DS'], d1['participacao_gol']]
                val2 = [d2['indice_pro'], d2['media_basica'], d2['G'], d2['finalizacoes'], d2['DS'], d2['participacao_gol']]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=val1, theta=categorias, fill='toself', name=f"{p1} ({d1['status_txt']})"))
                fig.add_trace(go.Scatterpolar(r=val2, theta=categorias, fill='toself', name=f"{p2} ({d2['status_txt']})"))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

    # ABA 3: TÁTICA (ATUALIZADA)
    with tab3:
        hm1, hm2, hm3 = st.tabs(["🛡️ Defesa (Quem cede pontos)", "⚔️ Ataque (Quem faz pontos)", "🏰 Mando de Campo (BI)"])
        
        with hm1:
            st.markdown("**Fragilidade Defensiva:** Times que mais CEDEM pontos para cada posição.")
            heat = df_periodo.groupby(['adversario', 'posicao_nome'])['pontos'].mean().reset_index()
            if not heat.empty:
                piv = heat.pivot(index='adversario', columns='posicao_nome', values='pontos').fillna(0)
                st.plotly_chart(px.imshow(piv, text_auto=".1f", color_continuous_scale="Reds", aspect="auto"), use_container_width=True)
        
        with hm2:
            st.markdown("**Poder Ofensivo:** Posições de times que mais FAZEM pontos.")
            heat_atk = df_periodo.groupby(['clube_nome', 'posicao_nome'])['pontos'].mean().reset_index()
            if not heat_atk.empty:
                piv2 = heat_atk.pivot(index='clube_nome', columns='posicao_nome', values='pontos').fillna(0)
                st.plotly_chart(px.imshow(piv2, text_auto=".1f", color_continuous_scale="Greens", aspect="auto"), use_container_width=True)

        with hm3:
            st.subheader("📊 Análise de Desempenho: Casa x Fora")
            st.markdown("Analise como os times se comportam dependendo do mando de campo (usando os filtros da sidebar).")
            
            if df_periodo.empty:
                st.warning("Sem dados históricos no período selecionado.")
            else:
                # 1. Agrupamento por Time e Mando (Média de Pontos)
                stats_mando = df_periodo.groupby(['clube_nome', 'mando'])['pontos'].mean().reset_index()
                
                # Gráfico 1: Pontuação Média (Casa vs Fora)
                st.markdown("#### Média de Pontos: Quem é forte em casa e quem surpreende fora?")
                fig_pts = px.bar(
                    stats_mando, 
                    x='clube_nome', 
                    y='pontos', 
                    color='mando', 
                    barmode='group',
                    labels={'pontos': 'Média de Pontos', 'clube_nome': 'Time'},
                    color_discrete_map={'CASA': '#FFD700', 'FORA': '#696969'} # Dourado e Cinza
                )
                fig_pts.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_pts, use_container_width=True)
                
                st.divider()
                
                # 2. Agrupamento por Scouts (Soma)
                col_scout = st.selectbox("Selecione a métrica de scout para comparar:", ["Gols (G)", "Desarmes (DS)", "Finalizações (FF+FD)"])
                
                # Mapeamento para o nome real da coluna
                mapa_scout_cols = {
                    "Gols (G)": "G",
                    "Desarmes (DS)": "DS",
                    "Finalizações (FF+FD)": "finalizacoes"
                }
                scout_view_col = mapa_scout_cols[col_scout]
                
                stats_scout = df_periodo.groupby(['clube_nome', 'mando'])[scout_view_col].sum().reset_index()
                
                # Gráfico 2: Comparação de Scouts
                st.markdown(f"#### Produtividade em Mando: {col_scout}")
                fig_scout = px.bar(
                    stats_scout,
                    x='clube_nome',
                    y=scout_view_col,
                    color='mando',
                    barmode='group',
                    labels={scout_view_col: f'Total de {col_scout}', 'clube_nome': 'Time'},
                    color_discrete_map={'CASA': '#FF8C00', 'FORA': '#708090'} # Cores levemente diferentes para diferenciar
                )
                fig_scout.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_scout, use_container_width=True)

    # ABA 4: MERCADO
    with tab4:
        st.markdown("### 📋 Tabela Completa")
        # Coluna Status inserida após a foto
        cols_view = ['foto', 'status', 'apelido', 'posicao_nome', 'clube_nome', 'jogos_disputados', 'preco', 'indice_pro', 'media_geral', 'media_basica'] + scouts_cols
        
        st.dataframe(
            df_agrupado[cols_view].sort_values('indice_pro', ascending=False),
            column_config={
                "foto": st.column_config.ImageColumn("Foto", width="small"),
                "status": "Status",
                "jogos_disputados": st.column_config.NumberColumn("Jogos", format="%d"),
                "preco": st.column_config.NumberColumn("C$", format="%.2f"),
                "indice_pro": st.column_config.NumberColumn("Índice PRO ✨", format="%.2f"),
                "media_geral": st.column_config.NumberColumn("Média Tot", format="%.2f"),
                "media_basica": st.column_config.ProgressColumn("Pont. Básica", format="%.2f", min_value=-5, max_value=15),
            },
            use_container_width=True, hide_index=True, height=600
        )

    # ABA 5: DESTAQUES
    with tab5:
        st.subheader("🏆 Líderes por Fundamento")
        
        def render_leader_card(titulo, col_sort, col_container, sufixo=""):
            if df_agrupado.empty: return
            df_valid = df_agrupado[df_agrupado[col_sort] > 0]
            if df_valid.empty: return
            
            lider = df_valid.sort_values(col_sort, ascending=False).iloc[0]
            val = int(lider[col_sort])
            
            with col_container:
                c_img, c_txt = st.columns([1, 2])
                c_img.image(lider['foto'], width=70)
                c_txt.caption(f"{titulo}")
                c_txt.markdown(f"**{lider['apelido']}**")
                c_txt.markdown(f"### {val} {sufixo}")
                st.divider()

        r1, r2, r3, r4 = st.columns(4)
        render_leader_card("Participação (G+A)", "participacao_gol", r1)
        render_leader_card("Artilheiro", "G", r2, "Gols")
        render_leader_card("Garçom", "A", r3, "Assis")
        render_leader_card("Finalizações", "finalizacoes", r4, "Chutes")

        r5, r6, r7, r8 = st.columns(4)
        render_leader_card("Desarmes", "DS", r5)
        render_leader_card("Faltas Sofridas", "FS", r6)
        render_leader_card("Defesas (Gol)", "DE", r7)
        render_leader_card("Paredão (SG)", "SG", r8, "Jgs")