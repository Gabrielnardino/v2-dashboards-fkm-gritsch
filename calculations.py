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

# COPIE E COLE ESTE CÓDIGO NO LUGAR DA SUA FUNÇÃO exibir_dashboard_executivo ATUAL
# ARQUIVO: calculations.py

def exibir_dashboard_executivo(df_filtrado, df_completo, titulo_principal):
    """
    Visão Resumida com foco em análise anual comparativa, projeção para o ano
    corrente e detalhamento de performance mensal e por grupo.
    """
    st.subheader(f"👔 Visão Resumida - {titulo_principal}")

    if df_completo.empty:
        st.warning("Não há dados para exibir.")
        return

    # --- 1. CSS (Ajustando altura mínima do card) ---
    st.markdown("""
    <style>
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
    .card-purple { border-color: #8b5cf6; }
    .card-yellow { border-color: #f59e0b; }
    .card-orange { border-color: #ea580c; }
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
    .card-purple .card-value { color: #8b5cf6; }
    .card-yellow .card-value { color: #f59e0b; }
    .card-orange .card-value { color: #ea580c; }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. CÁLCULOS PARA ANÁLISE ANUAL ---
    st.subheader("Análise Anual de Custos da Frota")

    # Verificar se há filtro de ano específico
    ano_selecionado = st.session_state.get('ano_selecionado', 'Todos')

    if ano_selecionado != 'Todos':
        # Mostrar apenas o ano selecionado
        anos_para_exibir = [int(ano_selecionado)]
        # Para 2025, também mostrar projeção
        if int(ano_selecionado) == 2025:
            col_cards_anuais = st.columns(2)  # Atual + Projeção
        else:
            col_cards_anuais = st.columns(1)  # Apenas o ano
    else:
        # Mostrar os 3 anos mais recentes
        anos_disponiveis = sorted(df_completo['ano'].unique(), reverse=True)
        anos_para_exibir = anos_disponiveis[:3]
        anos_para_exibir.reverse()  # Ordem cronológica
        col_cards_anuais = st.columns(len(anos_para_exibir) + 1)  # +1 para projeção

    for i, ano in enumerate(anos_para_exibir):
        with col_cards_anuais[i]:
            df_ano = df_completo[df_completo['ano'] == ano]
            
            # Cálculos dos KPIs anuais
            custo_total_ano = df_ano['custo_frota_total'].sum()
            num_veiculos_ano = df_ano['Placa'].nunique()
            total_km_ano = df_ano['total_km'].sum()
            total_dias_uteis_ano = df_ano.groupby('mes_ano')['Dias Úteis'].first().sum()

            # Cálculos derivados e de eficiência
            custo_por_km = custo_total_ano / total_km_ano if total_km_ano > 0 else 0
            # Usando a coluna de Km/L já limpa e ajustada do data_provider
            eficiencia_media_kml = df_ano['media_km_litro_ajustado'].mean()
            km_medio_por_veiculo = total_km_ano / num_veiculos_ano if num_veiculos_ano > 0 else 0
            custo_dia_util = custo_total_ano / total_dias_uteis_ano if total_dias_uteis_ano > 0 else 0
            ticket_medio_por_veiculo = custo_total_ano / num_veiculos_ano if num_veiculos_ano > 0 else 0

            st.html(f"""
<div class="custom-card card-blue">
    <div class="card-title">🗓️ Custo Frota - {ano}</div>
    <div class="card-value">R$ {custo_total_ano:,.2f}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>🛣️ Km Total:</strong> {total_km_ano:,.0f} Km
    </div>
    <div class="card-detail">
        <strong>⛽ Eficiência Média:</strong> {eficiencia_media_kml:.2f} Km/L
    </div>
    <div class="card-detail">
        <strong>💰 Custo/Km:</strong> R$ {custo_por_km:.2f}
    </div>
    <div class="card-detail">
        <strong>🚛 Km Médio/Veículo:</strong> {km_medio_por_veiculo:,.0f} Km
    </div>
    <div class="card-detail">
        <strong>📅 Custo/Dia Útil:</strong> R$ {custo_dia_util:,.2f}
    </div>
    <div class="card-detail">
        <strong>🎫 Ticket Médio/Veículo:</strong> R$ {ticket_medio_por_veiculo:,.2f}
    </div>
</div>
            """)

    # --- 3. CÁLCULO E CARD DE PROJEÇÃO PARA 2025 ---
    # Mostrar projeção apenas quando 'Todos' ou quando 2025 estiver selecionado
    if ano_selecionado == 'Todos' or (ano_selecionado != 'Todos' and int(ano_selecionado) == 2025):
        if ano_selecionado == 'Todos':
            coluna_projecao = len(anos_para_exibir)
        else:  # 2025 selecionado
            coluna_projecao = 1

        with col_cards_anuais[coluna_projecao]:
            ano_atual = 2025
            df_ano_atual = df_completo[df_completo['ano'] == ano_atual]

            # Definir título baseado no contexto
            if ano_selecionado == 'Todos':
                titulo_card = f"📈 Projeção {ano_atual}"
            else:
                titulo_card = f"📈 Projeção Anual {ano_atual}"

            if not df_ano_atual.empty and 'data' in df_ano_atual.columns:
                try:
                    # Cálculos dos valores parciais de 2025
                    custo_parcial_2025 = df_ano_atual['custo_frota_total'].sum()
                    km_parcial_2025 = df_ano_atual['total_km'].sum()
                    num_veiculos_2025 = df_ano_atual['Placa'].nunique()
                    eficiencia_parcial_2025 = df_ano_atual['media_km_litro_ajustado'].mean()
                    dias_uteis_parciais_2025 = df_ano_atual.groupby('mes_ano')['Dias Úteis'].first().sum()

                    # Garantir que a coluna data seja datetime
                    df_ano_atual_copy = df_ano_atual.copy()
                    df_ano_atual_copy['data'] = pd.to_datetime(df_ano_atual_copy['data'], errors='coerce')
                    ultimo_mes_dados = df_ano_atual_copy['data'].dt.month.max()

                    if pd.isna(ultimo_mes_dados) or ultimo_mes_dados == 0:
                        ultimo_mes_dados = 12

                    # Projeções para o ano completo
                    projecao_2025 = (custo_parcial_2025 / ultimo_mes_dados) * 12
                    km_projetado_2025 = (km_parcial_2025 / ultimo_mes_dados) * 12
                    custo_por_km_projetado = projecao_2025 / km_projetado_2025 if km_projetado_2025 > 0 else 0
                    km_medio_veiculo_projetado = km_projetado_2025 / num_veiculos_2025 if num_veiculos_2025 > 0 else 0
                    dias_uteis_projetados = (dias_uteis_parciais_2025 / ultimo_mes_dados) * 12
                    custo_dia_util_projetado = projecao_2025 / dias_uteis_projetados if dias_uteis_projetados > 0 else 0
                    ticket_medio_projetado = projecao_2025 / num_veiculos_2025 if num_veiculos_2025 > 0 else 0

                except Exception as e:
                    projecao_2025 = 0
                    ultimo_mes_dados = 0
                    custo_parcial_2025 = 0
                    km_projetado_2025 = 0
                    custo_por_km_projetado = 0
                    eficiencia_parcial_2025 = 0
                    km_medio_veiculo_projetado = 0
                    custo_dia_util_projetado = 0
                    ticket_medio_projetado = 0

                st.html(f"""
<div class="custom-card card-purple">
    <div class="card-title">{titulo_card}</div>
    <div class="card-value">R$ {projecao_2025:,.2f}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>🛣️ Km Total:</strong> {km_projetado_2025:,.0f} Km
    </div>
    <div class="card-detail">
        <strong>⛽ Eficiência Média:</strong> {eficiencia_parcial_2025:.2f} Km/L
    </div>
    <div class="card-detail">
        <strong>💰 Custo/Km:</strong> R$ {custo_por_km_projetado:.2f}
    </div>
    <div class="card-detail">
        <strong>🚛 Km Médio/Veículo:</strong> {km_medio_veiculo_projetado:,.0f} Km
    </div>
    <div class="card-detail">
        <strong>📅 Custo/Dia Útil:</strong> R$ {custo_dia_util_projetado:,.2f}
    </div>
    <div class="card-detail">
        <strong>🎫 Ticket Médio/Veículo:</strong> R$ {ticket_medio_projetado:,.2f}
    </div>
</div>
                """)
            else:
                st.html(f"""
<div class="custom-card card-purple">
    <div class="card-title">{titulo_card}</div>
    <div class="card-value">N/A</div>
</div>
                """)
            
    st.markdown("---")

    # --- O RESTANTE DA VISÃO RESUMIDA (Análises mensais, por grupo, etc.) ---
    # Essas seções continuam funcionando com base no df_filtrado pelos seletores da interface

    # Cálculos para comparações mensais (baseado no período filtrado)
    if not df_filtrado.empty and 'data' in df_filtrado.columns:
        try:
            # Garantir que a coluna data seja datetime
            df_filtrado_copy = df_filtrado.copy()
            df_filtrado_copy['data'] = pd.to_datetime(df_filtrado_copy['data'], errors='coerce')

            data_max_filtrado = df_filtrado_copy['data'].max()

            if pd.isna(data_max_filtrado):
                # Se não há data válida, usar data atual
                data_max_filtrado = pd.Timestamp.now()

            mes_atual_data = data_max_filtrado.replace(day=1)
            mes_anterior_data = mes_atual_data - relativedelta(months=1)

            # Garantir que df_completo também tenha data como datetime
            df_completo_copy = df_completo.copy()
            df_completo_copy['data'] = pd.to_datetime(df_completo_copy['data'], errors='coerce')

            df_mes_atual = df_completo_copy[df_completo_copy['data'].dt.to_period('M') == mes_atual_data.to_period('M')]
            df_mes_anterior = df_completo_copy[df_completo_copy['data'].dt.to_period('M') == mes_anterior_data.to_period('M')]
        except Exception as e:
            # Em caso de erro, criar DataFrames vazios
            df_mes_atual = pd.DataFrame()
            df_mes_anterior = pd.DataFrame()
            data_max_filtrado = pd.Timestamp.now()
    else:
        df_mes_atual = pd.DataFrame()
        df_mes_anterior = pd.DataFrame()
        data_max_filtrado = pd.Timestamp.now()
    
    colunas_custo = {
        'Combustível': 'custo_combustivel', 'Manutenção': 'custo_manutencao_geral',
        'Pneus': 'custo_rodas_pneus', 'Lataria': 'custo_lataria_pintura', 'Arla': 'custo_arla'
    }

    # Verificar se as colunas existem antes de calcular
    custos_atuais = {}
    custos_anteriores = {}

    for nome, coluna in colunas_custo.items():
        if coluna in df_mes_atual.columns:
            custos_atuais[nome] = df_mes_atual[coluna].sum()
        else:
            custos_atuais[nome] = 0

        if coluna in df_mes_anterior.columns:
            custos_anteriores[nome] = df_mes_anterior[coluna].sum()
        else:
            custos_anteriores[nome] = 0

    def calcular_delta(atual, anterior):
        if anterior > 0: return ((atual - anterior) / anterior) * 100
        elif atual > 0: return 100.0
        return 0.0

    # Verificar se deve mostrar análise mensal ou anual
    mes_selecionado = st.session_state.get('mes_selecionado', 'Todos')

    if mes_selecionado == 'Todos':
        # Análise Anual Comparativa por Categoria de Custo
        st.subheader("Análise Anual Comparativa por Categoria de Custo")

        # Calcular custos por ano para cada categoria
        custos_por_ano = {}
        anos_para_comparar = sorted(df_completo['ano'].unique(), reverse=True)[:3]  # Últimos 3 anos
        anos_para_comparar.reverse()  # Ordem cronológica

        for ano in anos_para_comparar:
            df_ano = df_completo[df_completo['ano'] == ano]
            custos_por_ano[ano] = {}

            if ano == 2025:
                # Para 2025, usar projeções baseadas nos dados parciais
                try:
                    # Garantir que a coluna data seja datetime para 2025
                    df_ano_copy = df_ano.copy()
                    df_ano_copy['data'] = pd.to_datetime(df_ano_copy['data'], errors='coerce')
                    ultimo_mes_2025 = df_ano_copy['data'].dt.month.max()

                    if pd.isna(ultimo_mes_2025) or ultimo_mes_2025 == 0:
                        ultimo_mes_2025 = 12

                    # Calcular projeções para cada categoria
                    for nome, coluna in colunas_custo.items():
                        if coluna in df_ano.columns:
                            custo_parcial = df_ano[coluna].sum()
                            projecao_categoria = (custo_parcial / ultimo_mes_2025) * 12
                            custos_por_ano[ano][nome] = projecao_categoria
                        else:
                            custos_por_ano[ano][nome] = 0
                except Exception as e:
                    # Em caso de erro, usar valores parciais
                    for nome, coluna in colunas_custo.items():
                        if coluna in df_ano.columns:
                            custos_por_ano[ano][nome] = df_ano[coluna].sum()
                        else:
                            custos_por_ano[ano][nome] = 0
            else:
                # Para outros anos, usar valores reais
                for nome, coluna in colunas_custo.items():
                    if coluna in df_ano.columns:
                        custos_por_ano[ano][nome] = df_ano[coluna].sum()
                    else:
                        custos_por_ano[ano][nome] = 0

        cols_variacao = st.columns(len(colunas_custo))
        for i, nome in enumerate(colunas_custo.keys()):
            with cols_variacao[i]:
                # Pegar valores dos anos disponíveis
                valores_anos = [custos_por_ano.get(ano, {}).get(nome, 0) for ano in anos_para_comparar]

                # Calcular variação entre o último e penúltimo ano
                if len(valores_anos) >= 2 and valores_anos[-2] > 0:
                    delta = ((valores_anos[-1] - valores_anos[-2]) / valores_anos[-2]) * 100
                else:
                    delta = 0

                delta_symbol = "▲" if delta >= 0 else "▼"
                delta_color = "#ff4b4b" if delta >= 0 else "#28a745"

                valor_atual = valores_anos[-1] if valores_anos else 0
                valor_atual_str = f"R$ {valor_atual/1000:.0f}k" if valor_atual >= 10000 else f"R$ {valor_atual:,.2f}"

                # Criar detalhes com histórico dos anos
                detalhes_anos = ""
                for j, ano in enumerate(anos_para_comparar):
                    valor = valores_anos[j] if j < len(valores_anos) else 0
                    valor_str = f"R$ {valor/1000:.0f}k" if valor >= 10000 else f"R$ {valor:,.0f}"

                    # Adicionar indicação de projeção para 2025
                    ano_label = f"{ano} (Proj.)" if ano == 2025 else str(ano)

                    if j == 0:  # Primeiro ano, adicionar border-top
                        detalhes_anos += f'<div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;"><strong>{ano_label}:</strong> {valor_str}</div>'
                    else:
                        detalhes_anos += f'<div class="card-detail"><strong>{ano_label}:</strong> {valor_str}</div>'

                st.html(f"""
<div class="custom-card card-yellow" style="min-height: 180px;">
    <div class="card-title">{nome}</div>
    <div class="card-value">{valor_atual_str}</div>
    <div class="card-detail" style="color: {delta_color}; font-weight: bold;">
        {delta_symbol} {abs(delta):.1f}% vs. Ano Anterior
    </div>
    {detalhes_anos}
</div>
                """)
    else:
        # Análise Mensal (comportamento original)
        st.subheader(f"Análise Mensal Detalhada (Base: {data_max_filtrado.strftime('%m/%Y')})")
        cols_variacao = st.columns(len(colunas_custo))
        for i, nome in enumerate(colunas_custo.keys()):
            with cols_variacao[i]:
                valor_atual, valor_anterior = custos_atuais[nome], custos_anteriores[nome]
                delta = calcular_delta(valor_atual, valor_anterior)
                delta_symbol = "▲" if delta >= 0 else "▼"
                delta_color = "#ff4b4b" if delta >= 0 else "#28a745"
                valor_atual_str = f"R$ {valor_atual/1000:.0f}k" if valor_atual >= 10000 else f"R$ {valor_atual:,.2f}"
                valor_anterior_str = f"R$ {valor_anterior/1000:.0f}k" if valor_anterior >= 10000 else f"R$ {valor_anterior:,.2f}"
                st.html(f"""
<div class="custom-card card-yellow" style="min-height: 180px;">
    <div class="card-title">{nome}</div>
    <div class="card-value">{valor_atual_str}</div>
    <div class="card-detail" style="color: {delta_color}; font-weight: bold;">
        {delta_symbol} {abs(delta):.1f}% vs. Mês Ant.
    </div>
    <div class="card-detail">Anterior: {valor_anterior_str}</div>
</div>
                """)
    st.markdown("---")

    # CUSTO MÉDIO POR GRUPO - Responsivo aos filtros
    if 'grupocorreto' in df_filtrado.columns and not df_filtrado.empty:
        # Definir título baseado nos filtros ativos
        ano_selecionado = st.session_state.get('ano_selecionado', 'Todos')
        mes_selecionado = st.session_state.get('mes_selecionado', 'Todos')
        regiao_selecionada = st.session_state.get('regiao_selecionada', 'Todos')
        filial_selecionada = st.session_state.get('filial_selecionada', 'Todos')

        # Construir título dinâmico
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
            titulo_grupo = f"Custo Médio por Grupo de Veículo ({', '.join(filtros_ativos)})"
        else:
            titulo_grupo = "Custo Médio por Grupo de Veículo (Dados Completos)"

        st.subheader(titulo_grupo)

        # Verificar se as colunas necessárias existem
        required_cols = ['custo_frota_total', 'Placa']
        if all(col in df_filtrado.columns for col in required_cols):
            try:
                custo_por_grupo = df_filtrado.groupby('grupocorreto').agg(
                    CustoTotal=('custo_frota_total', 'sum'),
                    NumVeiculos=('Placa', 'nunique')
                ).reset_index()

                # Cálculo seguro do custo médio
                def calcular_custo_medio(row):
                    if row['NumVeiculos'] > 0:
                        return row['CustoTotal'] / row['NumVeiculos']
                    return 0

                custo_por_grupo['CustoMedio'] = custo_por_grupo.apply(calcular_custo_medio, axis=1)
            except Exception as e:
                custo_por_grupo = pd.DataFrame()
        else:
            custo_por_grupo = pd.DataFrame()
        def get_grupo_info(grupo):
            grupo_lower = str(grupo).lower()
            if 'leve' in grupo_lower: return '🚗', 1
            elif 'médio' in grupo_lower or 'medio' in grupo_lower: return '🚐', 2
            elif 'pesado' in grupo_lower: return '🚚', 3
            elif 'caminhão' in grupo_lower or 'caminhao' in grupo_lower: return '🚛', 4
            else: return '🚙', 5
        custo_por_grupo['emoji'] = custo_por_grupo['grupocorreto'].apply(lambda x: get_grupo_info(x)[0])
        custo_por_grupo['ordem'] = custo_por_grupo['grupocorreto'].apply(lambda x: get_grupo_info(x)[1])
        custo_por_grupo = custo_por_grupo.sort_values('ordem')
        if not custo_por_grupo.empty:
            # Limitar o número de colunas para evitar problemas de layout
            num_grupos = len(custo_por_grupo)
            max_colunas = min(num_grupos, 5)  # Máximo 5 colunas
            cols_grupos = st.columns(max_colunas)

            for i, (idx, row) in enumerate(custo_por_grupo.iterrows()):
                with cols_grupos[i % max_colunas]:
                    # Cálculos adicionais para o grupo
                    df_grupo = df_filtrado[df_filtrado['grupocorreto'] == row['grupocorreto']]

                    # Formatação dos valores
                    custo_total_str = f"R$ {row['CustoTotal']/1000:.0f}k" if row['CustoTotal'] >= 10000 else f"R$ {row['CustoTotal']:,.2f}"
                    custo_medio_str = f"R$ {row['CustoMedio']/1000:.1f}k" if row['CustoMedio'] >= 10000 else f"R$ {row['CustoMedio']:,.2f}"

                    # Informações adicionais
                    try:
                        km_total_grupo = df_grupo['total_km'].sum() if 'total_km' in df_grupo.columns else 0
                        km_por_veiculo = km_total_grupo / row['NumVeiculos'] if row['NumVeiculos'] > 0 else 0
                        custo_por_km = row['CustoTotal'] / km_total_grupo if km_total_grupo > 0 else 0

                        km_total_str = f"{km_total_grupo:,.0f} Km" if km_total_grupo > 0 else "N/A"
                        km_veiculo_str = f"{km_por_veiculo:,.0f} Km/Veículo" if km_por_veiculo > 0 else "N/A"
                        custo_km_str = f"R$ {custo_por_km:.2f}/Km" if custo_por_km > 0 else "N/A"
                    except:
                        km_total_str = "N/A"
                        km_veiculo_str = "N/A"
                        custo_km_str = "N/A"

                    st.html(f"""
<div class="custom-card card-orange">
    <div class="card-title">{row['emoji']} {row['grupocorreto']}</div>
    <div class="card-value">{custo_medio_str}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>🚛 Veículos:</strong> {row['NumVeiculos']}
    </div>
    <div class="card-detail">
        <strong>💰 Total:</strong> {custo_total_str}
    </div>
    <div class="card-detail">
        <strong>🛣️ Km Total:</strong> {km_total_str}
    </div>
    <div class="card-detail">
        <strong>📊 Km/Veículo:</strong> {km_veiculo_str}
    </div>
    <div class="card-detail">
        <strong>💸 Custo/Km:</strong> {custo_km_str}
    </div>
</div>
                    """)
        st.markdown("---")

    # ANÁLISE POR FILIAL - Responsiva aos filtros
    # Construir título dinâmico para filiais
    filtros_filial = []
    if ano_selecionado != 'Todos':
        filtros_filial.append(f"Ano {ano_selecionado}")
    if mes_selecionado != 'Todos':
        filtros_filial.append(f"Mês {mes_selecionado}")
    if regiao_selecionada != 'Todos':
        filtros_filial.append(f"Região {regiao_selecionada}")

    if filtros_filial:
        titulo_filial = f"Análise Detalhada por Filial ({', '.join(filtros_filial)})"
    else:
        titulo_filial = "Análise Detalhada por Filial (Dados Completos)"

    st.subheader(titulo_filial)

    if 'filial' in df_filtrado.columns and 'custo_frota_total' in df_filtrado.columns and not df_filtrado.empty:
        try:
            gastos_por_filial = df_filtrado.groupby('filial')['custo_frota_total'].sum().sort_values(ascending=False)

            if not gastos_por_filial.empty:
                num_colunas = 3
                cols = st.columns(num_colunas)

                for i, (filial_nome, custo_total_filial) in enumerate(gastos_por_filial.items()):
                    with cols[i % num_colunas]:
                        df_da_filial = df_filtrado[df_filtrado['filial'] == filial_nome]

                        # Cálculos dos KPIs da filial (similar à análise anual)
                        try:
                            num_veiculos_filial = df_da_filial['Placa'].nunique() if 'Placa' in df_da_filial.columns else 0
                            total_km_filial = df_da_filial['total_km'].sum() if 'total_km' in df_da_filial.columns else 0
                            total_dias_uteis_filial = df_da_filial.groupby('mes_ano')['Dias Úteis'].first().sum() if 'Dias Úteis' in df_da_filial.columns else 0

                            # Cálculos derivados
                            custo_por_km_filial = custo_total_filial / total_km_filial if total_km_filial > 0 else 0
                            eficiencia_media_filial = df_da_filial['media_km_litro_ajustado'].mean() if 'media_km_litro_ajustado' in df_da_filial.columns else 0
                            km_medio_por_veiculo_filial = total_km_filial / num_veiculos_filial if num_veiculos_filial > 0 else 0
                            custo_dia_util_filial = custo_total_filial / total_dias_uteis_filial if total_dias_uteis_filial > 0 else 0
                            ticket_medio_por_veiculo_filial = custo_total_filial / num_veiculos_filial if num_veiculos_filial > 0 else 0

                            # Formatação dos valores
                            total_km_str = f"{total_km_filial:,.0f}" if total_km_filial > 0 else "0"
                            eficiencia_str = f"{eficiencia_media_filial:.2f}" if eficiencia_media_filial > 0 else "N/A"
                            custo_km_str = f"{custo_por_km_filial:.2f}" if custo_por_km_filial > 0 else "0.00"
                            km_veiculo_str = f"{km_medio_por_veiculo_filial:,.0f}" if km_medio_por_veiculo_filial > 0 else "0"
                            custo_dia_str = f"{custo_dia_util_filial:,.2f}" if custo_dia_util_filial > 0 else "0.00"
                            ticket_str = f"{ticket_medio_por_veiculo_filial:,.2f}" if ticket_medio_por_veiculo_filial > 0 else "0.00"

                        except Exception as e:
                            num_veiculos_filial = 0
                            total_km_str = "N/A"
                            eficiencia_str = "N/A"
                            custo_km_str = "N/A"
                            km_veiculo_str = "N/A"
                            custo_dia_str = "N/A"
                            ticket_str = "N/A"

                        st.html(f"""
<div class="custom-card card-blue">
    <div class="card-title">🏢 {filial_nome}</div>
    <div class="card-value">R$ {custo_total_filial:,.2f}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>🛣️ Km Total:</strong> {total_km_str} Km
    </div>
    <div class="card-detail">
        <strong>⛽ Eficiência Média:</strong> {eficiencia_str} Km/L
    </div>
    <div class="card-detail">
        <strong>💰 Custo/Km:</strong> R$ {custo_km_str}
    </div>
    <div class="card-detail">
        <strong>🚛 Km Médio/Veículo:</strong> {km_veiculo_str} Km
    </div>
    <div class="card-detail">
        <strong>📅 Custo/Dia Útil:</strong> R$ {custo_dia_str}
    </div>
    <div class="card-detail">
        <strong>🎫 Ticket Médio/Veículo:</strong> R$ {ticket_str}
    </div>
</div>
                        """)
        except Exception as e:
            st.warning("Erro ao processar análise por filial.")
    else:
        st.info("Dados insuficientes para análise por filial.")

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

def exibir_panorama_filiais(df_filtrado):
    """
    Análise panorâmica das filiais em formato de tabela interativa rica
    com formatação condicional e gráficos de comparação integrados.
    """
    st.subheader("🏢 Panorama Geral das Filiais - Tabela Comparativa Interativa")

    if df_filtrado.empty or 'filial' not in df_filtrado.columns:
        st.warning("Dados insuficientes para análise de filiais.")
        return

    # --- PREPARAÇÃO DOS DADOS POR FILIAL ---
    dados_filiais = df_filtrado.groupby('filial').agg(
        # Custos detalhados
        custo_total=('custo_frota_total', 'sum'),
        custo_manutencao=('custo_manutencao_geral', 'sum'),
        custo_combustivel=('custo_combustivel', 'sum'),
        custo_lataria=('custo_lataria_pintura', 'sum'),
        custo_pneus=('custo_rodas_pneus', 'sum'),
        custo_arla=('custo_arla', 'sum'),
        # Métricas operacionais
        num_veiculos=('Placa', 'nunique'),
        total_km=('total_km', 'sum'),
        total_dias_uteis=('Dias Úteis', 'sum'),
        eficiencia_media=('media_km_litro_ajustado', 'mean')
    ).reset_index()

    # Cálculos derivados
    dados_filiais['custo_por_km'] = dados_filiais['custo_total'] / dados_filiais['total_km']
    dados_filiais['km_medio_veiculo'] = dados_filiais['total_km'] / dados_filiais['num_veiculos']
    dados_filiais['custo_dia_util'] = dados_filiais['custo_total'] / dados_filiais['total_dias_uteis']
    dados_filiais['ticket_medio_veiculo'] = dados_filiais['custo_total'] / dados_filiais['num_veiculos']

    # Tratar valores infinitos e NaN
    dados_filiais = dados_filiais.replace([np.inf, -np.inf], 0).fillna(0)

    # Adicionar grupos de veículos mais comuns por filial
    if 'grupocorreto' in df_filtrado.columns:
        grupos_por_filial = df_filtrado.groupby('filial')['grupocorreto'].apply(
            lambda x: x.value_counts().index[0] if not x.empty else 'N/A'
        ).to_dict()
        dados_filiais['grupo_principal'] = dados_filiais['filial'].map(grupos_por_filial)
    else:
        dados_filiais['grupo_principal'] = 'N/A'

    # Calcular rankings para cada métrica
    dados_filiais['rank_custo_total'] = dados_filiais['custo_total'].rank(ascending=False, method='min').astype(int)
    dados_filiais['rank_custo_km'] = dados_filiais['custo_por_km'].rank(ascending=True, method='min').astype(int)  # Menor é melhor
    dados_filiais['rank_eficiencia'] = dados_filiais['eficiencia_media'].rank(ascending=False, method='min').astype(int)
    dados_filiais['rank_frota'] = dados_filiais['num_veiculos'].rank(ascending=False, method='min').astype(int)

    # Ordenar por custo total (padrão)
    dados_filiais = dados_filiais.sort_values('custo_total', ascending=False)


    # Preparar dados para a tabela
    tabela_comparativa = dados_filiais.copy()

    # Renomear colunas para exibição (apenas informações mais úteis)
    tabela_display = tabela_comparativa[[
        'filial', 'custo_total', 'custo_por_km', 'num_veiculos', 'eficiencia_media',
        'ticket_medio_veiculo', 'total_km'
    ]].rename(columns={
        'filial': '🏢 Filial',
        'custo_total': '💰 Custo Total',
        'custo_por_km': '⚡ Custo/Km',
        'num_veiculos': '🚛 Veículos',
        'eficiencia_media': '⛽ Km/L',
        'ticket_medio_veiculo': '🎫 Ticket Médio',
        'total_km': '🛣️ Total Km'
    })

    # Configuração da tabela simplificada
    st.dataframe(
        tabela_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "💰 Custo Total": st.column_config.NumberColumn(format="R$ %.2f"),
            "⚡ Custo/Km": st.column_config.NumberColumn(format="R$ %.2f"),
            "🚛 Veículos": st.column_config.NumberColumn(format="%d"),
            "⛽ Km/L": st.column_config.NumberColumn(format="%.2f Km/L"),
            "🎫 Ticket Médio": st.column_config.NumberColumn(format="R$ %.2f"),
            "🛣️ Total Km": st.column_config.NumberColumn(format="%.0f Km")
        }
    )
    st.markdown("---")
    # --- INSIGHTS E ANÁLISES INCREMENTADOS ---
    st.markdown("### 🔍- Insights e Análises Avançadas")

    # Cards de insights fixos (sempre 4)
    cols_insights = st.columns(4)

    # Top performers baseado no número de filiais disponíveis
    with cols_insights[0]:
        melhor_eficiencia = dados_filiais.loc[dados_filiais['custo_por_km'].idxmin()]
        economia_potencial = (dados_filiais['custo_por_km'].max() - melhor_eficiencia['custo_por_km']) * dados_filiais['total_km'].sum()
        st.html(f"""
<div class="custom-card card-green" style="min-height: 180px;">
    <div class="card-title">⚡ Filial Mais Eficiente</div>
    <div class="card-value" style="font-size: 18px;">{melhor_eficiencia['filial']}</div>
    <div class="card-detail">💰 R$ {melhor_eficiencia['custo_por_km']:.2f}/Km</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>💡 Economia potencial:</strong> R$ {economia_potencial:,.0f}
    </div>
</div>
        """)

    with cols_insights[1]:
        melhor_combustivel = dados_filiais.loc[dados_filiais['eficiencia_media'].idxmax()]
        diferenca_eficiencia = melhor_combustivel['eficiencia_media'] - dados_filiais['eficiencia_media'].min()
        st.html(f"""
<div class="custom-card card-yellow" style="min-height: 180px;">
    <div class="card-title">⛽ Melhor Eficiência Combustível</div>
    <div class="card-value" style="font-size: 18px;">{melhor_combustivel['filial']}</div>
    <div class="card-detail">⛽ {melhor_combustivel['eficiencia_media']:.2f} Km/L</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>📈 {diferenca_eficiencia:.2f} Km/L</strong> acima da menor
    </div>
</div>
        """)

    with cols_insights[2]:
        maior_frota = dados_filiais.loc[dados_filiais['num_veiculos'].idxmax()]
        percentual_frota = (maior_frota['num_veiculos'] / dados_filiais['num_veiculos'].sum()) * 100
        st.html(f"""
<div class="custom-card card-blue" style="min-height: 180px;">
    <div class="card-title">🚛 Maior Frota</div>
    <div class="card-value" style="font-size: 18px;">{maior_frota['filial']}</div>
    <div class="card-detail">🚛 {int(maior_frota['num_veiculos'])} veículos</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>📊 {percentual_frota:.1f}%</strong> da frota total
    </div>
</div>
        """)

    with cols_insights[3]:
        maior_custo = dados_filiais.iloc[0]  # Já ordenado por custo total
        percentual_custo = (maior_custo['custo_total'] / dados_filiais['custo_total'].sum()) * 100
        st.html(f"""
<div class="custom-card card-orange" style="min-height: 180px;">
    <div class="card-title">💰 Maior Operação</div>
    <div class="card-value" style="font-size: 18px;">{maior_custo['filial']}</div>
    <div class="card-detail">💰 R$ {maior_custo['custo_total']/1000:.0f}k</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>📊 {percentual_custo:.1f}%</strong> do custo total
    </div>
</div>
        """)



    # --- OPÇÃO 1: CARDS COMPARATIVOS LADO A LADO ---
    st.markdown("### 🎴 Cards Comparativos por Filial")

    # Obter filtros superiores atuais
    filtros_superiores_atuais = {
        'ano': st.session_state.get('ano_selecionado', 'Todos'),
        'mes': st.session_state.get('mes_selecionado', 'Todos'),
        'regiao': st.session_state.get('regiao_selecionada', 'Todos'),
        'filial': st.session_state.get('filial_selecionada', 'Todos')
    }

    # Verificar se os filtros superiores mudaram
    filtros_anteriores = st.session_state.get('filtros_superiores_opcao1', {})
    filtros_mudaram = filtros_superiores_atuais != filtros_anteriores

    # Atualizar filtros salvos
    st.session_state.filtros_superiores_opcao1 = filtros_superiores_atuais

    # Filtro de seleção de filiais com padrão top 3
    todas_filiais = dados_filiais['filial'].tolist()
    top_3_filiais = dados_filiais.head(3)['filial'].tolist()  # Top 3 por custo total (já ordenado)

    # Se os filtros superiores mudaram, resetar para o padrão
    if filtros_mudaram:
        filiais_default = top_3_filiais
        # Limpar cache do multiselect se existir
        if 'filiais_opcao1_selecionadas' in st.session_state:
            del st.session_state.filiais_opcao1_selecionadas
    else:
        # Manter seleção anterior ou usar padrão
        filiais_default = st.session_state.get('filiais_opcao1_selecionadas', top_3_filiais)

    filiais_selecionadas = st.multiselect(
        "🏢 Selecione as filiais para comparação:",
        options=todas_filiais,
        default=filiais_default,
        help="Por padrão, as 3 filiais com maior custo total estão selecionadas. Os filtros superiores resetam esta seleção.",
        key='filiais_opcao1_selecionadas'
    )

    if not filiais_selecionadas:
        st.warning("Selecione pelo menos uma filial para exibir os cards comparativos.")
        dados_filiais_filtradas = dados_filiais.head(0)  # DataFrame vazio
    else:
        dados_filiais_filtradas = dados_filiais[dados_filiais['filial'].isin(filiais_selecionadas)]

    # Determinar número de colunas baseado no número de filiais selecionadas
    num_filiais = len(dados_filiais_filtradas)
    if num_filiais <= 4:
        cols_cards = st.columns(num_filiais) if num_filiais > 0 else st.columns(1)
    else:
        # Para mais de 4 filiais, usar 4 colunas e quebrar linha
        cols_cards = st.columns(4)

    # Criar cards para as filiais selecionadas
    for i, (idx, filial_data) in enumerate(dados_filiais_filtradas.iterrows()):
        # Determinar qual coluna usar baseado no número de filiais
        if num_filiais <= 4:
            # Se há 4 ou menos filiais, usar todas as colunas disponíveis
            coluna_atual = i
        else:
            # Se há mais de 4 filiais, usar módulo para quebrar linha
            coluna_atual = i % 4

        # Primeira linha (primeiras 4 filiais ou todas se <= 4)
        if i < 4:
            with cols_cards[coluna_atual]:
                filial_nome = filial_data['filial']

                # Determinar cor do card baseado na performance (custo/km)
                if filial_data['custo_por_km'] <= dados_filiais_filtradas['custo_por_km'].quantile(0.33):
                    cor_card = 'card-green'  # Eficiente
                elif filial_data['custo_por_km'] <= dados_filiais_filtradas['custo_por_km'].quantile(0.66):
                    cor_card = 'card-yellow'  # Médio
                else:
                    cor_card = 'card-orange'  # Alto custo

                # Cálculo da posição no ranking
                posicao_ranking = i + 1
                emoji_ranking = "🥇" if posicao_ranking == 1 else "🥈" if posicao_ranking == 2 else "🥉" if posicao_ranking == 3 else f"#{posicao_ranking}"

                st.html(f"""
<div class="custom-card {cor_card}" style="min-height: 380px;">
    <div class="card-title">🏢 {filial_nome}</div>
    <div class="card-value" style="font-size: 24px;">{emoji_ranking} Ranking</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>💰 Custo Total:</strong> R$ {filial_data['custo_total']:,.0f}
    </div>
    <div class="card-detail">
        <strong>💸 Custo/Km:</strong> R$ {filial_data['custo_por_km']:.2f}
    </div>
    <div class="card-detail">
        <strong>🚛 Veículos:</strong> {int(filial_data['num_veiculos'])}
    </div>
    <div class="card-detail">
        <strong>🛣️ Total Km:</strong> {filial_data['total_km']:,.0f}
    </div>
    <div class="card-detail">
        <strong>⛽ Km/L:</strong> {filial_data['eficiencia_media']:.2f}
    </div>
    <div class="card-detail">
        <strong>🎫 Ticket Médio:</strong> R$ {filial_data['ticket_medio_veiculo']:,.0f}
    </div>
    <div class="card-detail">
        <strong>📅 Custo/Dia:</strong> R$ {filial_data['custo_dia_util']:,.0f}
    </div>
</div>
                """)

    # Segunda linha se necessário (mais de 4 filiais)
    if num_filiais > 4:
        # Criar nova linha de colunas para as filiais restantes
        filiais_restantes = num_filiais - 4
        cols_cards_2 = st.columns(min(4, filiais_restantes))

        for i, (idx, filial_data) in enumerate(list(dados_filiais_filtradas.iterrows())[4:]):
            if i < len(cols_cards_2):  # Verificação de segurança
                with cols_cards_2[i]:
                    filial_nome = filial_data['filial']

                    if filial_data['custo_por_km'] <= dados_filiais_filtradas['custo_por_km'].quantile(0.33):
                        cor_card = 'card-green'
                    elif filial_data['custo_por_km'] <= dados_filiais_filtradas['custo_por_km'].quantile(0.66):
                        cor_card = 'card-yellow'
                    else:
                        cor_card = 'card-orange'

                    posicao_ranking = i + 5  # +5 porque esta é a segunda linha
                    emoji_ranking = f"#{posicao_ranking}"

                    st.html(f"""
<div class="custom-card {cor_card}" style="min-height: 380px;">
    <div class="card-title">🏢 {filial_nome}</div>
    <div class="card-value" style="font-size: 24px;">{emoji_ranking} Ranking</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>💰 Custo Total:</strong> R$ {filial_data['custo_total']:,.0f}
    </div>
    <div class="card-detail">
        <strong>💸 Custo/Km:</strong> R$ {filial_data['custo_por_km']:.2f}
    </div>
    <div class="card-detail">
        <strong>🚛 Veículos:</strong> {int(filial_data['num_veiculos'])}
    </div>
    <div class="card-detail">
        <strong>🛣️ Total Km:</strong> {filial_data['total_km']:,.0f}
    </div>
    <div class="card-detail">
        <strong>⛽ Km/L:</strong> {filial_data['eficiencia_media']:.2f}
    </div>
    <div class="card-detail">
        <strong>🎫 Ticket Médio:</strong> R$ {filial_data['ticket_medio_veiculo']:,.0f}
    </div>
    <div class="card-detail">
        <strong>📅 Custo/Dia:</strong> R$ {filial_data['custo_dia_util']:,.0f}
    </div>
</div>
                    """)

    # --- ANÁLISE POR GRUPO DE VEÍCULOS ---
    st.markdown("### 🚗 **Análise por Grupo de Veículos**")
    st.markdown("*Análise consolidada baseada nos filtros selecionados*")

    if 'grupocorreto' in df_filtrado.columns:
        # Calcular dados por grupo de veículos (consolidado)
        dados_grupo_consolidado = df_filtrado.groupby('grupocorreto').agg(
            custo_total=('custo_frota_total', 'sum'),
            total_km=('total_km', 'sum'),
            num_veiculos=('Placa', 'nunique'),
            eficiencia_media=('media_km_litro_ajustado', 'mean'),
            custo_manutencao=('custo_manutencao_geral', 'sum'),
            custo_combustivel=('custo_combustivel', 'sum')
        ).reset_index()

        # Calcular métricas derivadas
        dados_grupo_consolidado['custo_por_km'] = dados_grupo_consolidado['custo_total'] / dados_grupo_consolidado['total_km']
        dados_grupo_consolidado['ticket_medio'] = dados_grupo_consolidado['custo_total'] / dados_grupo_consolidado['num_veiculos']
        dados_grupo_consolidado['km_medio_veiculo'] = dados_grupo_consolidado['total_km'] / dados_grupo_consolidado['num_veiculos']
        dados_grupo_consolidado = dados_grupo_consolidado.replace([np.inf, -np.inf], 0).fillna(0)
        dados_grupo_consolidado = dados_grupo_consolidado.sort_values('custo_total', ascending=False)

        # Cards resumo por grupo (Top 4)
        st.markdown("#### 📊 **Top 4 Grupos por Custo Total**")

        top_4_grupos = dados_grupo_consolidado.head(4)
        cols_grupos = st.columns(4)

        for i, (idx, grupo_data) in enumerate(top_4_grupos.iterrows()):
            with cols_grupos[i]:
                # Determinar cor baseada na eficiência de custo/km
                if grupo_data['custo_por_km'] <= dados_grupo_consolidado['custo_por_km'].quantile(0.33):
                    cor_card = 'card-green'
                elif grupo_data['custo_por_km'] <= dados_grupo_consolidado['custo_por_km'].quantile(0.66):
                    cor_card = 'card-yellow'
                else:
                    cor_card = 'card-orange'

                posicao = i + 1
                emoji_pos = "🥇" if posicao == 1 else "🥈" if posicao == 2 else "🥉" if posicao == 3 else "🏆"

                st.html(f"""
<div class="custom-card {cor_card}" style="min-height: 300px;">
    <div class="card-title">🚗 {grupo_data['grupocorreto']}</div>
    <div class="card-value" style="font-size: 20px;">{emoji_pos} #{posicao}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>💰 Custo Total:</strong> R$ {grupo_data['custo_total']:,.0f}
    </div>
    <div class="card-detail">
        <strong>💸 Custo/Km:</strong> R$ {grupo_data['custo_por_km']:.2f}
    </div>
    <div class="card-detail">
        <strong>🚛 Veículos:</strong> {int(grupo_data['num_veiculos'])}
    </div>
    <div class="card-detail">
        <strong>🛣️ Total Km:</strong> {grupo_data['total_km']:,.0f}
    </div>
    <div class="card-detail">
        <strong>⛽ Km/L:</strong> {grupo_data['eficiencia_media']:.2f}
    </div>
    <div class="card-detail">
        <strong>🎫 Ticket Médio:</strong> R$ {grupo_data['ticket_medio']:,.0f}
    </div>
</div>
                """)


        # Análise Consolidada por Grupo de Veículo
        st.markdown("#### 📊 **Análise Consolidada por Grupo de Veículo**")

        # Cards de métricas resumo usando nosso CSS
        total_grupos = len(dados_grupo_consolidado)
        custo_total_geral = dados_grupo_consolidado['custo_total'].sum()
        grupo_mais_custoso = dados_grupo_consolidado.iloc[0]['grupocorreto']
        eficiencia_media_geral = dados_grupo_consolidado['eficiencia_media'].mean()

        cols_resumo = st.columns(4)

        with cols_resumo[0]:
            st.html(f"""
<div class="custom-card card-blue">
    <div class="card-title">📈 Total de Grupos</div>
    <div class="card-value">{total_grupos}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>Categorias analisadas</strong> no período
    </div>
</div>
            """)

        with cols_resumo[1]:
            st.html(f"""
<div class="custom-card card-green">
    <div class="card-title">💰 Custo Total Geral</div>
    <div class="card-value">R$ {custo_total_geral:,.0f}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>Soma consolidada</strong> de todos os grupos
    </div>
</div>
            """)

        with cols_resumo[2]:
            st.html(f"""
<div class="custom-card card-orange">
    <div class="card-title">🥇 Grupo Mais Custoso</div>
    <div class="card-value" style="font-size: 24px;">{grupo_mais_custoso}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>Líder em custos</strong> no período
    </div>
</div>
            """)

        with cols_resumo[3]:
            st.html(f"""
<div class="custom-card card-yellow">
    <div class="card-title">⛽ Eficiência Média</div>
    <div class="card-value">{eficiencia_media_geral:.2f} Km/L</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>Performance geral</strong> de combustível
    </div>
</div>
            """)

        # Filtros de controle
        col_filtro1, col_filtro2 = st.columns([3, 1])

        with col_filtro1:
            tipo_ordenacao = st.selectbox(
                "🎯 Ordenar tabela por:",
                options=[
                    ("custo_total", "💰 Custo Total (Maior → Menor)"),
                    ("custo_por_km", "💸 Custo/Km (Menor → Maior)"),
                    ("eficiencia_media", "⛽ Eficiência (Maior → Menor)"),
                    ("num_veiculos", "🚛 Número de Veículos (Maior → Menor)")
                ],
                format_func=lambda x: x[1]
            )

        with col_filtro2:
            mostrar_top = st.selectbox(
                "📊 Exibir:",
                options=[("todos", "Todos"), ("5", "Top 5"), ("10", "Top 10")],
                format_func=lambda x: x[1]
            )

        # Aplicar filtros
        coluna_ordenacao, _ = tipo_ordenacao
        ascending = coluna_ordenacao == "custo_por_km"
        dados_ordenados = dados_grupo_consolidado.sort_values(coluna_ordenacao, ascending=ascending)

        if mostrar_top[0] != "todos":
            dados_ordenados = dados_ordenados.head(int(mostrar_top[0]))

        # Tabela consolidada
        tabela_grupos_display = dados_ordenados.rename(columns={
            'grupocorreto': '🚗 Grupo de Veículo',
            'custo_total': '💰 Custo Total',
            'custo_por_km': '💸 Custo/Km',
            'num_veiculos': '🚛 Veículos',
            'total_km': '🛣️ Total Km',
            'eficiencia_media': '⛽ Km/L',
            'ticket_medio': '🎫 Ticket Médio'
        })

        st.dataframe(
            tabela_grupos_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "💰 Custo Total": st.column_config.NumberColumn(format="R$ %.0f"),
                "💸 Custo/Km": st.column_config.NumberColumn(format="R$ %.2f"),
                "🚛 Veículos": st.column_config.NumberColumn(format="%d"),
                "🛣️ Total Km": st.column_config.NumberColumn(format="%.0f"),
                "⛽ Km/L": st.column_config.NumberColumn(format="%.2f"),
                "🎫 Ticket Médio": st.column_config.NumberColumn(format="R$ %.0f")
            }
        )

        # Insights com cards
        st.markdown("##### 💡 **Insights da Análise**")

        grupo_mais_eficiente = dados_grupo_consolidado.loc[dados_grupo_consolidado['custo_por_km'].idxmin()]
        grupo_menos_eficiente = dados_grupo_consolidado.loc[dados_grupo_consolidado['custo_por_km'].idxmax()]
        melhor_combustivel = dados_grupo_consolidado.loc[dados_grupo_consolidado['eficiencia_media'].idxmax()]

        cols_insights = st.columns(3)

        with cols_insights[0]:
            st.html(f"""
<div class="custom-card card-green">
    <div class="card-title">🎯 Mais Eficiente</div>
    <div class="card-value" style="font-size: 20px;">{grupo_mais_eficiente['grupocorreto']}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>💸 Custo/Km:</strong> R$ {grupo_mais_eficiente['custo_por_km']:.2f}
    </div>
    <div class="card-detail">
        <strong>🚛 Veículos:</strong> {int(grupo_mais_eficiente['num_veiculos'])}
    </div>
</div>
            """)

        with cols_insights[1]:
            st.html(f"""
<div class="custom-card card-orange">
    <div class="card-title">💸 Menos Eficiente</div>
    <div class="card-value" style="font-size: 20px;">{grupo_menos_eficiente['grupocorreto']}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>💸 Custo/Km:</strong> R$ {grupo_menos_eficiente['custo_por_km']:.2f}
    </div>
    <div class="card-detail">
        <strong>📈 Diferença:</strong> {((grupo_menos_eficiente['custo_por_km']/grupo_mais_eficiente['custo_por_km'] - 1)*100):.1f}% maior
    </div>
</div>
            """)

        with cols_insights[2]:
            st.html(f"""
<div class="custom-card card-yellow">
    <div class="card-title">⛽ Melhor Combustível</div>
    <div class="card-value" style="font-size: 20px;">{melhor_combustivel['grupocorreto']}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>⛽ Eficiência:</strong> {melhor_combustivel['eficiencia_media']:.2f} Km/L
    </div>
    <div class="card-detail">
        <strong>💰 Custo Total:</strong> R$ {melhor_combustivel['custo_total']:,.0f}
    </div>
</div>
            """)

    else:
        st.warning("⚠️ Coluna 'grupocorreto' não encontrada nos dados. Análise por grupo de veículos indisponível.")

    st.markdown("---")

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

        # --- Diversidade de Contratos ---
        contratos_unicos = df_filtrado['contrato_agrupado'].nunique()
        kpis['diversidade_categorias'] = contratos_unicos

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
    """Exibe KPIs operacionais organizados por categorias com layout padronizado"""

    kpis = calcular_kpis_operacionais(df_filtrado)

    st.markdown("---")

    # === CATEGORIA 1: INDICADORES FINANCEIROS (Amarelo) ===
    st.markdown("### 💰 **Indicadores Financeiros**")
    cols_financeiros = st.columns(5)

    with cols_financeiros[0]:
        valor_custo_km = kpis.get('custo_por_km', 0)
        st.html(f"""
<div class="custom-card card-yellow">
    <div class="card-title">💰 Custo por Km</div>
    <div class="card-value">R$ {valor_custo_km:.2f}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>Base:</strong> Custo total / Km rodados
    </div>
</div>
        """)

    with cols_financeiros[1]:
        valor_custo_dia = kpis.get('custo_por_dia_util', 0)
        dias_operacao = kpis.get('total_dias_operacao', 0)
        st.html(f"""
<div class="custom-card card-yellow">
    <div class="card-title">📅 Custo/Dia Útil</div>
    <div class="card-value">R$ {valor_custo_dia:,.2f}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>Dias úteis no período:</strong> {dias_operacao}
    </div>
</div>
        """)

    with cols_financeiros[2]:
        valor_manutencao_km = kpis.get('media_manutencao_por_km', 0)
        st.html(f"""
<div class="custom-card card-yellow">
    <div class="card-title">🔧 Manutenção/Km</div>
    <div class="card-value">R$ {valor_manutencao_km:.2f}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>Base:</strong> Custo de manutenção por Km rodado
    </div>
</div>
        """)

    with cols_financeiros[3]:
        valor_km_medio = kpis.get('km_medio_por_veiculo', 0)
        total_km = kpis.get('total_km_frota', 0)
        st.html(f"""
<div class="custom-card card-yellow">
    <div class="card-title">🚛 Km Médio/Veículo</div>
    <div class="card-value">{valor_km_medio:,.0f} Km</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>Total Frota:</strong> {total_km:,.0f} Km
    </div>
</div>
        """)

    with cols_financeiros[4]:
        eficiencia_media = kpis.get('media_km_por_litro', 0)
        melhor_veiculo = kpis.get('melhor_eficiencia_veiculo', 'N/A')
        melhor_valor = kpis.get('melhor_eficiencia_valor', 0)
        st.html(f"""
<div class="custom-card card-yellow">
    <div class="card-title">⛽ Eficiência Combustível</div>
    <div class="card-value">{eficiencia_media:.2f} Km/L</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>📈 Melhor:</strong> {melhor_veiculo} ({melhor_valor:.2f})
    </div>
</div>
        """)

    st.markdown("---")

    # === CATEGORIA 2: INDICADORES DE CONTRATOS (Azul) ===
    st.markdown("### 📋 **Indicadores de Contratos**")
    cols_contratos = st.columns(3)

    with cols_contratos[0]:
        total_categorias = kpis.get('diversidade_categorias', 0)
        st.html(f"""
<div class="custom-card card-blue">
    <div class="card-title">📑 Diversidade de Contratos</div>
    <div class="card-value">{total_categorias}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>Base:</strong> Categorias de contrato ativas no período
    </div>
</div>
        """)

    with cols_contratos[1]:
        contrato_maior = kpis.get('contrato_maior_custo', 'N/A')
        custo_maior = kpis.get('custo_contrato_maior', 0)
        st.html(f"""
<div class="custom-card card-blue">
    <div class="card-title">📋 Contrato de Maior Custo</div>
    <div class="card-value">{contrato_maior}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>Valor:</strong> R$ {custo_maior:,.2f}
    </div>
</div>
        """)

    with cols_contratos[2]:
        contrato_ativo = kpis.get('contrato_mais_ativo', 'N/A')
        num_veiculos_ativo = kpis.get('num_veiculos_mais_ativo', 0)
        st.html(f"""
<div class="custom-card card-blue">
    <div class="card-title">📊 Contrato Mais Ativo</div>
    <div class="card-value">{contrato_ativo}</div>
    <div class="card-detail" style="border-top: 1px solid #4a4e69; padding-top: 8px;">
        <strong>Utilizou:</strong> {int(num_veiculos_ativo)} veículos
    </div>
</div>
        """)

