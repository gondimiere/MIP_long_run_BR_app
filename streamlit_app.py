# -*- coding: utf-8 -*-
"""MIP Long-Run Brasil 1965–2021 (V2.2, COMMON17): explorador interativo em Streamlit.
Dados: streamlit_app/dados_app.npz (gerado por V2_2/scripts/s9_dados_app.py a partir do dashboard). Convenção: linhas = fornecedores i, colunas = usuários j."""
import json
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

AQUI = os.path.dirname(os.path.abspath(__file__))
PAINEIS = os.path.join(AQUI, "V2_2", "dashboard", "paineis")

st.set_page_config(page_title="MIP Long-Run Brasil V2.2", page_icon="📊", layout="wide")

SERIES = {
    "candidate": dict(label="V2.2 total (doméstico + importado)", color="#2563eb", width=3.2, dash="solid", mode="lines"),
    "domestic": dict(label="V2.2 doméstica", color="#009e73", width=2.6, dash="solid", mode="lines"),
    "wiod": dict(label="Backbone LR-WIOD (total)", color="#667085", width=2.2, dash="dash", mode="lines"),
    "ibge": dict(label="IBGE âncora (total)", color="#d55e00", width=0, dash="solid", mode="markers"),
    "ibge_dom": dict(label="IBGE âncora (doméstica)", color="#7a3fb0", width=0, dash="solid", mode="markers"),
    "nereus": dict(label="NEREUS 1995–2009 (Guilhoto)", color="#c026d3", width=2.6, dash="solid", mode="lines"),
}
SEGMENTOS = {
    "MIP_IBGE_ANCORA": "âncora: MIP do IBGE", "INTERPOLADO_ENTRE_ANCORAS": "estimado entre âncoras", "EXTRAPOLADO_1965_69": "extrapolado (campo de 1970)",
    "PONTE_1997_99": "ponte linear 1996→2000", "APF_OBSERVADA": "A-P&F observada",
}
OBJETOS = {
    "A": dict(nome="Coeficientes técnicos (A)", eixo="R$ de insumo por R$ 1 de produção bruta"),
    "Z": dict(nome="Transações intersetoriais (Z)", eixo="R$ bilhões de agosto de 2026"),
    "L": dict(nome="Inversa de Leontief (L)", eixo="R$ de produção por R$ 1 de demanda final"),
    "M": dict(nome="Multiplicadores de produção", eixo="R$ totais por R$ 1 de demanda final"),
}


@st.cache_data
def carregar():
    z = np.load(os.path.join(AQUI, "streamlit_app", "dados_app.npz"), allow_pickle=False)
    return {k: z[k] for k in z.files}


D = carregar()
anos = D["years"]; codigos = [str(c) for c in D["codes"]]; nomes = [str(n) for n in D["names"]]; segmento = [str(s) for s in D["segment"]]


def valor(src, obj, setor, contra, direcao):
    chave = f"{src}__{obj}"
    if chave not in D:
        return None
    a = D[chave]; ys = D[f"{src}__years"]
    if obj == "M":
        return pd.Series(a[:, setor], index=ys)
    return pd.Series(a[:, contra, setor] if direcao == "compras" else a[:, setor, contra], index=ys)


st.title("MIP Long-Run Brasil 1965–2021")
st.caption("Série V2.2 (COMMON17, 17 setores) · final com ressalvas · explorador interativo")

