"""A taxonomia é a fonte única de verdade — estes testes travam suas invariantes."""

from apps.baseline import taxonomia as tx


def test_dezoito_situacoes_em_oito_categorias():
    assert len(tx.SITUACOES) == 18
    assert len(tx.CATEGORIAS) == 8


def test_codigos_sao_unicos_e_ascii_snake_case():
    # Situações, categorias e estados são namespaces independentes: cada um deve ter códigos únicos
    # dentro de si, mas a mesma string pode aparecer em namespaces diferentes (ex: "outro").

    situacoes = [c for c, _ in tx.SITUACOES]
    categorias = [c for c, _ in tx.CATEGORIAS]
    estados = [c for c, _ in tx.ESTADOS]

    # Unicidade dentro de cada namespace
    assert len(situacoes) == len(set(situacoes)), "Código duplicado em SITUACOES"
    assert len(categorias) == len(set(categorias)), "Código duplicado em CATEGORIAS"
    assert len(estados) == len(set(estados)), "Código duplicado em ESTADOS"

    # Formato ASCII, minúsculo, sem espaço, sem hífen — em todos os códigos
    for c in situacoes + categorias + estados:
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


def test_outro_existe_nos_dois_namespaces_e_isso_e_de_proposito():
    # Situação e estado são namespaces independentes: cada um tem sua válvula de escape.
    assert "outro" in tx.CODIGOS_SITUACAO
    assert "outro" in tx.CODIGOS_ESTADO


def test_cinco_substituicoes_com_os_codigos_que_ja_existiam_no_banco():
    # Os códigos precisam bater com os de Substitution.categoria — a migração lê deles.
    assert [c for c, _ in tx.SUBSTITUICOES] == [
        "oral", "movimento", "social", "cognitivo", "ambiental"
    ]
    assert tx.CODIGOS_SUBSTITUICAO == {"oral", "movimento", "social", "cognitivo", "ambiental"}


def test_rotulos_das_substituicoes_nao_sao_listas_fechadas():
    """O bug real: o rótulo "Movimento (caminhar, alongar)" era lido como menu fechado, e uma
    corrida parecia não caber. O rótulo novo diz explicitamente que cabe."""
    movimento = tx.rotulo_substituicao("movimento")
    assert "correr" in movimento
    assert "qualquer coisa com o corpo" in movimento
    # Respirar e "surfar a onda" ganham casa explícita em cognitivo.
    cognitivo = tx.rotulo_substituicao("cognitivo")
    assert "respirar" in cognitivo
    assert "esperar a onda passar" in cognitivo


def test_rotulo_substituicao_devolve_o_proprio_codigo_se_desconhecido():
    assert tx.rotulo_substituicao("inexistente") == "inexistente"


def test_lista_substituicoes_e_o_payload_da_api():
    itens = tx.lista_substituicoes()
    assert len(itens) == 5
    assert itens[1] == {"codigo": "movimento", "rotulo": tx.rotulo_substituicao("movimento")}


def test_nao_existe_outro_em_substituicoes():
    # Diferente do gatilho: o campo é opcional, e vazio ("") já significa "não registrei".
    assert "outro" not in tx.CODIGOS_SUBSTITUICAO
