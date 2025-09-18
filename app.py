# app.py (VERSÃO COMPLETA COM KPIs AVANÇADOS)
import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dateutil.relativedelta import relativedelta
from src.config.data_provider import get_data

st.set_page_config(page_title="Dashboard FKM Gritsch", layout="wide", page_icon="🚚")

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
    
    # Cálculos de dias úteis
    dias_uteis_atual = df_mes_atual['Dias Úteis'].iloc[0] if not df_mes_atual.empty and 'Dias Úteis' in df_mes_atual.columns else 0
    dias_uteis_anterior = df_mes_anterior['Dias Úteis'].iloc[0] if not df_mes_anterior.empty and 'Dias Úteis' in df_mes_anterior.columns else 0
    
    custo_dia_util_atual = custo_mes_atual / dias_uteis_atual if dias_uteis_atual > 0 else 0
    custo_dia_util_anterior = custo_mes_anterior / dias_uteis_anterior if dias_uteis_anterior > 0 else 0
    
    # Médias por dia útil
    soma_dias_uteis_3m = df_ultimos_3_meses.groupby('mes_ano')['Dias Úteis'].first().sum() if 'Dias Úteis' in df_ultimos_3_meses.columns else 0
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
    st.subheader(f"📊 Indicadores de Performance Mensal ({tipo_custo})")
    
    # CSS aprimorado
    st.markdown("""
    <style>
    .kpi-card{
        background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
        border-radius:12px;
        padding:20px;
        margin-bottom:20px;
        border:1px solid #404040;
        box-shadow:0 6px 12px 0 rgba(0,0,0,0.3);
    }
    .kpi-title{
        font-size:16px;
        font-weight:600;
        color:#E0E0E0;
        margin-bottom:12px;
    }
    .kpi-value{
        font-size:24px;
        font-weight:bold;
        color:#007bff;
        margin-bottom:8px;
    }
    .kpi-comparison{
        font-size:13px;
        color:#B0B0B0;
        margin-bottom:5px;
    }
    .kpi-delta-positive{
        color:#ff4b4b;
        font-weight:bold;
        font-size:12px;
    }
    .kpi-delta-negative{
        color:#28a745;
        font-weight:bold;
        font-size:12px;
    }
    .kpi-trend{
        background:#333;
        padding:4px 8px;
        border-radius:4px;
        font-size:11px;
        margin-top:5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Primeira linha - KPIs principais
    cols1 = st.columns(4)
    
    with cols1[0]:
        diff = kpis['diff_mes_anterior']
        var_perc = kpis['var_perc_mes_anterior']
        cor_delta = "positive" if diff > 0 else "negative"
        sinal_delta = "↑" if diff > 0 else "↓"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">💰 Custo vs. Mês Anterior</div>
            <div class="kpi-value">R$ {kpis['custo_mes_atual']:,.2f}</div>
            <div class="kpi-comparison">Mês Anterior: R$ {kpis['custo_mes_anterior']:,.2f}</div>
            <div class="kpi-delta-{cor_delta}">{sinal_delta} R$ {abs(diff):,.2f} ({var_perc:+.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols1[1]:
        diff = kpis['diff_media_3_meses']
        var_perc = kpis['var_perc_media_3m']
        cor_delta = "positive" if diff > 0 else "negative"
        sinal_delta = "↑" if diff > 0 else "↓"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">📊 Custo vs. Média 3M</div>
            <div class="kpi-value">R$ {kpis['custo_mes_atual']:,.2f}</div>
            <div class="kpi-comparison">Média 3M: R$ {kpis['media_3_meses']:,.2f}</div>
            <div class="kpi-delta-{cor_delta}">{sinal_delta} R$ {abs(diff):,.2f} ({var_perc:+.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols1[2]:
        diff = kpis['diff_media_6_meses']
        cor_delta = "positive" if diff > 0 else "negative"
        sinal_delta = "↑" if diff > 0 else "↓"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">📈 Custo vs. Média 6M</div>
            <div class="kpi-value">R$ {kpis['custo_mes_atual']:,.2f}</div>
            <div class="kpi-comparison">Média 6M: R$ {kpis['media_6_meses']:,.2f}</div>
            <div class="kpi-delta-{cor_delta}">{sinal_delta} R$ {abs(diff):,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols1[3]:
        diff = kpis['diff_media_12_meses']
        cor_delta = "positive" if diff > 0 else "negative"
        sinal_delta = "↑" if diff > 0 else "↓"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">📅 Custo vs. Média 12M</div>
            <div class="kpi-value">R$ {kpis['custo_mes_atual']:,.2f}</div>
            <div class="kpi-comparison">Média 12M: R$ {kpis['media_12_meses']:,.2f}</div>
            <div class="kpi-delta-{cor_delta}">{sinal_delta} R$ {abs(diff):,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Segunda linha - KPIs operacionais
    cols2 = st.columns(4)
    
    with cols2[0]:
        diff = kpis['diff_dia_util_anterior']
        cor_delta = "positive" if diff > 0 else "negative"
        sinal_delta = "↑" if diff > 0 else "↓"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">🗓️ Custo/Dia Útil</div>
            <div class="kpi-value">R$ {kpis['custo_dia_util_atual']:,.2f}</div>
            <div class="kpi-comparison">Mês Anterior: R$ {kpis['custo_dia_util_anterior']:,.2f}</div>
            <div class="kpi-delta-{cor_delta}">{sinal_delta} R$ {abs(diff):,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols2[1]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">🚛 Custo por Veículo</div>
            <div class="kpi-value">R$ {kpis['custo_por_veiculo']:,.2f}</div>
            <div class="kpi-comparison">Total de Veículos: {kpis['total_veiculos']}</div>
            <div class="kpi-trend">Análise por unidade</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols2[2]:
        cor_tendencia = "#28a745" if kpis['tendencia'] == "Decrescente" else "#ff4b4b"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">📈 Tendência (3M)</div>
            <div class="kpi-value" style="color:{cor_tendencia}">{kpis['tendencia']}</div>
            <div class="kpi-comparison">Baseado nos últimos 3 meses</div>
            <div class="kpi-trend">Análise de comportamento</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols2[3]:
        eficiencia = "Alta" if kpis['var_perc_mes_anterior'] < 5 else "Baixa" if kpis['var_perc_mes_anterior'] > 15 else "Média"
        cor_eficiencia = "#28a745" if eficiencia == "Alta" else "#ff4b4b" if eficiencia == "Baixa" else "#ffa500"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">⚡ Eficiência de Custo</div>
            <div class="kpi-value" style="color:{cor_eficiencia}">{eficiencia}</div>
            <div class="kpi-comparison">Variação: {kpis['var_perc_mes_anterior']:+.1f}%</div>
            <div class="kpi-trend">Controle de gastos</div>
        </div>
        """, unsafe_allow_html=True)

