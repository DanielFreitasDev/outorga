# Resultados da avaliação

Gerado por `scripts/relatorio_resultados.py` a partir de `avaliacoes/`. Corpus: 38 cenários fictícios (`corpus/CENARIOS.md`), mais 8 de validação cega, 10 independentes, 14 do lote ATPV-e e 15 de consulta por CPF. *Erro perigoso* = aceite automático (faixa verde) quando o gabarito diz que não pode; *erro caro* = recusa automática quando pode.

| Execução | Leitura | Política | Veredito | Faixa aceitável | Quem pode | Perigosos | Caros | Automático | Duração |
|---|---|---|---|---|---|---|---|---|---|
| `oraculo-ce` | gabarito (oráculo) | DETRAN-CE | 38/38 | 38/38 | 37/37 | 0 | 0 | 84% | 0 min |
| `oraculo-generica` | gabarito (oráculo) | Código Civil (genérica) | 38/38 | 38/38 | 37/37 | 0 | 0 | 79% | 0 min |
| `llm-completa1` | IA local (Qwen 27B) | DETRAN-CE | 37/38 | 37/38 | 36/37 | 0 | 1 | 84% | 32 min |
| `llm-final-ce` | IA local (Qwen 27B) | DETRAN-CE | 38/38 | 38/38 | 37/37 | 0 | 0 | 84% | 0 min |
| `llm-final-generica` | IA local (Qwen 27B) | Código Civil (genérica) | 38/38 | 38/38 | 37/37 | 0 | 0 | 79% | 0 min |
| `llm-cega-ce` | IA local (Qwen 27B) | DETRAN-CE | 7/8 | 7/8 | 6/8 | 0 | 1 | 100% | 20 min |
| `llm-cega-pos-ajuste` | IA local (Qwen 27B) | DETRAN-CE | 8/8 | 8/8 | 8/8 | 0 | 0 | 100% | 0 min |
| `llm-independente-ce` | IA local (Qwen 27B) | DETRAN-CE | 7/10 | 7/10 | 5/8 | 2 | 0 | 70% | 22 min |
| `llm-independente-pos-ajuste` | IA local (Qwen 27B) | DETRAN-CE | 9/10 | 9/10 | 7/8 | 0 | 0 | 60% | 0 min |
| `profunda-amostras3` | IA local (Qwen 27B) | DETRAN-CE | 4/4 | 3/4 | 4/4 | 0 | 0 | 75% | 24 min |
| `oraculo-atpv-ce` | gabarito (oráculo) | DETRAN-CE | 14/14 | 14/14 | 14/14 | 0 | 0 | 100% | 0 min |
| `llm-atpv-cega` | IA local (Qwen 27B) | DETRAN-CE | 14/14 | 10/14 | 11/14 | 0 | 0 | 71% | 15 min |
| `llm-atpv` | IA local (Qwen 27B) | DETRAN-CE | 14/14 | 14/14 | 14/14 | 0 | 0 | 100% | 0 min |
| `oraculo-pf-ce` | gabarito (oráculo) | DETRAN-CE | 15/15 | 15/15 | 15/15 | 0 | 0 | 87% | 0 min |
| `llm-pf-cega` | IA local (Qwen 27B) | DETRAN-CE | 15/15 | 15/15 | 15/15 | 0 | 0 | 87% | 10 min |

**Como ler:** `oraculo-*` usam a leitura perfeita do gabarito e validam só o motor jurídico. `llm-completa1` é a execução **cega** da IA local (cada documento lido do zero). As execuções `llm-final-*` reaplicam o motor já corrigido sobre **as mesmas leituras** (cache) — a correção do C33 ("2 (dois) Diretores" = quaisquer dois) foi feita depois de ver o erro, então elas **não são teste cego**. O teste cego de generalização é o conjunto `llm-cega-*` (8 cenários novos, com redações inéditas, criados depois dos ajustes e avaliados sem nenhum ajuste posterior).

## Caso a caso — IA local, execução cega (leitura nova de cada documento)

