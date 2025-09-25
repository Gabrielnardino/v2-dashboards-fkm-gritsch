import os
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime

def clean_col_names(df):
    cols = df.columns
    new_cols = [col.strip().replace('  ', ' ') for col in cols]
    df.columns = new_cols
    return df

def limpar_dados_combustivel(df):
    """Padroniza os tipos de combustível"""
    if 'TP.Comb' not in df.columns:
        return df
    
    # Converter para string e limpar espaços
    df['TP.Comb'] = df['TP.Comb'].astype(str).str.strip().str.upper()
    
    # Mapeamento para padronização
    mapeamento_combustivel = {
        'GASOLINA': 'Gasolina',
        'GASOLINA E ETANOL': 'Gasolina',
        'GASOLINAEEETANOL': 'Gasolina',
        'GASOLINAEEETANOL': 'Gasolina',
        'ETANOL': 'Gasolina',
        'DIESEL': 'Diesel',
        'DÍESEL': 'Diesel',
        'DIESEL S10': 'Diesel',
        'DIESEL S500': 'Diesel'
    }
    
    # Aplicar mapeamento
    df['TP.Comb'] = df['TP.Comb'].replace(mapeamento_combustivel)
    
    # Para valores não mapeados que contenham "GASOLINA" ou "ETANOL"
    mask_gasolina = df['TP.Comb'].str.contains('GASOLINA|ETANOL', na=False)
    df.loc[mask_gasolina, 'TP.Comb'] = 'Gasolina'
    
    # Para valores não mapeados que contenham "DIESEL"
    mask_diesel = df['TP.Comb'].str.contains('DIESEL|DÍESEL', na=False)
    df.loc[mask_diesel, 'TP.Comb'] = 'Diesel'
    
    return df

def limpar_dados_tp_rota(df):
    """Padroniza os tipos de rota"""
    if 'TP.Rota' not in df.columns:
        return df
    
    df['TP.Rota'] = df['TP.Rota'].astype(str).str.strip()
    
    # Mapeamento para padronização
    mapeamento_rota = {
        'urbano': 'Urbano',
        'Urbano': 'Urbano',
        'rodoviário': 'Rodoviário',
        'Rodoviário': 'Rodoviário',
        'urbano e rodoviário': 'Urbano e Rodoviário',
        'Urbano e Rodoviário': 'Urbano e Rodoviário',
        'Urbano E Rodoviário': 'Urbano e Rodoviário'
    }
    
    df['TP.Rota'] = df['TP.Rota'].replace(mapeamento_rota)
    return df

def limpar_dados_grupo_veiculo(df):
    """Padroniza e agrupa os tipos de veículo em 4 categorias"""
    if 'grupocorreto' not in df.columns:
        return df

    # Converter para string, limpar espaços e padronizar
    df['grupocorreto'] = df['grupocorreto'].astype(str).str.strip()

    # Criar nova coluna com grupos padronizados
    def classificar_veiculo(grupo):
        if pd.isna(grupo) or grupo == 'nan' or str(grupo).strip() == '' or str(grupo) == '0':
            return 'Outros'

        grupo_clean = str(grupo).upper().strip()

        # Verificar caminhões (qualquer coisa que contenha "CAMINHAO" ou "CAMINHÃO")
        if 'CAMINHÃO' in grupo_clean or 'CAMINHAO' in grupo_clean:
            return 'Caminhão'

        # Verificar tipos específicos
        elif grupo_clean == 'KOMBI':
            return 'Médio'
        elif grupo_clean == 'MOTO':
            return 'Leve'
        elif grupo_clean == 'LEVE':
            return 'Leve'
        elif grupo_clean in ['MÉDIO', 'MEDIO']:
            return 'Médio'
        elif grupo_clean == 'PESADO':
            return 'Pesado'
        elif grupo_clean == '0' or grupo_clean == 'NAN':
            return 'Outros'
        else:
            print(f"Valor não classificado: '{grupo}' -> '{grupo_clean}'")
            return 'Outros'

    # Aplicar a classificação
    df['grupocorreto'] = df['grupocorreto'].apply(classificar_veiculo)

    return df

