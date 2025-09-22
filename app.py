# app.py (VERSÃO COMPLETA COM KPIs AVANÇADOS)
import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from calculations import *
from plotly.subplots import make_subplots
from dateutil.relativedelta import relativedelta
from src.config.data_provider import get_data

# Adicionar temporariamente no início do app.py, após os imports
if st.button("🗑️ Limpar Cache"):
    st.cache_data.clear()
    st.rerun()

st.set_page_config(page_title="Dashboard FKM Gritsch", layout="wide", page_icon="🚚")      
        
# --- CARREGAMENTO E FILTROS APRIMORADOS ---
with st.spinner('🔄 Analisando dados da frota... Por favor, aguarde.'):
    df = get_data()
    # ADICIONAR ESTA LINHA:
    df = df[df['ano'] == 2025] if not df.empty else df

if not df.empty:
    # Preparação dos dados
    df['custo_combustivel_total'] = df['custo_combustivel'] + df['custo_arla']
    df['custo_frota_total'] = df['valor'] + df['custo_combustivel_total']
    
    # Sidebar aprimorada
    with st.sidebar:
        st.title("🚛 FKM Gritsch")
        st.markdown("Análise da Frota")
        selected = st.radio(
            "📊 Selecione a Análise:", 
            options=["Dashboard Executivo", "Visão Geral", "Manutenção", "Combustível", "Análise Detalhada"], 
            horizontal=False
        )
        
        # Adicionar informações do sistema
        st.markdown("---")
        st.markdown("### 📈 Resumo Geral")
        st.info(f"**Total de Registros:** {len(df):,}\n\n**Período:** {df['ano'].min()} - {df['ano'].max()}\n\n**Última Atualização:** {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")

    # Header principal
    st.title("🚛 Dashboard FKM Gritsch - Controle de Frota")
    st.markdown("Sistema Integrado de Gestão e Análise de Custos")
    
    # Filtros aprimorados
    with st.expander("🔍 Filtros Avançados de Análise", expanded=True):
        col1, col2, col3, col4,  = st.columns(4)
        
        with col1:
            anos_disponiveis = ['Todos'] + sorted(df['ano'].unique().tolist(), reverse=True)
            ano_selecionado = st.selectbox("📅 Ano", options=anos_disponiveis)
        
        mes_selecionado = 'Todos'
        with col2:
            if ano_selecionado != 'Todos':
                df_ano_filtrado = df[df['ano'] == ano_selecionado]
                meses_disponiveis = ['Todos'] + sorted(df_ano_filtrado['mes_ano'].unique().tolist())
                mes_selecionado = st.selectbox("📆 Mês", options= meses_disponiveis)
        
        with col3:
            regioes_disponiveis = ['Todos'] + sorted(df['regiao'].unique().tolist())
            regiao_selecionada = st.selectbox("🌍 Região", options=regioes_disponiveis)
        
        with col4:
            if regiao_selecionada != 'Todos':
                df_regiao_filtrada = df[df['regiao'] == regiao_selecionada]
                filiais_disponiveis = ['Todos'] + sorted(df_regiao_filtrada['filial'].unique().tolist())
                filial_selecionada = st.selectbox("🏢 Filial", options=filiais_disponiveis)
            else:
                filiais_disponiveis = ['Todos'] + sorted(df['filial'].unique().tolist())
                filial_selecionada = st.selectbox("🏢 Filial", options=filiais_disponiveis)

    # Aplicação dos filtros
    df_filtrado = df.copy()
    if ano_selecionado != 'Todos': 
        df_filtrado = df_filtrado[df_filtrado['ano'] == ano_selecionado]
    if mes_selecionado != 'Todos': 
        df_filtrado = df_filtrado[df_filtrado['mes_ano'] == mes_selecionado]
    if regiao_selecionada != 'Todos': 
        df_filtrado = df_filtrado[df_filtrado['regiao'] == regiao_selecionada]
    if filial_selecionada != 'Todos': 
        df_filtrado = df_filtrado[df_filtrado['filial'] == filial_selecionada]
    
    # Informações do contexto atual
    if filial_selecionada == 'Todos':
        titulo_principal = "Gritsch Transportes - Visão Consolidada"
    else:
        titulo_principal = f"Filial {filial_selecionada.title()}"
    
    st.markdown("---")

    # --- LÓGICA PRINCIPAL DAS ABAS APRIMORADA ---
    
    if selected == "Dashboard Executivo":
        if df_filtrado.empty:
            st.error("❌ Nenhum dado encontrado para os filtros selecionados.")
        else:
            exibir_dashboard_executivo(df_filtrado, titulo_principal)
            st.markdown("---")
            
            # Análise regional se aplicável
            if regiao_selecionada != 'Todos' or len(df_filtrado['regiao'].unique()) > 1:
                exibir_kpis_regionais(df_filtrado, 'custo_frota_total', regiao_selecionada)
    
    elif selected == "Visão Geral":
        titulo_aba = "Custo Total da Frota"
        st.header(f"📊 Visão Geral dos Custos - {titulo_principal}")
        
        if df_filtrado.empty:
            st.error("❌ Nenhum dado encontrado para os filtros selecionados.")
        else:
            if ano_selecionado == 'Todos':
                exibir_analise_anual_completa(df_filtrado, titulo_aba)
            else:
                kpis = calcular_kpis_performance(df, ano_selecionado, mes_selecionado, 'custo_frota_total')
                if kpis:
                    exibir_kpis_em_cartoes(kpis, titulo_aba)
                    st.markdown("---")
                    exibir_graficos_performance_avancados(df, mes_selecionado, kpis, 'custo_frota_total', titulo_aba)
                else:
                    st.info("ℹ️ Selecione um mês específico para ver a análise de performance mensal.")
            
            st.markdown("---")
            
            # Análise regional
            if len(df_filtrado['regiao'].unique()) > 1 or regiao_selecionada != 'Todos':
                exibir_kpis_regionais(df_filtrado, 'custo_frota_total', regiao_selecionada)
                st.markdown("---")

            # Detalhamento existente aprimorado
            st.subheader("💡 Detalhamento dos Custos por Macro Categoria")
            custo_manutencao_total = df_filtrado['valor'].sum()
            custo_combustivel_total = df_filtrado['custo_combustivel_total'].sum()
            
            # Métricas adicionais
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🛠️ Manutenção", f"R$ {custo_manutencao_total:,.2f}", 
                         f"{custo_manutencao_total/(custo_manutencao_total+custo_combustivel_total)*100:.1f}%" if (custo_manutencao_total+custo_combustivel_total) > 0 else "0%")
            with col2:
                st.metric("⛽ Combustível + Arla", f"R$ {custo_combustivel_total:,.2f}",
                         f"{custo_combustivel_total/(custo_manutencao_total+custo_combustivel_total)*100:.1f}%" if (custo_manutencao_total+custo_combustivel_total) > 0 else "0%")
            with col3:
                st.metric("💰 Total Geral", f"R$ {custo_manutencao_total+custo_combustivel_total:,.2f}")
            
            # Gráficos existentes...
            dados_grafico_geral = {'Categoria': ['Manutenção', 'Combustível e Arla'], 'Custo': [custo_manutencao_total, custo_combustivel_total]}
            df_grafico_geral = pd.DataFrame(dados_grafico_geral).sort_values('Custo', ascending=False)
            cores_geral = ['#007bff', '#28a745']
            mapa_cores_geral = {'Manutenção': cores_geral[0], 'Combustível e Arla': cores_geral[1]}
            
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                fig_pie_geral = px.pie(df_grafico_geral, names='Categoria', values='Custo', 
                                     title='Distribuição Percentual dos Custos', hole=.3, 
                                     color='Categoria', color_discrete_map=mapa_cores_geral)
                fig_pie_geral.update_traces(textposition='outside', textinfo='percent+label')
                fig_pie_geral.update_layout(legend_font_size=14, uniformtext_minsize=12, uniformtext_mode='hide')
                st.plotly_chart(fig_pie_geral, width='content')
            
            with g_col2:
                fig_bar_geral = px.bar(df_grafico_geral, x='Categoria', y='Custo', text_auto='.2s', 
                                     title='Comparativo de Custos por Macro Categoria', 
                                     color='Categoria', color_discrete_map=mapa_cores_geral)
                fig_bar_geral.update_layout(showlegend=False)
                fig_bar_geral.update_traces(width=0.4, textangle=0, textposition="outside")
                fig_bar_geral.update_yaxes(range=[0, df_grafico_geral['Custo'].max() * 1.1])
                st.plotly_chart(fig_bar_geral, width='content')
            
            st.markdown("---")
            st.subheader(f"📋 Relatório Detalhado por Veículo - {titulo_principal}")
            
            # Relatório com mais informações
            df_detalhado = df_filtrado.groupby('Placa').agg({
                'Modelo': 'first', 'Grupo Veículo': 'first', 'Marca': 'first', 
                'TP.Comb': 'first', 'TP.Rota': 'first', 'contrato': 'first', 
                'Roteiro Principal': 'first', 'Motorista Principal': 'first',
                'regiao': 'first', 'filial': 'first',
                'custo_combustivel': 'sum', 'custo_arla': 'sum', 
                'custo_manutencao_geral': 'sum', 'custo_rodas_pneus': 'sum', 
                'custo_lataria_pintura': 'sum'
            }).reset_index()
            
            df_detalhado['Custo Total'] = df_detalhado[['custo_combustivel', 'custo_arla', 
                                                       'custo_manutencao_geral', 'custo_rodas_pneus', 
                                                       'custo_lataria_pintura']].sum(axis=1)
            
            # Ranking dos veículos
            df_detalhado['Ranking'] = df_detalhado['Custo Total'].rank(ascending=False).astype(int)
            
            df_detalhado.rename(columns={
                'custo_combustivel': 'Valor Comb.', 'custo_arla': 'Arla', 
                'custo_manutencao_geral': 'Manutenção em Geral', 
                'custo_rodas_pneus': 'Rodas / Pneus', 
                'custo_lataria_pintura': 'Lataria e Pintura', 
                'contrato': 'Contrato', 'TP.Comb': 'Tipo Combustível', 
                'TP.Rota': 'Tipo de Rota', 'regiao': 'Região', 'filial': 'Filial'
            }, inplace=True)
            
            ordem_colunas_detalhado = ['Ranking', 'Placa', 'Modelo', 'Marca', 'Grupo Veículo', 
                                     'Região', 'Filial', 'Tipo Combustível', 'Tipo de Rota', 
                                     'Contrato', 'Roteiro Principal', 'Motorista Principal', 
                                     'Valor Comb.', 'Arla', 'Manutenção em Geral', 
                                     'Rodas / Pneus', 'Lataria e Pintura', 'Custo Total']
            
            st.dataframe(df_detalhado[ordem_colunas_detalhado], width='content', hide_index=True,
                        column_config={
                            "Custo Total": st.column_config.NumberColumn(format="R$ %.2f"),
                            "Valor Comb.": st.column_config.NumberColumn(format="R$ %.2f"),
                            "Arla": st.column_config.NumberColumn(format="R$ %.2f"),
                            "Manutenção em Geral": st.column_config.NumberColumn(format="R$ %.2f"),
                            "Rodas / Pneus": st.column_config.NumberColumn(format="R$ %.2f"),
                            "Lataria e Pintura": st.column_config.NumberColumn(format="R$ %.2f")
                        })

    elif selected == "Manutenção":
        titulo_aba = "Custo de Manutenção"
        st.header(f"🛠️ Análise de Manutenção - {titulo_principal}")
        
        if df_filtrado.empty:
            st.error("❌ Nenhum dado encontrado para os filtros selecionados.")
        else:
            if ano_selecionado == 'Todos':
                exibir_analise_anual_completa(df_filtrado, titulo_aba)
            else:
                kpis = calcular_kpis_performance(df, ano_selecionado, mes_selecionado, 'valor')
                if kpis:
                    exibir_kpis_em_cartoes(kpis, titulo_aba)
                    st.markdown("---")
                    exibir_graficos_performance_avancados(df, mes_selecionado, kpis, 'valor', titulo_aba)
                else:
                    st.info("ℹ️ Selecione um mês específico para ver a análise de performance mensal.")
            
            st.markdown("---")
            
            # Análise regional para manutenção
            if len(df_filtrado['regiao'].unique()) > 1 or regiao_selecionada != 'Todos':
                exibir_kpis_regionais(df_filtrado, 'valor', regiao_selecionada)
                st.markdown("---")

            # Detalhamento existente das categorias de manutenção...
            st.subheader("🔧 Detalhamento dos Custos por Categoria")
            custo_lataria = df_filtrado['custo_lataria_pintura'].sum()
            custo_manutencao = df_filtrado['custo_manutencao_geral'].sum()
            custo_rodas = df_filtrado['custo_rodas_pneus'].sum()
            
            # KPIs aprimorados
            total_manutencao = custo_manutencao + custo_rodas + custo_lataria
            kpi_cols = st.columns(4)
            kpi_cols[0].metric("🔧 Manutenção Geral", f"R$ {custo_manutencao:,.2f}",
                              f"{custo_manutencao/total_manutencao*100:.1f}%" if total_manutencao > 0 else "0%")
            kpi_cols[1].metric("🛞 Rodas e Pneus", f"R$ {custo_rodas:,.2f}",
                              f"{custo_rodas/total_manutencao*100:.1f}%" if total_manutencao > 0 else "0%")
            kpi_cols[2].metric("🎨 Lataria e Pintura", f"R$ {custo_lataria:,.2f}",
                              f"{custo_lataria/total_manutencao*100:.1f}%" if total_manutencao > 0 else "0%")
            kpi_cols[3].metric("💰 Total Manutenção", f"R$ {total_manutencao:,.2f}")
            
            st.markdown("---")
            st.subheader(f"📊 Análise Visual dos Custos - {titulo_principal}")
            
            # Gráficos de manutenção existentes...
            dados_grafico = {'Categoria': ['Manutenção Geral', 'Rodas e Pneus', 'Lataria e Pintura'], 
                           'Custo': [custo_manutencao, custo_rodas, custo_lataria]}
            df_grafico = pd.DataFrame(dados_grafico).sort_values('Custo', ascending=False)
            cores_vivas = ["#1b69a0", '#ff7f0e', '#2ca02c']
            mapa_cores = {'Manutenção Geral': cores_vivas[0], 'Rodas e Pneus': cores_vivas[1], 'Lataria e Pintura': cores_vivas[2]}
            
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                fig_pie = px.pie(df_grafico, names='Categoria', values='Custo', 
                               title='Distribuição Percentual dos Custos', hole=.3, 
                               color='Categoria', color_discrete_map=mapa_cores)
                fig_pie.update_traces(textposition='outside', textinfo='percent+label')
                fig_pie.update_layout(legend_font_size=14, uniformtext_minsize=12, uniformtext_mode='hide')
                st.plotly_chart(fig_pie, width='content')
            
            with g_col2:
                fig_bar = px.bar(df_grafico, x='Categoria', y='Custo', text_auto='.2s', 
                               title='Comparativo de Custos por Categoria', 
                               color='Categoria', color_discrete_map=mapa_cores)
                fig_bar.update_layout(showlegend=False)
                fig_bar.update_traces(width=0.5, textangle=0, textposition="outside")
                fig_bar.update_yaxes(range=[0, df_grafico['Custo'].max() * 1.1])
                st.plotly_chart(fig_bar, width='content')
            
            st.markdown("---")
            st.subheader(f"📋 Detalhamento por Veículo - {titulo_principal}")
            
            # Relatório de veículos para manutenção
            df_veiculos = df_filtrado.groupby('Placa').agg({
                'Modelo': 'first', 'Grupo Veículo': 'first', 'Marca': 'first', 
                'TP.Comb': 'first', 'TP.Rota': 'first', 'contrato': 'first', 
                'Roteiro Principal': 'first', 'Motorista Principal': 'first',
                'regiao': 'first', 'filial': 'first',
                'custo_manutencao_geral': 'sum', 'custo_rodas_pneus': 'sum', 
                'custo_lataria_pintura': 'sum', 'valor': 'sum'
            }).reset_index()
            
            # Ranking e estatísticas
            df_veiculos['Ranking'] = df_veiculos['valor'].rank(ascending=False).astype(int)
            
            df_veiculos.rename(columns={
                'valor': 'Custo Total', 'custo_manutencao_geral': 'Manutenção Geral', 
                'custo_rodas_pneus': 'Rodas e Pneus', 'custo_lataria_pintura': 'Lataria e Pintura', 
                'contrato': 'Contrato', 'regiao': 'Região', 'filial': 'Filial'
            }, inplace=True)
            
            ordem_colunas = ['Ranking', 'Placa', 'Modelo', 'Marca', 'Grupo Veículo', 'Região', 'Filial',
                           'TP.Comb', 'TP.Rota', 'Contrato', 'Roteiro Principal', 'Motorista Principal', 
                           'Manutenção Geral', 'Rodas e Pneus', 'Lataria e Pintura', 'Custo Total']
            
            st.dataframe(df_veiculos[ordem_colunas], width='content', hide_index=True,
                        column_config={
                            "Custo Total": st.column_config.NumberColumn(format="R$ %.2f"),
                            "Manutenção Geral": st.column_config.NumberColumn(format="R$ %.2f"),
                            "Rodas e Pneus": st.column_config.NumberColumn(format="R$ %.2f"),
                            "Lataria e Pintura": st.column_config.NumberColumn(format="R$ %.2f")
                        })

    elif selected == "Combustível":
        titulo_aba = "Custo de Combustível"
        st.header(f"⛽ Análise de Combustível e Arla - {titulo_principal}")
        
        if df_filtrado.empty:
            st.error("❌ Nenhum dado encontrado para os filtros selecionados.")
        else:
            if ano_selecionado == 'Todos':
                exibir_analise_anual_completa(df_filtrado, titulo_aba)
            else:
                kpis = calcular_kpis_performance(df, ano_selecionado, mes_selecionado, 'custo_combustivel_total')
                if kpis:
                    exibir_kpis_em_cartoes(kpis, titulo_aba)
                    st.markdown("---")
                    exibir_graficos_performance_avancados(df, mes_selecionado, kpis, 'custo_combustivel_total', titulo_aba)
                else:
                    st.info("ℹ️ Selecione um mês específico para ver a análise de performance mensal.")
            
            st.markdown("---")
            
            # Análise regional para combustível
            if len(df_filtrado['regiao'].unique()) > 1 or regiao_selecionada != 'Todos':
                exibir_kpis_regionais(df_filtrado, 'custo_combustivel_total', regiao_selecionada)
                st.markdown("---")

            st.subheader(f"⛽ Análise Visual dos Custos - {titulo_principal}")
            
            custo_combustivel = df_filtrado['custo_combustivel'].sum()
            custo_arla = df_filtrado['custo_arla'].sum()
            total_combustivel = custo_combustivel + custo_arla
            
            # KPIs de combustível
            kpi_cols = st.columns(3)
            kpi_cols[0].metric("⛽ Combustível", f"R$ {custo_combustivel:,.2f}",
                              f"{custo_combustivel/total_combustivel*100:.1f}%" if total_combustivel > 0 else "0%")
            kpi_cols[1].metric("💧 Arla", f"R$ {custo_arla:,.2f}",
                              f"{custo_arla/total_combustivel*100:.1f}%" if total_combustivel > 0 else "0%")
            kpi_cols[2].metric("💰 Total", f"R$ {total_combustivel:,.2f}")
            
            # Análise por tipo de combustível
            if 'TP.Comb' in df_filtrado.columns:
                st.markdown("---")
                st.subheader("🔍 Análise por Tipo de Combustível")
                
                analise_combustivel = df_filtrado.groupby('TP.Comb').agg({
                    'custo_combustivel_total': 'sum',
                    'Placa': 'nunique'
                }).reset_index()
                
                analise_combustivel['Custo_por_Veiculo'] = (
                    analise_combustivel['custo_combustivel_total'] / 
                    analise_combustivel['Placa']
                )
                
                fig_combustivel_tipo = px.bar(
                    analise_combustivel,
                    x='TP.Comb',
                    y='custo_combustivel_total',
                    title='Custos por Tipo de Combustível',
                    text='custo_combustivel_total',
                    color='custo_combustivel_total',
                    color_continuous_scale='viridis'
                )
                fig_combustivel_tipo.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                st.plotly_chart(fig_combustivel_tipo, width='content')
            
            # Gráficos existentes
            dados_grafico_comb = {'Categoria': ['Combustível', 'Arla'], 'Custo': [custo_combustivel, custo_arla]}
            df_grafico_comb = pd.DataFrame(dados_grafico_comb).sort_values('Custo', ascending=False)
            cores_comb = ["#e02222", "#1410e0"] 
            mapa_cores_comb = {'Combustível': cores_comb[0], 'Arla': cores_comb[1]}
            
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                fig_pie_comb = px.pie(df_grafico_comb, names='Categoria', values='Custo', 
                                    title='Distribuição Percentual dos Custos', hole=.3, 
                                    color='Categoria', color_discrete_map=mapa_cores_comb)
                fig_pie_comb.update_traces(textposition='outside', textinfo='percent+label')
                fig_pie_comb.update_layout(legend_font_size=14, uniformtext_minsize=12, uniformtext_mode='hide')
                st.plotly_chart(fig_pie_comb, width='content')
            
            with g_col2:
                fig_bar_comb = px.bar(df_grafico_comb, x='Categoria', y='Custo', text_auto='.2s', 
                                    title='Comparativo de Custos por Categoria', 
                                    color='Categoria', color_discrete_map=mapa_cores_comb)
                fig_bar_comb.update_layout(showlegend=False)
                fig_bar_comb.update_traces(width=0.4, textangle=0, textposition="outside")
                fig_bar_comb.update_yaxes(range=[0, df_grafico_comb['Custo'].max() * 1.1])
                st.plotly_chart(fig_bar_comb, width='content')
            
            # Relatório detalhado por veículo para combustível
            st.markdown("---")
            st.subheader(f"📋 Consumo Detalhado por Veículo - {titulo_principal}")
            
            df_combustivel_veiculos = df_filtrado.groupby('Placa').agg({
                'Modelo': 'first', 'Grupo Veículo': 'first', 'Marca': 'first', 
                'TP.Comb': 'first', 'TP.Rota': 'first', 'contrato': 'first', 
                'Roteiro Principal': 'first', 'Motorista Principal': 'first',
                'regiao': 'first', 'filial': 'first',
                'custo_combustivel': 'sum', 'custo_arla': 'sum', 
                'custo_combustivel_total': 'sum'
            }).reset_index()
            
            # Ranking por consumo
            df_combustivel_veiculos['Ranking'] = df_combustivel_veiculos['custo_combustivel_total'].rank(ascending=False).astype(int)
            
            df_combustivel_veiculos.rename(columns={
                'custo_combustivel': 'Combustível', 'custo_arla': 'Arla', 
                'custo_combustivel_total': 'Total Combustível',
                'contrato': 'Contrato', 'regiao': 'Região', 'filial': 'Filial'
            }, inplace=True)
            
            ordem_colunas_comb = ['Ranking', 'Placa', 'Modelo', 'Marca', 'Grupo Veículo', 'Região', 'Filial',
                                 'TP.Comb', 'TP.Rota', 'Contrato', 'Roteiro Principal', 'Motorista Principal', 
                                 'Combustível', 'Arla', 'Total Combustível']
            
            st.dataframe(df_combustivel_veiculos[ordem_colunas_comb], width='content', hide_index=True,
                        column_config={
                            "Combustível": st.column_config.NumberColumn(format="R$ %.2f"),
                            "Arla": st.column_config.NumberColumn(format="R$ %.2f"),
                            "Total Combustível": st.column_config.NumberColumn(format="R$ %.2f")
                        })

    elif selected == "Análise Detalhada":
        st.header(f"🔍 Análise Detalhada e Insights - {titulo_principal}")
        
        if df_filtrado.empty:
            st.error("❌ Nenhum dados encontrados para os filtros selecionados.")
        else:
            # Análises cruzadas e insights avançados
            st.subheader("🧠 Insights Avançados de Performance")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Análise de correlação entre custos
                st.write("##### 📊 Matriz de Correlação de Custos")
                custos_correlacao = df_filtrado[['custo_combustivel', 'custo_arla', 'custo_manutencao_geral', 
                                               'custo_rodas_pneus', 'custo_lataria_pintura']].corr()
                
                fig_corr = px.imshow(custos_correlacao, 
                                   title="Correlação entre Tipos de Custos",
                                   color_continuous_scale='RdBu_r',
                                   aspect="auto")
                fig_corr.update_layout(width=500, height=400)
                st.plotly_chart(fig_corr, width='content')
            
            with col2:
                # Análise de eficiência por grupo de veículo
                st.write("##### 🚛 Eficiência por Grupo de Veículo")
                eficiencia_grupo = df_filtrado.groupby('Grupo Veículo').agg({
                    'custo_frota_total': 'mean'
                }).reset_index().sort_values('custo_frota_total', ascending=True)
                
                fig_eficiencia = px.bar(eficiencia_grupo, 
                                      x='custo_frota_total', 
                                      y='Grupo Veículo',
                                      orientation='h',
                                      title="Custo Médio por Grupo de Veículo",
                                      text='custo_frota_total',
                                      color='custo_frota_total',
                                      color_continuous_scale='RdYlGn_r')
                fig_eficiencia.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                st.plotly_chart(fig_eficiencia, width='content')
            
            # Análise temporal se temos dados de múltiplos períodos
            if ano_selecionado != 'Todos' and len(df_filtrado['mes_ano'].unique()) > 1:
                st.markdown("---")
                st.subheader("📈 Análise de Tendências Temporais")
                
                # Evolução mensal dos custos
                evolucao_temporal = df_filtrado.groupby('mes_ano').agg({
                    'custo_frota_total': 'sum',
                    'custo_combustivel_total': 'sum',
                    'valor': 'sum',
                    'Placa': 'nunique'
                }).reset_index()
                
                evolucao_temporal['custo_por_veiculo'] = (
                    evolucao_temporal['custo_frota_total'] / 
                    evolucao_temporal['Placa']
                )
                
                fig_temporal = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('Evolução dos Custos Totais', 'Custo por Veículo'),
                    vertical_spacing=0.15
                )
                
                # Gráfico 1: Custos totais
                fig_temporal.add_trace(
                    go.Scatter(x=evolucao_temporal['mes_ano'], 
                             y=evolucao_temporal['valor'],
                             mode='lines+markers',
                             name='Manutenção',
                             line=dict(color='#ff7f0e')), 
                    row=1, col=1
                )
                
                fig_temporal.add_trace(
                    go.Scatter(x=evolucao_temporal['mes_ano'], 
                             y=evolucao_temporal['custo_combustivel_total'],
                             mode='lines+markers',
                             name='Combustível',
                             line=dict(color='#2ca02c')), 
                    row=1, col=1
                )
                
                # Gráfico 2: Custo por veículo
                fig_temporal.add_trace(
                    go.Scatter(x=evolucao_temporal['mes_ano'], 
                             y=evolucao_temporal['custo_por_veiculo'],
                             mode='lines+markers',
                             name='Custo/Veículo',
                             line=dict(color='#007bff')), 
                    row=2, col=1
                )
                
                fig_temporal.update_layout(height=600, title_text="Análise Temporal Completa")
                st.plotly_chart(fig_temporal, width='content')
            
            # Análise de outliers
            st.markdown("---")
            st.subheader("🎯 Identificação de Outliers e Oportunidades")
            
            # Veículos com custos anômalos
            Q1 = df_filtrado.groupby('Placa')['custo_frota_total'].sum().quantile(0.25)
            Q3 = df_filtrado.groupby('Placa')['custo_frota_total'].sum().quantile(0.75)
            IQR = Q3 - Q1
            limite_superior = Q3 + 1.5 * IQR
            limite_inferior = Q1 - 1.5 * IQR
            
            custos_por_veiculo = df_filtrado.groupby('Placa')['custo_frota_total'].sum()
            outliers_superiores = custos_por_veiculo[custos_por_veiculo > limite_superior]
            outliers_inferiores = custos_por_veiculo[custos_por_veiculo < limite_inferior]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🚨 Veículos Alto Custo", len(outliers_superiores),
                         help=f"Veículos com custo acima de R$ {limite_superior:,.2f}")
            
            with col2:
                st.metric("✅ Veículos Baixo Custo", len(outliers_inferiores),
                         help=f"Veículos com custo abaixo de R$ {limite_inferior:,.2f}")
            
            with col3:
                economia_potencial = outliers_superiores.sum() - (len(outliers_superiores) * custos_por_veiculo.median())
                st.metric("💰 Economia Potencial", f"R$ {economia_potencial:,.2f}",
                         help="Economia se veículos alto custo chegassem à mediana")
            
            # Tabela de veículos outliers
            if len(outliers_superiores) > 0:
                st.write("##### 🚨 Veículos que Requerem Atenção (Alto Custo)")
                
                outliers_info = df_filtrado[df_filtrado['Placa'].isin(outliers_superiores.index)].groupby('Placa').agg({
                    'Modelo': 'first',
                    'Marca': 'first', 
                    'Grupo Veículo': 'first',
                    'regiao': 'first',
                    'filial': 'first',
                    'custo_frota_total': 'sum',
                    'Motorista Principal': 'first'
                }).reset_index()
                
                outliers_info['Economia_Potencial'] = outliers_info['custo_frota_total'] - custos_por_veiculo.median()
                outliers_info = outliers_info.sort_values('custo_frota_total', ascending=False)
                
                st.dataframe(outliers_info.rename(columns={
                    'custo_frota_total': 'Custo Total',
                    'regiao': 'Região',
                    'filial': 'Filial',
                    'Economia_Potencial': 'Economia Potencial'
                }), width='content', hide_index=True,
                column_config={
                    "Custo Total": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Economia Potencial": st.column_config.NumberColumn(format="R$ %.2f")
                })
            
            # Recomendações baseadas em dados
            st.markdown("---")
            st.subheader("💡 Recomendações Estratégicas")
            
            recomendacoes = []
            
            # Análise de custos por categoria
            total_manutencao = df_filtrado['valor'].sum()
            total_combustivel = df_filtrado['custo_combustivel_total'].sum()
            
            if total_manutencao > total_combustivel:
                recomendacoes.append("🔧 **Foco na Manutenção**: Os custos de manutenção superam os de combustível. Considere implementar manutenção preventiva.")
            
            if len(outliers_superiores) > len(custos_por_veiculo) * 0.1:
                recomendacoes.append(f"🚨 **Gestão de Outliers**: {len(outliers_superiores)} veículos ({len(outliers_superiores)/len(custos_por_veiculo)*100:.1f}%) apresentam custos elevados. Investigação necessária.")
            
            # Análise regional
            if len(df_filtrado['regiao'].unique()) > 1:
                custos_regionais = df_filtrado.groupby('regiao')['custo_frota_total'].sum()
                regiao_mais_cara = custos_regionais.idxmax()
                regiao_mais_barata = custos_regionais.idxmin()
                diferenca = custos_regionais.max() - custos_regionais.min()
                
                if diferenca > custos_regionais.mean() * 0.3:
                    recomendacoes.append(f"🌍 **Equalização Regional**: Região {regiao_mais_cara} tem custos R$ {diferenca:,.2f} maiores que {regiao_mais_barata}. Analisar práticas operacionais.")
            
            # Análise de eficiência de combustível por tipo
            if 'TP.Comb' in df_filtrado.columns:
                eficiencia_combustivel = df_filtrado.groupby('TP.Comb')['custo_combustivel_total'].mean()
                if len(eficiencia_combustivel) > 1:
                    combustivel_mais_eficiente = eficiencia_combustivel.idxmin()
                    recomendacoes.append(f"⛽ **Otimização de Combustível**: Veículos {combustivel_mais_eficiente} apresentam melhor custo-benefício em combustível.")
            
            if recomendacoes:
                for rec in recomendacoes:
                    st.markdown(f"- {rec}")
            else:
                st.info("🎯 A operação está dentro dos padrões esperados. Continue o monitoramento regular.")

else:
    st.error("❌ Erro ao carregar os dados. Verifique a conexão com a fonte de dados.")
    st.info("💡 Dica: Verifique se o arquivo de dados está disponível e acessível.")

# Footer com informações do sistema
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🚛 <strong>FKM Gritsch - Sistema de Gestão de Frota</strong></p>
    <p>Desenvolvido para otimização de custos e eficiência operacional</p>
    <p><small>Versão 2.0 - Dashboard Avançado com IA e Analytics</small></p>
</div>
""", unsafe_allow_html=True)