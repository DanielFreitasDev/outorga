# Regras jurídicas codificadas no motor

O motor (`src/outorga/engine.py`) é **determinístico**: recebe os fatos lidos dos documentos (já conferidos e
ancorados) e decide quem pode assinar a ATPV-e **por cada pessoa jurídica envolvida — vendendo ou comprando**.
A IA generativa **não decide**; ela lê. Cada regra abaixo tem
teste no corpus (`corpus/CENARIOS.md`) e fundamento citado no parecer.

Base normativa e prática administrativa pesquisadas em 16–17/10/2026: `docs/PESQUISA_JURIDICA.md`.

## 1. Regime vigente na data da venda

| Regra | Fundamento | Caso |
|---|---|---|
| Vale o ato societário em vigor na data da venda; alteração posterior substitui a cláusula alterada | Lei 8.934/94, art. 36 | C29 |
| Ato arquivado em até 30 dias produz efeito desde a assinatura; depois, desde o arquivamento | Lei 8.934/94, art. 36 | — |
| Ltda: administrador com prazo vencido e sem recondução perde o cargo | CC, art. 1.063 | C30 |
| S.A.: prazo de gestão se estende até a posse dos sucessores (alerta para confirmar eleição) | LSA, art. 150, §4º | — |
| Consolidação/estatuto consolidado substitui o contrato inteiro | — | C02 |

## 2. Quem representa a empresa

| Regra | Fundamento | Caso |
|---|---|---|
| Ser sócio (mesmo majoritário) não dá poder de representação; só o administrador | CC, arts. 1.060 e 1.064 | C04, C06 |
| Administrador não sócio designado no contrato representa | CC, art. 1.061 | C05 |
| "Isoladamente", "indistintamente", "qualquer deles", "de per si" = cada um assina sozinho | vocabulário societário; conferência léxica | C01 |
| "Em conjunto", "conjuntamente", "vedada a prática isolada" = todos juntos | CC, art. 1.014 | C02, C03 |
| Contrato omisso sobre a forma de atuação → atuação separada (art. 1.013), **mas vai para revisão** | CC, arts. 1.013 e 1.053 | C07 |
| Especialidade: cláusula do veículo específico > veículos > bens móveis/ativo > regra geral | interpretação contratual | C13, C14 |
| Restrição só sobre **imóveis** não alcança veículo (bem móvel) | CC, arts. 82 e 1.015 | C01 |
| Alçada por valor: só vale se o valor do veículo cruzar o limite; sem valor → indeterminado | contrato | C08–C10 |
| Exigência de aprovação de sócios (quórum) → precondição; ata com quórum suficiente satisfaz; todos os sócios assinando também | CC, arts. 1.071–1.076 | C11, C12, C38 |
| Revendedora: restrição a "ativo imobilizado" pode não alcançar o estoque → revisão | CC, art. 1.015 | C35 |
| S.A.: representação pelos diretores na forma do estatuto (combinações) | LSA, arts. 138 e 144 | C32, C33 |
| S.A. sem regra estatutária sobre alienação do ativo → autorização do Conselho | LSA, art. 142, VIII | — |
| Empresário individual: o titular assina pelo CNPJ | CC, art. 966 | C34 |
| Sociedade limitada unipessoal: o sócio único administrador assina | CC, art. 1.052, §1º | C31 |
| "Veda" dirigido a pessoas ("não lhes cabendo poderes") exclui essas pessoas; "vedada a prática isolada" é regra de assinatura conjunta | interpretação | C04, C02 |
| Anuência exigida por qualquer cláusula aplicável (mesmo que só imponha condição) entra em todas as combinações | contrato | teste de regressão |
| "2 (dois) Diretores" / "quaisquer dois dos três" = quaisquer N do cargo (N de M: vale N); a regra só completa a leitura da IA | interpretação | C33, H02 |

## 3. Procuração (delegação)

| Regra | Fundamento | Caso |
|---|---|---|
| Precisa ser outorgada **pela empresa** (PJ), não pelo sócio em nome próprio | CC, arts. 47 e 1.018 | C21 |
| Quem outorgou precisava ter, **na data da outorga**, poder para o ato — ninguém delega mais do que tem | CC, arts. 47 e 1.014 | C20 |
| Regra estatutária sobre outorga (ex.: "2 diretores") deve ser cumprida | estatuto | C33 |
| Poderes gerais de administração não bastam; alienar exige poder especial e expresso | CC, art. 661, caput e §1º | C17 |
| Procuração para veículo específico não serve para outro veículo | CC, art. 661, §1º; CJF, Enunciado 183 | C22 |
| Vencida → não vale | CC, art. 682, IV | C18 |
| Revogada antes da venda → não vale (revogação feita por outro administrador vale: a outorgante é a PJ) | CC, arts. 682, I, e 686 | C19 |
| Revogação genérica ("todas as procurações outorgadas a Fulano", "quaisquer procurações anteriores") alcança todas as anteriores daquele outorgado (ou todas) | CC, art. 682, I | teste de regressão |
| Revogação embutida em outro documento ("revogando a procuração anterior", "ficam revogadas as procurações") também vale; "poderá ser revogada" e "até revogação" não são revogação | CC, art. 682, I | teste de regressão |
| Revogação que não se liga a nenhuma procuração → alerta (revisão humana) | prudência | — |
| "Em conjunto com um Diretor" só restringe o procurador se estiver escrito na procuração ("representada conjuntamente por seus administradores" descreve quem outorga) | interpretação | H06 |
| Troca do administrador que outorgou **não** extingue o mandato da PJ | CC, art. 682; STJ, AgInt no REsp 1.997.964/SC | C28 |
| Procuradores "sempre em conjunto" → precisam assinar juntos | CC, art. 672 | C27 |
| "Em conjunto com um Diretor" → combinação procurador + diretor | estatuto/procuração | C33 |

