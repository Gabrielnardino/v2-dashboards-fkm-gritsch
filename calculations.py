import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta

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
    """Dashboard executivo com KPIs de alto nível aprimorado"""
    st.subheader(f"👔 Dashboard Executivo - {titulo_principal}")
    
    # Cálculos base
    custo_total = df_filtrado['custo_frota_total'].sum()
    custo_combustivel = df_filtrado['custo_combustivel'].sum()
    custo_arla = df_filtrado['custo_arla'].sum()
    custo_manutencao = df_filtrado['custo_manutencao_geral'].sum()
    custo_lataria = df_filtrado['custo_lataria_pintura'].sum()
    custo_pneus = df_filtrado['custo_rodas_pneus'].sum()
    
    # Período de dados
    data_min = df_filtrado['data'].min()
    data_max = df_filtrado['data'].max()
    periodo_str = f"{data_min.strftime('%m/%Y')} até {data_max.strftime('%m/%Y')}"
    
    # CSS aprimorado com fontes maiores e mais cores
    st.markdown("""
    <style>
    .exec-card {
        background: linear-gradient(145deg, #1a1a1a 0%, #2d2d2d 50%, #1e1e1e 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 
            0 10px 25px -5px rgba(0, 0, 0, 0.4),
            0 4px 6px -2px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .exec-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    }

    .exec-card:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 20px 40px -5px rgba(0, 0, 0, 0.5),
            0 8px 16px -4px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-color: rgba(0, 123, 255, 0.3);
    }

    .exec-title {
        font-size: 18px;
        font-weight: 600;
        color: #f0f0f0;
        margin-bottom: 16px;
        letter-spacing: -0.01em;
        line-height: 1.4;
        text-transform: uppercase;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .exec-value {
        font-size: 32px;
        font-weight: 700;
        color: #0ea5e9;
        margin-bottom: 12px;
        letter-spacing: -0.02em;
        line-height: 1.2;
        text-shadow: 0 2px 4px rgba(14, 165, 233, 0.3);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .exec-detail.1 {
        font-size: 15px;
        color: #c1c1c1;
        margin: 8px 0;
        font-weight: 500;
        line-height: 1.5;
        letter-spacing: 0.01em;
        text-shadow: 0 1px 2px rgba(245, 158, 11, 0.3);
    }
    .exec-detail.2 {
        font-size: 15px;
        color: #c1c1c1;
        margin: 8px 0;
        font-weight: 500;
        line-height: 1.5;
        letter-spacing: 0.01em;
        text-shadow: 0 1px 2px rgba(25, 180, 11, 90);
    }
    .exec-detail.3 {
        font-size: 15px;
        color: #c1c1c1;
        margin: 8px 0;
        font-weight: 500;
        line-height: 1.5;
        letter-spacing: 0.01em;
        text-shadow: 0 1px 2px rgba(145, 95, 11, 10);
    }
    .exec-detail.4 {
        font-size: 15px;
        color: #c1c1c1;
        margin: 8px 0;
        font-weight: 500;
        line-height: 1.5;
        letter-spacing: 0.01em;
        text-shadow: 0 1px 2px rgba(245, 158, 11, 0.3);
    }

    .exec-detail-highlight {
        font-size: 15px;
        color: #22c55e;
        margin: 8px 0;
        font-weight: 600;
        line-height: 1.5;
        letter-spacing: 0.01em;
        text-shadow: 0 1px 2px rgba(34, 197, 94, 0.3);
    }

    .exec-detail-warning {
        font-size: 15px;
        color: #f59e0b;
        margin: 8px 0;
        font-weight: 600;
        line-height: 1.5;
        letter-spacing: 0.01em;
        text-shadow: 0 1px 2px rgba(245, 158, 11, 0.3);
    }

    .exec-projection {
        background: linear-gradient(145deg, #1e3a28 0%, #2d5a3d 50%, #1a3324 100%);
        border: 1px solid rgba(34, 197, 94, 0.2);
        position: relative;
    }

    .exec-projection::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(34, 197, 94, 0.4), transparent);
    }

    .exec-projection:hover {
        border-color: rgba(34, 197, 94, 0.4);
        box-shadow: 
            0 20px 40px -5px rgba(0, 0, 0, 0.5),
            0 8px 16px -4px rgba(34, 197, 94, 0.2),
            inset 0 1px 0 rgba(34, 197, 94, 0.1);
    }

    .exec-projection .exec-value {
        color: #22c55e;
        text-shadow: 0 2px 4px rgba(34, 197, 94, 0.4);
    }

    .exec-rank {
        font-size: 13px;
        color: #fbbf24;
        font-weight: 700;
        margin: 4px 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        text-shadow: 0 1px 2px rgba(251, 191, 36, 0.4);
    }

    .veiculo-card {
        background: linear-gradient(145deg, #1a1a1a 0%, #2d2d2d 50%, #1e1e1e 100%);
        border-radius: 14px;
        padding: 20px;
        margin: 16px 0;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 
            0 8px 20px -4px rgba(0, 0, 0, 0.3),
            0 4px 6px -1px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .veiculo-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
    }

    .veiculo-card:hover {
        transform: translateY(-1px);
        box-shadow: 
            0 12px 25px -4px rgba(0, 0, 0, 0.4),
            0 6px 10px -2px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.08);
        border-color: rgba(0, 123, 255, 0.2);
    }

    .veiculo-title {
        font-size: 20px;
        font-weight: 700;
        color: #0ea5e9;
        margin-bottom: 16px;
        text-align: center;
        letter-spacing: -0.01em;
        line-height: 1.3;
        text-shadow: 0 2px 4px rgba(14, 165, 233, 0.3);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .veiculo-item {
        font-size: 15px;
        color: #e5e5e5;
        margin: 10px 0;
        font-weight: 500;
        line-height: 1.6;
        letter-spacing: 0.01em;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .veiculo-item:last-child {
        border-bottom: none;
        margin-bottom: 0;
    }

    .veiculo-value {
        color: #22c55e;
        font-weight: 700;
        text-shadow: 0 1px 2px rgba(34, 197, 94, 0.3);
        font-variant-numeric: tabular-nums;
    }

    .veiculo-count {
        color: #f59e0b;
        font-weight: 700;
        text-shadow: 0 1px 2px rgba(245, 158, 11, 0.3);
        font-variant-numeric: tabular-nums;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .exec-card,
    .veiculo-card {
        animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }

    @media (max-width: 768px) {
        .exec-card,
        .veiculo-card {
            padding: 16px;
            margin-bottom: 16px;
        }
        
        .exec-title {
            font-size: 16px;
        }
        
        .exec-value {
            font-size: 28px;
        }
        
        .veiculo-title {
            font-size: 18px;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        .exec-card,
        .veiculo-card {
            animation: none;
            transition: none;
        }
        
        .exec-card:hover,
        .veiculo-card:hover {
            transform: none;
        }
    }

    .exec-card:focus-within,
    .veiculo-card:focus-within {
        outline: 2px solid #0ea5e9;
        outline-offset: 2px;
    }
    </style>
    """, unsafe_allow_html=True)
   
    
    # Primeira linha - Cards principais
    cols1 = st.columns(2)
    
    with cols1[0]:
        st.markdown(f"""
        <div class="exec-card">
            <div class="exec-title">💰 Custo Total da Frota</div>
            <div class="exec-value">R$ {custo_total:,.2f}</div>
            <div class="exec-detail">Período: {periodo_str}</div>
            <div class="exec-detail-highlight">⛽ Combustível: R$ {custo_combustivel:,.2f}</div>
            <div class="exec-detail-warning">🔧 Manutenção: R$ {custo_manutencao:,.2f}</div>
            <div class="exec-detail.1">🎨 Lataria: R$ {custo_lataria:,.2f}</div>
            <div class="exec-detail.2">🛞 Pneus: R$ {custo_pneus:,.2f}</div>
            <div class="exec-detail.3">💧 Arla: R$ {custo_arla:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols1[1]:
        # Projeção anual
        meses_dados = df_filtrado['mes_ano'].nunique()
        projecao_anual = (custo_total / meses_dados) * 12 if meses_dados > 0 else 0
        projecao_combustivel = (custo_combustivel / meses_dados) * 12 if meses_dados > 0 else 0
        projecao_manutencao = (custo_manutencao / meses_dados) * 12 if meses_dados > 0 else 0
        projecao_lataria = (custo_lataria / meses_dados) * 12 if meses_dados > 0 else 0
        projecao_pneus = (custo_pneus / meses_dados) * 12 if meses_dados > 0 else 0
        projecao_arla = (custo_arla / meses_dados) * 12 if meses_dados > 0 else 0
        
        st.markdown(f"""
        <div class="exec-card exec-projection">
            <div class="exec-title">📈 Estimativa Anual</div>
            <div class="exec-value">R$ {projecao_anual:,.2f}</div>
            <div class="exec-detail">Base: {meses_dados} meses de dados</div>
            <div class="exec-detail-highlight">⛽ Combustível: R$ {projecao_combustivel:,.2f}</div>
            <div class="exec-detail-warning">🔧 Manutenção: R$ {projecao_manutencao:,.2f}</div>
            <div class="exec-detail">🎨 Lataria: R$ {projecao_lataria:,.2f}</div>
            <div class="exec-detail">🛞 Pneus: R$ {projecao_pneus:,.2f}</div>
            <div class="exec-detail">💧 Arla: R$ {projecao_arla:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""<style>
    /* Aumenta o tamanho do NÚMERO da métrica */
    [data-testid="stMetricValue"] {
        font-size: 32px; 
    }
    /* Aumenta o tamanho do TÍTULO da métrica */
    [data-testid="stMetricLabel"] {
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Analise Resumida por Filial ---

    # Supondo que essas variáveis venham dos seus widgets de filtro (st.selectbox, etc.)
    ano_selecionado = 'Todos' # Substitua pelo seu seletor de ano
    mes_selecionado = 'Todos' # Substitua pelo seu seletor de mês
    regiao_selecionada = 'Todos' # Substitua pelo seu seletor de região
    filial_selecionada = 'Todos' # Substitua pelo seu seletor de filial

    if ('filial' in df_filtrado.columns and not df_filtrado.empty and
        ano_selecionado == 'Todos' and mes_selecionado == 'Todos' and
        regiao_selecionada == 'Todos' and filial_selecionada == 'Todos'):

        st.subheader("Análise Resumida por Filial")

        # --- PARTE 1: ORDENAÇÃO DAS FILIAIS POR GASTO (NOVA LÓGICA) ---

        # Primeiro, calculamos o custo total para todo o DataFrame
        colunas_custo = [
            'custo_combustivel', 'custo_manutencao_geral', 'custo_arla',
            'custo_lataria_pintura', 'custo_rodas_pneus'
        ]
        df_filtrado['custo_total'] = df_filtrado[colunas_custo].sum(axis=1)

        # Agora, agrupamos por filial, somamos o custo total e ordenamos do maior para o menor
        gastos_por_filial = df_filtrado.groupby('filial')['custo_total'].sum().sort_values(ascending=False)

        # Pegamos a lista de filiais JÁ ORDENADA
        filiais_ordenadas = gastos_por_filial.index
        
        # Define o número de colunas para os cards (ex: 3 cards por linha)
        num_colunas = 3
        cols = st.columns(num_colunas)

        # O loop agora usa a lista de filiais ordenadas
        for i, filial_nome in enumerate(filiais_ordenadas):
            with cols[i % num_colunas]:
                df_da_filial = df_filtrado[df_filtrado['filial'] == filial_nome]
                
                # Cálculos dos valores (agora podemos pegar o total direto da nossa série pré-calculada)
                custo_total_filial = gastos_por_filial[filial_nome]
                custo_combustivel = df_da_filial['custo_combustivel'].sum()
                custo_manut_geral = df_da_filial['custo_manutencao_geral'].sum()
                custo_lataria = df_da_filial['custo_lataria_pintura'].sum()
                custo_pneus = df_da_filial['custo_rodas_pneus'].sum()
                custo_arla = df_da_filial['custo_arla'].sum()
                num_veiculos = df_da_filial['Placa'].nunique()

                # Exibição do card
                st.markdown(f"""
                <div class="exec-card">
                    <div class="exec-title">🏢 Resumo: {filial_nome}</div>
                    <div class="exec-value">R$ {custo_total_filial:,.2f}</div>
                    <div class="exec-detail">Total de {num_veiculos} veículos</div>
                    <div class="exec-detail-highlight">⛽ Combustível: R$ {custo_combustivel:,.2f}</div>
                    <div class="exec-detail-warning">🔧 Manutenção: R$ {custo_manut_geral:,.2f}</div>
                    <div class="exec-detail">🎨 Lataria: R$ {custo_lataria:,.2f}</div>
                    <div class="exec-detail">🛞 Pneus: R$ {custo_pneus:,.2f}</div>
                    <div class="exec-detail">💧 Arla: R$ {custo_arla:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---") # Adiciona um separador visual
            
        try:
            # Lista dos grupos que queremos analisar, com seus respectivos emojis
            grupos_para_analise = {
                'Leve': '🚗',
                'Médio': '🚗',
                'Pesado': ' 🚚',
                'Caminhão': '🚛'
            }
            
            st.subheader("Análise da Frota por Grupo")

            # Loop para criar um card para cada grupo de veículo
            for grupo, emoji in grupos_para_analise.items():
                
                # Filtra o DataFrame para o grupo atual
                df_grupo = df_filtrado[df_filtrado['Grupo Veículo'] == grupo]
                
                # Só continua se houver dados para o grupo
                if not df_grupo.empty:
                    
                    # --- CÁLCULOS PARA O CARD ---
                    
                    # 1. Total de veículos (placas únicas) no grupo
                    total_veiculos_grupo = df_grupo['Placa'].nunique()
                    
                    # 2. LÓGICA DE CONTAGEM CORRIGIDA para Top 3 Modelos
                    # Primeiro, removemos as duplicatas de placas, mantendo a primeira ocorrência do modelo associado
                    df_veiculos_unicos = df_grupo.drop_duplicates(subset=['Placa'], keep='first')
                    # Agora, contamos os modelos a partir dos veículos únicos
                    top3_modelos = df_veiculos_unicos['Modelo'].value_counts().nlargest(3)
                    
                    # --- GERAÇÃO DO HTML PARA O RANKING ---
                    
                    html_top_modelos = ""
                    emojis_ranking = ['🥇', '🥈', '🥉'] # Emojis para o pódio
                    
                    if not top3_modelos.empty:
                        for i, (modelo, contagem) in enumerate(top3_modelos.items()):
                            # Limita o tamanho do nome do modelo para não quebrar o layout
                            modelo_short = modelo[:30] + '...' if len(modelo) > 30 else modelo
                            html_top_modelos += f'<div class="vehicle-group-ranking-item">{emojis_ranking[i]} {modelo_short} ({contagem} veículos)</div>'
                    else:
                        html_top_modelos = '<div class="vehicle-group-ranking-item">Nenhum modelo registrado.</div>'

                    # --- MONTAGEM E EXIBIÇÃO DO CARD COMPLETO ---
                    
                    st.markdown(f"""
                    <div class="vehicle-group-card">
                        <div class="vehicle-group-title">{emoji} {grupo}s</div>
                        <div class="vehicle-group-value">{total_veiculos_grupo} Veículos</div>
                        <div class="vehicle-group-ranking-title">Top 3 Modelos:</div>
                        {html_top_modelos}
                    </div>
                    """, unsafe_allow_html=True)

        except KeyError:
            st.warning("A coluna 'Grupo Veículo' não foi encontrada. O resumo da frota não pode ser exibido.")
            st.info("Verifique se o nome da coluna no seu DataFrame está correto e se a função de limpeza de dados foi executada.")
            
    st.markdown("---")
    st.subheader("📊 Análise por Grupo de Veículo - Custo Médio Anual")
    
    if 'Grupo Veículo' in df_filtrado.columns and len(df_filtrado) > 0:
        # Calcular custos médios por grupo de veículo
        analise_veiculo = df_filtrado.groupby('Grupo Veículo').agg({
            'custo_combustivel': 'mean',
            'custo_manutencao_geral': 'mean', 
            'custo_arla': 'mean',
            'custo_lataria_pintura': 'mean',
            'custo_rodas_pneus': 'mean',
            'custo_frota_total': 'mean',
            'Placa': 'nunique'
        }).reset_index()

        # Calcular manutenção total
        analise_veiculo['manut_total_mean'] = (
            analise_veiculo['custo_manutencao_geral'] + 
            analise_veiculo['custo_arla'] + 
            analise_veiculo['custo_lataria_pintura'] + 
            analise_veiculo['custo_rodas_pneus']
        )

        # Projeção anual por veículo
        analise_veiculo['comb_anual'] = analise_veiculo['custo_combustivel'] * 12
        analise_veiculo['manut_anual'] = analise_veiculo['manut_total_mean'] * 12
        analise_veiculo['total_anual'] = analise_veiculo['custo_frota_total'] * 12

        # Ordenar por custo total (maior para menor)
        analise_veiculo = analise_veiculo.sort_values('total_anual', ascending=False)

        cols2 = st.columns(3)

        with cols2[0]:
            combustivel_html = ""
            for _, row in analise_veiculo.iterrows():
                tipo = row['Grupo Veículo']
                valor = row['comb_anual']
                qtd = row['Placa']
                combustivel_html += f'<div class="veiculo-item"><span class="veiculo-value">{tipo}:</span> R$ {valor:,.2f} (<span class="veiculo-count">{qtd} veículos</span>)</div>'
            
            st.markdown(f"""
            <div class="veiculo-card">
                <div class="veiculo-title">⛽ Combustível Anual</div>
                {combustivel_html}
            </div>
            """, unsafe_allow_html=True)

        with cols2[1]:
            manutencao_html = ""
            for _, row in analise_veiculo.iterrows():
                tipo = row['Grupo Veículo']
                valor = row['manut_anual']
                qtd = row['Placa']
                manutencao_html += f'<div class="veiculo-item"><span class="veiculo-value">{tipo}:</span> R$ {valor:,.2f} (<span class="veiculo-count">{qtd} veículos</span>)</div>'
            
            st.markdown(f"""
            <div class="veiculo-card">
                <div class="veiculo-title">🔧 Manutenção Total Anual</div>
                {manutencao_html}
            </div>
            """, unsafe_allow_html=True)

        with cols2[2]:
            total_html = ""
            for _, row in analise_veiculo.iterrows():
                tipo = row['Grupo Veículo']
                valor = row['total_anual']
                qtd = row['Placa']
                total_html += f'<div class="veiculo-item"><span class="veiculo-value">{tipo}:</span> R$ {valor:,.2f} (<span class="veiculo-count">{qtd} veículos</span>)</div>'
            
            st.markdown(f"""
            <div class="veiculo-card">
                <div class="veiculo-title">💰 Custo Total Anual</div>
                {total_html}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Dados de Grupo Veículo não encontrados ou DataFrame vazio")
    
    # Gráficos mantidos
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
        
        