def limpar_dados_contratos(df):
    """
    Padroniza e agrupa os contratos, fazendo o merge obrigatório com a filial
    e formatando o resultado em Title Case.
    """
    # Verifica se as colunas necessárias existem
    if 'contrato' not in df.columns or 'filial' not in df.columns:
        print("AVISO: Colunas 'contrato' e/ou 'filial' não encontradas para agrupamento detalhado.")
        return df

    # Garante que as colunas sejam do tipo string e limpa espaços
    df['contrato'] = df['contrato'].astype(str).str.strip()
    df['filial'] = df['filial'].astype(str).str.strip()

    def classificar_e_juntar_com_filial(row):
        contrato_clean = str(row['contrato']).upper().strip()
        filial_clean = str(row['filial']).upper().strip()

        # --- Parte 1: Determinar a Categoria Base (Lógica simplificada e corrigida) ---
        categoria_base = ''
        if pd.isna(contrato_clean) or contrato_clean in ['NAN', 'CONT', '']:
            categoria_base = 'Contrato Não Informado'
        elif 'FEBRABAN' in contrato_clean:
            categoria_base = 'FEBRABAN'
        elif 'ECT' in contrato_clean:
            categoria_base = 'ECT'
        elif 'LATAM' in contrato_clean:
            categoria_base = 'LATAM'
        elif 'ADMINISTRATIVO' in contrato_clean:
            categoria_base = 'ADMINISTRATIVO'
        elif 'CARGAS' in contrato_clean:
            categoria_base = 'CARGAS'
        elif 'LEROY' in contrato_clean:
            categoria_base = 'LEROY MERLIN'
        elif 'DHL' in contrato_clean:
            categoria_base = 'DHL'
        elif 'BANCOOB' in contrato_clean:
            categoria_base = 'BANCOOB'
        elif 'BASSO' in contrato_clean:
            categoria_base = 'BASSO'
        elif 'FAHECE' in contrato_clean:
            categoria_base = 'FAHECE'
        elif 'ESTRUTURAL' in contrato_clean:
            categoria_base = 'ESTRUTURAL'
        elif 'OUTRA FILIAL' in contrato_clean:
            categoria_base = 'OUTRA FILIAL'
        else:
            categoria_base = 'Outros'

        # --- Parte 2: Preparar a Filial e Fazer o Merge Obrigatório ---
        filial_formatada = ''
        if pd.isna(filial_clean) or filial_clean in ['NÃO INFORMADO', 'NAN', '']:
            # "Penaliza" os dados não preenchidos como solicitado
            filial_formatada = 'Filial Não Informada'
        else:
            filial_formatada = filial_clean

        # Junta a categoria e a filial, sempre
        resultado_final = f"{categoria_base} - {filial_formatada}"

        # --- Parte 3: Aplicar a Formatação para Title Case ---
        return resultado_final.title()

    # Aplica a função para cada linha do DataFrame
    df['contrato_agrupado'] = df.apply(classificar_e_juntar_com_filial, axis=1)

    return df

