import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import database as db
import data_pipeline as pipe

st.set_page_config(
    page_title="Turnaround & Liquidity Cockpit",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""

<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Cartões de KPI no Modo Escuro */
    .kpi-container {
        background-color: #111827 !important;
        border: 1px solid #1F2937 !important;
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .kpi-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #9CA3AF !important;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #F9FAFB !important;
        line-height: 1.2;
    }
    .kpi-subtitle {
        font-size: 0.80rem;
        color: #9CA3AF !important;
        margin-top: 6px;
    }
    
    /* Badges refinadas */
    .kpi-badge-critical {
        background-color: rgba(225, 29, 72, 0.15);
        color: #FB7185;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid rgba(225, 29, 72, 0.3);
    }
    .kpi-badge-success {
        background-color: rgba(5, 150, 105, 0.15);
        color: #34D399;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid rgba(5, 150, 105, 0.3);
    }
</style>
""", unsafe_allow_html=True)

PALETTE = {
    "slate_dark": "#0F172A",
    "slate_light": "#64748B",
    "classe_a": "#059669", 
    "classe_b": "#0284C7",  
    "classe_c": "#E11D48",  
    "grid_color": "#F1F5F9",
    "border_color": "#E2E8F0",
    "bg_light": "#FFFFFF"
}

@st.cache_data
def carregar_dados():
    df_bruto = db.processar_base_sql("dados_varejo_raw.csv")
    df_final = pipe.aplicar_diretrizes_operacionais(df_bruto)
    return df_final

try:
    df_base = carregar_dados()
except Exception as erro:
    st.error(f"Erro ao carregar a base de dados: {erro}")
    st.stop()

with st.sidebar:
    st.markdown("### 🏛️ **Governança & Portfólio**")
    st.caption("Filtros de segmentação estratégica de catálogo.")
    
    categorias_unicas = df_base["categoria"].unique().tolist()
    cat_selecionadas = st.multiselect(
        "Categorias Ativas",
        options=categorias_unicas,
        default=categorias_unicas
    )

    classes_opcoes = ["Classe A", "Classe B", "Classe C"]
    class_selecionadas = st.multiselect(
        "Classificação ABC (Margem)",
        options=classes_opcoes,
        default=classes_opcoes
    )

    st.markdown("---")
    st.markdown("### 💳 **Estrutura de Liquidez**")
    st.caption("Simulação da carteira de crédito ao consumidor.")
    modelo_credito = st.radio(
        "Modelo Financeiro:",
        ["Banco Parceiro (White Label / D+30)", "Crediário Próprio (Carnê 18x-24x)"]
    )

df_filtrado = db.filtrar_dados_sql(df_base, cat_selecionadas, class_selecionadas)
kpis = db.calcular_kpis_sql(df_filtrado)

st.markdown("## **Turnaround Analytics: Alocação de Capital & Giro**")
st.markdown(
    "<p style='color: #64748B; font-size: 0.95rem; margin-top: -10px; margin-bottom: 24px;'>"
    "Painel estratégico de gestão de margem bruta, liberação de capital em cauda longa e mitigação de risco de balanço."
    "</p>", 
    unsafe_allow_html=True
)

margem_perc = (kpis["lucro_bruto"] / kpis["faturamento"] * 100) if kpis["faturamento"] > 0 else 0.0

col_k1, col_k2, col_k3, col_k4 = st.columns(4)

with col_k1:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Faturamento Total</div>
        <div class="kpi-value">R$ {kpis['faturamento']:,.2f}</div>
        <div class="kpi-subtitle">Volume bruto da carteira</div>
    </div>
    """, unsafe_allow_html=True)

with col_k2:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Lucro Bruto (Margem)</div>
        <div class="kpi-value">R$ {kpis['lucro_bruto']:,.2f}</div>
        <div class="kpi-subtitle"><span class="kpi-badge-success">{margem_perc:.1f}% de margem</span></div>
    </div>
    """, unsafe_allow_html=True)

with col_k3:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Capital em Estoque</div>
        <div class="kpi-value">R$ {kpis['estoque_total']:,.2f}</div>
        <div class="kpi-subtitle">Ativo circulante imobilizado</div>
    </div>
    """, unsafe_allow_html=True)

with col_k4:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Imobilizado em Linha C</div>
        <div class="kpi-value" style="color: #BE123C;">R$ {kpis['estoque_classe_c']:,.2f}</div>
        <div class="kpi-subtitle"><span class="kpi-badge-critical">Bloqueio 1P Obrigatório</span></div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

