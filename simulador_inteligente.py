
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import math

# Tabela de IR Regressivo para CDB
def obter_aliquota_ir(dias):
    """
    Retorna a alíquota de IR baseada no prazo do investimento
    """
    if dias <= 180:
        return 0.225  # 22,5%
    elif dias <= 360:
        return 0.20   # 20%
    elif dias <= 720:
        return 0.175  # 17,5%
    else:
        return 0.15   # 15%

def calcular_rentabilidade_mensal(tipo_rentabilidade, taxa, cdi_anual, ipca_anual):
    """
    Calcula a rentabilidade mensal baseada no tipo de indexador
    """
    if tipo_rentabilidade == 'Prefixada':
        return (1 + taxa) ** (1/12) - 1
    elif tipo_rentabilidade == 'CDI':
        return (1 + cdi_anual) ** (1/12) - 1 * taxa
    elif tipo_rentabilidade == 'IPCA +':
        return ((1 + ipca_anual) * (1 + taxa)) ** (1/12) - 1
    else:
        return 0

def simular_valor_futuro(tipo_rentabilidade, taxa, meses, aporte_inicial, aporte_mensal, cdi_anual, ipca_anual, isento_ir):
    rent_mensal = calcular_rentabilidade_mensal(tipo_rentabilidade, taxa, cdi_anual, ipca_anual)
    saldo = aporte_inicial
    valores = [saldo]
    total_rendimentos = 0
    for i in range(1, meses + 1):
        saldo *= (1 + rent_mensal)
        saldo += aporte_mensal
        valores.append(saldo)
    rendimento_bruto = saldo - (aporte_inicial + aporte_mensal * meses)
    if not isento_ir:
        dias = meses * 30
        aliquota = obter_aliquota_ir(dias)
        imposto = rendimento_bruto * aliquota
        saldo -= imposto
        rendimento_bruto -= imposto
    return saldo, valores, rendimento_bruto, rent_mensal

# Interface Streamlit
st.set_page_config(page_title="Simulador de Investimento em Renda Fixa", layout="wide")
st.title("📊 Simulador Inteligente de Investimento em Renda Fixa")

col1, col2, col3 = st.columns(3)
with col1:
    aporte_inicial = st.number_input("Aporte Inicial (R$)", min_value=0.0, value=1000.0, step=100.0)
with col2:
    aporte_mensal = st.number_input("Aporte Mensal (R$)", min_value=0.0, value=500.0, step=50.0)
with col3:
    meses = st.number_input("Prazo (meses)", min_value=1, value=36, step=1)

st.markdown("---")
st.subheader("🧠 Configurações do Cenário Econômico")
col4, col5 = st.columns(2)
with col4:
    cdi_anual = st.number_input("CDI Anual (%)", min_value=0.0, value=0.1375)  # 13,75%
with col5:
    ipca_anual = st.number_input("IPCA Anual (%)", min_value=0.0, value=0.045)  # 4,5%

# Produtos disponíveis para simulação
produtos = [
    {"nome": "CDB - Prefixada", "tipo": "Prefixada", "taxa": 0.1175, "isento_ir": False},
    {"nome": "LCI - Pós CDI", "tipo": "CDI", "taxa": 0.94, "isento_ir": True},
    {"nome": "LCA - IPCA +", "tipo": "IPCA +", "taxa": 0.058, "isento_ir": True}
]

# Cores para o gráfico
cores = ['red', 'blue', 'green']

# Simulação
resultados = []
fig = go.Figure()
for idx, produto in enumerate(produtos):
    saldo_final, valores, rendimento_bruto, rentabilidade_mensal = simular_valor_futuro(
        produto["tipo"], produto["taxa"], meses, aporte_inicial, aporte_mensal, cdi_anual, ipca_anual, produto["isento_ir"]
    )
    resultados.append((produto["nome"], saldo_final, rendimento_bruto))
    fig.add_trace(go.Scatter(x=list(range(meses+1)), y=valores, mode='lines+markers', name=produto["nome"], line=dict(color=cores[idx])))

# Melhor opção
melhor = max(resultados, key=lambda x: x[1])
segundo = sorted(resultados, key=lambda x: x[1])[-2]

# Resultado final
st.plotly_chart(fig, use_container_width=True)
st.success(f"🏆 **MELHOR OPÇÃO:** {melhor[0]} - Valor final: R$ {melhor[1]:,.2f}")

st.warning("⚠️ Esta é uma simulação educativa. Rentabilidades passadas não garantem resultados futuros.")

# Explicações adicionais
with st.expander("ℹ️ Informações Importantes"):
    st.write("• Premissas: CDI e IPCA permanecem constantes. IR regressivo para CDB. Não considera IOF.")
    st.write("• LCI e LCA normalmente são isentas de IR, mas **existem LCI híbridas que podem ter tributação**.")

with st.sidebar:
    st.subheader("📚 Guia Rápido")
    st.markdown("""
    **CDB (Certificado de Depósito Bancário)**  
    • Garantido pelo FGC até R$ 250 mil  
    • Tributação: IR regressivo  
    • Liquidez: Varia conforme produto  

    **LCI (Letra de Crédito Imobiliário)**  
    • Garantido pelo FGC até R$ 250 mil  
    • Tributação: Isento de IR  
    • Carência: Mínimo 90 dias  

    **LCA (Letra de Crédito do Agronegócio)**  
    • Garantido pelo FGC até R$ 250 mil  
    • Tributação: Isento de IR  
    • Carência: Mínimo 90 dias  

    **Tabela IR - CDB**  
    • Até 180 dias: 22,5%  
    • 181-360 dias: 20%  
    • 361-720 dias: 17,5%  
    • Acima de 720 dias: 15%  
    """)