| Caso | Cenário | Esperado | Previsto | Faixa | Índice | Quem pode | Tempo |
|---|---|---|---|---|---|---|---|
| ✓ C01 | Administração 'indistintamente' — um sócio assina | PODE | PODE | 🟢 aceito | 100 | ok | 53s |
| ✓ C02 | Assinatura conjunta exigida — só um assina | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 63s |
| ✓ C03 | Assinatura conjunta — os dois assinam | PODE | PODE | 🟢 aceito | 100 | ok | 0s |
| ✓ C04 | Sócia quotista sem poder de administração assina | NAO_PODE | NAO_PODE | 🔴 recusado | 8 | ok | 66s |
| ✓ C05 | Administrador não sócio assina | PODE | PODE | 🟢 aceito | 100 | ok | 80s |
| ✓ C06 | Sócio majoritário (70%) que não é administrador | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 0s |
| ✓ C07 | Contrato omisso sobre a forma de atuação | PODE | PODE | 🟡 revisão | 100 | ok | 58s |
| ✓ C08 | Alçada por valor — abaixo do limite | PODE | PODE | 🟢 aceito | 100 | ok | 62s |
| ✓ C09 | Alçada por valor — acima do limite | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 0s |
| ✓ C10 | Alçada por valor — valor não informado | INDETERMINADO | INDETERMINADO | 🟡 revisão | 50 | — | 0s |
| ✓ C11 | Ativo não circulante (inclui veículos) sem deliberação | INDETERMINADO | INDETERMINADO | 🟡 revisão | 50 | ok | 70s |
| ✓ C12 | Ativo não circulante com ata aprovando a venda | PODE | PODE | 🟢 aceito | 100 | ok | 27s |
| ✓ C13 | Carro integralizado pelo sócio — o OUTRO sócio vende sozinho | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 94s |
| ✓ C14 | Carro integralizado pelo sócio — ele mesmo vende | PODE | PODE | 🟢 aceito | 100 | ok | 0s |
| ✓ C15 | Carro integralizado, mas o CRLV ainda está no CPF do sócio | INDETERMINADO | INDETERMINADO | 🟡 revisão | 50 | ok | 0s |
| ✓ C16 | Procuração pública válida com poderes especiais | PODE | PODE | 🟢 aceito | 91 | ok | 45s |
| ✓ C17 | Procuração só com poderes gerais de administração | NAO_PODE | NAO_PODE | 🔴 recusado | 7 | ok | 36s |
| ✓ C18 | Procuração vencida | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 36s |
| ✓ C19 | Procuração revogada | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 66s |
| ✓ C20 | Procuração outorgada por quem não tinha poder sozinho | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 26s |
| ✓ C21 | Procuração do sócio em nome próprio (PF), não da empresa | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 35s |
| ✓ C22 | Procuração para OUTRO veículo específico | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 99s |
| ✓ C23 | Substabelecimento com reserva, permitido | PODE | PODE | 🟢 aceito | 91 | ok | 26s |
| ✓ C24 | Substabelecimento vedado na procuração | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 50s |
| ✓ C25 | Substabelecimento sem reserva — o procurador original assina | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 46s |
| ✓ C26 | Procuração particular sem firma reconhecida | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 35s |
| ✓ C27 | Procuradores que devem agir em conjunto — só um assina | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 42s |
| ✓ C28 | Administrador que outorgou saiu da administração depois | PODE | PODE | 🟢 aceito | 97 | ok | 151s |
| ✓ C29 | Alteração contratual mudou de isolada para conjunta | NAO_PODE | NAO_PODE | 🔴 recusado | 8 | ok | 134s |
| ✓ C30 | Administrador com mandato por prazo determinado vencido | NAO_PODE | NAO_PODE | 🟡 revisão | 0 | ok | 63s |
| ✓ C31 | Sociedade limitada unipessoal — sócio único assina | PODE | PODE | 🟢 aceito | 100 | ok | 0s |
| ✓ C32 | S.A. — um diretor sozinho | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 139s |
| ✗ C33 | S.A. — diretor + procurador com procuração válida | PODE | NAO_PODE | 🔴 recusado | 0 | diverge | 46s |
| ✓ C34 | Empresário individual | PODE | PODE | 🟢 aceito | 100 | ok | 28s |
| ✓ C35 | Revendedora: restrição a ativo imobilizado x estoque | PODE | PODE | 🟡 revisão | 100 | ok | 63s |
| ✓ C36 | Procuração válida — documentos ESCANEADOS (OCR) | PODE | PODE | 🟢 aceito | 96 | ok | 124s |
| ✓ C37 | Procuração antiga sem prazo (3 anos) | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok | 31s |
| ✓ C38 | Todos os sócios assinam (com exigência de deliberação) | PODE | PODE | 🟢 aceito | 100 | ok | 0s |

## Divergências

- **C33 — S.A. — diretor + procurador com procuração válida**: esperado PODE (VERDE), obtido NAO_PODE (VERMELHO, índice 0). Os assinantes informados não bastam. Quem pode assinar: Helena Castro Lins e Marcelo Augusto Feitosa ou Helena Castro Lins e Tiago Rolim Vasconcelos ou Marcelo Augusto Feitosa e Tiago Rolim Vasconcelos. O caminho por procuração pública de 18/02/2026 (tabelionato jaguaribe – ofício único de notas de aracati/ce) não vale: outorga em desacordo com o estatuto/contrato. Motivos da faixa: índice 0.1 ≤ limiar 15.