aba_graficos, aba_matriz, aba_liquidez = st.tabs([
    "Curva de Rentabilidade & Giro", 
    "Portfólio & Matriz SKU", 
    "Simulador de Ciclo de Caixa"
])

with aba_graficos:
    st.write("")
    c_left, c_right = st.columns([6, 4])

    with c_left:
        st.markdown("##### **Curva de Pareto: Rentabilidade Acumulada por Produto**")
        st.caption("Contribuição individual de lucro bruto e corte acumulado de 80% (Classe A) e 95% (Classe B).")

        fig_pareto = go.Figure()

        cores_barras = [
            PALETTE["classe_a"] if c == "Classe A" else (PALETTE["classe_b"] if c == "Classe B" else PALETTE["classe_c"])
            for c in df_filtrado["classe_abc"]
        ]

        # 1. Barras de Lucro
        fig_pareto.add_trace(go.Bar(
            x=df_filtrado["nome_produto"],
            y=df_filtrado["lucro_bruto"],
            name="Lucro Bruto",
            marker=dict(color=cores_barras, opacity=0.85, line=dict(width=0)),
            hovertemplate="<b>%{x}</b><br>Lucro Bruto: R$ %{y:,.2f}<extra></extra>"
        ))

        # 2. Linha Acumulada de Pareto
        fig_pareto.add_trace(go.Scatter(
            x=df_filtrado["nome_produto"],
            y=df_filtrado["perc_acumulado_lucro"],
            name="% Acumulado",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color=PALETTE["slate_dark"], width=2.2),
            marker=dict(size=5, color=PALETTE["slate_dark"]),
            hovertemplate="% Acumulado: %{y:.1f}%<extra></extra>"
        ))

        # Linha de corte dos 80% (Classe A)
        fig_pareto.add_hline(
            y=80, yref="y2", line_dash="dot", line_color="#94A3B8", line_width=1.2,
            annotation_text="Corte 80% (Classe A)", annotation_position="top left",
            annotation_font=dict(size=10, color="#64748B")
        )

        fig_pareto.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
            margin=dict(l=10, r=10, t=20, b=10),
            hoverlabel=dict(bgcolor="#0F172A", font_size=12, font_color="#FFFFFF", font_family="Inter"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
            xaxis=dict(showgrid=False, tickfont=dict(size=10, color=PALETTE["slate_light"]), tickangle=-20),
            yaxis=dict(
                title=None,
                showgrid=True,
                gridcolor=PALETTE["grid_color"],
                tickfont=dict(size=10, color=PALETTE["slate_light"]),
                tickprefix="R$ "
            ),
            yaxis2=dict(
                title=None,
                overlaying="y",
                side="right",
                range=[0, 105],
                ticksuffix="%",
                showgrid=False,
                tickfont=dict(size=10, color=PALETTE["slate_light"])
            )
        )
        st.plotly_chart(fig_pareto, use_container_width=True, config={"displayModeBar": False})

    with c_right:
        st.markdown("##### **Matriz Giro vs. Margem (Dias de Cobertura)**")
        st.caption("Tamanho da bolha representa o capital imobilizado no galpão.")

        fig_scatter = px.scatter(
            df_filtrado,
            x="pme_dias_cobertura",
            y="margem_bruta_perc",
            color="classe_abc",
            size="capital_imobilizado_estoque",
            hover_name="nome_produto",
            labels={
                "pme_dias_cobertura": "Cobertura (Dias)",
                "margem_bruta_perc": "Margem Bruta (%)",
                "classe_abc": "Classe",
                "capital_imobilizado_estoque": "Estoque Imobilizado"
            },
            color_discrete_map={
                "Classe A": PALETTE["classe_a"],
                "Classe B": PALETTE["classe_b"],
                "Classe C": PALETTE["classe_c"]
            }
        )

        fig_scatter.add_vline(
            x=90, line_dash="dash", line_color="#CBD5E1", line_width=1.2,
            annotation_text="Alerta > 90d", annotation_position="top right",
            annotation_font=dict(size=10, color="#64748B")
        )

        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
            margin=dict(l=10, r=10, t=20, b=10),
            hoverlabel=dict(bgcolor="#0F172A", font_size=12, font_color="#FFFFFF", font_family="Inter"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11), title=None),
            xaxis=dict(
                showgrid=True, gridcolor=PALETTE["grid_color"],
                tickfont=dict(size=10, color=PALETTE["slate_light"]),
                title=dict(text="Prazo Médio de Estoque (Dias)", font=dict(size=11, color=PALETTE["slate_light"]))
            ),
            yaxis=dict(
                showgrid=True, gridcolor=PALETTE["grid_color"],
                tickfont=dict(size=10, color=PALETTE["slate_light"]),
                ticksuffix="%",
                title=dict(text="Margem Bruta (%)", font=dict(size=11, color=PALETTE["slate_light"]))
            )
        )
        st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")
    st.markdown("##### **Alocação de Capital Imobilizado em Estoque por Categoria**")
    
    df_cat = df_filtrado.groupby(["categoria", "classe_abc"])["capital_imobilizado_estoque"].sum().reset_index()
    fig_cat = px.bar(
        df_cat,
        y="categoria",
        x="capital_imobilizado_estoque",
        color="classe_abc",
        orientation="h",
        color_discrete_map={
            "Classe A": PALETTE["classe_a"],
            "Classe B": PALETTE["classe_b"],
            "Classe C": PALETTE["classe_c"]
        }
    )
    fig_cat.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=240,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, font=dict(size=11), title=None),
        xaxis=dict(
            showgrid=True, gridcolor=PALETTE["grid_color"],
            tickprefix="R$ ",
            tickfont=dict(size=10, color=PALETTE["slate_light"]),
            title=None
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=11, color="#1E293B", weight="bold"),
            title=None
        )
    )
    st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})