def filtrar_outliers_de_kml(df):
    
    # Verifica se as colunas essenciais para a nova lógica existem
    required_cols = ['media_km_litro', 'grupocorreto', 'Modelo']
    if not all(col in df.columns for col in required_cols):
        print(f"AVISO: Faltam colunas para o ajuste de Km/L. Requer: {required_cols}")
        return df

    # --- 1. PREPARAÇÃO ---
    # Define os limites
    LIMITE_MINIMO_KML = 2.5
    LIMITE_MAXIMO_KML = 35.0
    
    # Cria a nova coluna de trabalho, convertendo para numérico
    df['media_km_litro_ajustado'] = pd.to_numeric(df['media_km_litro'], errors='coerce')
    
    # Garante que a coluna 'grupocorreto' esteja limpa e em maiúsculas para a verificação
    df['grupocorreto'] = df['grupocorreto'].astype(str).str.upper()

    # --- 2. CÁLCULO DAS MÉDIAS DE REFERÊNCIA ---
    # Primeiro, criamos um dataframe apenas com os dados "bons" para calcular as médias
    df_validos = df[
        (df['media_km_litro_ajustado'] >= LIMITE_MINIMO_KML) &
        (df['media_km_litro_ajustado'] <= LIMITE_MAXIMO_KML) &
        (df['grupocorreto'] != 'MOTO') # Exclui motos do cálculo da média
    ].copy()

    # Calcula a média de Km/L para cada modelo de veículo
    media_por_modelo = df_validos.groupby('Modelo')['media_km_litro_ajustado'].mean()
    
    # Calcula uma média geral de fallback, caso um modelo não tenha nenhum dado válido
    media_geral_fallback = df_validos['media_km_litro_ajustado'].mean()

    # --- 3. APLICAÇÃO DA LÓGICA DE AJUSTE (LINHA A LINHA) ---
    def ajustar_linha(row):
        kml_original = row['media_km_litro_ajustado']
        grupo = row['grupocorreto']
        modelo = row['Modelo']
        ajustes_aplicados = []

        # Se o valor original for nulo, retorna nulo para não interferir
        if pd.isna(kml_original):
            return np.nan

        # REGRA 1: Se for MOTO, retorna o valor original sem alteração
        if grupo == 'MOTO':
            ajustes_aplicados.append("Original (Moto)")
            return kml_original

        # REGRA 2: Se o valor estiver fora dos limites (e não for moto)
        if kml_original < LIMITE_MINIMO_KML or kml_original > LIMITE_MAXIMO_KML:
            ajustes_aplicados.append("Ajustado pela Média do Modelo")
            return media_por_modelo.get(modelo, media_geral_fallback)
        
        # REGRA 3: Se o valor estiver dentro dos limites, retorna o valor original
        else:
            ajustes_aplicados.append("Original (Valido)")
            return kml_original

    # Aplica a função de ajuste para criar a coluna final
    df['media_km_litro_ajustado'] = df.apply(ajustar_linha, axis=1)

    return df

