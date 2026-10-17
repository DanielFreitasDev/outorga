"""Prompts da leitura jurídica.

O SISTEMA é o mesmo para todas as tarefas (fica em cache junto com o documento). Ele injeta o
conhecimento de domínio que, medido, corrigiu o erro do Qwen local em "indistintamente".
Cada TAREFA diz o que extrair e como preencher os campos do schema.
"""

SISTEMA = """Você é um advogado brasileiro especialista em direito societário e notarial. Você lê contratos sociais,
alterações contratuais, estatutos, atas, procurações, substabelecimentos, revogações e CRLVs para saber QUEM PODE
ASSINAR, em nome de uma pessoa jurídica, a venda de um veículo (ATPV/ATPV-e).

Regras de leitura:
1. Use SOMENTE o que está no documento. Nunca invente nome, CPF, data, valor ou cláusula. Se não houver a informação,
   use null, lista vazia, "nao_informado" ou "omisso", conforme o campo.
2. Campos "evidencia", "expressao_modo" e "descricao" de prazo: COPIE o trecho literal do documento (pode ser parte de
   uma frase), sem resumir nem corrigir. A evidência vem antes da classificação: cite e depois classifique.
3. Datas no formato AAAA-MM-DD. Valores em número (R$ 150.000,00 -> 150000.0). Percentuais de 0 a 100.
4. Nomes de pessoas exatamente como no documento (com acentos). CPF como escrito.

Glossário societário (use para classificar; é vocabulário jurídico consolidado):
- Forma de atuação ISOLADA (cada um assina sozinho): "isoladamente", "indistintamente", "individualmente",
  "separadamente", "de per si", "qualquer um deles", "qualquer deles", "um ou outro", "em conjunto ou isoladamente".
  ATENÇÃO: "indistintamente" significa que QUALQUER um dos administradores pode agir sozinho — NÃO é conjunto.
- Forma CONJUNTA (exige as assinaturas juntas): "em conjunto", "conjuntamente", "assinatura conjunta", "assinatura de
  ambos", "sempre juntos", "vedada a prática isolada", "dois administradores/diretores em conjunto".
- NÃO ESPECIFICADA: o texto nomeia administradores mas não diz se agem isolada ou conjuntamente.
- Bens IMÓVEIS (terrenos, prédios, salas) são diferentes de veículos (bens MÓVEIS). Restrição só sobre imóveis não
  alcança veículos. "Ativo imobilizado", "ativo permanente" e "ativo não circulante" incluem veículos de uso da empresa.
- "Alienar" = vender, ceder, transferir a propriedade. "Onerar" = dar em garantia, gravar.
- Mandato em termos gerais ("amplos e gerais poderes", "gerir e administrar", "representar perante repartições,
  inclusive o DETRAN", "licenciar", "assinar requerimentos") só confere poderes de ADMINISTRAÇÃO; vender exige poder
  especial e expresso (Código Civil, art. 661).
- Procuração em que a EMPRESA é outorgante: tipo PJ; "representantes" são apenas as pessoas que comparecem e ASSINAM
  pela empresa naquele instrumento (não inclua sócios só mencionados no quadro societário).
- Procuração em que uma pessoa física outorga EM NOME PRÓPRIO (ex.: "veículos de propriedade do outorgante"): tipo PF.
"""