with aba_matriz:
    st.write("")
    st.markdown("##### **Matriz de Governança de Compras e Estoque 1P**")
    st.caption("Visão detalhada por SKU com regras automáticas de reabastecimento ou desmobilização.")

    colunas_foco = [
        "id_produto", "nome_produto", "categoria", "classe_abc",
        "margem_bruta_perc", "pme_dias_cobertura", "capital_imobilizado_estoque", "diretriz_compras"
    ]

    st.dataframe(
        df_filtrado[colunas_foco].style.format({
            "margem_bruta_perc": "{:.2f}%",
            "pme_dias_cobertura": "{:.0f} dias",
            "capital_imobilizado_estoque": "R$ {:,.2f}"
        }),
        use_container_width=True,
        hide_index=True,
        height=450
    )

with aba_liquidez:
    st.write("")
    st.markdown("##### **Diagnóstico Estrutural de Liquidez (PMR vs. PMP)**")
    
    pmp_medio = int(df_filtrado["pmp_dias"].mean()) if not df_filtrado.empty else 75
    diagnostico = pipe.simular_cenario_credito(modelo_credito, pmp_medio)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Prazo Médio Fornecedor (PMP)</div>
            <div class="kpi-value">{diagnostico['pmp']} dias</div>
            <div class="kpi-subtitle">Tempo de quitação junto à indústria</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Prazo Médio Recebimento (PMR)</div>
            <div class="kpi-value">{diagnostico['pmr']} dias</div>
            <div class="kpi-subtitle">Ciclo de liquidação da venda</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        status_cor = "#059669" if diagnostico['gap'] <= 0 else "#BE123C"
        badge_tipo = "kpi-badge-success" if diagnostico['gap'] <= 0 else "kpi-badge-critical"
        texto_badge = "Caixa Positivo (Recebe antes)" if diagnostico['gap'] <= 0 else "Buraco de Liquidez"
        
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Descompasso Temporal (Gap)</div>
            <div class="kpi-value" style="color: {status_cor};">{diagnostico['gap']} dias</div>
            <div class="kpi-subtitle"><span class="{badge_tipo}">{texto_badge}</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    
    card_borda = "#D1FAE5" if diagnostico["status"] == "success" else "#FFE4E6"
    card_fundo = "#F0FDF4" if diagnostico["status"] == "success" else "#FFF1F2"
    titulo_cor = "#065F46" if diagnostico["status"] == "success" else "#9F1239"

    st.markdown(f"""
    <div style="background-color: {card_fundo}; border: 1px solid {card_borda}; border-radius: 12px; padding: 20px 24px; margin-top: 10px;">
        <h4 style="color: {titulo_cor}; margin-top: 0; font-weight: 600;">{diagnostico['titulo']}</h4>
        <p style="color: #334155; font-size: 0.95rem; margin-bottom: 8px;">
            <b>Impacto em Balanço / Risco PDD:</b> {diagnostico['pdd']}
        </p>
        <p style="color: #475569; font-size: 0.90rem; margin-bottom: 0;">
            {diagnostico['detalhes']}
        </p>
    </div>
    """, unsafe_allow_html=True)