## Validação cega — `llm-cega-ce`

| Caso | Cenário | Esperado | Previsto | Faixa | Índice | Quem pode |
|---|---|---|---|---|---|---|
| ✓ H01 | ‘De per si’ — um administrador assina | PODE | PODE | 🟢 aceito | 100 | ok |
| ✗ H02 | Quaisquer dois dos três administradores — um assina | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | diverge |
| ✓ H03 | Veículos da frota exigem os dois (sem valor) — um assina | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ H04 | Procuração ‘pelo período de doze meses’ vencida | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ H05 | ‘Sem direito de substabelecer’ e houve substabelecimento | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✗ H06 | Procuração conjunta, veículo identificado, no prazo | PODE | NAO_PODE | 🔴 recusado | 0 | diverge |
| ✓ H07 | Antiga administradora assina depois da troca | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ H08 | Restrição a imóveis e participações; veículo de R$ 320 mil | PODE | PODE | 🟢 aceito | 100 | ok |
- **H02**: esperado NAO_PODE, obtido NAO_PODE (VERMELHO). Os assinantes informados não bastam. Quem pode assinar: Caio Ferreira Paz, Lucas Ferreira Paz e Renata Albuquerque Paz. Regra aplicável: regra geral de representação (Cláusula Sexta).
- **H06**: esperado PODE, obtido NAO_PODE (VERMELHO). Os assinantes informados não bastam. Quem pode assinar: Breno Sampaio Tavares e Clarice Tavares Mourão ou Breno Sampaio Tavares e Nilton Arruda Coelho (procurador) ou Clarice Tavares Mourão e Nilton Arruda Coelho (procurador). Regra aplicável: regra geral de representação (Cláusula Sétima).

## Validação cega — `llm-cega-pos-ajuste`

| Caso | Cenário | Esperado | Previsto | Faixa | Índice | Quem pode |
|---|---|---|---|---|---|---|
| ✓ H01 | ‘De per si’ — um administrador assina | PODE | PODE | 🟢 aceito | 100 | ok |
| ✓ H02 | Quaisquer dois dos três administradores — um assina | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ H03 | Veículos da frota exigem os dois (sem valor) — um assina | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ H04 | Procuração ‘pelo período de doze meses’ vencida | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ H05 | ‘Sem direito de substabelecer’ e houve substabelecimento | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ H06 | Procuração conjunta, veículo identificado, no prazo | PODE | PODE | 🟢 aceito | 92 | ok |
| ✓ H07 | Antiga administradora assina depois da troca | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ H08 | Restrição a imóveis e participações; veículo de R$ 320 mil | PODE | PODE | 🟢 aceito | 100 | ok |

## Validação independente — `llm-independente-ce`

Casos escritos por um agente independente, **sem acesso ao código, aos cenários nem aos gabaritos do projeto**, com documentos e gabarito próprios (`corpus/independente/`). Nada foi ajustado antes da rodada.

