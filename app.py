# app.py (VERSÃO COMPLETA COM KPIs AVANÇADOS)
import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dateutil.relativedelta import relativedelta
from src.config.data_provider import get_data, get_custos_db
from calculations import (
    exibir_dashboard_executivo,
    calcular_kpis_performance,
    exibir_kpis_em_cartoes,
    exibir_graficos_performance_avancados,
    exibir_tendencias_mensais,
    exibir_kpis_operacionais_visao_geral,
    exibir_panorama_filiais
)
if st.button("🗑️ Limpar Cache"):
    st.cache_data.clear()
    st.rerun()

st.set_page_config(page_title="Dashboard FKM Gritsch", layout="wide", page_icon="🚚")


# --- CARREGAMENTO E FILTROS APRIMORADOS ---
with st.spinner('🔄 Analisando dados da frota... Por favor, aguarde.'):
    df = get_data()


if not df.empty:

    # Sidebar aprimorada
    with st.sidebar:
        st.title("🚛 FKM Gritsch")
        st.markdown("Análise da Frota")
        selected = st.radio(
            "📊 Selecione a Análise:",
            options=["Visão Resumida", "Visão Geral"],
            horizontal=False
        )

        # Adicionar informações do sistema
        st.markdown("---")
        st.markdown("### 📈 Resumo Geral")
        st.info(f"**Total de Registros:** {len(df):,}\n\n**Período:** {df['ano'].min()} - {df['ano'].max()}\n\n**Última Atualização:** {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")

    # Header principal
    st.title("🚛 Dashboard FKM Gritsch - Controle de Frota")
    st.markdown("Sistema Integrado de Gestão e Análise de Custos")

    # Filtros aprimorados com Session State e mensagem customizada
    with st.expander("🔍 Filtros Avançados de Análise", expanded=True):
        col1, col2, col3, col4, = st.columns(4)

        # --- Filtro de Ano ---
        with col1:
            anos_disponiveis = ['Todos'] + sorted(df['ano'].unique().tolist(), reverse=True)
            ano_selecionado = st.selectbox(
                "📅 Ano",
                options=anos_disponiveis,
                key='ano_selecionado'
            )

        # --- Filtro de Mês (com lógica aprimorada) ---
        with col2:
            if st.session_state.ano_selecionado != 'Todos':
                df_ano_filtrado = df[df['ano'] == st.session_state.ano_selecionado]
                meses_disponiveis = ['Todos'] + sorted(df_ano_filtrado['mes_ano'].unique().tolist())
                mes_selecionado = st.selectbox(
                    "📆 Mês",
                    options=meses_disponiveis,
                    key='mes_selecionado'
                )
            else:
                # Comportamento Aprimorado: Caixa bloqueada e mensagem customizada
                mes_selecionado = 'Todos'
                st.selectbox(
                    "📆 Mês",
                    options=['Todos'],
                    key='mes_selecionado',
                    disabled=True
                )
                # MENSAGEM COM TAMANHO AJUSTADO USANDO MARKDOWN
                st.markdown(
                    '<div style="font-size: 18px; color: #888;">👆 Selecione um ano para filtrar por mês</div>',
                    unsafe_allow_html=True
                )

        # --- Filtro de Região ---
        with col3:
            regioes_disponiveis = ['Todos'] + sorted(df['regiao'].unique().tolist())
            regiao_selecionada = st.selectbox(
                "🌍 Região",
                options=regioes_disponiveis,
                key='regiao_selecionada'
            )

        # --- Filtro de Filial (depende da Região) ---
        with col4:
            if st.session_state.regiao_selecionada != 'Todos':
                df_regiao_filtrado = df[df['regiao'] == st.session_state.regiao_selecionada]
                filiais_disponiveis = ['Todos'] + sorted(df_regiao_filtrado['filial'].unique().tolist())
            else:
                filiais_disponiveis = ['Todos'] + sorted(df['filial'].unique().tolist())

            filial_selecionada = st.selectbox(
                "🏢 Filial",
                options=filiais_disponiveis,
                key='filial_selecionada'
            )

    # Aplicação dos filtros
    df_filtrado = df.copy()
    if st.session_state.ano_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['ano'] == st.session_state.ano_selecionado]
    if st.session_state.mes_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['mes_ano'] == st.session_state.mes_selecionado]
    if st.session_state.regiao_selecionada != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['regiao'] == st.session_state.regiao_selecionada]
    if st.session_state.filial_selecionada != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['filial'] == st.session_state.filial_selecionada]

    # Título principal responsivo
    if st.session_state.filial_selecionada == 'Todos':
        titulo_principal = "Gritsch Transportes - Visão Consolidada"
    else:
        titulo_principal = f"Filial {filial_selecionada}"

    st.markdown("---")

    if selected == "Visão Resumida":
        if df_filtrado.empty:
            st.error("❌ Nenhum dado encontrado para os filtros selecionados.")
        else:
            exibir_dashboard_executivo(df_filtrado, df, "Resumo da Frota")
            st.markdown("---")


    elif selected == "Visão Geral":
        titulo_aba = "Custo Total da Frota"
        # Construir título responsivo
        ano_selecionado = st.session_state.get('ano_selecionado', 'Todos')
        mes_selecionado = st.session_state.get('mes_selecionado', 'Todos')
        regiao_selecionada = st.session_state.get('regiao_selecionada', 'Todos')
        filial_selecionada = st.session_state.get('filial_selecionada', 'Todos')

        # Construir subtítulo com filtros ativos
        filtros_ativos = []
        if ano_selecionado != 'Todos':
            filtros_ativos.append(f"Ano {ano_selecionado}")
        if mes_selecionado != 'Todos':
            filtros_ativos.append(f"Mês {mes_selecionado}")
        if regiao_selecionada != 'Todos':
            filtros_ativos.append(f"Região {regiao_selecionada}")
        if filial_selecionada != 'Todos':
            filtros_ativos.append(f"Filial {filial_selecionada}")

        if filtros_ativos:
            subtitulo = f"({', '.join(filtros_ativos)})"
        else:
            subtitulo = "(Visão Consolidada)"

        st.header(f"📊 Visão Geral dos Custos - {titulo_principal}")

        if df_filtrado.empty:
            st.error("❌ Nenhum dado encontrado para os filtros selecionados.")
        else:
            # CSS para os cards da Visão Geral e ajustes nas tabelas
            st.markdown("""
            <style>
            /* Aumentar fonte das tabelas/dataframes */
            .stDataFrame {
                font-size: 16px !important;
            }
            .stDataFrame table {
                font-size: 16px !important;
            }
            .stDataFrame th {
                font-size: 17px !important;
                font-weight: bold !important;
            }
            .stDataFrame td {
                font-size: 16px !important;
                padding: 8px !important;
            }

            .custom-card {
                background-color: #ffffff;
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 24px;
                border: 3px solid;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                min-height: 320px;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }
            .card-blue { border-color: #3b82f6; }
            .card-green { border-color: #22c55e; }
            .card-orange { border-color: #ea580c; }
            .card-yellow { border-color: #eab308; }
            .card-title {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 12px;
                text-transform: uppercase;
            }
            .card-detail {
                font-size: 16px;
                color: #666666;
                margin: 4px 0;
            }
            .card-value {
                font-size: 30px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .card-blue .card-value { color: #3b82f6; }
            .card-green .card-value { color: #22c55e; }
            .card-orange .card-value { color: #ea580c; }
            .card-yellow .card-value { color: #eab308; }
            </style>
            """, unsafe_allow_html=True)
            # Primeiro: Exibir KPIs Operacionais
            exibir_kpis_operacionais_visao_geral(df_filtrado)

            # Segundo: Panorama das Filiais
            exibir_panorama_filiais(df_filtrado)

            # Terceiro: Análise temporal ou por mês específico
            if mes_selecionado == 'Todos':
                # Mostra as tendências para o período selecionado (seja 1 ano ou todos)
                exibir_tendencias_mensais(df_filtrado, titulo_aba)
            else:
                # Mostra a análise de performance detalhada para o mês específico
                # O parâmetro 'ano_selecionado' é necessário para o contexto, mas a função foca no 'mes_selecionado'
                kpis = calcular_kpis_performance(df, ano_selecionado, mes_selecionado, 'custo_frota_total')
                if kpis:
                    exibir_kpis_em_cartoes(kpis, titulo_aba)
                    st.markdown("---")
                    exibir_graficos_performance_avancados(df, mes_selecionado, kpis, 'custo_frota_total', titulo_aba)
                else:
                    # Esta mensagem pode aparecer se houver dados no ano, mas não no mês específico selecionado
                    st.warning("Não foram encontrados dados de performance para o mês selecionado.")

            st.markdown("---")