def exibir_kpis_regionais(df_filtrado, coluna_custo, regiao_selecionada):
    """Exibe KPIs comparativos entre regiões"""
    st.subheader("🌍 Análise Comparativa Regional")
    
    if regiao_selecionada != 'Todos':
        # Comparação da região selecionada com a média geral
        custo_regiao = df_filtrado[coluna_custo].sum()
        df_todas_regioes = df_filtrado  # Assumindo que já está filtrado por outros critérios
        df_outras_regioes = df_todas_regioes[df_todas_regioes['regiao'] != regiao_selecionada] if regiao_selecionada != 'Todos' else pd.DataFrame()
        
        custo_total_geral = df_todas_regioes[coluna_custo].sum()
        custo_outras_regioes = df_outras_regioes[coluna_custo].sum() if not df_outras_regioes.empty else 0
        
        # Cálculos de participação
        participacao_regiao = (custo_regiao / custo_total_geral * 100) if custo_total_geral > 0 else 0
        
        cols = st.columns(4)
        with cols[0]:
            st.metric("💰 Custo da Região", f"R$ {custo_regiao:,.2f}")
        with cols[1]:
            st.metric("📊 Participação no Total", f"{participacao_regiao:.1f}%")
        with cols[2]:
            veiculos_regiao = df_filtrado['Placa'].nunique()
            custo_por_veiculo_regiao = custo_regiao / veiculos_regiao if veiculos_regiao > 0 else 0
            st.metric("🚛 Custo/Veículo", f"R$ {custo_por_veiculo_regiao:,.2f}")
        with cols[3]:
            # Ranking da região
            ranking_regioes = df_todas_regioes.groupby('regiao')[coluna_custo].sum().sort_values(ascending=False)
            posicao = list(ranking_regioes.index).index(regiao_selecionada) + 1 if regiao_selecionada in ranking_regioes.index else 0
            st.metric("🏆 Ranking Regional", f"{posicao}º lugar")
    
    # Comparativo entre todas as regiões
    st.subheader("📊 Ranking Regional Completo")
    comparativo_regioes = df_filtrado.groupby('regiao').agg({
        coluna_custo: 'sum',
        'Placa': 'nunique'
    }).reset_index()
    
    comparativo_regioes['Custo_por_Veiculo'] = comparativo_regioes[coluna_custo] / comparativo_regioes['Placa']
    comparativo_regioes['Participacao'] = (comparativo_regioes[coluna_custo] / comparativo_regioes[coluna_custo].sum() * 100)
    comparativo_regioes = comparativo_regioes.sort_values(coluna_custo, ascending=False)
    
    # Gráfico de barras por região
    fig_regioes = px.bar(
        comparativo_regioes, 
        x='regiao', 
        y=coluna_custo,
        title='Custos por Região',
        text=coluna_custo,
        color=coluna_custo,
        color_continuous_scale='RdYlBu_r'
    )
    fig_regioes.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig_regioes.update_layout(showlegend=False, xaxis_title="Região", yaxis_title="Custo Total (R$)")
    st.plotly_chart(fig_regioes, width='content')
    
    # Tabela detalhada
    comparativo_regioes.rename(columns={
        'regiao': 'Região',
        coluna_custo: 'Custo Total',
        'Placa': 'Qtd Veículos',
        'Custo_por_Veiculo': 'Custo/Veículo',
        'Participacao': 'Participação (%)'
    }, inplace=True)
    
    st.dataframe(
        comparativo_regioes,
        width='content',
        hide_index=True,
        column_config={
            "Custo Total": st.column_config.NumberColumn(format="R$ %.2f"),
            "Custo/Veículo": st.column_config.NumberColumn(format="R$ %.2f"),
            "Participação (%)": st.column_config.NumberColumn(format="%.1f%%")
        }
    )

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
    
    # Análise de variabilidade
    st.subheader("📊 Análise de Variabilidade e Controle")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Coeficiente de variação
        cv = (evolucao_mensal[coluna_custo].std() / evolucao_mensal[coluna_custo].mean()) * 100
        st.metric("📈 Coeficiente de Variação", f"{cv:.1f}%", help="Medida de variabilidade relativa dos custos")
    
    with col2:
        # Maior e menor custo do período
        max_custo = evolucao_mensal[coluna_custo].max()
        min_custo = evolucao_mensal[coluna_custo].min()
        amplitude = max_custo - min_custo
        st.metric("📊 Amplitude de Variação", f"R$ {amplitude:,.2f}", help=f"Diferença entre maior (R${max_custo:,.2f}) e menor custo (R${min_custo:,.2f})")
    
    with col3:
        # Tendência estatística
        from scipy.stats import linregress
        x = np.arange(len(evolucao_mensal))
        slope, _, r_value, _, _ = linregress(x, evolucao_mensal[coluna_custo])
        tendencia_stat = "📈 Crescente" if slope > 0 else "📉 Decrescente"
        st.metric("📈 Tendência Estatística", tendencia_stat, f"R²: {r_value**2:.3f}")

