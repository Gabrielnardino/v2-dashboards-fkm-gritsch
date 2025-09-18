import pandas as pd
import streamlit as st
import os
from datetime import datetime

def clean_col_names(df):
    cols = df.columns
    new_cols = [col.strip().replace('  ', ' ') for col in cols]
    df.columns = new_cols
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
        df_bd['mes_ano'] = df_bd['data'].dt.strftime('%Y-%m')
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