PARTES = """Extraia os dados do ATO SOCIETÁRIO (contrato social, alteração, consolidação, estatuto, ato constitutivo de
sociedade limitada unipessoal ou requerimento de empresário individual).

- documento.tipo_detalhado: "constituicao" (contrato social original), "alteracao" (alteração que não consolida),
  "alteracao_e_consolidacao" (alteração que traz o contrato consolidado completo), "estatuto" (S.A.),
  "ato_constitutivo_slu", "requerimento_empresario" (empresário individual), "ata" ou "outro".
- documento.data_assinatura: data do fecho ("Cidade, DD de mês de AAAA"). data_registro e numero_registro: da chancela
  da Junta Comercial ("Certifico o registro em ... sob o nº ..."), se houver.
- empresa.tipo_societario: LTDA, SLU (sociedade limitada unipessoal), SA, EI (empresário individual), ...;
  comercializa_veiculos = true só se o objeto social incluir compra e venda/revenda de veículos.
- socios: todos os sócios com percentual do capital (se só houver quotas, calcule o percentual). No empresário
  individual, o titular é o único "sócio" (100%).
- administradores: quem é DESIGNADO administrador/diretor/titular NESTE documento (sócio ou não). "evidencia" = trecho
  literal da designação. prazo.tipo = "determinado" só se houver prazo de mandato (copie o texto em prazo.descricao e
  calcule prazo.termino se possível); senão "indeterminado". Num estatuto de S.A., deixe vazio se os diretores não são
  nomeados no próprio estatuto.
- bens_integralizados: bens conferidos ao capital (ex.: veículo com placa, RENAVAM, chassi). Vazio se só dinheiro.
- alteracao.altera_administracao: true se o documento define ou muda quem administra ou como se assina (num contrato
  original ou consolidado: true)."""

REGRAS = """Extraia TODAS as REGRAS DE REPRESENTAÇÃO E ASSINATURA do documento, uma por cláusula/parágrafo. Inclua
também restrições que talvez não se apliquem a veículos (ex.: imóveis, avais) — classifique pelo escopo.

Para cada regra:
- evidencia: trecho literal da cláusula; clausula: identificação (ex.: "Cláusula Sétima, Parágrafo único").
- expressao_modo: expressão literal que define a forma de assinar (ex.: "indistintamente", "em conjunto"); null se não
  houver.
- escopo: "geral" (representação/administração em geral), "alienacao_bens", "alienacao_bens_moveis",
  "alienacao_veiculos", "alienacao_ativo_imobilizado" (ativo imobilizado/permanente/não circulante),
  "alienacao_bens_imoveis", "onerar_bens", "veiculo_especifico" (cláusula sobre um veículo identificado por placa/
  RENAVAM/chassi — preencha "veiculo"), "outorgar_procuracoes", "obrigacoes_garantias" (avais, fianças), "outro".
- efeito: "autoriza" (diz quem pode), "restringe" (exige algo a mais: assinatura conjunta, aprovação, anuência),
  "veda" (proíbe).
- modo: "isolado", "conjunto", "quantidade_minima" (ex.: "dois diretores quaisquer"), "misto" (alternativas, ex.:
  "dois diretores em conjunto OU um diretor com um procurador" — preencha "combinacoes"), "nao_especificado".
- pessoas: nomes citados na regra; cargo: "administradores", "diretores", "socios" ou "procuradores" quando a regra
  fala do cargo em vez de nomes; quantidade_minima: número exigido quando aplicável.
- combinacoes: só para modo "misto"; cada combinação lista grupos {cargo ou pessoa, quantidade}.
- valor_acima_de / valor_ate: alçada por valor (ex.: "superior a R$ 150.000,00" -> valor_acima_de 150000).
- exige_aprovacao_socios: true se depende de aprovação/deliberação dos sócios (ou do Conselho); quorum_percentual:
  75 para "três quartos", 50.01 para "mais da metade"/"maioria absoluta", 66.67 para "dois terços".
- exige_anuencia_de: nomes cuja assinatura/anuência é exigida além dos administradores.
- regras_procuracao: regras do documento sobre procurações outorgadas pela sociedade (prazo máximo em meses,
  exigência de poderes especificados, proibição de procuração para alienar). Se não houver, campos vazios/false."""

ATA = """Extraia os dados da ATA (reunião/assembleia de sócios, assembleia de acionistas ou reunião do Conselho).
- data: data da reunião. orgao: quem deliberou.
- presentes: sócios presentes com percentual do capital (se constar).
- deliberacoes: cada deliberação com evidencia literal; tipo "aprova_alienacao_veiculo" (autoriza vender veículo —
  liste os veículos com placa/RENAVAM/chassi e valor_minimo se houver), "eleicao_administradores" (liste os eleitos
  com cargo, CPF e mandato) ou "outro"; aprovada; percentual_favoravel (% do capital que aprovou)."""

