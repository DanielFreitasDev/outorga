# Outorga — resumo para a chefia

**Demonstração on-line:** https://outorga.cepify.com.br (dados fictícios). Código: repositório `outorga` no GitHub.

## O pedido (como entendi, com as respostas de 17/10/2026)

Um agente que, **antes da assinatura da ATPV-e**, lê o contrato social (e alterações), estatutos, atas, procurações e
substabelecimentos e responde **se quem vai assinar tem poder — vendendo ou comprando** — e, se não tiver, quem
teria: um sócio, dois em conjunto, só um sócio específico (ex.: o que integralizou aquele carro no capital), o
Presidente com o Tesoureiro, um procurador… Leitura **semântica**, com **faixa intermediária de aceitação**: a IA
generativa lê, mas o resultado sai num índice 0–100 com três faixas (aceito · revisão humana · recusado) e limites
ajustáveis.

Respostas do chefe: entrada principal = **ATPV-e**; **todos os tipos de empresa**; verificar **vendendo ou
comprando**; **local, como um agente**; foco **só no digital**. Depois (17/10, 11:40): **"poderia ser até antes do
ATPV"** — a pessoa informa um CPF; se o veículo for de empresa, verifica se esse CPF tem poder para vender (ou comprar);
e, **mesmo sendo pessoa física**, se o CPF for diferente do vendedor ou do comprador, **pergunta se tem procuração** e
confere na procuração se aquele CPF tem poder de transferir o veículo. Ainda sem resposta: o significado exato da
"faixa intermediária" (segue o modelo de três faixas).

## Por que agora

- **Res. CONTRAN nº 1.027/2026, art. 28, §7º** (DOU 18/08/2026): quando o antigo **ou o novo** proprietário é PJ, a assinatura da ATPV-e só é
  admitida com **comprovação eletrônica dos poderes do signatário** — outorgante, outorgado, poderes, prazo e
  revogação. A forma nacional dessa comprovação ainda não foi publicada (até 17/10/2026). Adequação: ~16/11/2026.
- **Provimento CNJ nº 252/2026**: a plataforma federal de venda digital não aceita PJ "em razão da inviabilidade de
  verificação automatizada e segura de poderes societários".
- **Firma reconhecida prova autoria, não poderes** — o Código de Normas do CE exige que o reconhecimento diga isso.
- **DETRAN-CE**: procurador só com procuração **pública e específica**, válida até **1 ano** da expedição.

O Outorga faz exatamente essa verificação e entrega o parecer nos cinco elementos do §7º.

## O que existe hoje (protótipo funcionando)

- **Consulta por CPF, antes da ATPV-e**: veículo + CPF + vender/comprar. O dono vem da base veicular (simulada no
  protótipo). Empresa: confere o CPF nos atos e procurações. Pessoa física: o próprio dono passa direto; outro CPF →
  "tem procuração?" → confere se a procuração é do dono, dá poder para o ato e para aquele veículo, está no prazo, não foi
  revogada e é pública (DETRAN-CE).
- **ATPV-e como entrada**: o agente lê dela veículo, vendedor, comprador (CPF/CNPJ), valor, data e assinaturas já
  registradas; separa os documentos de cada empresa pelo CNPJ e verifica **cada lado PJ** (vendedor e comprador). Com
  PJ dos dois lados, vale o lado mais fraco.
- **Todos os tipos de PJ**: Ltda, unipessoal, S.A., cooperativa, associação, empresário individual/MEI, EIRELI e
  sociedade simples (cargos de estatuto, atas de eleição, registro em Junta ou em cartório de pessoas jurídicas).
- **Local, como agente**: `outorga agente` vigia uma pasta, processa sozinho cada pedido (ATPV-e + documentos) e
  devolve parecer em PDF, resumo e resultado estruturado — nada sai da máquina. Também tem interface web e API.
- Leitura de PDF, PDF digitalizado (OCR), DOCX e imagem; IA generativa **local** (Qwen 27B).
- Conferência da leitura (léxico jurídico + citação literal ancorada no documento) e **motor de regras jurídicas**:
  regime vigente na data da venda, cláusula do veículo específico, alçadas (de venda e de compra), aprovação de
  sócios, procuração (poderes de vender ≠ poderes de comprar, art. 661; prazo; revogação; quem outorgou),
  substabelecimento (art. 667), CRLV, política DETRAN-CE.
- Índice de aceitação com faixa intermediária **calibrável** (tela própria), revisão humana, simulador "e se…?",
  parecer em PDF por lado (vendedor/comprador) e trilha de auditoria encadeada por hash.
- 38 cenários jurídicos de teste (fictícios) com gabarito, incluindo os exemplos do áudio, mais 8 de validação cega,
  10 de um autor independente e 14 do lote ATPV-e (comprador PJ, PJ dos dois lados e os novos tipos de empresa).

Resultados medidos (detalhes em `docs/RESULTADOS.md`):

- motor jurídico com leitura perfeita: **38/38**;
- IA local lendo os 38 cenários do zero (execução cega): **37/38**, **nenhum aceite indevido**;
- 8 cenários novos com redações inéditas (validação cega): **7/8**, **nenhum aceite indevido**;
- **10 casos escritos por um autor independente, sem acesso ao código: 7/10 e 2 aceites indevidos** (classes de
  administradores; ata "por unanimidade dos presentes" sem o quórum de capital). Corrigidos como regras gerais — com as
  correções, 9/10 e nenhum aceite indevido (já não é teste cego);
- **lote ATPV-e (vendendo ou comprando, todos os tipos de empresa) — 14 casos novos, rodada cega: 14/14 vereditos,
  nenhum aceite indevido**; 4 foram para revisão sem necessidade e a lista de "quem pode assinar" divergiu em 3. O teste
  achou um risco latente: em associação e cooperativa, "Compete ao Presidente representar…" foi lido como "qualquer
  administrador", com o Conselho Fiscal tratado como administração. Corrigido como regra geral; com as correções,
  14/14 (já não é teste cego).

- **consulta por CPF antes da ATPV-e — 15 casos novos, rodada cega: 15/15**, nenhum aceite indevido: o próprio dono
  passa direto; CPF diferente sem procuração → o sistema pede a procuração; procurações só com poderes gerais, vencidas,
  de outro veículo, revogadas, particulares (DETRAN-CE) ou dadas pela esposa e não pelo dono → recusadas; procuração
  pública válida, substabelecimento com reserva e compradora representada → aceitos.

Conclusão: o protótipo é promissor, mas só deve decidir sozinho depois de um piloto com processos reais; até lá, a
faixa intermediária deve ser larga.

## O que ainda precisa ser confirmado

1. "Faixa intermediária" = aceita / revisão humana / recusa? (única pergunta sem resposta)
2. O sistema pode consultar a base veicular do DETRAN (dono por placa/RENAVAM)? No protótipo, é simulada.
3. A procuração vem anexada pela pessoa ou deve ser conferida também na CENSEC (procurações públicas)?
4. Entendimento do DETRAN-CE sobre "procuração específica para o ato" (exige identificar o veículo?).
5. Layout oficial do PDF da ATPV-e (o leitor foi calibrado num modelo simulado).

## Próximos passos sugeridos

1. Testar com 20–30 processos reais anonimizados e recalibrar a faixa.
2. Consulta a bases oficiais (Receita/Junta) para confirmar administradores e situação do CNPJ.
3. Casar o CPF do certificado que assinou a ATPV-e com as combinações devolvidas pelo motor.
4. API para o sistema de transferência consumir no momento da assinatura.
