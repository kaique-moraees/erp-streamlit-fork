import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from faker import Faker

# Interface Streamlit
def main():
    st.title("ERP Financeiro com Streamlit")
    
    st.write(f'Aluno: Kaique Moraes - RA: 10410548')
    
    menu = ["Clientes", "Contas a Pagar", "Contas a Receber", "Lançamentos", "Relatórios", "Gráficos"]
    choice = st.sidebar.selectbox("Selecione uma opção", menu)
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    if choice == "Clientes":
        st.subheader("Cadastro de Clientes")
        df = pd.read_sql_query("SELECT * FROM clientes", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Pagar":
        st.subheader("Contas a Pagar")
        df = pd.read_sql_query("SELECT * FROM contas_pagar", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Receber":
        st.subheader("Contas a Receber")
        df = pd.read_sql_query("SELECT * FROM contas_receber", conn)
        st.dataframe(df)
        
    elif choice == "Lançamentos":
        st.subheader("Lançamentos Financeiros")
        df = pd.read_sql_query("SELECT * FROM lancamentos", conn)
        st.dataframe(df)
        
    elif choice == "Relatórios":
        st.subheader("Relatório de Fluxo de Caixa")
        df = pd.read_sql_query("SELECT tipo, SUM(valor) as total FROM lancamentos GROUP BY tipo", conn)
        st.dataframe(df)

    elif choice == "Gráficos":
        st.subheader("Status das Contas a Pagar e Receber")
        df = pd.read_sql_query("SELECT * FROM contas_pagar", conn)
        df_status = df["status"].value_counts().reset_index()
        df_status.columns = ["status", "quantidade"]
        
        color_map = {"Pago": "green", "Pendente": "red"}
        
        fig = px.bar(df_status, x="status", y="quantidade", text_auto=True,
                     labels={"status": "Status", "quantidade": "Quantidade"},
                     title="Quantidade de Contas a Pagar e Receber por Status",
                     color="status", color_discrete_map=color_map)
        st.plotly_chart(fig)

        st.subheader("Comportamento da Receita e Despesa ao Longo dos Dias")
        
        df = pd.read_sql_query("SELECT tipo, valor, data FROM lancamentos", conn)
        
        df['data'] = pd.to_datetime(df['data'])
        
        df_grouped = df.groupby([df['data'].dt.date, 'tipo'])['valor'].sum().reset_index()
        
        color_map = {"Receita": "green", "Despesa": "red"}

        fig = px.line(df_grouped, x='data', y='valor', color='tipo', markers=True,
                      labels={'data': 'Data', 'valor': 'Valor (R$)', 'tipo': 'Tipo'},
                      color_discrete_map=color_map)
        st.plotly_chart(fig)

        st.subheader("Clientes que Geram Maior Receita")
        
        df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
        df_contas_receber = pd.read_sql_query("SELECT * FROM contas_receber", conn)
        
        df_contas_receber = df_contas_receber[df_contas_receber['status'] == 'Recebido']
    
        df_receitas = df_contas_receber.groupby('cliente_id')['valor'].sum().reset_index()
        
        df_top_clientes = pd.merge(df_receitas, df_clientes[['id', 'nome']], left_on='cliente_id', right_on='id')
        
        df_top_clientes = df_top_clientes.sort_values(by='valor', ascending=False).head(5)
         
        fig_bar = px.bar(df_top_clientes, x='nome', y='valor', text_auto=True,
                         labels={'nome': 'Cliente', 'valor': 'Total Receita (R$)'},
                         color='valor',  
                         color_continuous_scale='RdYlGn')
        
        st.plotly_chart(fig_bar)
    
    conn.close()
    
if __name__ == "__main__":
    main()
