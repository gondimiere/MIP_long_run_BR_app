# MIP Long-Run Brasil 1965–2021 — explorador interativo (V2.2)

App Streamlit para explorar a série longa de matrizes insumo-produto do Brasil (17 setores, COMMON17), 1965–2021: coeficientes técnicos (A), transações (Z), inversa de Leontief (L) e multiplicadores, com as MIPs do IBGE como âncoras e o NEREUS (1995–2009) para comparação de trajetória.

**Status da série: V2.2 final com ressalvas.** Principais ressalvas:
- 1996→2000 é janela de quebra de fonte (MIP do IBGE → A-P&F); 1997–99 é ponte, não dado observado.
- Erro de `A_total` de ~14% (36% em 1970) quando `A_d` também é estimado; nível de produção com erro médio de ~5%.
- Serviços pré-1980 limitados à cobertura das MIPs; 1989/90 é descontinuidade de fonte.

Rodar localmente:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Este repositório contém só o app, os dados exibidos (`streamlit_app/dados_app.npz`) e os painéis PNG. Método, dicionário de dados, scripts e manifesto de hashes ficam no repositório da dissertação (privado).