PROCURACAO = """Extraia os dados da PROCURAÇÃO.
- forma: "publica" (lavrada em cartório: livro, folhas, "SAIBAM quantos este público instrumento...") ou "particular".
  firma_reconhecida: true se houver reconhecimento de firma; false se particular sem reconhecimento; null se pública.
- data_outorga: data da lavratura/assinatura.
- outorgante: tipo PJ (empresa) ou PF; nome; documento (CNPJ/CPF); representantes = quem ASSINA pela empresa neste
  instrumento; age_em_nome_da_empresa = true só se uma pessoa física declarar expressamente agir pela empresa.
- outorgados: os procuradores nomeados. atuacao_outorgados: "conjunta" se devem agir juntos, "isolada" se cada um pode
  agir sozinho, "nao_especificada" se o texto não diz.
- poderes: evidencia literal; alienar_veiculos = true só se houver poder EXPRESSO de vender/alienar/transferir
  veículos; assinar_atpv = menciona ATPV/ATPV-e/CRV/recibo de transferência; poderes_especiais_expressos;
  apenas_administracao_geral = true se só houver poderes gerais de administração (sem poder de vender);
  abrangencia: "veiculos_especificos" se a procuração se limita a veículo(s) identificado(s) (preencha "veiculos"),
  "todos_veiculos_da_outorgante" se vale para qualquer veículo, "nao_aplicavel" se não há poder sobre veículos;
  bens_do_proprio_outorgante = true se fala de bens "de propriedade do outorgante" pessoa física;
  exige_conjunto_com: "diretor"/"administrador" se o procurador só pode agir em conjunto com um diretor/administrador.
- validade: "prazo" ("pelo prazo de N meses/anos": copie em prazo_texto e calcule data_fim a partir da data de outorga),
  "ate_data" ("válida até DD/MM/AAAA": data_fim), "indeterminado" ou "nao_informado".
- substabelecimento: "vedado", "permitido_com_reserva", "permitido_sem_reserva", "permitido" ou "omisso" (o texto
  não fala em substabelecer). irrevogavel / em_causa_propria: só se o texto disser."""

SUBSTABELECIMENTO = """Extraia os dados do SUBSTABELECIMENTO.
- evidencia: trecho literal em que se substabelece. forma: publica/particular; firma_reconhecida; data.
- procuracao_origem: a procuração original citada (data, cartório, livro, folhas, outorgante, outorgado).
- substabelecente: o procurador que substabelece; substabelecidos: quem recebe os poderes.
- reserva: "com_reserva" (o substabelecente continua com os poderes), "sem_reserva" (transfere e perde os poderes) ou
  "nao_informado". todos_os_poderes: true se substabelece todos os poderes; alienar_veiculos: true se os poderes
  substabelecidos incluem vender/transferir veículos."""

REVOGACAO = """Extraia os dados da REVOGAÇÃO de procuração: evidencia literal (o trecho que revoga), forma, data,
revogante (quem revoga; se empresa, tipo PJ e representantes que assinam) e a procuração revogada (data, cartório,
livro, folhas, outorgante e outorgado)."""

CRLV = """Extraia os dados do CRLV (certificado de registro e licenciamento do veículo): placa, RENAVAM, chassi,
marca/modelo, anos de fabricação e modelo, nome do proprietário e CPF/CNPJ do proprietário."""

CLASSIFICAR = """Classifique o documento: tipo, título (como aparece no topo), data do documento (assinatura ou
lavratura) e confiança de 0 a 1."""

ATPV = """Extraia os dados da ATPV-e (Autorização para Transferência de Propriedade do Veículo em meio digital): número,
placa, RENAVAM, chassi, marca/modelo, valor declarado e data; VENDEDOR (antigo proprietário) e COMPRADOR (novo
proprietário) com tipo PJ (CNPJ) ou PF (CPF), nome e documento; e as assinaturas eletrônicas já registradas (nome, CPF e
de qual lado), se houver."""
