import numpy as np
import pandas as pd
import streamlit as st
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from scipy.stats import linregress
import plotly.express as px
import plotly.graph_objects as go

st.markdown("""
<style>
/* Estilo principal do card */
.vehicle-group-card {
    background-color: #1a1a2e; /* Cor de fundo escura */
    border-radius: 10px;      /* Bordas arredondadas */
    padding: 20px;            /* Espaçamento interno */
    margin-bottom: 20px;      /* Espaço entre os cards */
    border: 1px solid #4a4e69; /* Borda sutil */
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); /* Sombra para dar profundidade */
}
/* Título do card (Ex: 🚗 Leves) */
.vehicle-group-title {
    font-size: 24px;
    font-weight: bold;
    color: #e0e1dd; /* Cor clara para o título */
    margin-bottom: 15px;
}
/* Valor principal (Ex: 89 Veículos) */
.vehicle-group-value {
    font-size: 28px;
    font-weight: bold;
    color: #00a8e8; /* Cor de destaque (azul) */
    margin-bottom: 20px;
}
/* Subtítulo para o ranking */
.vehicle-group-ranking-title {
    font-size: 16px;
    color: #a9a9a9; /* Cinza claro */
    border-top: 1px solid #4a4e69; /* Linha separadora */
    padding-top: 15px;
    margin-bottom: 10px;
}
/* Cada item do ranking */
.vehicle-group-ranking-item {
    font-size: 16px;
    color: #e0e1dd;
    margin-bottom: 5px;
    padding-left: 10px;
}
</style>
""", unsafe_allow_html=True)

