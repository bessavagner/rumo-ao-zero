"""A taxonomia é a fonte única de verdade — estes testes travam suas invariantes."""

from apps.baseline import taxonomia as tx


def test_dezoito_situacoes_em_oito_categorias():
    assert len(tx.SITUACOES) == 18
    assert len(tx.CATEGORIAS) == 8


def test_codigos_sao_unicos_e_ascii_snake_case():
    codigos = [c for c, _ in tx.SITUACOES] + [c for c, _ in tx.CATEGORIAS] + [c for c, _ in tx.ESTADOS]
    assert len(codigos) == len(set(codigos))
    for c in codigos:
        assert c.isascii() and c.islower() and " " not in c and "-" not in c


def test_toda_situacao_menos_outro_tem_categoria_valida():
    validas = {c for c, _ in tx.CATEGORIAS}
    for codigo, _ in tx.SITUACOES:
        if codigo == "outro":
            continue
        assert tx.SITUACAO_CATEGORIA[codigo] in validas


def test_categoria_de_deriva_e_e_none_para_outro():
    assert tx.categoria_de("tristeza_solidao") == "emocoes_desagradaveis"
    assert tx.categoria_de("fim_expediente") == "urges_tentacoes"  # ritual de horário, não emoção
    assert tx.categoria_de("bebendo") == "urges_tentacoes"
    assert tx.categoria_de("outro") is None
    assert tx.categoria_de("codigo_inexistente") is None


def test_grupos_gatilhos_cobre_todas_as_situacoes_uma_vez():
    payload = tx.grupos_gatilhos()
    vistos = [s["codigo"] for g in payload["grupos"] for s in g["situacoes"]]
    vistos += [s["codigo"] for s in payload["sem_categoria"]]
    assert sorted(vistos) == sorted(c for c, _ in tx.SITUACOES)
    assert [s["codigo"] for s in payload["sem_categoria"]] == ["outro"]
    assert payload["grupos"][0]["rotulo"] == "Emoções desagradáveis"


def test_normalizar_tira_acento_caixa_e_espaco_duplicado():
    assert tx.normalizar("  Fim do  Expediente ") == "fim do expediente"
    assert tx.normalizar("Cansaço") == "cansaco"


def test_classificar_gatilho_colapsa_as_variacoes_do_bug_original():
    # O bug que originou a spec: duas digitações, duas barras.
    assert tx.classificar_gatilho("fim de expediente")[0] == "fim_expediente"
    assert tx.classificar_gatilho("Fim do expediente")[0] == "fim_expediente"
    assert tx.classificar_gatilho("bati de frente com o chefe")[0] == "discussao_atrito"
    assert tx.classificar_gatilho("xyzzy nada a ver") == (None, None)


def test_classificar_estado_colapsa_cansaco_e_solidao():
    assert tx.classificar_estado("cansaço")[0] == "cansaco"
    assert tx.classificar_estado("cansado")[0] == "cansaco"
    assert tx.classificar_estado("solidão")[0] == "solidao"
    assert tx.classificar_estado("solitário")[0] == "solidao"
