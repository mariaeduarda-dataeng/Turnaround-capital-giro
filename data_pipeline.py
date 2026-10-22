import pandas as pd

def aplicar_diretrizes_operacionais(df: pd.DataFrame) -> pd.DataFrame:
    df_resultado = df.copy()
    
    def definir_acao(row):
        if row["bloqueio_compra_1p"]:
            return "BLOQUEIO 1P: Liquidar / Migrar para 3P"
        elif row["pme_dias_cobertura"] <= 35:
            return "PRIORIDADE: Reabastecimento Imediato"
        else:
            return "CADENCIADO: Reposição Normal"
            
    df_resultado["diretriz_compras"] = df_resultado.apply(definir_acao, axis=1)
    return df_resultado


def simular_cenario_credito(modelo: str, pmp_medio: int) -> dict:
    if "Banco Parceiro" in modelo:
        pmr = 30
        gap = pmr - pmp_medio
        return {
            "status": "success",
            "titulo": "Cenário Turnaround (Resolução Proposta)",
            "pmr": pmr,
            "pmp": pmp_medio,
            "gap": gap,
            "pdd": "R$ 0,00 (100% transferido ao banco)",
            "detalhes": f"A varejista recebe em D+{pmr}, ou seja, {abs(gap)} dias antes de pagar os fornecedores."
        }
    else:
        pmr = 450
        gap = pmr - pmp_medio
        return {
            "status": "error",
            "titulo": "Cenário Legado (Efeito Tesoura em Ação)",
            "pmr": pmr,
            "pmp": pmp_medio,
            "gap": gap,
            "pdd": "Absorvido pelo balanço (Prejuízo direto)",
            "detalhes": f"Buraco de liquidez de +{gap} dias descobertos exigindo empréstimos bancários contínuos."
        }