def exibir_analise_anual_completa(df_filtrado, titulo_aba):
    """Versão aprimorada da análise anual com mais KPIs"""
    
    st.subheader(f"🗓️ Análise Comparativa Anual Completa ({titulo_aba})")
    
    # Calcula os custos anuais com mais detalhes
    custos_anuais = df_filtrado.groupby('ano').agg(
        custo_frota_total=('custo_frota_total', 'sum'),
        custo_manutencao=('valor', 'sum'),
        custo_combustivel=('custo_combustivel_total', 'sum'),
        qtd_veiculos=('Placa', 'nunique'),
        qtd_registros=('Placa', 'count')
    ).reset_index().sort_values('ano', ascending=False)
    
    # Cálculos adicionais
    custos_anuais['custo_por_veiculo'] = custos_anuais['custo_frota_total'] / custos_anuais['qtd_veiculos']
    custos_anuais['crescimento_ano_anterior'] = custos_anuais['custo_frota_total'].pct_change(periods=-1) * 100
    
    # CSS aprimorado para análise anual
    st.markdown("""
    <style>
    .analise-anual-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        border: 2px solid #404040;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    .ano-titulo {
        font-size: 28px;
        font-weight: bold;
        color: #007bff;
        margin-bottom: 20px;
        text-align: center;
        background: linear-gradient(45deg, #007bff, #0056b3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .delta-anual-positivo { 
        color: #ff4b4b; 
        font-size: 16px; 
        font-weight: bold;
    }
    .delta-anual-negativo { 
        color: #28a745; 
        font-size: 16px; 
        font-weight: bold;
    }
    .kpi-anual {
        text-align: center;
        padding: 15px;
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        margin: 5px;
    }
    .kpi-anual-valor {
        font-size: 20px;
        font-weight: bold;
        color: #fff;
    }
    .kpi-anual-label {
        font-size: 12px;
        color: #ccc;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Exibe os KPIs anuais
    for i, row in custos_anuais.iterrows():
        ano_atual = row['ano']
        
        st.markdown(f'<div class="analise-anual-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="ano-titulo">📅 Análise do Ano {ano_atual}</div>', unsafe_allow_html=True)
        
        # KPIs principais em colunas
        cols_principais = st.columns(5)
        
        with cols_principais[0]:
            st.markdown(f'''
            <div class="kpi-anual">
                <div class="kpi-anual-valor">R$ {row['custo_frota_total']:,.0f}</div>
                <div class="kpi-anual-label">Custo Total da Frota</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with cols_principais[1]:
            st.markdown(f'''
            <div class="kpi-anual">
                <div class="kpi-anual-valor">R$ {row['custo_manutencao']:,.0f}</div>
                <div class="kpi-anual-label">Custo de Manutenção</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with cols_principais[2]:
            st.markdown(f'''
            <div class="kpi-anual">
                <div class="kpi-anual-valor">R$ {row['custo_combustivel']:,.0f}</div>
                <div class="kpi-anual-label">Custo de Combustível</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with cols_principais[3]:
            st.markdown(f'''
            <div class="kpi-anual">
                <div class="kpi-anual-valor">{row['qtd_veiculos']}</div>
                <div class="kpi-anual-label">Qtd de Veículos</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with cols_principais[4]:
            st.markdown(f'''
            <div class="kpi-anual">
                <div class="kpi-anual-valor">R$ {row['custo_por_veiculo']:,.0f}</div>
                <div class="kpi-anual-label">Custo por Veículo</div>
            </div>
            ''', unsafe_allow_html=True)

        # Comparativo com o ano anterior
        if i + 1 < len(custos_anuais):
            ano_anterior_row = custos_anuais.iloc[i + 1]
            ano_anterior = ano_anterior_row['ano']
            
            st.write(f"**📊 Comparativo com {ano_anterior}:**")
            comp_cols = st.columns(4)

            # Comparativo Custo Total
            diff_total = row['custo_frota_total'] - ano_anterior_row['custo_frota_total']
            perc_total = (diff_total / ano_anterior_row['custo_frota_total'] * 100) if ano_anterior_row['custo_frota_total'] > 0 else 0
            cor_total = "positivo" if diff_total > 0 else "negativo"
            sinal_total = "↗️" if diff_total > 0 else "↘️"
            comp_cols[0].markdown(f'**Frota Total:** <span class="delta-anual-{cor_total}">{sinal_total} R$ {abs(diff_total):,.0f} ({perc_total:+.1f}%)</span>', unsafe_allow_html=True)

            # Comparativo Custo Manutenção
            diff_manut = row['custo_manutencao'] - ano_anterior_row['custo_manutencao']
            perc_manut = (diff_manut / ano_anterior_row['custo_manutencao'] * 100) if ano_anterior_row['custo_manutencao'] > 0 else 0
            cor_manut = "positivo" if diff_manut > 0 else "negativo"
            sinal_manut = "↗️" if diff_manut > 0 else "↘️"
            comp_cols[1].markdown(f'**Manutenção:** <span class="delta-anual-{cor_manut}">{sinal_manut} R$ {abs(diff_manut):,.0f} ({perc_manut:+.1f}%)</span>', unsafe_allow_html=True)

            # Comparativo Custo Combustível
            diff_comb = row['custo_combustivel'] - ano_anterior_row['custo_combustivel']
            perc_comb = (diff_comb / ano_anterior_row['custo_combustivel'] * 100) if ano_anterior_row['custo_combustivel'] > 0 else 0
            cor_comb = "positivo" if diff_comb > 0 else "negativo"
            sinal_comb = "↗️" if diff_comb > 0 else "↘️"
            comp_cols[2].markdown(f'**Combustível:** <span class="delta-anual-{cor_comb}">{sinal_comb} R$ {abs(diff_comb):,.0f} ({perc_comb:+.1f}%)</span>', unsafe_allow_html=True)

            # Comparativo Eficiência por Veículo
            diff_eficiencia = row['custo_por_veiculo'] - ano_anterior_row['custo_por_veiculo']
            perc_eficiencia = (diff_eficiencia / ano_anterior_row['custo_por_veiculo'] * 100) if ano_anterior_row['custo_por_veiculo'] > 0 else 0
            cor_eficiencia = "positivo" if diff_eficiencia > 0 else "negativo"
            sinal_eficiencia = "↗️" if diff_eficiencia > 0 else "↘️"
            comp_cols[3].markdown(f'**Custo/Veículo:** <span class="delta-anual-{cor_eficiencia}">{sinal_eficiencia} R$ {abs(diff_eficiencia):,.0f} ({perc_eficiencia:+.1f}%)</span>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True) # Fecha o card
        st.markdown("---")

    # Visualizações avançadas
    st.write("#### 📊 Visualizações Comparativas Anuais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de evolução anual
        fig_evolucao_anual = go.Figure()
        
        fig_evolucao_anual.add_trace(go.Bar(
            x=custos_anuais['ano'],
            y=custos_anuais['custo_manutencao'],
            name='Manutenção',
            marker_color='#ff7f0e'
        ))
        
        fig_evolucao_anual.add_trace(go.Bar(
            x=custos_anuais['ano'],
            y=custos_anuais['custo_combustivel'],
            name='Combustível',
            marker_color='#2ca02c'
        ))
        
        fig_evolucao_anual.update_layout(
            title='Evolução Anual por Categoria',
            xaxis_title='Ano',
            yaxis_title='Custo (R$)',
            barmode='group'
        )
        
        st.plotly_chart(fig_evolucao_anual, width='content')
    
    with col2:
        # Gráfico de custo por veículo
        fig_eficiencia = px.line(
            custos_anuais.sort_values('ano'),
            x='ano',
            y='custo_por_veiculo',
            title='Evolução do Custo por Veículo',
            markers=True,
            line_shape='linear'
        )
        fig_eficiencia.update_traces(
            line=dict(color='#007bff', width=3),
            marker=dict(size=10, color='#007bff')
        )
        st.plotly_chart(fig_eficiencia, width='content')
    
    # Tabela resumo com ranking
    st.write("#### 📈 Resumo Executivo Anual")
    custos_anuais_display = custos_anuais.copy()
    custos_anuais_display['ranking_custo'] = custos_anuais_display['custo_frota_total'].rank(ascending=False).astype(int)
    custos_anuais_display['ranking_eficiencia'] = custos_anuais_display['custo_por_veiculo'].rank(ascending=True).astype(int)
    
    custos_anuais_display = custos_anuais_display.rename(columns={
        'ano': 'Ano',
        'custo_frota_total': 'Custo Total (R$)',
        'custo_manutencao': 'Manutenção (R$)',
        'custo_combustivel': 'Combustível (R$)',
        'qtd_veiculos': 'Qtd Veículos',
        'custo_por_veiculo': 'Custo/Veículo (R$)',
        'crescimento_ano_anterior': 'Crescimento (%)',
        'ranking_custo': 'Rank Custo',
        'ranking_eficiencia': 'Rank Eficiência'
    })
    
    st.dataframe(
        custos_anuais_display[[
            'Ano', 'Custo Total (R$)', 'Manutenção (R$)', 'Combustível (R$)', 
            'Qtd Veículos', 'Custo/Veículo (R$)', 'Crescimento (%)', 
            'Rank Custo', 'Rank Eficiência'
        ]],
        width='content',
        hide_index=True,
        column_config={
            "Custo Total (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
            "Manutenção (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
            "Combustível (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
            "Custo/Veículo (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
            "Crescimento (%)": st.column_config.NumberColumn(format="%.1f%%"),
        }
    )

def exibir_dashboard_executivo(df_filtrado, titulo_principal):
    """Dashboard executivo com KPIs de alto nível"""
    st.subheader(f"👔 Dashboard Executivo - {titulo_principal}")
    
    col1,col2,col3,col4 = st.columns(4)
    
    #Custo Frota
    custo_total = df_filtrado['custo_frota_total'].sum()
    qtd_veiculos = df_filtrado['Placa'].nunique()
    qtd_filiais = df_filtrado['filial'].nunique()
    custo_medio_veiculo = custo_total / qtd_veiculos if qtd_veiculos > 0 else 0
    
    with col1:
        st.metric("💰 Investimento Total", f"R$ {custo_total:,.2f}")
    with col2:
        st.metric("🚛 Frota Ativa", f"{qtd_veiculos} veículos")
    with col3:
        st.metric("🏢 Filiais Ativas", f"{qtd_filiais} filiais")
    with col4:
        st.metric("📊 Custo Médio/Veículo", f"R$ {custo_medio_veiculo:,.0f}")
    
    # Análise de distribuição
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 5 veículos com maior custo
        top_veiculos = df_filtrado.groupby(['Placa', 'Modelo'])['custo_frota_total'].sum().reset_index()
        top_veiculos = top_veiculos.nlargest(5, 'custo_frota_total')
        
        fig_top_veiculos = px.bar(
            top_veiculos,
            x='custo_frota_total',
            y='Placa',
            orientation='h',
            title='🚛 Top 5 Veículos - Maior Custo',
            text='custo_frota_total',
            color='custo_frota_total',
            color_continuous_scale='Reds'
        )
        fig_top_veiculos.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig_top_veiculos.update_layout(showlegend=False)
        st.plotly_chart(fig_top_veiculos, width='content')
    
    with col2:
        # Distribuição por tipo de rota
        dist_rota = df_filtrado.groupby('TP.Rota')['custo_frota_total'].sum().reset_index()
        
        fig_rota = px.pie(
            dist_rota,
            names='TP.Rota',
            values='custo_frota_total',
            title='🛣️ Distribuição por Tipo de Rota',
            hole=0.4
        )
        fig_rota.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_rota, width='content')

# --- CARREGAMENTO E FILTROS APRIMORADOS ---
with st.spinner('🔄 Analisando dados da frota... Por favor, aguarde.'):
    df = get_data()

if not df.empty:
    # Preparação dos dados
    df['custo_combustivel_total'] = df['custo_combustivel'] + df['custo_arla']
    df['custo_frota_total'] = df['valor'] + df['custo_combustivel_total']
    
    # Sidebar aprimorada
    with st.sidebar:
        st.title("🚛 FKM Gritsch")
        st.markdown("### Análise Inteligente de Frota")
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
    st.markdown("### Sistema Integrado de Gestão e Análise de Custos")
    
    # Filtros aprimorados
    with st.expander("🔍 Filtros Avançados de Análise", expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            anos_disponiveis = ['Todos'] + sorted(df['ano'].unique().tolist(), reverse=True)
            ano_selecionado = st.selectbox("📅 Ano", options=anos_disponiveis)
        
        mes_selecionado = 'Todos'
        with col2:
            if ano_selecionado != 'Todos':
                df_ano_filtrado = df[df['ano'] == ano_selecionado]
                meses_disponiveis = ['Todos'] + sorted(df_ano_filtrado['mes_ano'].unique().tolist())
                mes_selecionado = st.selectbox("📆 Mês", options=meses_disponiveis)
        
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
        
        with col5:
            # Filtro adicional por tipo de combustível
            combustiveis_disponiveis = ['Todos'] + sorted(df['TP.Comb'].unique().tolist())
            combustivel_selecionado = st.selectbox("⛽ Combustível", options=combustiveis_disponiveis)

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
    if combustivel_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['TP.Comb'] == combustivel_selecionado]
    
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