| Caso | Cenário | Esperado | Previsto | Faixa | Índice | Quem pode |
|---|---|---|---|---|---|---|
| ✓ I01 | S.A. com Diretoria de mandato vencido, prorrogado por lei, e nova Diretoria eleita depois da venda | PODE | PODE | 🟡 revisão | 86 | ok |
| ✗ I02 | Dois administradores assinam juntos, mas da mesma classe: a cláusula exige um Administrador A e um Administrador B | NAO_PODE | PODE | 🟢 aceito | 91 | diverge |
| ✓ I03 | Procuração de venda revogada por nova procuração que só autoriza assinar a ATPV-e 'na qualidade de adquirente' | NAO_PODE | NAO_PODE | 🔴 recusado | 7 | ok |
| ✓ I04 | Cadeia de substabelecimentos: o primeiro 'sem reserva' e o último por instrumento particular | NAO_PODE | NAO_PODE | 🔴 recusado | 6 | ok |
| ✗ I05 | Procuração pública sem prazo, com mais de 1 ano, outorgada por administrador que depois saiu da sociedade | NAO_PODE | NAO_PODE | 🟡 revisão | 7 | diverge |
| ✗ I06 | Ata 'aprovada por unanimidade dos presentes' e pela 'maioria dos sócios', mas com só 55% do capital quando o contrato exige 2/3 | NAO_PODE | PODE | 🟢 aceito | 100 | diverge |
| ✗ I07 | Procuração outorgada por sócio cujo poder de administração depende de alterações contratuais não apresentadas | INDETERMINADO | NAO_PODE | 🔴 recusado | 7 | — |
| ✓ I08 | Sócio único de SLU assina a venda, mas só foi nomeado administrador uma semana depois; a administradora era não sócia | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ I09 | Alçada de valor para assinatura conjunta, alterada no tempo, e venda sem valor informado | INDETERMINADO | INDETERMINADO | 🟡 revisão | 50 | — |
| ✓ I10 | Ex-EIRELI com nome alterado: CRLV no nome antigo e mesmo CNPJ, restrição só para imóveis e revogação genérica de procuração anterior | PODE | PODE | 🟢 aceito | 100 | ok |
- **I02** — esperado NAO_PODE (VERMELHO), obtido PODE (VERDE). Sistema: Germana Castro Leite e Raimundo Nonato Castro Filho podem, em conjunto, assinar o ATPV — alienação de veículos — Cláusula Oitava, § 2º, I; alienação de veículos — Cláusula Oitava, § 2º, I. Autor: A Cláusula Oitava, § 2º, I, exige, para alienar bens do ativo imobilizado 'compreendidos os veículos automotores', a assinatura conjunta de um Administrador A e de um Administrador B; a isolada do § 1º cobre só a gestão ordinária, como a venda do estoque de bebidas, e não a venda da van de entrega. RAIMUNDO e GERMANA são ambos Administradores A, de modo que a dupla pedida não satisfaz a combinação exigida, por mais que sejam dois administradores. Na data da venda (19/08/2026) o único Administrador B era EXPEDITO, porque FRANCISCA VALDENIA renunciou e a Sexta Alteração, arquivada em 14/07/2026, a retirou da administração. A procuração de 03/03/2026 a ANTÔNIO WAGNER foi bem outorgada (A + B), mas confere poder especial apenas para o FIAT/STRADA placa FML8E58, e não para a FIAT/DUCATO placa MLS9L81 (CC art. 661, § 1º). Restam como conjuntos válidos RAIMUNDO + EXPEDITO e GERMANA + EXPEDITO.
- **I05** — esperado NAO_PODE (VERMELHO/AMARELO), obtido NAO_PODE (AMARELO). Sistema: Os assinantes informados não bastam. Quem pode assinar: ninguém. O caminho por procuração pública de 23/06/2025 (tabelionato ponte ferreira – 2º ofício de notas de sobral) não vale: procuração com mais de 1 ano. Autor: Em 23/06/2025, OTÁVIO era o administrador isolado, com poder de constituir procuradores (Cláusula Sexta da consolidação de 2021), e outorgou a GILDÁSIO procuração pública com poder especial e expresso de vender o FIAT/CRONOS placa UFZ6V24, sem prazo. A saída de OTÁVIO em 15/01/2026 não extingue o mandato: a outorgante é a sociedade, o art. 682 não prevê essa causa de extinção, a Quinta Alteração não revogou procurações e o STJ (AgInt no REsp 1.997.964/SC) reconhece a subsistência da procuração mesmo com a morte do signatário. O Código Civil não fixa validade para procuração sem prazo; pelo direito civil, GILDÁSIO pode assinar em 12/08/2026, assim como SUELI, administradora isolada desde a Quinta Alteração (BRUNO é só sócio). A política do DETRAN-CE limita a procuração a 1 ano da expedição; como a de 23/06/2025 tem mais de 13 meses na data da venda, por essa política só SUELI pode assinar e o pedido feito por GILDÁSIO deve ser recusado ou, no mínimo, ir para revisão com pedido de nova procuração.
- **I06** — esperado NAO_PODE (VERMELHO), obtido PODE (VERDE). Sistema: Ivanilda Bezerra Correia pode assinar o ATPV — regra geral de representação — Cláusula Sétima. Autor: A Cláusula Nona, I, condiciona a alienação de veículos do ativo imobilizado à aprovação prévia de sócios titulares de no mínimo 2/3 do capital social (1.333.334 das 2.000.000 quotas), e a Cláusula Décima, § 2º, manda contar os votos pelo valor das quotas (CC art. 1.010). A reunião instalou-se validamente em segunda convocação, mas os três sócios presentes somam 1.100.000 quotas, ou 55% do capital; a 'unanimidade dos presentes' e a 'maioria dos sócios (três dos quatro)' não alcançam o quórum contratual, que se mede sobre o capital total e não sobre os presentes nem por cabeça. O arquivamento da ata na JUCEC não supre a falta de quórum, e a deliberação contrária ao contrato não vincula a sociedade (art. 1.072, § 5º, a contrario). A limitação consta de contrato arquivado e é oponível a terceiros (art. 1.154, parágrafo único). Sem aprovação válida, a administradora IVANILDA não pode alienar o FIAT/TITANO, e ninguém mais tem poderes para isso: o conjunto de signatários válidos na data é vazio.
- **I07** — esperado INDETERMINADO (AMARELO), obtido NAO_PODE (VERMELHO). Sistema: Os assinantes informados não bastam. Quem pode assinar: Tereza Cristina Sobreira ou Afonso Henrique Sobreira Maciel. O caminho por procuração pública de 04/12/2025 (cartório alencar peixoto – 1º ofício de notas do crato (fictício)) não vale: quem outorgou não tinha poder sozinho, outorga em desacordo com o estatuto/contrato. Autor: A procuração de 04/12/2025 é pública, identifica o veículo, tem prazo de 1 ano e confere poder especial de venda; também sobreviveria à retirada de CLÁUDIO em 20/05/2026. A dúvida está na origem: o único ato societário anterior à outorga que foi apresentado é o contrato de 2016, que designa só AFONSO como administrador e exclui TEREZA; a Terceira Alteração (19/03/2024), invocada na escritura, e a Quarta (14/08/2025), que pode ter mudado a administração antes da outorga, não estão no dossiê. A consolidação de 2026 diz apenas que CLÁUDIO deixa 'qualquer cargo ou função' e não informa se ele administrava isoladamente nem se podia constituir procuradores para alienar veículos (CC arts. 1.018 e 47). A menção do tabelião à certidão simplificada não substitui o exame do ato que conferiu os poderes. Na data da venda (16/09/2026), AFONSO e TEREZA podem assinar isoladamente pela Cláusula Sétima consolidada, mas a inclusão de SEVERINO depende de documentos ausentes; por isso os conjuntos ficam indeterminados, e o pedido deve ir para revisão humana, com exigência da Terceira e da Quarta Alterações (ou certidão de inteiro teor).

