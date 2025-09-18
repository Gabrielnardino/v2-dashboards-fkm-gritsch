import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta

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
    
    # KPIs executivos em destaque
    col1, col2, col3, col4, col5 = st.columns(5)
    
    custo_total = df_filtrado['custo_frota_total'].sum()
    qtd_veiculos = df_filtrado['Placa'].nunique()
    qtd_regioes = df_filtrado['regiao'].nunique()
    qtd_filiais = df_filtrado['filial'].nunique()
    custo_medio_veiculo = custo_total / qtd_veiculos if qtd_veiculos > 0 else 0
    
    with col1:
        st.metric("💰 Investimento Total", f"R$ {custo_total:,.0f}")
    with col2:
        st.metric("🚛 Frota Ativa", f"{qtd_veiculos} veículos")
    with col3:
        st.metric("🌍 Regiões Atendidas", f"{qtd_regioes} regiões")
    with col4:
        st.metric("🏢 Filiais Ativas", f"{qtd_filiais} filiais")
    with col5:
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