@st.cache_data(ttl=3600)
def get_data():
    file_path = os.path.join('data', 'raw', 'Evolução.xlsb')

    try:
        abas = ['BD 2023', 'FROTA', 'Filiais']
        dfs = pd.read_excel(file_path, sheet_name=abas, engine='pyxlsb')
        df_bd, df_frota, df_filiais = (clean_col_names(dfs['BD 2023']),
                                      clean_col_names(dfs['FROTA']),
                                      clean_col_names(dfs['Filiais']))
        
        df_frota_join = df_frota[['Placa', 'Ano']].copy()
        df_bd = pd.merge(df_bd, df_frota_join, on='Placa', how='left')
        df_filiais_join = df_filiais[['ID Filial', 'Filial', 'Regiao']].copy()
        df_filiais_join.rename(columns={'Filial': 'Filial Padronizada', 'Regiao': 'Regiao Padronizada'}, inplace=True)
        df_bd = pd.merge(df_bd, df_filiais_join, on='ID Filial', how='left')

        colunas_custo = ['Lataria e Pintura', 'Manutenção', 'Rodas / Pneus', 'Valor Comb.', 'Arla']
        for col in colunas_custo:
            if col in df_bd.columns:
                df_bd[col] = pd.to_numeric(df_bd[col], errors='coerce').fillna(0)

        # Colunas de quilometragem e eficiência
        colunas_km = ['Km Inicial', 'Km Final', 'Total de Km', 'Média Km/l', 'Comb / Km', 'Litros Comb.']
        for col in colunas_km:
            if col in df_bd.columns:
                df_bd[col] = pd.to_numeric(df_bd[col], errors='coerce').fillna(0)

        # Colunas de dias úteis e operacionais
        colunas_operacionais = ['Dias Úteis', 'DUC', 'DUK', 'DUL']
        for col in colunas_operacionais:
            if col in df_bd.columns:
                df_bd[col] = pd.to_numeric(df_bd[col], errors='coerce').fillna(0)

        # Calcular KM rodados se temos Km Inicial e Final
        if 'Km Inicial' in df_bd.columns and 'Km Final' in df_bd.columns:
            df_bd['KM_Rodados'] = df_bd['Km Final'] - df_bd['Km Inicial']
            df_bd['KM_Rodados'] = df_bd['KM_Rodados'].where(df_bd['KM_Rodados'] >= 0, 0)

        # Verificar se existe coluna 'Total de Km' ou 'Total de KM' e usar KM_Rodados como fallback
        if 'Total de Km' in df_bd.columns:
            # Usar a coluna existente, mas verificar se tem valores válidos
            df_bd['Total de Km'] = df_bd['Total de Km'].fillna(df_bd.get('KM_Rodados', 0))
        elif 'Total de KM' in df_bd.columns:
            df_bd['Total de Km'] = df_bd['Total de KM']
        else:
            # Criar coluna usando KM_Rodados
            df_bd['Total de Km'] = df_bd.get('KM_Rodados', 0)

        df_bd['Total Geral Manutenção'] = df_bd[['Lataria e Pintura', 'Manutenção', 'Rodas / Pneus', 'Arla']].sum(axis=1)

        rename_map = {
            'Mês': 'data',
            'Total Geral Manutenção': 'valor',
            'GrupoCorreto': 'grupocorreto',
            'Regiao Padronizada': 'regiao',
            'Filial Padronizada': 'filial',
            'Contrato': 'contrato',
            'Lataria e Pintura': 'custo_lataria_pintura',
            'Manutenção': 'custo_manutencao_geral',
            'Rodas / Pneus': 'custo_rodas_pneus',
            'Valor Comb.': 'custo_combustivel',
            'Arla': 'custo_arla',
            'Km Inicial': 'km_inicial',
            'Km Final': 'km_final',
            'Total de Km': 'total_km',
            'Média Km/l': 'media_km_litro',
            'Comb / Km': 'custo_comb_por_km',
            'Litros Comb.': 'litros_combustivel',
            'Man / Km': 'manutencao_por_km'
        }
        df_bd.rename(columns=rename_map, inplace=True)

        df_bd['data'] = pd.to_datetime(df_bd['data'], unit='D', origin='1899-12-30')
        df_bd.dropna(subset=['data'], inplace=True)
        df_bd['valor'] = pd.to_numeric(df_bd['valor'], errors='coerce').fillna(0)
        df_bd['ano'] = df_bd['data'].dt.year
        df_bd = df_bd[df_bd['ano'] == 2025]
        df_bd['mes_ano'] = df_bd['data'].dt.strftime('%Y-%m')
        
        # APLICAR LIMPEZA DOS DADOS AQUI (ANTES DAS OUTRAS TRANSFORMAÇÕES)
        df_bd = limpar_dados_combustivel(df_bd)
        df_bd = limpar_dados_tp_rota(df_bd)
        df_bd = limpar_dados_grupo_veiculo(df_bd)
        df_bd = limpar_dados_contratos(df_bd)
        df_bd = filtrar_outliers_de_kml(df_bd)
        
        df_bd['Idade'] = datetime.now().year - pd.to_numeric(df_bd['Ano'], errors='coerce')

        for col in ['grupocorreto', 'regiao', 'filial', 'contrato']:
            if col in df_bd.columns:
                df_bd[col] = df_bd[col].astype(str).str.strip().str.upper().replace('NAN', 'NÃO INFORMADO')

        # Calcular colunas derivadas importantes
        df_bd['custo_combustivel_total'] = df_bd['custo_combustivel']
        df_bd['custo_frota_total'] = df_bd['valor'] + df_bd['custo_combustivel_total']

        # Lista final de colunas incluindo dados de quilometragem e eficiência
        colunas_finais = [
            'data', 'valor', 'grupocorreto', 'regiao', 'filial',
            'contrato', 'contrato_agrupado', 'ano', 'mes_ano', 'Placa', 'Idade',
            'custo_lataria_pintura', 'custo_manutencao_geral', 'custo_rodas_pneus',
            'custo_combustivel', 'custo_arla', 'custo_combustivel_total', 'custo_frota_total',
            'Modelo', 'Marca', 'TP.Comb', 'TP.Rota',
            'Roteiro Principal', 'Motorista Principal',
            'Dias Úteis', 'DUC', 'DUK', 'DUL',
            'km_inicial', 'km_final', 'total_km', 'media_km_litro', 'custo_comb_por_km',
            'litros_combustivel', 'manutencao_por_km', 'KM_Rodados', 'media_km_litro_ajustado'
        ]
        df_final = df_bd[[col for col in colunas_finais if col in df_bd.columns]].copy()
    
        return df_final


    except Exception as e:
        st.error(f"Ocorreu um erro crítico ao processar a planilha: {e}")
        return pd.DataFrame()