## Validação independente — `llm-independente-pos-ajuste`

Casos escritos por um agente independente, **sem acesso ao código, aos cenários nem aos gabaritos do projeto**, com documentos e gabarito próprios (`corpus/independente/`). Nada foi ajustado antes da rodada.

| Caso | Cenário | Esperado | Previsto | Faixa | Índice | Quem pode |
|---|---|---|---|---|---|---|
| ✓ I01 | S.A. com Diretoria de mandato vencido, prorrogado por lei, e nova Diretoria eleita depois da venda | PODE | PODE | 🟡 revisão | 86 | ok |
| ✗ I02 | Dois administradores assinam juntos, mas da mesma classe: a cláusula exige um Administrador A e um Administrador B | NAO_PODE | PODE | 🟡 revisão | 100 | diverge |
| ✓ I03 | Procuração de venda revogada por nova procuração que só autoriza assinar a ATPV-e 'na qualidade de adquirente' | NAO_PODE | NAO_PODE | 🔴 recusado | 7 | ok |
| ✓ I04 | Cadeia de substabelecimentos: o primeiro 'sem reserva' e o último por instrumento particular | NAO_PODE | NAO_PODE | 🔴 recusado | 6 | ok |
| ✓ I05 | Procuração pública sem prazo, com mais de 1 ano, outorgada por administrador que depois saiu da sociedade | NAO_PODE | NAO_PODE | 🔴 recusado | 5 | ok |
| ✓ I06 | Ata 'aprovada por unanimidade dos presentes' e pela 'maioria dos sócios', mas com só 55% do capital quando o contrato exige 2/3 | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ I07 | Procuração outorgada por sócio cujo poder de administração depende de alterações contratuais não apresentadas | INDETERMINADO | INDETERMINADO | 🟡 revisão | 50 | — |
| ✓ I08 | Sócio único de SLU assina a venda, mas só foi nomeado administrador uma semana depois; a administradora era não sócia | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ I09 | Alçada de valor para assinatura conjunta, alterada no tempo, e venda sem valor informado | INDETERMINADO | INDETERMINADO | 🟡 revisão | 50 | — |
| ✓ I10 | Ex-EIRELI com nome alterado: CRLV no nome antigo e mesmo CNPJ, restrição só para imóveis e revogação genérica de procuração anterior | PODE | PODE | 🟢 aceito | 100 | ok |
- **I02** — esperado NAO_PODE (VERMELHO), obtido PODE (AMARELO). Sistema: Raimundo Nonato Castro Filho pode assinar a ATPV-e — regra geral de representação — Cláusula Oitava, Caput. Autor: A Cláusula Oitava, § 2º, I, exige, para alienar bens do ativo imobilizado 'compreendidos os veículos automotores', a assinatura conjunta de um Administrador A e de um Administrador B; a isolada do § 1º cobre só a gestão ordinária, como a venda do estoque de bebidas, e não a venda da van de entrega. RAIMUNDO e GERMANA são ambos Administradores A, de modo que a dupla pedida não satisfaz a combinação exigida, por mais que sejam dois administradores. Na data da venda (19/08/2026) o único Administrador B era EXPEDITO, porque FRANCISCA VALDENIA renunciou e a Sexta Alteração, arquivada em 14/07/2026, a retirou da administração. A procuração de 03/03/2026 a ANTÔNIO WAGNER foi bem outorgada (A + B), mas confere poder especial apenas para o FIAT/STRADA placa FML8E58, e não para a FIAT/DUCATO placa MLS9L81 (CC art. 661, § 1º). Restam como conjuntos válidos RAIMUNDO + EXPEDITO e GERMANA + EXPEDITO.