with st.sidebar:
    st.header("1 · Setor focal")
    setor = st.selectbox("Setor", range(17), format_func=lambda i: f"{i + 1:02d} · {nomes[i]}", label_visibility="collapsed")
    st.header("2 · Objeto")
    obj = st.radio("Objeto", list(OBJETOS), format_func=lambda k: OBJETOS[k]["nome"], label_visibility="collapsed")
    direcao, contra = "compras", 0
    if obj != "M":
        st.header("3 · Relação")
        direcao = st.radio("Perspectiva", ["compras", "vendas"], format_func=lambda d: "Compras do setor (fornecedores → setor)" if d == "compras" else "Vendas do setor (setor → compradores)")
        contra = st.selectbox("Setor fornecedor" if direcao == "compras" else "Setor comprador", range(17), format_func=lambda i: f"{i + 1:02d} · {nomes[i]}")
    st.header("Séries")
    padrao = {"candidate": True, "domestic": False, "wiod": True, "ibge": True, "ibge_dom": False, "nereus": True}
    visiveis = []
    for k, m in SERIES.items():
        if obj == "Z" and k in ("wiod", "ibge", "ibge_dom", "nereus"):
            continue
        if st.checkbox(m["label"], value=padrao[k], key=f"s_{k}"):
            visiveis.append(k)
    faixa = st.select_slider("Intervalo", options=[int(a) for a in anos], value=(int(anos[0]), int(anos[-1])))

fornecedor_txt = "toda a economia" if obj == "M" else (nomes[contra] if direcao == "compras" else nomes[setor])
comprador_txt = nomes[setor] if (obj == "M" or direcao == "compras") else nomes[contra]
titulo = f"Multiplicador de {nomes[setor]}" if obj == "M" else f"{OBJETOS[obj]['nome']}: {fornecedor_txt} → {comprador_txt}"

aba_graf, aba_paineis, aba_dados, aba_sobre = st.tabs(["Gráfico", "Visão geral (painéis)", "Dados", "Método e ressalvas"])

with aba_graf:
    st.subheader(titulo)
    fig = go.Figure()
    a, b = faixa
    fig.add_vrect(x0=1965, x1=1969.5, fillcolor="#667085", opacity=0.07, line_width=0, layer="below")
    fig.add_vrect(x0=1996, x1=2000, fillcolor="#d55e00", opacity=0.10, line_width=0, layer="below",
                  annotation_text="quebra de fonte", annotation_position="top", annotation_font_size=11)
    fig.add_vrect(x0=2000, x1=2021.5, fillcolor="#009e73", opacity=0.04, line_width=0, layer="below")
    tabela = {}
    for k in visiveis:
        s = valor(k, obj, setor, contra, direcao)
        if s is None:
            continue
        s = s[(s.index >= a) & (s.index <= b)]; tabela[SERIES[k]["label"]] = s; m = SERIES[k]
        if m["mode"] == "markers":
            fig.add_trace(go.Scatter(x=s.index, y=s.values, mode="markers", name=m["label"], marker=dict(color=m["color"], size=9, symbol="diamond", line=dict(color="white", width=1))))
        else:
            fig.add_trace(go.Scatter(x=s.index, y=s.values, mode="lines", name=m["label"], line=dict(color=m["color"], width=m["width"], dash=m["dash"]),
                                     hovertemplate="%{x}: %{y:.6g}<extra>" + m["label"] + "</extra>"))
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=30, b=10), xaxis=dict(title="Ano", range=[a, b]), yaxis=dict(title=OBJETOS[obj]["eixo"]),
                      legend=dict(orientation="h", y=-0.2), hovermode="x unified", template="plotly_white")
    st.plotly_chart(fig, width="stretch")
    st.caption("Faixa laranja: 1996–2000, quebra de fonte (MIP do IBGE → A-P&F); 1997–99 é ponte, não dado observado. Cinza: 1965–69 extrapolado do campo de 1970.")

    cand = valor("candidate", obj, setor, contra, direcao)
    if cand is not None:
        v = lambda t: float(cand.loc[t])
        salto = v(2000) - v(1996)
        c = st.columns(6)
        c[0].metric("V2.2 em 1965", f"{v(1965):.4g}"); c[1].metric("V2.2 em 1996", f"{v(1996):.4g}", help="última MIP do IBGE")
        c[2].metric("V2.2 em 2000", f"{v(2000):.4g}", help="primeiro ano da A-P&F"); c[3].metric("V2.2 em 2021", f"{v(2021):.4g}")
        c[4].metric("Salto 1996→2000", f"{salto:+.4g}", f"{salto / abs(v(1996)) * 100:+.1f}%" if v(1996) else None, delta_color="off", help="majoritariamente quebra de fonte, não mudança técnica")
        c[5].metric("Intervalo V2.2", f"{cand.min():.3g} — {cand.max():.3g}")
    ano = st.slider("Procedência de um ano", int(anos[0]), int(anos[-1]), 1996)
    st.info(f"{ano}: {SEGMENTOS.get(segmento[list(anos).index(ano)], segmento[list(anos).index(ano)])}")

