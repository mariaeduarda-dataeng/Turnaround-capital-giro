import duckdb
import pandas as pd

def processar_base_sql(caminho_csv: str) -> pd.DataFrame:
    """Executa saneamento e cálculo da Curva ABC via SQL puro."""
    query = f"""
    WITH base_limpa AS (
        SELECT 
            TRIM(id_produto) AS id_produto,
            TRIM(nome_produto) AS nome_produto,
            TRIM(categoria) AS categoria,
            CAST(preco_unitario AS DOUBLE) AS preco_unitario,
            CAST(custo_unitario AS DOUBLE) AS custo_unitario,
            CAST(qtd_vendida_12m AS BIGINT) AS qtd_vendida_12m,
            CAST(qtd_estoque_atual AS BIGINT) AS qtd_estoque_atual,
            CAST(prazo_fornecedor_pmp_dias AS BIGINT) AS pmp_dias,
            TRIM(modalidade_pagamento_predominante) AS modalidade_pagamento
        FROM read_csv_auto('{caminho_csv}')
    ),
    metricas AS (
        SELECT 
            *,
            (qtd_vendida_12m * preco_unitario) AS faturamento_total,
            (qtd_vendida_12m * custo_unitario) AS cmv_total,
            (qtd_vendida_12m * preco_unitario) - (qtd_vendida_12m * custo_unitario) AS lucro_bruto,
            ROUND((((preco_unitario - custo_unitario) * qtd_vendida_12m) / 
                   NULLIF(preco_unitario * qtd_vendida_12m, 0)) * 100, 2) AS margem_bruta_perc,
            (qtd_estoque_atual * custo_unitario) AS capital_imobilizado_estoque,
            ROUND(CASE 
                WHEN qtd_vendida_12m > 0 THEN (qtd_estoque_atual / (qtd_vendida_12m / 365.0))
                ELSE 999.0 
            END, 0) AS pme_dias_cobertura
        FROM base_limpa
    ),
    pareto AS (
        SELECT 
            *,
            SUM(lucro_bruto) OVER (
                ORDER BY lucro_bruto DESC 
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS lucro_acumulado,
            SUM(lucro_bruto) OVER () AS lucro_total_geral,
            ROUND((SUM(lucro_bruto) OVER (
                ORDER BY lucro_bruto DESC 
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) / SUM(lucro_bruto) OVER ()) * 100, 2) AS perc_acumulado_lucro
        FROM metricas
    )
    SELECT 
        id_produto,
        nome_produto,
        categoria,
        preco_unitario,
        custo_unitario,
        qtd_vendida_12m,
        qtd_estoque_atual,
        pmp_dias,
        modalidade_pagamento,
        faturamento_total,
        cmv_total,
        lucro_bruto,
        margem_bruta_perc,
        capital_imobilizado_estoque,
        pme_dias_cobertura,
        perc_acumulado_lucro,
        CASE 
            WHEN perc_acumulado_lucro <= 80.0 THEN 'Classe A'
            WHEN perc_acumulado_lucro <= 95.0 THEN 'Classe B'
            ELSE 'Classe C'
        END AS classe_abc,
        CASE 
            WHEN perc_acumulado_lucro > 95.0 THEN TRUE 
            ELSE FALSE 
        END AS bloqueio_compra_1p
    FROM pareto
    ORDER BY lucro_bruto DESC;
    """
    return duckdb.sql(query).df()


def filtrar_dados_sql(df: pd.DataFrame, categorias: list, classes: list) -> pd.DataFrame:
    query = """
    SELECT * 
    FROM df
    WHERE categoria IN $categorias
      AND classe_abc IN $classes
    """
    return duckdb.execute(query, {"categorias": categorias, "classes": classes}).df()


def calcular_kpis_sql(df: pd.DataFrame) -> dict:
    query = """
    SELECT 
        COALESCE(SUM(faturamento_total), 0) AS faturamento,
        COALESCE(SUM(lucro_bruto), 0) AS lucro_bruto,
        COALESCE(SUM(capital_imobilizado_estoque), 0) AS estoque_total,
        COALESCE(SUM(CASE WHEN classe_abc = 'Classe C' THEN capital_imobilizado_estoque ELSE 0 END), 0) AS estoque_classe_c
    FROM df;
    """
    return duckdb.sql(query).df().iloc[0].to_dict()