## Lote ATPV-e (vendendo ou comprando; todos os tipos de PJ) — `llm-atpv-cega` (IA local, rodada cega)

Respostas do chefe em 17/10/2026: verificar quem assina **vendendo ou comprando**, **todos os tipos de empresa**, foco na **ATPV-e digital**. O pedido traz só quem vai assinar; veículo, partes, valor e data vêm da ATPV-e simulada. Documentos novos redigidos por agentes sem acesso ao código.

| Caso | Cenário | Esperado | Previsto | Faixa | Vendedor | Comprador | Quem pode |
|---|---|---|---|---|---|---|---|
| ✗ A01 | Comprador PJ: administrador assina compra abaixo da alçada | PODE | PODE | 🟡 revisão | PF | 🟡 revisão 97 | ok |
| ✓ A02 | Comprador PJ: compra acima da alçada com um só administrador | NAO_PODE | NAO_PODE | 🔴 recusado | PF | 🔴 recusado 10 | ok |
| ✓ A03 | Restrição de compra não alcança a venda | PODE | PODE | 🟢 aceito | 🟢 aceito 100 | PF | ok |
| ✓ A04 | Comprador PJ por procurador com poder de compra | PODE | PODE | 🟢 aceito | PF | 🟢 aceito 92 | ok |
| ✓ A05 | Procuração só de venda usada para comprar | NAO_PODE | NAO_PODE | 🔴 recusado | PF | 🔴 recusado 7 | ok |
| ✗ A06 | PJ dos dois lados: ambos com poder | PODE | PODE | 🟡 revisão | 🟢 aceito 100 | 🟡 revisão 97 | ok |
| ✓ A07 | PJ dos dois lados, assinaturas lidas da ATPV-e: comprador sem poder | NAO_PODE | NAO_PODE | 🔴 recusado | 🟢 aceito 100 | 🔴 recusado 8 | ok |
| ✗ A08 | Cooperativa: Diretor-Presidente e Diretor Financeiro assinam | PODE | PODE | 🟡 revisão | 🟡 revisão 100 | PF | diverge |
| ✗ A09 | Cooperativa: Diretor-Presidente sozinho | NAO_PODE | NAO_PODE | 🟡 revisão | 🟡 revisão 0 | PF | diverge |
| ✗ A10 | Associação compradora: Presidente eleita assina | PODE | PODE | 🟢 aceito | PF | 🟢 aceito 100 | diverge |
| ✓ A11 | MEI vende: o titular assina | PODE | PODE | 🟢 aceito | 🟢 aceito 100 | PF | ok |
| ✓ A12 | MEI compra: a esposa do titular assina | NAO_PODE | NAO_PODE | 🔴 recusado | PF | 🔴 recusado 10 | ok |
| ✓ A13 | EIRELI (hoje SLU) vende: o titular assina | PODE | PODE | 🟢 aceito | 🟢 aceito 100 | PF | ok |
| ✓ A14 | Sociedade simples: um sócio assina sozinho | NAO_PODE | NAO_PODE | 🔴 recusado | 🔴 recusado 0 | PF | ok |
- **A01**: esperado PODE (VERDE), obtido PODE (AMARELO). Gilberto Araújo Nunes pode assinar a ATPV-e como comprador(a) — regra supletiva (contrato não define a forma de assinar).
- **A06**: esperado PODE (VERDE), obtido PODE (AMARELO). Vendedor: João Batista Andrade pode assinar a ATPV-e — regra geral de representação — Cláusula Sétima. · Comprador: Simone Batista Nunes pode assinar a ATPV-e como comprador(a) — regra supletiva (contrato não define a forma de assinar).
- **A08**: esperado PODE (VERDE), obtido PODE (AMARELO). Expedito Lima Cordeiro e Manoel Messias Freitas podem, em conjunto, assinar a ATPV-e — alienação de bens — Art. 22, Parágrafo único.
- **A09**: esperado NAO_PODE (VERMELHO), obtido NAO_PODE (AMARELO). Os assinantes informados não bastam. Quem pode assinar: Expedito Lima Cordeiro e Joana Darc Ribeiro ou Joana Darc Ribeiro e Manoel Messias Freitas ou Cícero Romão Bezerra e Joana Darc Ribeiro ou Expedito Lima Cordeiro e Manoel Messias Freitas ou Cícero Romão Bezerra e Expedito Lima Cordeiro. Regra aplicável: alienação de bens (Art. 22, Parágrafo único).
- **A10**: esperado PODE (VERDE), obtido PODE (VERDE). Maria do Socorro Viana pode assinar a ATPV-e como comprador(a) — regra geral de representação — Art. 20.