else:
    st.error("🚨 Falha no carregamento dos dados. Verifique a fonte de dados.")

# Footer responsivo ao tema
st.markdown("""
<style>
/* Footer responsivo para tema claro/escuro */
.footer {
    margin-top: 50px;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    border: 1px solid var(--primary-color);
    background-color: var(--background-color);
    color: var(--text-color);
    transition: all 0.3s ease;
}

/* Tema claro */
@media (prefers-color-scheme: light) {
    .footer {
        background-color: #f8f9fa;
        color: #333333;
        border-color: #e9ecef;
    }
}

/* Tema escuro */
@media (prefers-color-scheme: dark) {
    .footer {
        background-color: #262730;
        color: #fafafa;
        border-color: #464754;
    }
}

/* Fallback para Streamlit */
[data-testid="stAppViewContainer"] [data-theme="light"] .footer {
    background-color: #f8f9fa !important;
    color: #333333 !important;
    border-color: #e9ecef !important;
}

[data-testid="stAppViewContainer"] [data-theme="dark"] .footer {
    background-color: #262730 !important;
    color: #fafafa !important;
    border-color: #464754 !important;
}

/* Estilos para o texto do footer */
.footer p {
    margin: 8px 0;
    line-height: 1.5;
}

.footer strong {
    font-weight: 600;
}

.footer small {
    opacity: 0.8;
    font-size: 0.85em;
}
</style>

<div class="footer">
    <p>🚛 <strong>FKM Gritsch - Sistema de Gestão de Frota</strong></p>
    <p>Desenvolvido para otimização de custos e eficiência operacional</p>
    <p><small>Versão 2.0 - Dashboard Avançado com IA e Analytics</small></p>
</div>
""", unsafe_allow_html=True)