## 4. Substabelecimento

| Regra | Fundamento | Caso |
|---|---|---|
| Permitido (ou omisso) → substabelecido herda os poderes e os limites da procuração de origem | CC, art. 667 | C23 |
| Vedado na procuração → atos do substabelecido não obrigam a empresa | CC, art. 667, §3º | C24 |
| Sem reserva → o substabelecente perde os poderes | CC, art. 667 | C25 |
| Herda vencimento, revogação e vícios da origem | — | — |
| Substabelecimento de substabelecimento: a cadeia é percorrida até a procuração original; vale com **alerta** (há órgãos que aceitam um só nível) | CC, art. 667 | teste de regressão |

## 5. Comprador pessoa jurídica (ATPV-e "vendendo ou comprando")

O § 7º fala do "antigo **ou** do novo proprietário" PJ. Cada lado PJ é verificado com os documentos **da própria
empresa** (separados pelo CNPJ/razão social citados em cada documento); pessoa física assina em nome próprio.

| Regra | Fundamento | Caso |
|---|---|---|
| Regra geral de representação vale para vender e para comprar | CC, arts. 47 e 1.022 | A01, A06 |
| Cláusula que atribui a administração/representação da sociedade "inclusive a venda de bens" continua sendo a regra geral (a venda é exemplo) e rege também a compra | interpretação contratual | A01, A06 (rodada cega) |
| Cláusula de **alienação** (venda) não alcança a compra; cláusula de **aquisição** não alcança a venda | interpretação estrita de cláusulas restritivas | A02, A03 |
| A IA às vezes rotula "aquisição de veículos acima de R$ X" como alienação: o léxico corrige o ato da regra | conferência léxica | teste de regressão |
| "Documentos que criem obrigações ou importem alienação" alcança as duas pontas (o preço é obrigação) | estatuto | — |
| Procuração só de venda não serve para comprar; para comprar, poder expresso de adquirir | CC, art. 661 (mandato interpreta-se estritamente) | A04, A05 |
| Procuração só com poderes gerais, usada para comprar → configurável (DETRAN-CE: bloqueio por exigir procuração específica) | CC, art. 661; DETRAN-CE | — |
| CRLV, CND e Conselho só se aplicam ao lado vendedor | CTB, art. 123 | — |
| PJ dos dois lados: o resultado geral é o do lado mais fraco | prudência | A06, A07 |
| Comprador PJ sem nenhum documento da empresa → faixa intermediária ("anexe o ato constitutivo") | prudência | — |
| Assinaturas já registradas na ATPV-e (quando houver) entram como assinantes de cada lado | — | A07 |

## 6. Todos os tipos de pessoa jurídica

| Tipo | Como se identifica quem assina | Caso |
|---|---|---|
| Sociedade limitada / unipessoal | contrato social (e alterações) | C01–C31 |
| S.A. | estatuto + ata de eleição da diretoria (combinações de diretores e procuradores) | C32, C33 |
| **Cooperativa** (Lei 5.764/71) | estatuto (cargos: "Diretor-Presidente em conjunto com o Diretor Financeiro") + **ata da AGO** que elegeu o Conselho; o motor casa o cargo da regra com o cargo do eleito ("Vice-Presidente" não vale por "Presidente") | A08, A09 |
| **Associação** (CC, arts. 53–61) | estatuto + ata de eleição da diretoria; registro no RCPJ | A10 |
| **Empresário individual / MEI** (CC, art. 966; LC 123, art. 18-A) | requerimento ou CCMEI: o titular assina; outra pessoa só com procuração | C34, A11, A12 |
| **EIRELI** | ato constitutivo; desde a Lei 14.195/2021 (art. 41) é sociedade limitada unipessoal: o titular administrador assina (aviso no parecer) | A13 |
| **Sociedade simples** (CC, arts. 997–1.038) | contrato social registrado no RCPJ (não na Junta) | A14 |
| Estatuto que não diz quem representa | revisão humana ("estatuto sem regra de representação") | teste de regressão |

Regras de estatuto com cargos (valem para cooperativas, associações e S.A.):

