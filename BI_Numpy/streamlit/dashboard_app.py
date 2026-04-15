import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA CHAMADA ST)
st.set_page_config(layout="wide", page_title="Dashboard Agro Goiás")

# Carregamento dos dados
@st.cache_data # Use isso para o app não ler o CSV toda vez que você mexer em um botão
def load_data():
    path = r"C:\Users\Usuario\Documents\Fatesg_IA2\BI_Numpy\streamlit\financiamentoPecuaria.csv"
    df = pd.read_csv(path, encoding='utf-8', sep=';')
    
    # Limpeza de dados (Substituir traço por zero e converter para numérico)
    df = df.replace('-', '0')
    
    # Converter colunas de anos (da segunda em diante) para float
    for col in df.columns[1:]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Criar coluna de Média por Linha (Investimento médio por categoria)
    df["Md_Invest"] = df.iloc[:, 1:].mean(axis=1).round(2)
    
    return df

df = load_data()

# --- INTERFACE DO DASHBOARD ---
st.title('📊 Dashboard Financeiro - Agro Goiás (2014-2024)')

# Criando abas para organizar o conteúdo
tab1, tab2 = st.tabs(["Tabela de Dados", "Visualização Gráfica"])

with tab1:
    st.subheader("Dados Consolidados")
    # Formatação para moeda brasileira na exibição
    st.dataframe(df.style.format(precision=2, decimal=',', thousands='.'), use_container_width=True)

with tab2:
    st.subheader("Análise de Evolução Temporal")
    
    # Seleção de qual categoria o usuário quer ver no gráfico
    categoria = st.selectbox("Selecione a Categoria para analisar:", df.iloc[:, 0].unique())
    
    # Filtrar dados para o gráfico
    dados_grafico = df[df.iloc[:, 0] == categoria].iloc[:, 1:-1] # Pega do primeiro ano até o último (sem a média)
    
    # Criando o gráfico com Matplotlib
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(dados_grafico.columns, dados_grafico.values[0], marker='o', linestyle='-', color='green')
    ax.set_title(f"Evolução: {categoria}")
    ax.set_ylabel("Valor em R$")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    st.pyplot(fig)

# Métricas rápidas no rodapé
st.divider()
col1, col2, col3 = st.columns(3)
col1.metric("Total de Categorias", len(df))
col2.metric("Maior Média", f"R$ {df['Md_Invest'].max():,.2f}")
col3.metric("Menor Média", f"R$ {df['Md_Invest'].min():,.2f}")