with aba_paineis:
    pasta = {"A": "A", "Z": "Z_BRL_2026", "L": "L"}.get(obj)
    sufixo = codigos[setor].replace("+", "_")
    caminho = os.path.join(PAINEIS, "multiplicadores", "multiplicadores_17_setores.png") if obj == "M" else os.path.join(PAINEIS, pasta, f"usuario_{setor + 1:02d}_{sufixo}.png")
    if os.path.exists(caminho):
        st.image(caminho, caption=f"{OBJETOS[obj]['nome']} · {nomes[setor]} (cada minigráfico = um fornecedor; faixa laranja = 1996–2000)", width="stretch")
    else:
        st.warning("Painel PNG não encontrado no repositório.")

with aba_dados:
    if tabela:
        df = pd.concat(tabela, axis=1).sort_index(); df.index.name = "ano"
        st.dataframe(df, width="stretch", height=420)
        st.download_button("Baixar CSV da relação", df.to_csv(sep=";", decimal=",").encode("utf-8-sig"), file_name=f"{obj}_{setor + 1:02d}_{contra + 1:02d}.csv", mime="text/csv")
    else:
        st.write("Selecione ao menos uma série na barra lateral.")

with aba_sobre:
    meta = json.loads(str(D["meta"]))
    st.markdown(
        """
**1965–1996.** 11 MIPs do IBGE como âncoras (1970, 75, 80, 85, 90–96). Entre âncoras, `A` doméstica da V2.1 e `A_m` (importada) do backbone LR-WIOD com campo; 1965–69 repete o campo de 1970. Erro de `A_total` de ~14% (36% em 1970) quando `A_d` também é estimado.

**1997–1999 e 2000–2021.** 1997–99 é uma ponte entre a MIP de 1996 e a A-P&F de 2000; a ponte de `A_d` não é linear simples. Em 2000–21, os dados são os da A-P&F. **O salto 1996→2000 é majoritariamente quebra de fonte:** não leia janelas que o cruzam como mudança técnica nem como substituição de importações.

**Total e doméstico.** `A_total = A_d + A_m`. Âncoras do IBGE aparecem em losangos (total e doméstica). Não há âncora em Z.

**Valores monetários.** Z em R$ bilhões de agosto de 2026, com deflator escalar (PIB real/corrente do Banco Mundial × IPCA), não setorial.

**NEREUS (Guilhoto), 1995–2009.** 42 setores, base CN 2000, agregados a 17 grupos. Outra classificação e conceito próximo ao doméstico; os níveis diferem 30–47% mesmo onde as fontes deveriam coincidir. Compare trajetória, não nível. Sem Z.

**Outras ressalvas.** Nível de produção com erro médio de ~5% (até ~9%); serviços pré-1980 limitados à cobertura das MIPs; 1989/90 é descontinuidade de fonte; substituição de importações só se lê entre âncoras; `y<0` em quatro células é artefato do fechamento; a interpolação linear simples de `A_d` supera a regra da V2.1 nas âncoras interiores (limitação conhecida, candidata a V2.3).

Status: **V2.2 final com ressalvas.** Relatório metodológico, dicionário de dados e manifesto de hashes em `V2_2/`.
"""
    )
    st.caption(f"Convenção: {meta.get('matrix_axis_convention')} · multiplicadores: {meta.get('multipliers_definition')}")
