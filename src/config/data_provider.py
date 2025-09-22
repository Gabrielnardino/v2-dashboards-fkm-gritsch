import pandas as pd
import streamlit as st
import os
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
    if 'Grupo Veículo' not in df.columns:
        return df
    
    # Converter para string, limpar espaços e padronizar
    df['Grupo Veículo'] = df['Grupo Veículo'].astype(str).str.strip()
    
    # Criar nova coluna com grupos padronizados
    def classificar_veiculo(grupo):
        if pd.isna(grupo) or grupo == 'nan':
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
        else:
            print(f"Valor não classificado: '{grupo}' -> '{grupo_clean}'")
            return 'Outros'
    
    # Aplicar a classificação
    df['Grupo Veículo'] = df['Grupo Veículo'].apply(classificar_veiculo)
    
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
            df_bd[col] = pd.to_numeric(df_bd[col], errors='coerce').fillna(0)
        
        df_bd['Total Geral Manutenção'] = df_bd[['Lataria e Pintura', 'Manutenção', 'Rodas / Pneus']].sum(axis=1)

        rename_map = {
            'Mês': 'data',
            'Total Geral Manutenção': 'valor',
            'GrupoCorreto': 'natureza_correta',
            'Regiao Padronizada': 'regiao',
            'Filial Padronizada': 'filial',
            'Contrato': 'contrato',
            'Lataria e Pintura': 'custo_lataria_pintura',
            'Manutenção': 'custo_manutencao_geral',
            'Rodas / Pneus': 'custo_rodas_pneus',
            'Valor Comb.': 'custo_combustivel',
            'Arla': 'custo_arla'
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
        
        df_bd['Idade'] = datetime.now().year - pd.to_numeric(df_bd['Ano'], errors='coerce')

        for col in ['natureza_correta', 'regiao', 'filial', 'contrato']:
            if col in df_bd.columns:
                df_bd[col] = df_bd[col].astype(str).str.strip().str.upper().replace('NAN', 'NÃO INFORMADO')

        # --- MUDANÇA AQUI: Adicionando 'Dias Úteis' à lista final ---
        colunas_finais = [
            'data', 'valor', 'natureza_correta', 'regiao', 'filial',
            'contrato', 'ano', 'mes_ano', 'Placa', 'Idade',
            'custo_lataria_pintura', 'custo_manutencao_geral', 'custo_rodas_pneus',
            'custo_combustivel', 'custo_arla',
            'Modelo', 'Grupo Veículo', 'Marca', 'TP.Comb', 'TP.Rota',
            'Roteiro Principal', 'Motorista Principal',
            'Dias Úteis' # Garantindo que a coluna seja passada
        ]
        df_final = df_bd[[col for col in colunas_finais if col in df_bd.columns]].copy()
    
        return df_final


    except Exception as e:
        st.error(f"Ocorreu um erro crítico ao processar a planilha: {e}")
        return pd.DataFrame()