## Lote consulta por CPF (antes da ATPV-e; pessoa física e procuração) — `llm-pf-cega`

Resposta do chefe em 17/10/2026 (11:40): "poderia ser até antes do ATPV" — veículo + CPF + vender/comprar; se o CPF não for o do dono (ou do comprador), perguntar pela procuração e conferir se ela dá poder àquele CPF. O dono vem da base veicular simulada; as procurações novas foram redigidas por agentes sem acesso ao código.

| Caso | Cenário | Esperado | Previsto | Faixa | Índice | Quem pode |
|---|---|---|---|---|---|---|
| ✓ P01 | Pessoa física: o próprio dono vai assinar | PODE | PODE | 🟢 aceito | 100 | ok |
| ✓ P02 | Procurador com procuração pública e específica | PODE | PODE | 🟢 aceito | 100 | ok |
| ✓ P03 | CPF diferente do dono, sem procuração | INDETERMINADO | INDETERMINADO | 🟡 revisão | 50 | ok |
| ✓ P04 | Procuração só com poderes gerais (DETRAN, IPVA, multas) | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ P05 | Procuração de 6 meses, vencida | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ P06 | Procuração específica de outro veículo | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ P07 | Compradora pessoa física representada por procuradora | PODE | PODE | 🟢 aceito | 92 | ok |
| ✓ P08 | Procuração revogada | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ P09 | Substabelecida pelo procurador, com reserva | PODE | PODE | 🟢 aceito | 100 | ok |
| ✓ P10 | Procuração particular com firma reconhecida | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ P11 | Procuração dada pela esposa, não pelo dono registral | NAO_PODE | NAO_PODE | 🔴 recusado | 0 | ok |
| ✓ P12 | Dona é empresa: CPF do administrador | PODE | PODE | 🟢 aceito | 91 | ok |
| ✓ P13 | Dona é empresa: CPF de sócia sem poder, sem procuração | INDETERMINADO | INDETERMINADO | 🟡 revisão | 50 | ok |
| ✓ P14 | Dona é empresa: CPF de procurador da empresa | PODE | PODE | 🟢 aceito | 91 | ok |
| ✓ P15 | Comprador é empresa: CPF do administrador, abaixo da alçada | PODE | PODE | 🟢 aceito | 100 | ok |

## Lições da validação cega

- **Nenhum aceite indevido** em nenhuma execução (38 cenários + 8 cegos + análise profunda). Os erros foram todos do lado seguro (recusa ou exigência maior que a necessária).
- **A validação cega pegou uma regressão minha.** A regra criada para o C33 ("2 (dois) Diretores" = quaisquer dois) leu "quaisquer dois dos **três** administradores" como 3 (H02). Correção: em "N dos M" vale N, e a regra léxica só **completa** o que a IA deixou em aberto, nunca sobrescreve um valor válido.
- **H06:** a IA confundiu "representada conjuntamente por seus administradores" (quem *outorga*) com uma exigência de o *procurador* assinar junto com um administrador. Agora essa exigência só vale se estiver escrita no texto da procuração; e, por segurança, a conferência nunca relaxa uma restrição que apareça em algum lugar do texto.
- **Análise profunda (3 leituras + voto):** quando as leituras divergem, a confiança cai e o caso vai para revisão humana (C33: índice 83, faixa intermediária) — é o comportamento desejado.
- `llm-cega-pos-ajuste` mostra 8/8 com as correções, mas **não é mais teste cego**. Para medir de novo é preciso outro lote de cenários inéditos — idealmente processos reais anonimizados.

## Lições da validação independente

- **O teste mais duro mostrou 2 aceites indevidos** (I02 e I06) em 10 casos escritos por um autor que não conhecia o código. Nos cenários escritos pelo próprio desenvolvedor isso nunca tinha aparecido — por isso validação independente (e, depois, processos reais) é obrigatória antes de qualquer automação.
- **I02 — classes de administradores** ("um Administrador A e um Administrador B"): a IA leu "dois em conjunto" e perdeu a restrição de classe. Correção imediata: cláusula com classes/grupos sem combinação explícita vai para revisão humana. Próximo passo: o schema aceitar grupos com várias pessoas para decidir sozinho.
- **I06 — ata "por unanimidade dos presentes"** com presentes somando 55% do capital (quórum de 2/3): a leitura somou 110%. Correção: o percentual vem do quadro societário vigente, nunca acima de 100% nem do que os presentes somam; quórum não atingido é fato negativo (não pode), não pendência.
- **I05 — regra antiga de quem saiu** vencia a regra nova por "especialidade" de rótulo. Correção: alteração que troca a administração derruba as regras que citam quem saiu; se a regra mais específica ficar sem ninguém, aplica-se a seguinte, com alerta.
- **I07 — alterações intermediárias ausentes** (3ª e 4ª) que podiam ter dado poder a quem outorgou: agora o motor detecta o buraco pela numeração (e pela alteração citada na escritura) e responde *indeterminado*.
- Antes do lote independente, uma revisão de código já tinha fechado outras lacunas (anuência em cláusula só de condição, revogação genérica ou embutida, substabelecimento em cadeia, consulta sem assinantes).
- `llm-independente-pos-ajuste` (9/10, 0 aceites indevidos) **não é teste cego**: as correções foram feitas depois de ver os erros.