| Regra | Fundamento | Caso |
|---|---|---|
| Quando a cláusula nomeia o cargo que representa ("Compete ao Presidente representar…", "assinados pelo Diretor-Presidente em conjunto com o Diretor Financeiro"), só esse cargo assina — mesmo que a IA tenha lido "administradores". A conferência só **restringe**: um cargo só não afrouxa uma assinatura conjunta | estatuto | A08–A10 (rodada cega) |
| Conselho Fiscal e suplentes eleitos na mesma ata **não** são administradores e nunca representam | CC, arts. 1.066–1.070; LSA, arts. 161–165; Lei 5.764/71, art. 56 | A08, A10 (rodada cega) |
| Substituto "na ausência ou impedimento" do titular (ex.: Vice-Presidente): a ausência não é verificável → assinatura do substituto vai para revisão humana; a do titular segue normal | estatuto | teste de regressão |
| "Vice-Presidente" não vale por "Presidente" (qualificadores: vice, adjunto, suplente, substituto, segundo, interino) | estatuto | teste de regressão |

## 7. Consulta por CPF e pessoa física com procuração (chefe, 17/10/2026 11:40)

"Poderia ser até antes do ATPV": a entrada é o veículo + o CPF de quem vai assinar + vender/comprar. Só o lado desse CPF é
verificado; o proprietário vem da base veicular (ou do CRLV).

| Regra | Fundamento | Caso |
|---|---|---|
| Pessoa física: o próprio dono (ou comprador) assina em nome próprio — nada a comprovar além da identidade (CPF) | CC, art. 1.228 | P01 |
| CPF diferente do titular e nenhuma procuração que cite esse CPF → **pergunta pela procuração** (revisão humana, não recusa) — vale também para empresa quando o CPF não tem poder pelos atos | CC, arts. 653 e 661 | P03, P13 |
| A procuração tem de ser outorgada pelo **titular registral**; a do cônjuge (mesmo dizendo que o carro é do casal) não serve para assinar a ATPV-e | CTB, arts. 123 e 134; CC, art. 653 | P11 |
| Poderes gerais ("representar perante o DETRAN em tudo o que for necessário", licenciar, pagar IPVA) não autorizam vender | CC, art. 661, §1º | P04 |
| Procuração específica de outro veículo não serve | CC, art. 661, §1º | P06 |
| Vencida, revogada, particular (DETRAN-CE), substabelecimento vedado/sem reserva: mesmas regras da procuração de empresa | CC, arts. 667 e 682 | P05, P08, P09, P10 |
| Comprador pessoa física representado: procuração com poder de **comprar** | CC, art. 661 | P07 |
| Dono conferido na base veicular dispensa o CRLV anexado | CTB, art. 123 | P12 |

## 8. Política administrativa (configurável) — perfil **DETRAN-CE** (padrão)

Fonte: página do serviço de transferência do DETRAN-CE (gov.br): procurador "por instrumento de procuração
**pública e específica para o ato** (com validade de até **01 ano** da data de expedição)".

| Parâmetro | DETRAN-CE | Genérica (só Código Civil) |
|---|---|---|
| Procuração particular (com ou sem firma) | **bloqueio** | atenção / alerta |
| Procuração com mais de 365 dias da expedição | **bloqueio** | alerta (pedir certidão atualizada) |
| Substabelecimento particular | alerta (prática conservadora; não é regra expressa) | atenção |
| Procuração que não identifica o veículo | atenção ("específica para o ato": confirmar entendimento) | informação |
| CND previdenciária (ativo imobilizado acima de R$ 87.493,73) | informação | informação |
| Limiar de aceite automático (índice) | ≥ 85 | ≥ 85 |
| Limiar de recusa automática (índice) | ≤ 15 | ≤ 15 |

Mude na tela **Faixa intermediária** ou em `PUT /api/politica`. Toda mudança entra na trilha de auditoria.

Nos casos C26 (procuração particular) e C37 (procuração de 2023), o Código Civil aceitaria a procuração,
mas a política do DETRAN-CE recusa. O gabarito registra os dois resultados (`esperado` e `esperado_ce`).

## 9. Consulta sem assinantes

Sem assinantes informados (nem no pedido, nem na ATPV-e), o resultado é uma **consulta**: "quem pode assinar a ATPV-e
deste veículo", por lado, com veredito
indeterminado e faixa intermediária (nada é aceito sem saber quem vai assinar).

## 10. Titularidade e identidade

| Regra | Fundamento | Caso |
|---|---|---|
| O ATPV é emitido em nome do proprietário no RENAVAM: CRLV no CPF do sócio (mesmo com o carro integralizado) → revisão para regularizar | CTB, art. 123 | C15 |
| CRLV de terceiro → bloqueio | CTB, art. 123 | — |
| Assinante identificado por CPF; só pelo nome → atenção | — | C01 |

## 11. O que a firma reconhecida NÃO resolve

O reconhecimento de firma prova **autoria**, não **poderes**. O Código de Normas do CE exige que o reconhecimento
mencione que "não comprova os poderes de representação". Por isso a verificação de poderes é tarefa do órgão
de trânsito — e a Res. CONTRAN 1.027/2026, art. 28, §7º, passou a exigir a "comprovação eletrônica dos poderes
do signatário" quando o antigo ou o novo proprietário é pessoa jurídica.