def exibir_dashboard_executivo(df_filtrado, df_completo, titulo_principal):
    """
    Visão Resumida com design 100% adaptativo, cores personalizadas por
    tipo de card e correção da exibição do Custo por Grupo.
    """
    st.subheader(f"👔 Visão Resumida - {titulo_principal}")

    if df_filtrado.empty:
        st.warning("Não há dados para exibir com os filtros selecionados.")
        return

    # --- 1. CÁLCULOS GLOBAIS ---
    data_min = df_filtrado['data'].min()
    data_max = df_filtrado['data'].max()
    periodo_str = f"{data_min.strftime('%m/%Y')} até {data_max.strftime('%m/%Y')}"
    custo_total = df_filtrado['custo_frota_total'].sum()
    contagem_veiculos = df_filtrado['Placa'].nunique()
    colunas_custo = {
        'Combustível': 'custo_combustivel', 'Manutenção': 'custo_manutencao_geral',
        'Pneus': 'custo_rodas_pneus', 'Lataria': 'custo_lataria_pintura', 'Arla': 'custo_arla'
    }
    custo_total_segmentado = {nome: df_filtrado[coluna].sum() for nome, coluna in colunas_custo.items()}
    mes_atual_data = data_max.replace(day=1)
    mes_anterior_data = (mes_atual_data - timedelta(days=1)).replace(day=1)
    df_mes_atual = df_completo[df_completo['data'].dt.to_period('M') == mes_atual_data.to_period('M')]
    df_mes_anterior = df_completo[df_completo['data'].dt.to_period('M') == mes_anterior_data.to_period('M')]
    custos_atuais = {nome: df_mes_atual[coluna].sum() for nome, coluna in colunas_custo.items()}
    custos_anteriores = {nome: df_mes_anterior[coluna].sum() for nome, coluna in colunas_custo.items()}
    

    def calcular_delta(atual, anterior):
        if anterior > 0: 
            return ((atual - anterior) / anterior) * 100
        elif atual > 0:
            return 100.0
        return 0.0

    # --- 2. CSS ADAPTATIVO COM BORDAS COLORIDAS ---
    st.markdown("""
    <style>
    /* Variáveis para tema inverso */
    :root {
        --card-bg-color: #000000;  /* PRETO no tema claro */
        --card-text-color: #ffffff;
        --card-detail-color: #e5e7eb;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --card-bg-color: #ffffff;  /* BRANCO no tema escuro */
            --card-text-color: #000000;
            --card-detail-color: #374151;
        }
    }

    /* Para Streamlit tema escuro */
    [data-theme="dark"] {
        --card-bg-color: #ffffff;
        --card-text-color: #000000;
        --card-detail-color: #374151;
    }

    /* Estilo Base para cards maiores */
    .custom-card {
        background-color: var(--card-bg-color);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 3px solid;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        min-height: 200px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Bordas coloridas apenas */
    .card-blue {
        border-color: #3b82f6;
    }

    .card-projection {
        border-color: #22c55e;
    }

    .card-orange {
        border-color: #f97316;
    }

    .card-yellow {
        border-color: #eab308;
    }

    /* Estilos de Texto dentro dos cards maiores */
    .card-title {
        font-size: 18px;
        font-weight: bold;
        color: var(--card-text-color);
        margin-bottom: 16px;
        text-transform: uppercase;
    }

    .card-detail {
        font-size: 15px;
        font-weight: bold;
        color: var(--card-detail-color);
        margin: 8px 0;
    }

    /* Valores dos cards - com cores da borda */
    .card-value {
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 12px;
    }

    .card-blue .card-value { color: #3b82f6; }
    .card-projection .card-value { color: #22c55e; }
    .card-orange .card-value { color: #f97316; }
    .card-yellow .card-value { color: #eab308; }

    /* Estilos para KPIs menores */
    .kpi-card {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--gray-80);
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
        text-align: center;
    }

    .kpi-title {
        font-size: 16px;
        color: var(--card-text-color);
        margin-bottom: 10px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .kpi-value {
        font-size: 26px;
        font-weight: bold;
        color: var(--card-text-color);
        margin-bottom: 10px;
    }

    .kpi-comparison {
        font-size: 14px;
        font-weight: bold;
        color: var(--card-detail-color);
    }

    .kpi-delta-positive { color: #f44336; }
    .kpi-delta-negative { color: #4caf50; }
    </style>
    """, unsafe_allow_html=True)

    # --- 3. LAYOUT E EXIBIÇÃO ---

    # LINHA 1: CARD PRINCIPAL E PROJEÇÃO
    meses_dados_visiveis = df_filtrado['mes_ano'].nunique()
    card_principal_html = f"""
        <div class="custom-card card-blue">
            <div class="card-title">💰 Custo Total da Frota</div>
            <div class="card-value">R$ {custo_total:,.2f}</div>
            <div class="card-detail"><strong>Período:</strong> {periodo_str}</div>
            <div class="card-detail"><strong>⛽ Combustível:</strong> R$ {custo_total_segmentado['Combustível']:,.2f}</div>
            <div class="card-detail"><strong>🔧 Manutenção:</strong> R$ {custo_total_segmentado['Manutenção']:,.2f}</div>
            <div class="card-detail"><strong>🎨 Lataria:</strong> R$ {custo_total_segmentado['Lataria']:,.2f}</div>
            <div class="card-detail"><strong>🚙 Pneus:</strong> R$ {custo_total_segmentado['Pneus']:,.2f}</div>
            <div class="card-detail"><strong>⛽ Arla:</strong> R$ {custo_total_segmentado['Arla']:,.2f}</div>
        </div>
    """

    # Calcular informações adicionais sobre veículos
    veiculos_por_grupo = df_filtrado.groupby('grupocorreto')['Placa'].nunique().to_dict()
    total_registros = len(df_filtrado)

    card_veiculos_html = f"""
        <div class="custom-card card-orange">
            <div class="card-title">🚚 Veículos na Operação</div>
            <div class="card-value">{contagem_veiculos}</div>
            <div class="card-detail"><strong>Período:</strong> {periodo_str}</div>
            <div class="card-detail"><strong>📊 Total de Registros:</strong> {total_registros:,}</div>
            <div class="card-detail"><strong>📈 Média Reg./Veículo:</strong> {total_registros/contagem_veiculos:.1f}</div>
            <div class="card-detail" style="margin-bottom: 4px;"><strong>🚛 Principais Grupos:</strong></div>
            {''.join([f'<div class="card-detail" style="margin: 2px 0;">  • {grupo}: {qtd} veículos</div>' for grupo, qtd in sorted(veiculos_por_grupo.items(), key=lambda x: x[1], reverse=True)[:3]])}
        </div>
    """

    if meses_dados_visiveis > 1:
        # COM estimativa anual: Card principal + Card estimativa / Card veículos ocupa linha inteira
        col_principal, col_projecao = st.columns(2)
        with col_principal:
            st.markdown(card_principal_html, unsafe_allow_html=True)
        with col_projecao:
            projecao_anual = (custo_total / meses_dados_visiveis) * 12
            st.markdown(f"""<div class="custom-card card-projection"><div class="card-title">📈 Estimativa Anual</div><div class="card-value">R$ {projecao_anual:,.2f}</div><div class="card-detail"><strong>Base:</strong> {meses_dados_visiveis} meses</div>{''.join([f'<div class="card-detail"><strong> • {nome}:</strong> R$ {((custos_atuais[nome] / meses_dados_visiveis) * 12):,.2f}</div>' for nome in colunas_custo.keys()])}</div>""", unsafe_allow_html=True)

        # LINHA 2: Card de Veículos ocupando linha inteira
        st.markdown(card_veiculos_html, unsafe_allow_html=True)
    else:
        # SEM estimativa anual: Card principal e Card veículos lado a lado com mesmo tamanho
        col_principal, col_veiculos = st.columns(2)
        with col_principal:
            st.markdown(card_principal_html, unsafe_allow_html=True)
        with col_veiculos:
            st.markdown(card_veiculos_html, unsafe_allow_html=True)
    st.markdown("---")

    # LINHA 3: Variações vs. Mês Anterior
    st.subheader("Variação vs. Mês Anterior")
    cols_variacao = st.columns(len(colunas_custo))
    for i, nome in enumerate(colunas_custo.keys()):
        with cols_variacao[i]:
            valor_atual, valor_anterior = custos_atuais[nome], custos_anteriores[nome]
            delta = calcular_delta(valor_atual, valor_anterior)
            delta_symbol = "▲" if delta >= 0 else "▼"
            delta_color = "#ff4b4b" if delta >= 0 else "#28a745"

            # Formatação mais compacta para valores grandes
            valor_atual_str = f"R$ {valor_atual/1000:.0f}k" if valor_atual >= 10000 else f"R$ {valor_atual:,.2f}"
            valor_anterior_str = f"R$ {valor_anterior/1000:.0f}k" if valor_anterior >= 10000 else f"R$ {valor_anterior:,.2f}"

            st.markdown(f"""
            <div class="custom-card card-yellow" style="min-height: 180px;">
                <div class="card-title">{nome}</div>
                <div class="card-value" style="font-size: 24px;">{valor_atual_str}</div>
                <div class="card-detail" style="color: {delta_color}; font-weight: bold; font-size: 16px;">{delta_symbol} {abs(delta):.1f}%</div>
                <div class="card-detail" style="color: {delta_color}; font-weight: bold;">Anterior: {valor_anterior_str}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("---")

    # LINHA 4: CUSTO MÉDIO POR GRUPO (CORRIGIDO E RESTAURADO)
    if 'grupocorreto' in df_filtrado.columns:
        st.subheader("Custo Médio por Grupo de Veículo")
        custo_por_grupo = df_filtrado.groupby('grupocorreto').agg(CustoTotal=('custo_frota_total', 'sum'), NumVeiculos=('Placa', 'nunique')).reset_index()
        custo_por_grupo['CustoMedio'] = custo_por_grupo.apply(lambda row: row['CustoTotal'] / row['NumVeiculos'] if row['NumVeiculos'] > 0 else 0, axis=1)

        # Adicionar emoji e ordem lógica baseado no tipo de grupo
        def get_grupo_info(grupo):
            grupo_lower = str(grupo).lower()
            if 'leve' in grupo_lower:
                return '🚗', 1
            elif 'médio' in grupo_lower or 'medio' in grupo_lower:
                return '🚐', 2
            elif 'pesado' in grupo_lower:
                return '🚚', 3
            elif 'caminhão' in grupo_lower or 'caminhao' in grupo_lower:
                return '🚛', 4
            else:
                return '🚙', 5

        # Adicionar emoji e ordem para ordenação
        custo_por_grupo['emoji'] = custo_por_grupo['grupocorreto'].apply(lambda x: get_grupo_info(x)[0])
        custo_por_grupo['ordem'] = custo_por_grupo['grupocorreto'].apply(lambda x: get_grupo_info(x)[1])

        # Ordenar por ordem lógica: Leve, Médio, Pesado, Caminhão
        custo_por_grupo = custo_por_grupo.sort_values('ordem')

        if not custo_por_grupo.empty:
            cols_grupos = st.columns(len(custo_por_grupo))
            for i, (idx, row) in enumerate(custo_por_grupo.iterrows()):
                with cols_grupos[i]:
                    # Formatação mais compacta para valores grandes
                    custo_total_str = f"R$ {row['CustoTotal']/1000:.0f}k" if row['CustoTotal'] >= 10000 else f"R$ {row['CustoTotal']:,.2f}"
                    custo_medio_str = f"R$ {row['CustoMedio']/1000:.1f}k" if row['CustoMedio'] >= 10000 else f"R$ {row['CustoMedio']:,.2f}"

                    st.markdown(f"""
                    <div class="custom-card card-orange">
                        <div class="card-title">{row['emoji']} {row['grupocorreto']}</div>
                        <div class="card-value" style="font-size: 24px;">{custo_medio_str}</div>
                        <div class="card-detail" style="font-weight: bold; font-size: 15px;">{row['NumVeiculos']} veículos</div>
                        <div class="card-detail" style="font-weight: bold; font-size: 15px; color: #ff8c00;">Total: {custo_total_str}</div>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown("---")

    # LINHA 5: ANÁLISE POR FILIAL (COM FUNDO AZUL E DETALHES)
    st.subheader("Análise Resumida por Filial")
    gastos_por_filial = df_filtrado.groupby('filial')['custo_frota_total'].sum().sort_values(ascending=False)
    if not gastos_por_filial.empty:
        num_colunas = 3
        cols = st.columns(num_colunas)
        for i, (filial_nome, custo_total_filial) in enumerate(gastos_por_filial.items()):
            with cols[i % num_colunas]:
                df_da_filial = df_filtrado[df_filtrado['filial'] == filial_nome]
                custos_filial = {nome: df_da_filial[coluna].sum() for nome, coluna in colunas_custo.items()}
                st.markdown(f"""
                <div class="custom-card card-blue">
                    <div class="card-title">🏢 {filial_nome}</div>
                    <div class="card-value">R$ {custo_total_filial:,.2f}</div>
                    <div class="card-detail"><strong>⛽ Combustível:</strong> R$ {custos_filial['Combustível']:,.2f}</div>
                    <div class="card-detail"><strong>🔧 Manutenção:</strong> R$ {custos_filial['Manutenção']:,.2f}</div>
                    <div class="card-detail"><strong>🎨 Lataria:</strong> R$ {custos_filial['Lataria']:,.2f}</div>
                    <div class="card-detail"><strong>🚙 Pneus:</strong> R$ {custos_filial['Pneus']:,.2f}</div>
                    <div class="card-detail"><strong>⛽ Arla:</strong> R$ {custos_filial['Arla']:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)

def calcular_kpis_performance(df_historico, ano_selecionado, mes_selecionado, coluna_custo):
    if mes_selecionado == 'Todos' or ano_selecionado == 'Todos':
        return None
    data_base = pd.to_datetime(f"{mes_selecionado}-01")
    mes_anterior = data_base - relativedelta(months=1)
    tres_meses_atras = data_base - relativedelta(months=3)
    seis_meses_atras = data_base - relativedelta(months=6)
    doze_meses_atras = data_base - relativedelta(months=12)
    
    # Filtros de dados
    df_mes_atual = df_historico[df_historico['mes_ano'] == data_base.strftime('%Y-%m')]
    df_mes_anterior = df_historico[df_historico['mes_ano'] == mes_anterior.strftime('%Y-%m')]
    df_ultimos_3_meses = df_historico[(df_historico['data'] >= tres_meses_atras) & (df_historico['data'] < data_base)]
    df_ultimos_6_meses = df_historico[(df_historico['data'] >= seis_meses_atras) & (df_historico['data'] < data_base)]
    df_ultimos_12_meses = df_historico[(df_historico['data'] >= doze_meses_atras) & (df_historico['data'] < data_base)]
    
    # Cálculos de custos
    custo_mes_atual = df_mes_atual[coluna_custo].sum()
    custo_mes_anterior = df_mes_anterior[coluna_custo].sum()
    custo_ultimos_3_meses = df_ultimos_3_meses[coluna_custo].sum()
    custo_ultimos_6_meses = df_ultimos_6_meses[coluna_custo].sum()
    custo_ultimos_12_meses = df_ultimos_12_meses[coluna_custo].sum()
    
    # Médias
    media_3_meses = custo_ultimos_3_meses / 3 if custo_ultimos_3_meses > 0 else 0
    media_6_meses = custo_ultimos_6_meses / 6 if custo_ultimos_6_meses > 0 else 0
    media_12_meses = custo_ultimos_12_meses / 12 if custo_ultimos_12_meses > 0 else 0
    
    # Cálculos de dias úteis - verificação mais robusta
    dias_uteis_atual = 0
    if not df_mes_atual.empty and 'Dias Úteis' in df_mes_atual.columns:
        dias_uteis_value = df_mes_atual['Dias Úteis'].iloc[0]
        dias_uteis_atual = dias_uteis_value if pd.notna(dias_uteis_value) else 22  # Default para mês com 22 dias úteis
    else:
        dias_uteis_atual = 22  # Default

    dias_uteis_anterior = 0
    if not df_mes_anterior.empty and 'Dias Úteis' in df_mes_anterior.columns:
        dias_uteis_value = df_mes_anterior['Dias Úteis'].iloc[0]
        dias_uteis_anterior = dias_uteis_value if pd.notna(dias_uteis_value) else 22
    else:
        dias_uteis_anterior = 22
    
    custo_dia_util_atual = custo_mes_atual / dias_uteis_atual if dias_uteis_atual > 0 else 0
    custo_dia_util_anterior = custo_mes_anterior / dias_uteis_anterior if dias_uteis_anterior > 0 else 0
    
    # Médias por dia útil - verificação mais robusta
    soma_dias_uteis_3m = 0
    if 'Dias Úteis' in df_ultimos_3_meses.columns and not df_ultimos_3_meses.empty:
        dias_uteis_3m = df_ultimos_3_meses.groupby('mes_ano')['Dias Úteis'].first()
        dias_uteis_3m = dias_uteis_3m.fillna(22)  # Preencher valores nulos com 22
        soma_dias_uteis_3m = dias_uteis_3m.sum()
    else:
        soma_dias_uteis_3m = 66  # 3 meses * 22 dias úteis

    media_dia_util_3m = custo_ultimos_3_meses / soma_dias_uteis_3m if soma_dias_uteis_3m > 0 else 0
    
    # Cálculo de variação percentual
    var_perc_mes_anterior = ((custo_mes_atual - custo_mes_anterior) / custo_mes_anterior * 100) if custo_mes_anterior > 0 else 0
    var_perc_media_3m = ((custo_mes_atual - media_3_meses) / media_3_meses * 100) if media_3_meses > 0 else 0
    
    # Tendência (últimos 3 meses)
    tendencia_meses = df_ultimos_3_meses.groupby('mes_ano')[coluna_custo].sum().values
    tendencia = "Crescente" if len(tendencia_meses) > 1 and np.mean(np.diff(tendencia_meses)) > 0 else "Decrescente"
    
    kpis = {
        'custo_mes_atual': custo_mes_atual,
        'custo_mes_anterior': custo_mes_anterior,
        'diff_mes_anterior': custo_mes_atual - custo_mes_anterior,
        'var_perc_mes_anterior': var_perc_mes_anterior,
        'media_3_meses': media_3_meses,
        'media_6_meses': media_6_meses,
        'media_12_meses': media_12_meses,
        'diff_media_3_meses': custo_mes_atual - media_3_meses,
        'diff_media_6_meses': custo_mes_atual - media_6_meses,
        'diff_media_12_meses': custo_mes_atual - media_12_meses,
        'var_perc_media_3m': var_perc_media_3m,
        'custo_dia_util_atual': custo_dia_util_atual,
        'custo_dia_util_anterior': custo_dia_util_anterior,
        'diff_dia_util_anterior': custo_dia_util_atual - custo_dia_util_anterior,
        'media_dia_util_3m': media_dia_util_3m,
        'diff_media_dia_util_3m': custo_dia_util_atual - media_dia_util_3m,
        'tendencia': tendencia,
        'total_veiculos': df_mes_atual['Placa'].nunique() if not df_mes_atual.empty else 0,
        'custo_por_veiculo': custo_mes_atual / df_mes_atual['Placa'].nunique() if not df_mes_atual.empty and df_mes_atual['Placa'].nunique() > 0 else 0
    }
    return kpis

def exibir_kpis_em_cartoes(kpis, tipo_custo):
    """
    Exibe os 8 KPIs de performance mensal com o CSS padrão do projeto,
    garantindo um tamanho uniforme para todos os cards.
    """
    st.subheader(f"📊 Indicadores de Performance Mensal ({tipo_custo})")
    
    # --- CSS PADRÃO DO PROJETO (ATUALIZADO) ---
    st.markdown("""
    <style>
    /* Estilo Base para cards */
    .custom-card {
        background-color: var(--card-bg-color); border-radius: 16px;
        padding: 24px; margin-bottom: 24px; border: 3px solid;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: all 0.3s ease;
        height: 100%; /* Manter height 100% para se expandir na coluna */
        min-height: 180px; /* <--- NOVO: Altura mínima para padronizar */
        display: flex; flex-direction: column;
        justify-content: space-between; /* Espaça o conteúdo */
    }
    /* Bordas coloridas */
    .card-blue { border-color: #3b82f6; }
    .card-green { border-color: #22c55e; }
    .card-orange { border-color: #f97316; }
    .card-yellow { border-color: #eab308; }
    /* Estilos de Texto */
    .card-title {
        font-size: 16px; font-weight: bold; color: var(--card-detail-color);
        margin-bottom: 12px; text-transform: uppercase;
        display: flex; align-items: center; /* <--- NOVO: Alinha ícone e texto */
        gap: 8px; /* <--- NOVO: Espaçamento entre ícone e texto */
    }
    .card-value { font-size: 26px; font-weight: bold; margin-bottom: 12px; } /* <--- AJUSTADO: Margin para espaçamento */
    .card-detail { 
        font-size: 14px; color: var(--card-detail-color); 
        min-height: 20px; /* <--- NOVO: Garante altura para detalhes de uma linha */
    }
    /* Cores dos valores */
    .card-blue .card-value { color: #3b82f6; }
    .card-green .card-value { color: #22c55e; }
    .card-orange .card-value { color: #f97316; }
    .card-yellow .card-value { color: #eab308; }
    /* Classes para deltas positivo/negativo */
    .delta-positive { color: #ff4b4b; font-weight: bold; font-size: 14px; margin-top: 8px; } /* <--- AJUSTADO: Margin e tamanho */
    .delta-negative { color: #28a745; font-weight: bold; font-size: 14px; margin-top: 8px; } /* <--- AJUSTADO: Margin e tamanho */
    </style>
    """, unsafe_allow_html=True)
    
    # --- LÓGICA DE PREPARAÇÃO ---
    cor_tendencia_card = "card-green" if kpis.get('tendencia') == "Decrescente" else "card-orange"
    
    eficiencia = "Alta" if kpis.get('var_perc_mes_anterior', 0) < 5 else "Baixa" if kpis.get('var_perc_mes_anterior', 0) > 15 else "Média"
    cor_eficiencia_card = {"Alta": "card-green", "Média": "card-yellow", "Baixa": "card-orange"}.get(eficiencia, "card-blue") # Default para evitar erro
    
    # --- EXIBIÇÃO DOS 8 CARDS ORIGINAIS ---

    # Primeira linha - KPIs principais
    cols1 = st.columns(4)
    with cols1[0]:
        diff = kpis.get('diff_mes_anterior', 0)
        var_perc = kpis.get('var_perc_mes_anterior', 0)
        cor_delta = "positive" if diff > 0 else "negative"
        st.markdown(f"""
        <div class="custom-card card-blue">
            <div class="card-title"><span>🗓️</span>Custo vs. Mês Anterior</div>
            <div class="card-value">R$ {kpis.get('custo_mes_atual', 0):,.2f}</div>
            <div class="card-detail">Anterior: R$ {kpis.get('custo_mes_anterior', 0):,.2f}</div>
            <div class="delta-{cor_delta}">
                {'↑' if diff > 0 else '↓'} R$ {abs(diff):,.2f} ({var_perc:+.1f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols1[1]:
        diff = kpis.get('diff_media_3_meses', 0)
        var_perc = kpis.get('var_perc_media_3m', 0)
        cor_delta = "positive" if diff > 0 else "negative"
        st.markdown(f"""
        <div class="custom-card card-blue">
            <div class="card-title"><span>📊</span>Custo vs. Média 3M</div>
            <div class="card-value">R$ {kpis.get('custo_mes_atual', 0):,.2f}</div>
            <div class="card-detail">Média 3M: R$ {kpis.get('media_3_meses', 0):,.2f}</div>
            <div class="delta-{cor_delta}">
                {'↑' if diff > 0 else '↓'} R$ {abs(diff):,.2f} ({var_perc:+.1f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols1[2]:
        diff = kpis.get('diff_media_6_meses', 0)
        var_perc = kpis.get('var_perc_media_6m', 0)
        cor_delta = "positive" if diff > 0 else "negative"
        st.markdown(f"""
        <div class="custom-card card-blue">
            <div class="card-title"><span>📈</span>Custo vs. Média 6M</div>
            <div class="card-value">R$ {kpis.get('custo_mes_atual', 0):,.2f}</div>
            <div class="card-detail">Média 6M: R$ {kpis.get('media_6_meses', 0):,.2f}</div>
            <div class="delta-{cor_delta}">
                {'↑' if diff > 0 else '↓'} R$ {abs(diff):,.2f} ({var_perc:+.1f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols1[3]:
        diff = kpis.get('diff_media_12_meses', 0)
        var_perc = kpis.get('var_perc_media_12m', 0)
        cor_delta = "positive" if diff > 0 else "negative"
        st.markdown(f"""
        <div class="custom-card card-blue">
            <div class="card-title"><span>📅</span>Custo vs. Média 12M</div>
            <div class="card-value">R$ {kpis.get('custo_mes_atual', 0):,.2f}</div>
            <div class="card-detail">Média 12M: R$ {kpis.get('media_12_meses', 0):,.2f}</div>
            <div class="delta-{cor_delta}">
                {'↑' if diff > 0 else '↓'} R$ {abs(diff):,.2f} ({var_perc:+.1f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Segunda linha - KPIs operacionais (CORRIGIDO)
    cols2 = st.columns(4)

    with cols2[0]:
        diff = kpis.get('diff_dia_util_anterior', 0)
        cor_delta = "positive" if diff > 0 else "negative"
        st.markdown(f"""
        <div class="custom-card card-blue">
            <div class="card-title"><span>🗓️</span>Custo/Dia Útil</div>
            <div class="card-value">R$ {kpis.get('custo_dia_util_atual', 0):,.2f}</div>
            <div class="card-detail">Anterior: R$ {kpis.get('custo_dia_util_anterior', 0):,.2f}</div>
            <div class="delta-{cor_delta}">
                {'↑' if diff > 0 else '↓'} R$ {abs(diff):,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with cols2[1]:
        st.markdown(f"""
        <div class="custom-card card-blue">
            <div class="card-title"><span>🚛</span>Custo por Veículo</div>
            <div class="card-value">R$ {kpis.get('custo_por_veiculo', 0):,.2f}</div>
            <div class="card-detail">Total Veículos: {kpis.get('total_veiculos', 0)}</div>
            <div class="delta-positive" style="visibility: hidden;">&nbsp;</div>
        </div>
        """, unsafe_allow_html=True)

    with cols2[2]:
        st.markdown(f"""
        <div class="custom-card {cor_tendencia_card}">
            <div class="card-title"><span>📈</span>Tendência (3M)</div>
            <div class="card-value">{kpis.get('tendencia', 'Indefinida')}</div>
            <div class="card-detail">Baseado nos últimos 3 meses</div>
            <div class="delta-positive" style="visibility: hidden;">&nbsp;</div>
        </div>
        """, unsafe_allow_html=True)

    with cols2[3]:
        st.markdown(f"""
        <div class="custom-card {cor_eficiencia_card}">
            <div class="card-title"><span>⚡</span>Eficiência de Custo</div>
            <div class="card-value">{eficiencia}</div>
            <div class="card-detail">Variação: {kpis.get('var_perc_mes_anterior', 0):+.1f}%</div>
            <div class="delta-positive" style="visibility: hidden;">&nbsp;</div>
        </div>
        """, unsafe_allow_html=True)


def exibir_graficos_performance_avancados(df_historico, mes_selecionado, kpis, coluna_custo, titulo_grafico):
    st.subheader("📈 Visualização Avançada da Performance")
    
    # Preparação dos dados para gráficos
    doze_meses_atras = (pd.to_datetime(f"{mes_selecionado}-01") - relativedelta(months=11)).strftime('%Y-%m')
    df_grafico = df_historico[df_historico['mes_ano'] >= doze_meses_atras]
    
    # Dados mensais e médias móveis
    evolucao_mensal = df_grafico.groupby('mes_ano')[coluna_custo].sum().reset_index()
    evolucao_mensal['Media_Movel_3M'] = evolucao_mensal[coluna_custo].rolling(window=3, min_periods=1).mean()
    evolucao_mensal['Media_Movel_6M'] = evolucao_mensal[coluna_custo].rolling(window=6, min_periods=1).mean()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de linha com médias móveis
        fig_evolucao = go.Figure()
        
        fig_evolucao.add_trace(go.Scatter(
            x=evolucao_mensal['mes_ano'],
            y=evolucao_mensal[coluna_custo],
            mode='lines+markers',
            name='Custo Mensal',
            line=dict(color='#007bff', width=3),
            marker=dict(size=8)
        ))
        
        fig_evolucao.add_trace(go.Scatter(
            x=evolucao_mensal['mes_ano'],
            y=evolucao_mensal['Media_Movel_3M'],
            mode='lines',
            name='Média Móvel 3M',
            line=dict(color='#28a745', width=2, dash='dash')
        ))
        
        fig_evolucao.add_trace(go.Scatter(
            x=evolucao_mensal['mes_ano'],
            y=evolucao_mensal['Media_Movel_6M'],
            mode='lines',
            name='Média Móvel 6M',
            line=dict(color='#ff7f0e', width=2, dash='dot')
        ))
        
        fig_evolucao.update_layout(
            title=f'Evolução {titulo_grafico} - Últimos 12 Meses',
            xaxis_title='Mês',
            yaxis_title='Custo (R$)',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_evolucao, width='content')
    
    with col2:
        # Gráfico de barras comparativo expandido
        dados_comparativo = {
            'Período': ['Mês Atual', 'Mês Anterior', 'Média 3M', 'Média 6M', 'Média 12M'],
            'Custo Total': [
                kpis['custo_mes_atual'],
                kpis['custo_mes_anterior'],
                kpis['media_3_meses'],
                kpis['media_6_meses'],
                kpis['media_12_meses']
            ]
        }
        df_comparativo = pd.DataFrame(dados_comparativo)
        
        fig_bar_comp = px.bar(
            df_comparativo,
            x='Período',
            y='Custo Total',
            title=f'Comparativo Ampliado - {titulo_grafico}',
            text='Custo Total',
            color='Custo Total',
            color_continuous_scale='viridis'
        )
        fig_bar_comp.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig_bar_comp.update_layout(showlegend=False)
        st.plotly_chart(fig_bar_comp, width='content')
    
    st.subheader("📊 Análise de Variabilidade e Controle")

    st.info("""
    Esta seção analisa o **comportamento** e a **previsibilidade** dos seus custos ao longo do tempo. 
    O objetivo é responder a perguntas estratégicas como: 'Nossos custos são estáveis ou voláteis?' 
    e 'A tendência geral é de melhora ou piora?'.
    """, icon="🧠")

    # Verifica se há dados suficientes para a análise
    if evolucao_mensal.empty or len(evolucao_mensal) < 2:
        st.warning("Dados insuficientes para análise de variabilidade (necessário mais de 1 mês).")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # --- CÁLCULO E EXIBIÇÃO: Coeficiente de Variação ---
            media_cv = evolucao_mensal[coluna_custo].mean()
            std_cv = evolucao_mensal[coluna_custo].std()
            cv = (std_cv / media_cv) * 100 if media_cv > 0 else 0
            
            if cv < 15:
                classificacao_cv, cor_cv = "Estável ✅", "card-green"
            elif cv < 30:
                classificacao_cv, cor_cv = "Moderada 🟡", "card-yellow"
            else:
                classificacao_cv, cor_cv = "Instável ⚠️", "card-orange"

            st.markdown(f"""
            <div class="custom-card {cor_cv}" style="min-height: 200px;">
                <div class="card-title"><span>🎛️</span>Coeficiente de Variação</div>
                <div class="card-value">{classificacao_cv}</div>
                <div class="card-detail">Variação de <b>{cv:.1f}%</b> em torno da média.</div>
                <div class="card-detail">Menor variação = Maior previsibilidade.</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # --- CÁLCULO E EXIBIÇÃO: Amplitude ---
            max_custo = evolucao_mensal[coluna_custo].max()
            min_custo = evolucao_mensal[coluna_custo].min()
            amplitude = max_custo - min_custo

            st.markdown(f"""
            <div class="custom-card card-blue" style="min-height: 200px;">
                <div class="card-title"><span>↔️</span>Amplitude de Custo</div>
                <div class="card-value">R$ {amplitude:,.0f}</div>
                <div class="card-detail"><b>Max:</b> R$ {max_custo:,.0f}</div>
                <div class="card-detail"><b>Min:</b> R$ {min_custo:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            # --- CÁLCULO E EXIBIÇÃO: Tendência com Minigráfico Embutido ---
            x = np.arange(len(evolucao_mensal))
            slope, _, r_value, _, _ = linregress(x, evolucao_mensal[coluna_custo])
            r_squared = r_value**2
            
            tendencia_stat = "Crescente" if slope > 0 else "Decrescente"
            cor_tendencia_card = "card-orange" if tendencia_stat == "Crescente" else "card-green"
            
            if r_squared > 0.5: forca_tendencia = "Forte"
            elif r_squared > 0.2: forca_tendencia = "Moderada"
            else: forca_tendencia = "Fraca"
                
            # Lógica do Sparkline (embutida, sem função auxiliar)
            sparkline_svg = ""
            dados_sparkline = evolucao_mensal[coluna_custo].tolist()
            cor_linha_sparkline = '#ff4b4b' if tendencia_stat == "Crescente" else '#28a745'
            dados_validos = [d for d in dados_sparkline if pd.notna(d)]
            if len(dados_validos) >= 2:
                min_val, max_val = min(dados_validos), max(dados_validos)
                range_val = max_val - min_val if max_val > min_val else 1
                pontos_y = [20 - ((val - min_val) / range_val * 18) if pd.notna(val) else 10 for val in dados_sparkline]
                pontos_str = " ".join([f"{i * (100 / (len(pontos_y)-1))},{y:.2f}" for i, y in enumerate(pontos_y)])
                sparkline_svg = f"""<svg width="100" height="20" viewBox="0 0 100 20" xmlns="http://www.w3.org/2000/svg" style="margin-top: 5px;"><polyline points="{pontos_str}" fill="none" stroke="{cor_linha_sparkline}" stroke-width="2"/></svg>"""

            st.markdown(f"""
            <div class="custom-card {cor_tendencia_card}" style="min-height: 200px;">
                <div class="card-title"><span>📈</span>Tendência Estatística</div>
                <div class="card-value">{tendencia_stat}</div>
                <div class="card-detail">Força da Tendência: <b>{forca_tendencia}</b> (R²: {r_squared:.2f})</div>
                {sparkline_svg}
            </div>
            """, unsafe_allow_html=True)

def exibir_tendencias_mensais(df_filtrado, titulo_aba):
    """
    Apresenta uma análise comparativa entre todos os meses do período selecionado,
    com foco em gráficos de tendência e uma tabela de dados ranqueada.
    """
    st.subheader(f"📈 Tendências e Desempenho Mensal ({titulo_aba})")

    if df_filtrado.empty or df_filtrado['mes_ano'].nunique() < 2:
        st.info("Selecione um período com pelo menos dois meses para visualizar as tendências comparativas.")
        return

    # --- 1. CÁLCULO DOS DADOS MENSAIS ---
    
    # Agrupa todos os dados por mês para a análise
    custos_mensais = df_filtrado.groupby('mes_ano').agg(
        custo_frota_total=('custo_frota_total', 'sum'),
        custo_manutencao=('valor', 'sum'),
        custo_combustivel=('custo_combustivel_total', 'sum'),
        total_km=('total_km', 'sum'),
        qtd_veiculos=('Placa', 'nunique')
    ).reset_index()

    # Adiciona o cálculo de Custo por KM
    custos_mensais['custo_por_km'] = custos_mensais['custo_frota_total'] / custos_mensais['total_km']
    custos_mensais['custo_por_km'].replace([pd.NA, float('inf'), -float('inf')], 0, inplace=True)
    
    # Ordena os dados cronologicamente para os gráficos
    custos_mensais = custos_mensais.sort_values('mes_ano', ascending=True)

    # --- 2. GRÁFICOS COMPARATIVOS MENSAIS ---
    
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de barras agrupadas para Manutenção vs. Combustível
        fig_composicao = go.Figure()
        fig_composicao.add_trace(go.Bar(
            name='Combustível',
            x=custos_mensais['mes_ano'],
            y=custos_mensais['custo_combustivel'],
            marker_color='#28a745' # Verde
        ))
        fig_composicao.add_trace(go.Bar(
            name='Manutenção',
            x=custos_mensais['mes_ano'],
            y=custos_mensais['custo_manutencao'],
            marker_color='#007bff'
        ))
        fig_composicao.update_layout(
            barmode='group', 
            title='Custo de Combustível vs. Manutenção',
            xaxis_title='Mês',
            yaxis_title='Custo (R$)',
            legend_title_text='Categoria de Custo'
        )
        st.plotly_chart(fig_composicao, use_container_width=True)

    with col2:
        st.write("#### Evolução da Eficiência (Custo por KM)")

        # --- 1. Cálculos de Suporte para o Gráfico ---
        
        # MUDANÇA PRINCIPAL: Cálculo da Média Móvel
        # Você pode ajustar a janela para 2 (mais reativa) ou 4 (mais suave)
        JANELA_MEDIA_MOVEL = 3
        custos_mensais['media_movel_custo_km'] = custos_mensais['custo_por_km'].rolling(window=JANELA_MEDIA_MOVEL).mean()

        # --- 2. Criação do Gráfico com plotly.graph_objects ---
        fig_eficiencia = go.Figure()

        # Adiciona a linha principal da evolução do Custo por KM
        fig_eficiencia.add_trace(go.Scatter(
            x=custos_mensais['mes_ano'],
            y=custos_mensais['custo_por_km'],
            mode='lines+markers', # Linhas com marcadores nos pontos
            name='Custo/KM Mensal',
            line=dict(color='#007bff', width=3)
        ))

        # MUDANÇA PRINCIPAL: Adiciona a linha de TENDÊNCIA (Média Móvel)
        fig_eficiencia.add_trace(go.Scatter(
            x=custos_mensais['mes_ano'],
            y=custos_mensais['media_movel_custo_km'],
            mode='lines',
            name=f'Tendência ({JANELA_MEDIA_MOVEL} meses)',
            line=dict(color='orange', width=2, dash='dash')
        ))

        # --- 3. Layout e Estilização Final ---
        fig_eficiencia.update_layout(
            title_text='Evolução da Eficiência com Tendência de Média Móvel',
            xaxis_title='Mês',
            yaxis_title='Custo por KM (R$)',
            hovermode="x unified", # Melhora a experiência ao passar o mouse
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_eficiencia, use_container_width=True)

        
    st.markdown("---")

    # --- 3. TABELA DE DESEMPENHO MENSAL COM RANKING ---
    st.write("#### 📈 Tabela de Desempenho Mensal")
    
    # Prepara a tabela para exibição
    tabela_display = custos_mensais.copy()
    
    
    
    # Renomeia colunas para visualização
    tabela_display = tabela_display.rename(columns={
        'mes_ano': 'Mês', 'custo_frota_total': 'Custo Total', 'custo_manutencao': 'Manutenção',
        'custo_combustivel': 'Combustível', 'total_km': 'Total de KM', 
        'qtd_veiculos': 'Veículos Únicos', 'custo_por_km': 'Custo/KM'
    }).sort_values('Mês', ascending=False)
    
    st.dataframe(
        tabela_display[[
            'Mês', 'Custo Total', 'Manutenção', 'Combustível', 'Total de KM',
            'Veículos Únicos', 'Custo/KM'
        ]], 
        use_container_width=True,
        hide_index=True,
        column_config={
            "Custo Total": st.column_config.NumberColumn(format="R$ %.2f"),
            "Manutenção": st.column_config.NumberColumn(format="R$ %.2f"),
            "Combustível": st.column_config.NumberColumn(format="R$ %.2f"),
            "Total de KM": st.column_config.NumberColumn(format="%.2f Km"),
            "Custo/KM": st.column_config.NumberColumn(format="R$ %.2f")
        }
    )

def calcular_kpis_operacionais(df_filtrado):
    """Calcula KPIs operacionais baseados nas colunas da base de dados"""
    kpis = {}
    if 'media_km_litro_ajustado' in df_filtrado.columns and 'Placa' in df_filtrado.columns:
        
        # A coluna já foi limpa, ajustada e não contém nulos, então os cálculos são diretos.
        df_eficiencia = df_filtrado.dropna(subset=['media_km_litro_ajustado'])

        if not df_eficiencia.empty:
            # Média geral
            kpis['media_km_por_litro'] = df_eficiencia['media_km_litro_ajustado'].mean()

            # Melhor eficiência (MAIOR valor de Km/L)
            idx_melhor = df_eficiencia['media_km_litro_ajustado'].idxmax()
            kpis['melhor_eficiencia_veiculo'] = df_eficiencia.loc[idx_melhor, 'Placa']
            kpis['melhor_eficiencia_valor'] = df_eficiencia.loc[idx_melhor, 'media_km_litro_ajustado']

            # Pior eficiência (MENOR valor de Km/L)
            idx_pior = df_eficiencia['media_km_litro_ajustado'].idxmin()
            kpis['pior_eficiencia_veiculo'] = df_eficiencia.loc[idx_pior, 'Placa']
            kpis['pior_eficiencia_valor'] = df_eficiencia.loc[idx_pior, 'media_km_litro_ajustado']

    # KPI 2: Custo por Km (simplificado)
    # MUDANÇA: Simplificado. A conversão para numérico já é feita no data_provider.py.
    if 'total_km' in df_filtrado.columns and 'custo_frota_total' in df_filtrado.columns:
        total_km_num = df_filtrado['total_km'].sum()
        total_custo_num = df_filtrado['custo_frota_total'].sum()
        kpis['custo_por_km'] = total_custo_num / total_km_num if total_km_num > 0 else 0

    # KPI 3: Quilometragem média por veículo (simplificado)
    # MUDANÇA: Simplificado. A coluna 'total_km' já é numérica e limpa.
    if 'total_km' in df_filtrado.columns and 'Placa' in df_filtrado.columns:
        km_por_veiculo = df_filtrado.groupby('Placa')['total_km'].sum()
        
        if not km_por_veiculo.empty:
            kpis['km_medio_por_veiculo'] = km_por_veiculo.mean()
            kpis['total_km_frota'] = km_por_veiculo.sum()
            
            if km_por_veiculo.max() > 0:
                kpis['veiculo_mais_rodou'] = km_por_veiculo.idxmax()
                kpis['km_veiculo_mais_rodou'] = km_por_veiculo.max()
    
    # ==================================================================
    #              FIM DO BLOCO DE CÓDIGO ATUALIZADO
    # ==================================================================

    # KPI 4: Taxa de Utilização (Dias Úteis) - Contagem real por mês
    if 'Dias Úteis' in df_filtrado.columns:
        # Agrupar por mês e pegar o primeiro valor de dias úteis de cada mês (valor correto)
        dias_uteis_por_mes = df_filtrado.groupby('mes_ano')['Dias Úteis'].first()
        dias_uteis_por_mes_num = pd.to_numeric(dias_uteis_por_mes, errors='coerce').fillna(0)

        kpis['media_dias_uteis'] = dias_uteis_por_mes_num.mean() if not dias_uteis_por_mes_num.empty else 0
        kpis['total_dias_operacao'] = dias_uteis_por_mes_num.sum() if not dias_uteis_por_mes_num.empty else 0

    # KPI 5: Custo por Dia Útil - Usando contagem real de dias úteis
    if 'Dias Úteis' in df_filtrado.columns and 'custo_frota_total' in df_filtrado.columns:
        # Usar a contagem real de dias úteis já calculada
        total_dias_uteis_real = kpis.get('total_dias_operacao', 0)
        total_custo = pd.to_numeric(df_filtrado['custo_frota_total'], errors='coerce').sum()
        kpis['custo_por_dia_util'] = total_custo / total_dias_uteis_real if total_dias_uteis_real > 0 else 0

    # --- KPI 7 & 8: Análise Consolidada de Contratos (Custo e Atividade) ---
    if ('contrato_agrupado' in df_filtrado.columns and 
        'custo_frota_total' in df_filtrado.columns and 
        'Placa' in df_filtrado.columns):

        # --- Análise por Custo ---
        custo_por_contrato = df_filtrado.groupby('contrato_agrupado')['custo_frota_total'].sum().sort_values(ascending=False)
        
        if not custo_por_contrato.empty and custo_por_contrato.iloc[0] > 0:
            kpis['contrato_maior_custo'] = custo_por_contrato.index[0]
            kpis['custo_contrato_maior'] = custo_por_contrato.iloc[0]
            
            # KPI Adicional: Percentual do Custo Total
            custo_total_geral = df_filtrado['custo_frota_total'].sum()
            if custo_total_geral > 0:
                percentual = (kpis['custo_contrato_maior'] / custo_total_geral) * 100
                kpis['percentual_contrato_maior'] = f"{percentual:.1f}% do custo total"
            else:
                kpis['percentual_contrato_maior'] = ""

        # --- Análise por Atividade (Número de Veículos) ---
        veiculos_por_contrato = df_filtrado.groupby('contrato_agrupado')['Placa'].nunique().sort_values(ascending=False)

        if not veiculos_por_contrato.empty:
            kpis['contrato_mais_ativo'] = veiculos_por_contrato.index[0]
            kpis['num_veiculos_mais_ativo'] = veiculos_por_contrato.iloc[0]

            # KPI Adicional: Percentual da Frota Utilizada
            total_veiculos_frota = df_filtrado['Placa'].nunique()
            if total_veiculos_frota > 0:
                percentual_frota = (kpis['num_veiculos_mais_ativo'] / total_veiculos_frota) * 100
                kpis['percentual_frota_ativa'] = f"Utilizou {percentual_frota:.1f}% da frota"
            else:
                kpis['percentual_frota_ativa'] = ""

    # KPI 8: Custo de Manutenção por Km
    if 'manutencao_por_km' in df_filtrado.columns:
        # Converter para numérico, ignorando valores não numéricos
        manutencao_numerica = pd.to_numeric(df_filtrado['manutencao_por_km'], errors='coerce')
        kpis['media_manutencao_por_km'] = manutencao_numerica.mean() if not manutencao_numerica.isna().all() else 0
    elif 'total_km' in df_filtrado.columns and 'valor' in df_filtrado.columns:
        # Calcular Man/Km se não existir
        total_km = df_filtrado['total_km'].sum()
        total_manutencao = df_filtrado['valor'].sum()
        kpis['media_manutencao_por_km'] = total_manutencao / total_km if total_km > 0 else 0

    # --- KPI 7: Eficiência Regional (Lógica Robusta de Custo por KM) ---
    if ('regiao' in df_filtrado.columns and 
        'custo_frota_total' in df_filtrado.columns and 
        'total_km' in df_filtrado.columns):
        
        # Agrupa por região e soma os custos totais e os KMs totais
        eficiencia_regional = df_filtrado.groupby('regiao').agg(
            CustoTotal=('custo_frota_total', 'sum'),
            KmTotal=('total_km', 'sum')
        )
        
        # Remove regiões que não rodaram (para evitar divisão por zero)
        eficiencia_regional = eficiencia_regional[eficiencia_regional['KmTotal'] > 0]
        
        if not eficiencia_regional.empty:
            # Calcula a nova métrica: Custo por KM
            eficiencia_regional['custo_por_km_regional'] = eficiencia_regional['CustoTotal'] / eficiencia_regional['KmTotal']
            
            # Encontra a região com o MENOR custo por km (a mais eficiente)
            regiao_mais_eficiente = eficiencia_regional['custo_por_km_regional'].idxmin()
            
            kpis['regiao_mais_eficiente'] = regiao_mais_eficiente
            # Guarda o valor do custo por km para exibir no card
            kpis['custo_regiao_mais_eficiente'] = eficiencia_regional.loc[regiao_mais_eficiente, 'custo_por_km_regional']

    # KPI 10: Análise por Contrato
    if 'contrato_agrupado' in df_filtrado.columns and 'custo_frota_total' in df_filtrado.columns:
    
        custo_por_contrato = df_filtrado.groupby('contrato_agrupado')['custo_frota_total'].sum().sort_values(ascending=False)
        
        if not custo_por_contrato.empty and custo_por_contrato.iloc[0] > 0:
            kpis['contrato_maior_custo'] = custo_por_contrato.index[0]
            kpis['custo_contrato_maior'] = custo_por_contrato.iloc[0]

            # --- NOVO CÁLCULO ADICIONADO ---
            # Calcula o percentual que o maior contrato representa do todo
            custo_total_geral = df_filtrado['custo_frota_total'].sum()
            if custo_total_geral > 0:
                percentual = (kpis['custo_contrato_maior'] / custo_total_geral) * 100
                kpis['percentual_contrato_maior'] = f"{percentual:.1f}% do custo total"
            else:
                kpis['percentual_contrato_maior'] = "" # Não mostra nada se o custo total for zero
                
            return kpis

def exibir_kpis_operacionais_visao_geral(df_filtrado):
    """Exibe KPIs operacionais específicos para a aba Visão Geral"""
    
    kpis = calcular_kpis_operacionais(df_filtrado)
    
    st.markdown("---")
    
    st.subheader("KPIs Operacionais - Visão Geral")

    # --- CSS ADAPTATIVO COM BORDAS COLORIDAS E ALTURAS FIXAS POR LINHA ---
    st.markdown("""
    <style>
    /* Variáveis para tema inverso */
    :root {
        --card-bg-color: #ffffff; /* BRANCO no tema claro */
        --card-text-color: #000000;
        --card-detail-color: #374151;
        --secondary-bg-color: #f9fafb;
        --gray-80: #e5e7eb;
    }

    /* Para Streamlit tema escuro */
    [data-theme="dark"] {
        --card-bg-color: #000000; /* PRETO no tema escuro */
        --card-text-color: #ffffff;
        --card-detail-color: #9ca3af;
        --secondary-bg-color: #1f2937;
        --gray-80: #374151;
    }

    /* Estilo Base para cards */
    .custom-card {
        background-color: var(--card-bg-color);
        border-radius: 16px;
        padding: 20px; /* Reduzido um pouco para dar mais espaço interno */
        margin-bottom: 20px; /* Ajustado para consistência */
        border: 3px solid;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box; /* Garante que padding e border sejam incluídos na altura */
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
    }

    /* Bordas coloridas */
    .card-blue { border-color: #3b82f6; }
    .card-green { border-color: #22c55e; }
    .card-orange { border-color: #f97316; }
    .card-yellow { border-color: #eab308; }

    /* Estilos de Texto dentro dos cards */
    .card-title {
        font-size: 15px; /* Ligeiramente reduzido para caber melhor */
        font-weight: bold;
        color: var(--card-detail-color);
        margin-bottom: 12px; /* Ajustado */
        text-transform: uppercase;
        height: 36px; /* Altura fixa para títulos de 2 linhas */
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        line-height: 1.2; /* Espaçamento entre linhas */
        overflow: hidden; /* Garante que não transborde */
    }
    .card-value {
        font-size: 30px; /* Ligeiramente reduzido */
        font-weight: bold;
        margin-bottom: 8px; /* Ajustado */
        line-height: 1.1;
        text-align: center;
        flex-grow: 1; /* Permite que o valor ocupe o espaço restante */
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .card-value .unit { /* Para 'Km/L' ou 'Km' */
        font-size: 16px; /* Ajustado */
        font-weight: normal;
        margin-left: 5px;
        color: var(--card-detail-color); /* Unidade em cinza */
    }
    .card-detail {
        font-size: 13px; /* Ligeiramente reduzido */
        color: var(--card-detail-color);
        margin-top: auto; /* Empurra os detalhes para o fundo */
        text-align: center;
        line-height: 1.3;
        overflow: hidden; /* Esconde o que transborda */
        text-overflow: ellipsis; /* Adiciona "..." */
        display: -webkit-box; /* Para controlar o número de linhas */
        -webkit-line-clamp: 2; /* Limita a 2 linhas */
        -webkit-box-orient: vertical;
        height: 38px; /* Altura fixa para 2 linhas */
    }
    .card-detail b {
        font-weight: bold;
        color: var(--card-text-color); /* Títulos de detalhe mais escuros/claros */
    }

    /* Cores dos valores combinando com as bordas */
    .card-blue .card-value { color: #3b82f6; }
    .card-green .card-value { color: #22c55e; }
    .card-orange .card-value { color: #f97316; }
    .card-yellow .card-value { color: #eab308; }

    /* ALTURAS FIXAS PARA CADA LINHA DE CARDS */
    .kpi-row-1 {
        min-height: 180px; /* Altura da primeira linha */
        height: 180px;
        max-height: 180px;
    }
    .kpi-row-2 {
        min-height: 160px; /* Altura da segunda linha */
        height: 160px;
        max-height: 160px;
    }
    .kpi-row-3 {
        min-height: 140px; /* Altura da terceira linha */
        height: 140px;
        max-height: 140px;
    }

    /* Ajustes responsivos */
    @media (max-width: 768px) {
        .custom-card { padding: 15px; margin-bottom: 10px; }
        .card-title { font-size: 14px; height: 32px; margin-bottom: 8px;}
        .card-value { font-size: 26px; margin-bottom: 5px;}
        .card-value .unit { font-size: 14px; }
        .card-detail { font-size: 12px; height: 36px; -webkit-line-clamp: 2;}

        .kpi-row-1 { min-height: 160px; height: 160px; max-height: 160px; }
        .kpi-row-2 { min-height: 140px; height: 140px; max-height: 140px; }
        .kpi-row-3 { min-height: 120px; height: 120px; max-height: 120px; }
    }

    </style>
    """, unsafe_allow_html=True)

    # --- Primeira linha - KPIs principais ---
    cols1 = st.columns(4)
    with cols1[0]:
        if 'media_km_por_litro' in kpis:
            st.markdown(f"""
            <div class="custom-card card-blue kpi-row-1">
                <div class="card-title">⛽ Eficiência Combustível</div>
                <div class="card-value">{kpis['media_km_por_litro']:.2f} <span class="unit">Km/L</span></div>
                <div class="card-detail">
                    📈 Melhor: {kpis.get('melhor_eficiencia_veiculo', 'N/A')} ({kpis.get('melhor_eficiencia_valor', 0):.2f})<br>
                    📉 Pior: {kpis.get('pior_eficiencia_veiculo', 'N/A')} ({kpis.get('pior_eficiencia_valor', 0):.2f})
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="custom-card card-blue kpi-row-1">
                <div class="card-title">⛽ Eficiência Combustível</div>
                <div class="card-value">N/A</div>
                <div class="card-detail">Dados não disponíveis</div>
            </div>
            """, unsafe_allow_html=True)


    with cols1[1]:
        if 'custo_por_km' in kpis:
            st.markdown(f"""
            <div class="custom-card card-blue kpi-row-1">
                <div class="card-title">💰 Custo por Km</div>
                <div class="card-value">R$ {kpis['custo_por_km']:.2f}</div>
                <div class="card-detail">Custo total / Km rodados</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="custom-card card-blue kpi-row-1">
                <div class="card-title">💰 Custo por Km</div>
                <div class="card-value">N/A</div>
                <div class="card-detail">Dados não disponíveis</div>
            </div>
            """, unsafe_allow_html=True)

    with cols1[2]:
        if 'km_medio_por_veiculo' in kpis:
            st.markdown(f"""
            <div class="custom-card card-blue kpi-row-1">
                <div class="card-title">🚛 Km Médio/Veículo</div>
                <div class="card-value">{kpis['km_medio_por_veiculo']:,.0f} <span class="unit">Km</span></div>
                <div class="card-detail">
                    <b>Total Frota:</b> {kpis.get('total_km_frota', 0):,.0f} Km<br>
                    <b>Top Veículo:</b> {kpis.get('veiculo_mais_rodou', 'N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="custom-card card-blue kpi-row-1">
                <div class="card-title">🚛 Km Médio/Veículo</div>
                <div class="card-value">N/A</div>
                <div class="card-detail">Dados não disponíveis</div>
            </div>
            """, unsafe_allow_html=True)

    with cols1[3]:
        if 'custo_por_dia_util' in kpis:
            st.markdown(f"""
            <div class="custom-card card-blue kpi-row-1">
                <div class="card-title">📅 Custo/Dia Útil</div>
                <div class="card-value">R$ {kpis['custo_por_dia_util']:,.2f}</div>
                <div class="card-detail"><b>Dias úteis no período:</b> {kpis.get('total_dias_operacao', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="custom-card card-blue kpi-row-1">
                <div class="card-title">📅 Custo/Dia Útil</div>
                <div class="card-value">N/A</div>
                <div class="card-detail">Dados não disponíveis</div>
            </div>
            """, unsafe_allow_html=True)

    # --- Segunda linha - KPIs de performance ---
    cols2 = st.columns(3)
        # --- CARD DE ROTEIROS REMOVIDO E SUBSTITUÍDO ---
    with cols2[0]:
        # NOVO CARD: Total de Categorias de Contrato
        if 'contrato_agrupado' in df_filtrado.columns:
            total_categorias = df_filtrado['contrato_agrupado'].nunique()
            st.markdown(f"""
            <div class="custom-card card-blue kpi-row-2">
                <div class="card-title">📑 Diversidade de Contratos</div>
                <div class="card-value">{total_categorias}</div>
                <div class="card-detail">Categorias de contrato ativas no período</div>
            </div>
            """, unsafe_allow_html=True)
        else: 
            st.markdown("""
            <div class="custom-card card-blue kpi-row-2">
                <div class="card-title">📑 Diversidade de Contratos</div>
                <div class="card-value">N/A</div>
                <div class="card-detail">Dados não disponíveis</div>
            </div>
            """, unsafe_allow_html=True)

    with cols2[1]:
        if 'regiao_mais_eficiente' in kpis:
            st.markdown(f"""
            <div class="custom-card card-blue kpi-row-2">
                <div class="card-title">🌍 Eficiência Regional</div>
                <div class="card-value">{kpis['regiao_mais_eficiente']}</div>
                <div class="card-detail">
                    <b>Custo por Km:</b> R$ {kpis['custo_regiao_mais_eficiente']:.2f} / Km
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Card para quando não há dados
            st.markdown("""
            <div class="custom-card card-blue kpi-row-2">
                <div class="card-title">🌍 Eficiência Regional</div>
                <div class="card-value">N/A</div>
                <div class="card-detail">Dados não disponíveis</div>
            </div>
            """, unsafe_allow_html=True)

    with cols2[2]:
        if 'contrato_maior_custo' in kpis:
            st.markdown(f"""
            <div class="custom-card card-blue kpi-row-2">
                <div class="card-title">📋 Contrato de Maior Custo</div>
                <div class="card-value">{kpis['contrato_maior_custo']}</div>
                <div class="card-detail"><b>Valor:</b> R$ {kpis['custo_contrato_maior']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="custom-card card-blue kpi-row-2">
                <div class="card-title">📋 Contrato de Maior Custo</div>
                <div class="card-value">N/A</div>
                <div class="card-detail">Dados não disponíveis</div>
            </div>
            """, unsafe_allow_html=True)

    # --- Terceira linha - KPIs adicionais ---
    cols3 = st.columns(2)
    with cols3[0]:
        if 'media_manutencao_por_km' in kpis:
            st.markdown(f"""
            <div class="custom-card card-blue kpi-row-3">
                <div class="card-title">🔧 Manutenção/Km</div>
                <div class="card-value">R$ {kpis['media_manutencao_por_km']:.2f}</div>
                <div class="card-detail">Custo de manutenção por Km rodado</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="custom-card card-blue kpi-row-3">
                <div class="card-title">🔧 Manutenção/Km</div>
                <div class="card-value">N/A</div>
                <div class="card-detail">Dados não disponíveis</div>
            </div>
            """, unsafe_allow_html=True)

    with cols3[1]:
        
        if 'contrato_mais_ativo' in kpis:
    

            st.markdown(f"""
            <div class="custom-card card-blue kpi-row-3">
                <div class="card-title">📊 Contrato Mais Ativo</div>
                <div class="card-value" style="font-size: 20px; line-height: 1.2;">{kpis['contrato_mais_ativo']}</div>
                <div class="card-detail" style="font-weight: bold;">
                    Utilizou {int(kpis['num_veiculos_mais_ativo'])} veículos
                </div>
                <div class="card-detail">
                    {kpis.get('percentual_frota_ativa', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Caso não haja dados para calcular
            st.markdown("""
            <div class="custom-card card-blue kpi-row-3">
                <div class="card-title">📊 Contrato Mais Ativo</div>
                <div class="card-value">N/A</div>
                <div class="card-detail">Dados não disponíveis</div>
            </div>
            """, unsafe_allow_html=True)
        
    return kpis


    """
    Recebe um dicionário com dados já calculados e exibe os componentes visuais.
    """
    st.subheader("💡 Detalhamento dos Custos por Macro Categoria")
    
    # Extrai os valores do dicionário
    custo_manutencao_total = resultados['custo_manutencao_total']
    custo_combustivel_total = resultados['custo_combustivel_total']
    custo_geral_total = resultados['custo_geral_total']
    df_grafico_geral = resultados['df_grafico_geral']
    df_detalhado = resultados['df_detalhado_veiculos']

    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🛠️ Manutenção", f"R$ {custo_manutencao_total:,.2f}", 
                  f"{custo_manutencao_total / custo_geral_total * 100:.1f}%" if custo_geral_total > 0 else "0%")
    with col2:
        st.metric("⛽ Combustível", f"R$ {custo_combustivel_total:,.2f}",
                  f"{custo_combustivel_total / custo_geral_total * 100:.1f}%" if custo_geral_total > 0 else "0%")
    with col3:
        st.metric("💰 Total Geral", f"R$ {custo_geral_total:,.2f}")
    
    # Gráficos
    cores_geral = ['#007bff', '#28a745']
    mapa_cores_geral = {'Manutenção': cores_geral[0], 'Combustível': cores_geral[1]}
    
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        fig_pie_geral = px.pie(df_grafico_geral, names='Categoria', values='Custo', 
                               title='Distribuição Percentual dos Custos', hole=.3, 
                               color='Categoria', color_discrete_map=mapa_cores_geral)
        fig_pie_geral.update_traces(textposition='outside', textinfo='percent+label')
        st.plotly_chart(fig_pie_geral, use_container_width=True)
    
    with g_col2:
        fig_bar_geral = px.bar(df_grafico_geral, x='Categoria', y='Custo', text_auto='.2s', 
                               title='Comparativo de Custos por Macro Categoria', 
                               color='Categoria', color_discrete_map=mapa_cores_geral)
        fig_bar_geral.update_layout(showlegend=False)
        st.plotly_chart(fig_bar_geral, use_container_width=True)
    
    st.markdown("---")
    
    # Relatório Detalhado
    st.subheader(f"📋 Relatório Detalhado por Veículo - {titulo_principal}")
    
    ordem_colunas = [col for col in ['Ranking', 'Placa', 'Modelo', 'Marca', 'grupocorreto', 
                                     'Região', 'Filial', 'Tipo Combustível', 'Tipo de Rota', 
                                     'Contrato', 'Roteiro Principal', 'Motorista Principal', 
                                     'Valor Comb.', 'Arla', 'Manutenção em Geral', 
                                     'Rodas / Pneus', 'Lataria e Pintura', 'Custo Total'] if col in df_detalhado.columns]
    
    st.dataframe(df_detalhado[ordem_colunas], hide_index=True, use_container_width=True,
                 column_config={
                     "Custo Total": st.column_config.NumberColumn(format="R$ %.2f"),
                     "Valor Comb.": st.column_config.NumberColumn(format="R$ %.2f"),
                     "Arla": st.column_config.NumberColumn(format="R$ %.2f"),
                     "Manutenção em Geral": st.column_config.NumberColumn(format="R$ %.2f"),
                     "Rodas / Pneus": st.column_config.NumberColumn(format="R$ %.2f"),
                     "Lataria e Pintura": st.column_config.NumberColumn(format="R$ %.2f")
                 })