## Lições do lote ATPV-e (vendendo ou comprando, todos os tipos de PJ)

- **Rodada cega: veredito 14/14, faixa aceitável 10/14, quem pode assinar 11/14, aceites indevidos 0.** O teste mostrou duas leituras da IA que o motor precisava saber tratar — as duas viraram regras gerais e testes de regressão.
- **A01/A06 — cláusula geral rotulada como venda.** "A administração da sociedade caberá aos sócios..., que a exercerão isoladamente..., inclusive a venda de bens" foi lida como regra só de *alienação*. Para o lado comprador não sobrava regra, e o caso caía na regra supletiva com alerta (revisão desnecessária). Correção: cláusula que atribui a administração/representação da sociedade vale também para comprar; a venda citada é exemplo.
- **A10 — cargo nomeado lido como "administradores"** (risco latente de aceite indevido). "Compete ao Presidente representar a Associação" virou "qualquer administrador" (o schema só tem cargos genéricos), e os membros do Conselho Fiscal eleitos na mesma ata entraram como administradores: se a Vice ou um conselheiro fiscal tivesse assinado, o sistema aceitaria. O veredito saiu certo só porque quem assinou foi a Presidente. Correções: Conselho Fiscal e suplentes nunca representam (CC 1.066–1.070; LSA 161–165; Lei 5.764, art. 56); quando a cláusula nomeia o cargo que representa, só esse cargo assina — a conferência **restringe**, nunca amplia, e não afrouxa assinatura conjunta ("pelo Diretor-Presidente em conjunto com outro Diretor").
- **A08/A09 — o mesmo padrão na cooperativa.** "Serão assinados pelo Diretor-Presidente em conjunto com o Diretor Financeiro" virou "dois administradores quaisquer" (Vice + Secretário passariam), e o Conselho Fiscal eleito por 1 ano entrou como administração com mandato vencido, o que gerou alertas falsos e mandou os dois casos para revisão. As mesmas duas correções resolvem (agora 2 de 2).
- **Substituto do titular.** Revisando as correções, ficou uma lacuna do mesmo tipo: "na ausência ou impedimento do Presidente, o Vice-Presidente". A ausência não é verificável, então a assinatura do substituto vai para revisão humana, e a do titular segue normal (teste de regressão).
- O leitor da ATPV-e por regras leu as 14 ATPV-e simuladas com os mesmos campos do gabarito, mas em 2 o nome longo da cooperativa, quebrado em duas linhas no PDF, saiu cortado (sem efeito na decisão, que casa pelo CNPJ). Corrigido: 14/14 idênticas ao gabarito, assinaturas inclusive. Com o PDF oficial, recalibrar.
- `llm-atpv` (depois das correções, mesmas leituras) **não é teste cego**. Para medir de novo: lote novo, de preferência processos reais anonimizados de cooperativas, associações e compradores PJ.

## Lições da consulta por CPF (antes da ATPV-e)

- **Rodada cega: veredito 15/15, faixa aceitável 15/15, quem pode assinar 15/15, aceites indevidos 0**, com as 10 procurações de pessoa física lidas pela IA pela primeira vez.
- Cobertura: o próprio dono assinando (sem documentos), CPF diferente sem procuração (pergunta pela procuração), procuração pública específica, só com poderes gerais, vencida, de outro veículo, revogada, particular (DETRAN-CE recusa), outorgada pela esposa e não pelo dono registral, substabelecimento com reserva, compradora representada, e consultas em que o dono ou o comprador é empresa.
- O motor reaproveitou toda a verificação de procuração já validada nos lotes anteriores; o que é novo é tratar a pessoa física como titular único e perguntar pela procuração em vez de recusar.
- Ressalva honesta: 15 casos escritos com o mesmo guia de redação não substituem processos reais. Em especial, procurações reais trazem variações ("por si e por seus herdeiros", procurações em causa própria, cláusulas de irrevogabilidade) que este lote não exercita.
