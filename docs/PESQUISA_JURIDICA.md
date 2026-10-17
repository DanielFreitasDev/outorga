> Pesquisa jurídico-regulatória automatizada (16–17/10/2026), com fontes oficiais e texto literal. Pontos marcados como "não confirmado" não foram verificados em fonte. Revise antes de usar como fundamento definitivo.

# Pesquisa jurídico-regulatória: quem pode assinar a ATPV/ATPV-e na venda de veículo de pessoa jurídica

**Data de referência:** pesquisa feita em 16 e 17/10/2026. **Finalidade:** base de regras e de citações para um agente de IA que lê contrato social, alterações, procurações e substabelecimentos e decide quem tem poder para assinar a ATPV/ATPV-e, e para fundamentar o parecer correspondente.

**Convenções**
- Texto entre aspas é transcrição literal da fonte indicada, com URL ao lado.
- "Não confirmado" significa que não encontrei fonte que comprove o ponto. Nada foi suposto.
- Nas Seções 2 e 7: [N] norma; [P] prática administrativa (página oficial de serviço); [J] jurisprudência ou decisão administrativa; [D] doutrina ou enunciado.
- Os textos de lei da Seção 3 foram baixados do Planalto em 16/10/2026 e extraídos por script, sem redigitação.
- As normas mais importantes de 2025–2026 foram conferidas diretamente no PDF ou HTML oficial (lista no Anexo A).
- Os 147 links citados responderam HTTP 200 em teste automatizado em 17/10/2026. Isso não garante que o conteúdo das páginas não mude depois.

---

## 0. Sumário executivo e matriz de regras para codificação

### 0.1 O que mudou em 2025–2026 (regras antigas que o agente NÃO deve mais aplicar)

1. **A Res. CONTRAN 809/2020 está revogada.** Quem a revogou foi a **Res. CONTRAN nº 1.027, de 17/08/2026** (DOU 18/08/2026, Ed. 155-B), art. 60, I. A nova resolução vale desde a publicação (art. 61) e dá **90 dias de adequação** (art. 58). Pela nossa contagem, o prazo termina por volta de 16/11/2026, e a SENATRAN pode prorrogá-lo (art. 58, § 3º). Durante esse prazo continuam válidos os "procedimentos operacionais regularmente instituídos sob a regulamentação anterior" (art. 58, § 1º). Fonte: https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/resolucao10272026.pdf (Seção 1.1.3).
2. **ATPV-e só aceita assinatura eletrônica.** Art. 28, § 1º: "É vedada a aposição de assinatura manuscrita na ATPV-e, sendo admitidas exclusivamente assinaturas eletrônicas avançadas ou qualificadas [...]". Já a ATPV do verso do **CRV em papel** exige "assinaturas manuscritas do antigo proprietário e do novo proprietário com reconhecimento de firma por autenticidade em Tabelionato de Notas" (art. 26).
3. **Regra específica para PJ (art. 28, § 7º):** "Quando o antigo ou o novo proprietário for pessoa jurídica, a assinatura será admitida mediante comprovação eletrônica dos poderes do signatário, por consulta a bases oficiais ou por instrumento de outorga verificável, com identificação do outorgante, do outorgado, dos poderes conferidos, do prazo de validade e de eventual revogação, na forma estabelecida pelo órgão máximo executivo de trânsito da União." Este é o núcleo do caso de uso do agente. **A regulamentação da SENATRAN prevista no dispositivo não foi localizada até 17/10/2026 (não confirmado que exista).**
4. **Base legal da transferência 100% eletrônica:** CTB, art. 123, § 4º, incluído pela **Lei 15.153/2025**. O contrato eletrônico deve ter "assinaturas eletrônicas qualificadas ou avançadas, na forma da Lei nº 14.063, de 23 de setembro de 2020, e das normas regulamentares do Contran". A assinatura avançada deve ser feita em plataforma homologada (inciso III, que tinha sido vetado; o veto foi derrubado e o inciso promulgado em 09/12/2025). Texto literal na Seção 3.7.
5. **Cartório de Registro Civil não pode assinar ATPV-e quando há PJ.** O Provimento CNJ nº 252, de 18/08/2026, art. 5º, I e parágrafo único, veda a assinatura quando houver PJ, empresário individual ou MEI em qualquer polo, "ainda que a pessoa jurídica compareça por meio de representante legal ou estatutário". Um dos considerandos registra que "a plataforma oficial de venda digital de veículos mantida pelo Governo Federal não admite a transferência por pessoas jurídicas, justamente em razão da inviabilidade de verificação automatizada e segura de poderes societários". Fonte: https://atos.cnj.jus.br/files/original124648202608206a86f73893e30.pdf
6. **RENAVE nacional.** A Res. CONTRAN 1.026/2026 revogou as Res. 797/2020 e 818/2021. O RENAVE é obrigatório para revendas em todo o país desde 28/09/2026 (fim dos 90 dias do art. 33). A integração com a assinatura e a transferência eletrônicas está prevista para 09 a 20/11/2026 (Circular SENATRAN nº 2/2026). Ver Seção 4.
7. **Ceará:** o Provimento CGJCE 17/2024 foi **revogado** pelo Provimento CGJCE nº 05/2025, art. 7º (Seção 1.3.1-c). No CE continuam valendo três exigências: reconhecimento de firma **por autenticidade** com selo tipo 14 digital (art. 4º), registro em **RTD** (Lei CE 14.605/2010, art. 16) e, para procurador, procuração **pública e específica**, segundo o DETRAN-CE.
8. **Código Civil:** o **parágrafo único do art. 1.015 está revogado** (Lei 14.195/2021, art. 57, XXIX, "c"). Esse dispositivo listava as hipóteses em que o excesso de poderes era oponível a terceiros. Os quóruns dos arts. 1.061 e 1.076 foram alterados pela Lei 14.451/2022. Ver Seção 3.0.

### 0.2 Meios de assinatura quando o VENDEDOR é PJ

| Meio | Situação para vendedor PJ (17/10/2026) | Base / seção |
|---|---|---|
| ATPV do **CRV em papel**: assinatura manuscrita do representante + firma reconhecida **por autenticidade** em Tabelionato de Notas | Admitido. O cartório reconhece a firma da **pessoa física** do representante. A firma prova autoria, **não poderes**: CN-CE, art. 963, § 5º, exige menção de que "o reconhecimento não comprova os poderes de representação". No CE é preciso ainda o **registro em RTD**. | Res. 1.027, arts. 20, § 1º, e 26; Seções 1.2.4, 1.3.1, 2.1 |
| **ATPV-e impressa** + firma por autenticidade | Era a regra da Res. 809, art. 17 (revogada). As páginas de DETRAN-SP (08/10/2026), DETRAN-MG e DETRAN-CE ainda descrevem esse fluxo. Não há previsão dele na Res. 1.027. Uso após o prazo de adequação: **não confirmado**. | Seções 1.1.3 e 1.5 |
| ATPV-e com assinatura **qualificada ICP-Brasil** (e-CPF do representante ou e-CNPJ) | Admitida sem homologação (Res. 1.027, art. 47, II), sujeita à prova de poderes do art. 28, § 7º. **DETRAN-PR proíbe e-CNPJ** e exige e-CPF de cada signatário quando o contrato social pede assinatura conjunta (Portaria 661/2025, art. 3º). No RENAVE, o e-CNPJ é obrigatório para a revenda e para o consignante PJ. | Seções 1.2.3, 2.1 (PR), 4.5 |
| ATPV-e com **gov.br** (assinatura avançada) | A conta gov.br é só de pessoa física; o vínculo com o CNPJ exige e-CNPJ no mesmo CPF. Não atendem PJ: o canal federal **CDT/"CNH do Brasil"** (o serviço diz "Pessoa física proprietária ou futura proprietária"), o Balcão Digital do DETRAN-CE e a transferência digital do DETRAN-MG. **Exceção: Detran-SP (TDV)**, de PJ para PF, pelo CPF do representante legal com procuração eletrônica (desde 02/2026). | Seções 1.2.2, 1.4 |
| **Registro Civil** (IdRC/ICP-RC, ARPEN) | **Vedado** para PJ, EI e MEI. | Prov. CNJ 252/2026, arts. 4º e 5º |
| **e-Notariado** (assinatura notarizada; reconhecimento remoto de firma) | A Res. 1.027, art. 47, III, admite soluções notariais. O CNN, art. 306, § 1º, fixa a competência territorial para documento de veículo. Disponibilidade para PJ na ATPV-e: **não confirmada**. Em 2022, o módulo de SP era "apenas pessoas físicas". | Seção 1.2.4 |
| **Revenda** (art. 330 do CTB) vendendo do estoque | Fluxo do RENAVE: NF-e de saída e "Autorização para Transferência de Propriedade do Veículo em Meio Digital assinada eletronicamente". Exige e-CNPJ ICP-Brasil (Res. 1.026, arts. 10, 18, § 2º, e 30). | Seção 4.5 |

### 0.3 Procuração para vender veículo: matriz por UF

Base civil (Seção 3): a lei **não exige forma pública** para vender bem móvel (CC, arts. 107 e 657). Para **alienar**, a procuração precisa de "poderes especiais e expressos" (art. 661, § 1º). O Enunciado 183/CJF exige "identificação do objeto". O art. 654, § 2º, permite ao terceiro exigir firma reconhecida. A forma é, portanto, **exigência administrativa de cada DETRAN**.

| UF | Forma da procuração (física) | Identificação do veículo | Prazo / recência | Observações | Seção |
|---|---|---|---|---|---|
| **CE** | **Pública e específica para o ato** | Não explicitada (não confirmado) | "validade de até 01 ano da data de expedição" | PJ vendedora: "Contrato Social", documento do representante e "Comprovante Situação Cadastral do CNPJ (validade 30 dias)". Firma por autenticidade (selo 14 digital) e registro em RTD. | 1.3.1, 2.1 |
| **SP** | Pública com poderes específicos, **ou** particular com poderes específicos + placa ou chassi + firma **por autenticidade**, ou procuração "nato digital" | Exigida na particular (placa ou chassi) | Não fixado em dias | PJ: "Contrato Social atualizado" (ou estatuto + ata). Advogado sem firma. Procuração eletrônica do Detran-SP via gov.br prata/ouro. Firma reconhecida fora de SP: sinal público. | 1.3.2, 2.1 |
| **RJ** | Não confirmado (para leasing: pública, com os mesmos nomes dos signatários do CRV) | Não confirmado | Firma recomendada "em até 8 dias antes" do atendimento (validação do selo) | "Cópia autenticada em cartório do contrato social que possibilite confirmar se a pessoa que assinou [...] tem poderes" (Lei RJ 5.069/07). Sinal público de tabelião fluminense. | 1.3.3, 2.1 |
| **MG** | **Pública** (procurador PF); pública + contrato social atualizado (procurador PJ) | Não explicitada | Não fixado | Proíbe firma por "abono ou semelhança" e mistura de assinatura física e digital na ATPV-e. Advogado: particular sem firma. | 1.3.4, 2.1 |
| PR | Pública ou particular com firma por autenticidade (salvo advogado) | Sem identificação, a procuração vale para todos os veículos do CPF/CNPJ | 3 anos se não houver prazo | Só a cláusula "vender" permite assinar CRV/ATPV-e; "representar" não basta. Substabelecimento permitido salvo vedação. | 2.1 |
| SC | Física: **pública**, "com fins especiais e expressos"; ou eletrônica com ICP-Brasil | Exigida na eletrônica | — | gov.br só na ATPV-e via CDT, com as duas partes em nível ouro | 2.1 |
| GO | Pública (pode dispensar identificação) ou particular com firma por autenticidade | Particular: placa ou chassi | — | Apenas 1 substabelecimento (particular aceito) | 2.1 |
| RS | Firma por autenticidade | Individualizada por veículo | — | 1 substabelecimento; vigência em 2026 não confirmada | 2.1 |

**Regras gerais de procuração** (Seções 2.2 a 2.6):
- Rejeitar firma reconhecida **por semelhança** em procuração de venda e em ATPV.
- Exigir o verbo **"vender/alienar"**.
- Não há prazo legal de validade (CN-CE, art. 924). O CNJ (PCA 0007885-89.2023, 13/06/2025) julgou ilegal a exigência **genérica** de procuração com no máximo 30 dias de expedição, "salvo [...] fundamentação idônea".
- Para verificar revogação de procuração pública: **certidão atualizada** do cartório de origem, porque a revogação é anotada lá (CNN, art. 272, § 4º). A consulta à CEP/CENSEC informa a existência do ato, mas não informa revogação.
- **Substabelecimento:** o art. 655 do CC permite substabelecimento particular de procuração pública. O Enunciado 182/CJF restringe essa possibilidade aos casos em que a forma pública é facultativa. Onde o DETRAN exige procuração pública (CE, MG, SC), a política conservadora é exigir substabelecimento público. Isso é inferência, não regra expressa.
- **Causa própria** (art. 685): "não é — nem pode vir a ser — título translativo de propriedade" (STJ, REsp 1.345.170/RS).
- **Procuração outorgada pela PJ:** verificar os poderes de quem a assinou **na data da outorga** (CC, art. 1.018, e LSA, art. 144, p.u., que na S.A. exige também a "duração do mandato"). A procuração **não perde validade** com a saída ou a morte do administrador que a assinou (STJ, AgInt no REsp 1.997.964/SC, 2024, caso de morte; aplicação à saída por argumento *a fortiori*).

### 0.4 Certidões e documentos societários: validade

- **Certidão simplificada da Junta Comercial não tem prazo legal de validade.** A IN DREI 81/2020, art. 101, § 2º, prevê apenas que "As certidões devem ficar disponíveis pelo prazo de 30 (trinta) dias" para download. A JUCEC informa "validade jurídica para todos os fins", sem prazo em dias. Se a certidão traz prazo impresso: não confirmado. Ver Seção 1.3.6.
- **Prazos fixados por quem recebe o documento** (devem ser parâmetros configuráveis):
  - DETRAN-CE: "Comprovante Situação Cadastral do CNPJ (validade 30 dias)", que é documento da RFB, não da Junta.
  - DETRAN-MG: "Cartão CNPJ com menos de 90 dias" (comprador PJ).
  - DETRAN-AL (2011, vigência não confirmada): contrato e alterações "atualizados até o prazo de 01 (um) ano"; certidão da Junta com "validade de 30 dias".
  - SP: contrato "atualizado", sem prazo em dias.
  - RJ: cópia autenticada do contrato social.
- **Janela de 30 dias (Lei 8.934/1994, art. 36):** ato arquivado em até 30 dias da assinatura tem efeitos que "retroagirão" à data da assinatura. Por isso uma alteração já assinada e ainda não arquivada pode retirar poderes de quem assina hoje (caso Empi, STJ; Seção 5.5). Política sugerida, que não é exigência legal: certidão simplificada de até 30 dias, mais declaração de que não existe alteração assinada pendente de arquivamento.
- **CND do INSS** (Lei 8.212/1991, art. 47, I, "c"): exigida na alienação de bem móvel "incorporado ao ativo permanente" acima do limite atualizado. Em 2026, segundo o DETRAN-MG, o limite é R$ 87.493,73 (Portaria Interministerial MPS/MF nº 13/2026). Exigida por MG, RJ e PR. Não se aplica a estoque de revenda (inferência a partir do texto legal).

### 0.5 Regras societárias para identificar o signatário

- **Ltda**
  - É administrada por pessoas "designadas no contrato social ou em ato separado" (CC, art. 1.060).
  - Se o contrato não diz nada sobre a forma de atuação, ela é **isolada**: a administração "compete separadamente a cada um" (art. 1.013 c/c art. 1.053).
  - Se a atuação for conjunta, é necessário "o concurso de todos", salvo urgência (art. 1.014).
  - O uso da denominação é privativo dos administradores "que tenham os necessários poderes" (art. 1.064).
  - Restrição contratual que fala só em **imóveis** não alcança veículos. O art. 1.015, caput, só restringe imóveis, e veículo é bem móvel (art. 82). O agente deve procurar outras cláusulas que alcancem o veículo: "bens móveis", "ativo imobilizado", "quaisquer bens", alçada por valor, assinatura conjunta para "atos de disposição". Ver Seção 7.5.
- **Mandato vencido sem recondução (Ltda):** o exercício do cargo cessa (art. 1.063). Como o prazo está registrado, o terceiro não pode alegar ignorância (art. 1.154, p.u.). A prorrogação "até a investidura dos novos administradores" existe só na LSA (art. 150, § 4º). Na Ltda ela depende de cláusula própria ou de regência supletiva pela LSA (art. 1.053, p.u.); a aplicação analógica não foi confirmada em doutrina ou jurisprudência. Ver Seção 7.3.
- **Administrador nomeado em ato separado (Ltda):**
  - Toma posse por termo no livro de atas em até 30 dias, sob pena de a designação ficar "sem efeito" (art. 1.062, § 1º).
  - A nomeação deve ser averbada (art. 1.062, § 2º).
  - Responde pessoal e solidariamente pelos atos praticados antes de requerer a averbação (art. 1.012).
- **Sociedade limitada unipessoal:** art. 1.052, §§ 1º e 2º (Lei 13.874/2019).
- **S.A.**
  - A representação é "privativa dos diretores" (LSA, art. 138, § 1º).
  - Se o estatuto for omisso e não houver deliberação do conselho, "qualquer diretor" representa a companhia (art. 144).
  - A alienação de bem do **ativo não circulante** depende de autorização do conselho de administração, "se o estatuto não dispuser em contrário" (art. 142, VIII).
  - O prazo de gestão se estende até a investidura dos sucessores (art. 150, § 4º).
- **Revenda** vendendo veículo do estoque: a venda é o próprio objeto social; segue o fluxo do RENAVE. **Veículo do imobilizado** de PJ comum com contrato omisso: a venda está dentro dos poderes de gestão (art. 1.015). Há corrente notarial mais cautelosa (Seção 7.4).
- **Teoria da aparência e boa-fé** (STJ, REsp 887.277/SC e REsp 704.546/DF): protegem o terceiro em litígio, **mas não substituem** a verificação formal de poderes no parecer. Ver Seção 5.4.

### 0.6 Fluxo de decisão sugerido para o agente

Esta é uma síntese derivada das fontes. Não é norma.

1. **Classificar o vendedor:**
   - Ltda, Ltda unipessoal ou sociedade simples;
   - S.A.;
   - EI ou MEI;
   - revenda (art. 330 do CTB, CNAE de comércio de veículos) → fluxo do RENAVE (Seção 4).
   - PJ baixada/inativa → SP exige alvará judicial, salvo MEI, ME e produtor rural.
2. **Classificar o suporte:**
   - CRV em papel → ATPV manuscrita com firma por autenticidade.
   - CRV-e → ATPV-e com assinatura avançada ou qualificada, mais prova eletrônica de poderes (Res. 1.027, art. 28, § 7º).
   - "ATPV-e impressa" → aceitar só enquanto o DETRAN da UF a aceitar, sinalizando o risco da transição.
3. **Montar o quadro de administradores vigente na data da assinatura**, a partir de:
   - contrato ou consolidação mais as alterações arquivadas;
   - certidão simplificada recente.
   Para cada administrador, extrair: nome/CPF, forma de atuação (isolada ou conjunta; omissão = isolada), limites (valor, tipo de bem, "bens móveis", "imobilizado"), prazo de mandato e recondução, e averbação de nomeação, renúncia ou destituição. Conferir os "Observações" da certidão simplificada.
4. **Verificar restrições:**
   - Cláusula só sobre imóveis → não bloqueia a venda do veículo.
   - Cláusula sobre bens móveis, ativo ou valor → exigir assinatura conjunta ou deliberação.
   - S.A. com conselho → ata do conselho ou dispensa estatutária (art. 142, VIII).
5. **Se assina um procurador**, verificar:
   - **(a)** o outorgante tinha poderes na data da outorga;
   - **(b)** a forma exigida pela UF (matriz 0.3);
   - **(c)** poder expresso de "vender/alienar", de preferência com identificação do veículo (placa, RENAVAM, chassi);
   - **(d)** prazo da procuração ou limite da UF (CE: 1 ano; PR: 3 anos);
   - **(e)** inexistência de revogação (certidão atualizada para procuração pública);
   - **(f)** cadeia de substabelecimentos: sem vedação (art. 667, § 3º), dentro dos poderes originais e no máximo 1 nível em GO e RS;
   - **(g)** mandatários conjuntos ou isolados (art. 672).
6. **Verificar o meio de assinatura conforme a UF e o canal** (tabela 0.2): PJ não usa CDT nem Registro Civil; o PR veda e-CNPJ; no CE, firma por autenticidade mais RTD.
7. **Exigências acessórias:**
   - CND, se o veículo for do imobilizado e o valor passar do limite;
   - sinal público, se a firma foi reconhecida em outra UF;
   - comprovante de situação cadastral do CNPJ (CE: até 30 dias).
8. **Saída do agente:** signatário(s) habilitado(s), fundamento por artigo (Seção 3), alertas e nível de confiança.
   - **Revisão humana obrigatória** em: cláusulas ambíguas ("em conjunto ou isoladamente", alçadas), mandato vencido, procuração antiga sem certidão, alteração recente não arquivada, e S.A. sem ata.

### 0.7 Lacunas principais (detalhe no Anexo B)

1. A regulamentação da SENATRAN para o art. 28, § 7º, da Res. 1.027/2026 (como provar eletronicamente os poderes da PJ) não foi localizada.
2. Não se sabe como os DETRANs tratarão a "ATPV-e impressa com firma" depois do prazo de adequação (~16/11/2026).
3. Não se confirmou se o DETRAN-CE exige certidão simplificada ou última alteração (a página pede só "Contrato Social"), nem se aceita ATPV-e de PJ assinada com ICP-Brasil ou e-Notariado.
4. A forma da procuração física no DETRAN-RJ não foi confirmada.
5. Não se encontrou fonte doutrinária ou jurisprudencial sobre a aplicação do art. 150, § 4º, da LSA à Ltda.
6. Não se confirmou se a certidão simplificada traz prazo de validade impresso (JUCEC, JUCESP, JUCERJA, JUCEMG).

---

## 1. ATPV / ATPV-e quando o VENDEDOR é PESSOA JURÍDICA (estado em 17/10/2026)

> Convenções: trechos entre aspas são transcrições literais da fonte indicada. "Não confirmado" = não localizei fonte oficial que comprove. Datas de página = "última atualização" exibida pela própria página quando disponível. Textos de norma foram extraídos do PDF/HTML oficial (DOU/gov.br/planalto/CNJ/TJCE) via download direto.

---

### 1.0 Resumo executivo (o que mudou e importa para o agente)

1. **A Resolução CONTRAN nº 809/2020 (que criou a ATPV-e) foi REVOGADA** pela **Resolução CONTRAN nº 1.027, de 17/08/2026** (DOU 18/08/2026, Edição 155-B, Seção 1 – Extra B, p. 10), em vigor na data da publicação, com **90 dias de adequação** para órgãos e entidades (até ≈16/11/2026, contagem minha). Revogou também as Res. 817/2021 e 999/2023 (que alteravam a 809). Fonte: https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/resolucao10272026.pdf
2. **Regra nova específica para PJ** (Res. 1.027, art. 28, § 7º): na ATPV-e assinada eletronicamente, a assinatura de PJ "será admitida mediante comprovação eletrônica dos poderes do signatário, por consulta a bases oficiais ou por instrumento de outorga verificável, com identificação do outorgante, do outorgado, dos poderes conferidos, do prazo de validade e de eventual revogação, na forma estabelecida pelo órgão máximo executivo de trânsito da União". **A regulamentação da SENATRAN desse § 7º não foi localizada até 17/10/2026 (não confirmado que exista).**
3. **Na ATPV-e (digital) passa a ser vedada a assinatura manuscrita** (art. 28, § 1º): só assinatura eletrônica **avançada ou qualificada**. O reconhecimento de firma por autenticidade em Tabelionato permanece para a **ATPV do verso do CRV em papel** (arts. 20 e 26). Porém, durante a transição, as páginas oficiais de DETRAN-SP (atualizada 08/10/2026), DETRAN-MG (08/06/2026) e DETRAN-CE (08/05/2026) ainda descrevem o fluxo antigo "ATPV-e impressa + firma reconhecida por autenticidade".
4. **Venda digital federal (CDT, hoje app "CNH do Brasil") NÃO atende PJ**: o serviço gov.br diz literalmente "Pessoa física proprietária ou futura proprietária de veículo"; o CNJ (Provimento 252/2026) registra que "a plataforma oficial de venda digital de veículos mantida pelo Governo Federal não admite a transferência por pessoas jurídicas"; e a nova funcionalidade prevista pela Res. 1.027 no app CNH do Brasil é para "veículos usados entre pessoas físicas" (Agência Gov, 20/08/2026).
5. **Cartórios de Registro Civil (ARPEN/IdRC) estão PROIBIDOS de assinar ATPV-e quando há PJ, empresário individual ou MEI em qualquer polo** (Provimento CNJ nº 252, de 18/08/2026), "ainda que a pessoa jurídica compareça por meio de representante legal".
6. **Conta gov.br é só de pessoa física**; para agir pela PJ é preciso vincular o CNPJ com **e-CNPJ (A1/A3) emitido no mesmo CPF**. A assinatura gov.br, portanto, identifica a pessoa física — não prova, por si, poderes societários.
7. **No Ceará (prioridade)**: (a) PJ vendedora apresenta "Contrato Social", documento do representante e "Comprovante Situação Cadastral do CNPJ (validade 30 dias)"; (b) procurador só com "Procuração pública e específica" (página gov.br/DETRAN-CE: "com validade de até 01 ano da data de expedição"); (c) no papel/ATPV-e impressa, firma reconhecida **por autenticidade** em Tabelionato (selo digital tipo 14) **e registro no RTD** (Lei estadual 14.605/2010, art. 16) — sem o registro no RTD o DETRAN-CE não recebe o documento; (d) a transferência digital do DETRAN-CE (Balcão Digital) é só para "pessoas físicas habilitadas no Ceará".
8. **Certidão simplificada da Junta não tem prazo de validade fixado em norma nacional**: a IN DREI 81/2020 (art. 101, § 2º) fala em 30 dias de **disponibilidade para download**, não de validade. Os prazos (30/90 dias, 1 ano) são exigências do órgão receptor — devem ser parâmetros configuráveis por UF/órgão.

---

### 1.1 Marco normativo nacional

#### 1.1.1 Linha do tempo
| Ato | Data / publicação | Situação em 17/10/2026 | Fonte |
|---|---|---|---|
| Res. CONTRAN 809/2020 (cria CRLV-e e ATPV-e) | 15/12/2020; DOU 24/12/2020; vigência 04/01/2021 (art. 27) | **Revogada** pela Res. 1.027/2026 (art. 60, I) | https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/Resolucao8092020.pdf |
| Res. CONTRAN 817/2021 (referenda Portaria CONTRAN 198/2021; altera a 809 — CRLV-e em papel A4; revoga arts. 8º e 9º da 809) | 17/03/2021 | **Revogada** (Res. 1.027, art. 60, II) | https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/Resolucao8172021.pdf |
| Res. CONTRAN 999/2023 (troca "Ministério da Infraestrutura/DENATRAN" por "Ministério dos Transportes/SENATRAN" nos modelos; vigência 02/10/2023) | 14/09/2023 | **Revogada** (Res. 1.027, art. 60, III) | Parecer SENATRAN: https://www.gov.br/transportes/pt-br/assuntos/transito/senatran/governanca-regulatoria-1/arquivos/Resoluo999_2023Relatriodedispensa.pdf ; texto: https://www.lex.com.br/resolucao-contran-no-999-de-14-de-setembro-de-2023/ |
| Portaria SENATRAN 1.137/2023 (credencia ARPEN-Brasil para disponibilizar e assinar ATPV-e) | 24/11/2023; DOU 27/11/2023 | Vigente, mas limitada pelo Prov. CNJ 252/2026 (sem PJ) | https://www.gov.br/transportes/pt-br/assuntos/transito/arquivos-senatran/portarias/2023/Portaria11372023.pdf |
| Lei 15.153/2025 (inclui § 4º no art. 123 do CTB — transferência integralmente eletrônica) | 26/06/2025; DOU 27/06/2025; art. 3º (vigência imediata) vetado, logo vacatio de 45 dias (LINDB); inciso III promulgado após derrubada do veto em 09/12/2025 (DOU 10/12/2025); inciso IV continua vetado (conferido no Planalto em 17/10/2026) | Vigente | https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/L15153.htm |
| **Res. CONTRAN 1.027/2026** (registro, licenciamento e transferência; modalidades; assinaturas avançadas/qualificadas; plataformas homologadas) | 17/08/2026; DOU 18/08/2026; vigência na publicação (art. 61); adequação 90 dias (art. 58) | **Vigente** | https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/resolucao10272026.pdf |
| Provimento CNJ 252/2026 (RCPN/ATPV-e; veda PJ) | 18/08/2026 (assinado 19/08/2026; retificação da ementa no DJe 20/08/2026) | Vigente, aplicação imediata (art. 10) | https://atos.cnj.jus.br/files/original124648202608206a86f73893e30.pdf ; retificação: https://portaldori.com.br/2026/08/21/provimento-corregedoria-nacional-de-justica-cnj-no-252-de-18-08-2026-d-j-e-20-08-2026-retificacao/ |
| Res. CONTRAN 1.026/2026 + Circular SENATRAN nº 2/2026 (RENAVE; integração do Renave à transferência/assinatura eletrônicas da Res. 1.027 entre 09 e 20/11/2026) | 26/06/2026; Circular 30/09/2026 | Vigente (detalhe na Seção 4) | https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/circular022026.pdf |

Observação: a página federal do serviço de venda digital ainda cita como base legal a "Resolução CONTRAN nº 809, de 15 de dezembro de 2020" (Última Modificação: 15/12/2025) — está desatualizada após 18/08/2026. https://www.gov.br/pt-br/servicos/vender-veiculos-digitalmente-pela-carteira-digital-de-transito-atpv-e

#### 1.1.2 Res. CONTRAN 809/2020 — dispositivos sobre ATPV-e (texto histórico, ainda citado pelos DETRANs)
Fonte (PDF do DOU): https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/Resolucao8092020.pdf
- Ementa: "Dispõe sobre os requisitos para emissão do Certificado de Registro de Veículo (CRV), do Certificado de Licenciamento Anual (CLA) e do comprovante de transferência de propriedade em meio digital."
- Art. 10: "Fica instituída a Autorização para Transferência de Propriedade do Veículo em meio digital (ATPV-e), expedida na forma estabelecida pelo órgão máximo executivo de trânsito da União, que constitui o comprovante de transferência de propriedade de que trata o inciso III do art. 124 do CTB."
- Art. 16: "Quando ambos, proprietário vendedor e comprador, possuírem os requisitos necessários para assinatura eletrônica da ATPV-e, o preenchimento e a assinatura poderão ocorrer nos sistemas do órgão máximo executivo de trânsito da União ou dos órgãos ou entidades executivos de trânsito dos Estados e do Distrito Federal que disponibilizarem essa funcionalidade, de acordo com a Lei nº 14.063, de 23 de setembro de 2020, e regulamentação vigente."
- Art. 17: "Na versão impressa, a ATPV-e deverá ser assinada e conter o reconhecimento de firma do vendedor e do comprador por autenticidade."
- Art. 18: "A Autorização para Transferência de Propriedade de Veículo (ATPV) constante no verso de CRV válido, emitido em meio físico, [...] deverá conter o reconhecimento de firma por autenticidade do antigo proprietário e do comprador."
- Art. 20, I: comunicação de venda eletrônica com "a) assinatura digital avançada, nos termos da Lei nº 14.063, de 2020, e de regulamentação vigente; ou b) certificado digital, de propriedade do vendedor e do comprador, emitido por autoridade certificadora, conforme padrão de Infraestrutura de Chaves Públicas Brasileira (ICP-Brasil)".
- Art. 21: "Nos casos previstos no art. 16, a assinatura eletrônica da ATPV-e pelo antigo proprietário caracteriza a comunicação de venda eletrônica do veículo."

#### 1.1.3 Res. CONTRAN 1.027/2026 — dispositivos-chave (texto literal do DOU)
Fonte: https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/resolucao10272026.pdf
- Base legal no preâmbulo: "art. 12, incisos I, II, VII e X, e o art. 123, § 4º, incisos I e III, da Lei nº 9.503".
- **Modalidades** — Art. 14: "I - transferência convencional; II - transferência eletrônica; e III - transferência eletrônica custodiada." § 1º: "Considera-se transferência convencional aquela em que uma ou mais etapas do processo de transferência de propriedade, ressalvada a vistoria de identificação veicular, dependam de atendimento presencial, apresentação física de documentos, processamento manual, reconhecimento de firma em meio físico ou da prática de atos não integralmente realizados em ambiente digital." § 2º: eletrônica = todas as etapas digitais, com "utilização de assinaturas eletrônicas avançadas ou qualificadas para manifestação de vontade".
- **Competência** — Art. 15, § 1º: a União (SENATRAN) executa "somente as modalidades de transferência eletrônica e de transferência eletrônica custodiada"; § 2º: os DETRANs executam "somente as modalidades de transferência convencional e de transferência eletrônica".
- **Etapas** — Art. 16: "I - registro da intenção de venda; II - comunicação de venda; e III - transferência de propriedade do veículo, com a correspondente expedição de novo CRLV-e."
- **Intenção de venda** — Art. 19: "A intenção de venda deverá ser manifestada formalmente pelo proprietário constante do registro do veículo no Renavam, por uma das seguintes formas: I - mediante preenchimento e assinatura da Autorização para Transferência de Propriedade do Veículo, constante no verso de Certificado de Registro de Veículo válido, emitido em meio físico; II - por solicitação de geração da [...] ATPV-e realizada eletronicamente em soluções, sistemas ou plataformas disponibilizados pelo órgão máximo executivo de trânsito da União ou pelos órgãos ou entidades executivos de trânsito dos Estados e do Distrito Federal; ou III - por solicitação de geração da ATPV-e realizada eletronicamente em plataformas de transferência eletrônica homologadas pelo órgão máximo executivo de trânsito da União."
- **CRV em papel** — Art. 20, § 1º: a manifestação "dependerá: I - da assinatura manuscrita do proprietário na Autorização para Transferência de Propriedade do Veículo; e II - do reconhecimento de firma por autenticidade da assinatura aposta no documento, em Tabelionato de Notas." Art. 26 (caput): a ATPV do verso do CRV físico "deverá conter as assinaturas manuscritas do antigo proprietário e do novo proprietário com reconhecimento de firma por autenticidade em Tabelionato de Notas." Art. 26, § 5º: o Tabelionato pode registrar a comunicação de venda eletronicamente no Renavam via plataforma homologada; § 6º: "na mesma data do reconhecimento de firma das assinaturas".
- **Desmaterialização do CRV** — Art. 8º, § 5º: "O reconhecimento de firma das assinaturas apostas em Autorização para Transferência de Propriedade do Veículo vinculada a Certificado de Registro de Veículo previamente desmaterializado não produzirá efeitos [...]".
- **ATPV-e** — Art. 27, § 1º: "A ATPV-e será gerada exclusivamente pelo órgão máximo executivo de trânsito da União [...]". § 3º: "a ATPV-e gerada somente será considerada formalizada como comprovante de transferência de propriedade após o registro, no Renavam, das assinaturas eletrônicas do antigo e do novo proprietário [...]". § 5º: "Somente poderá existir uma ATPV-e ativa por veículo [...]".
- **Assinatura da ATPV-e** — Art. 28 (caput): "Gerada a ATPV-e, o antigo proprietário e o novo proprietário deverão realizar suas assinaturas eletrônicas avançadas ou qualificadas por meio de plataformas de assinatura eletrônica homologadas pelo órgão responsável pela execução da transferência eletrônica, ressalvadas as soluções autorizadas independentemente de homologação específica, nos termos do art. 47." **§ 1º: "É vedada a aposição de assinatura manuscrita na ATPV-e, sendo admitidas exclusivamente assinaturas eletrônicas avançadas ou qualificadas [...]".** § 2º: assinaturas podem ocorrer "em momentos distintos". § 4º: registradas as duas assinaturas, "a comunicação de venda será automaticamente gerada e registrada no Renavam". § 6º: para revendedores (art. 330 CTB), comunicação automática via integração Renave. **§ 7º (PJ): "Quando o antigo ou o novo proprietário for pessoa jurídica, a assinatura será admitida mediante comprovação eletrônica dos poderes do signatário, por consulta a bases oficiais ou por instrumento de outorga verificável, com identificação do outorgante, do outorgado, dos poderes conferidos, do prazo de validade e de eventual revogação, na forma estabelecida pelo órgão máximo executivo de trânsito da União."** § 9º: vedado aos DETRANs instituir requisitos técnicos adicionais às plataformas homologadas.
- **Cancelamento** — Art. 29, § 2º: após a comunicação de venda, a ATPV-e só pode ser cancelada "por decisão judicial, fraude ou erro material comprovado em processo administrativo, ou distrato formal das partes [...] formalizada com assinaturas eletrônicas avançadas ou qualificadas".
- **Efeitos** — Art. 30: "O registro da comunicação de venda no Renavam produzirá os efeitos previstos no art. 134 do Código de Trânsito Brasileiro [...]". Art. 26, § 4º (papel): sem providência do comprador, o antigo proprietário deve encaminhar "no prazo máximo de sessenta dias, a cópia autenticada [...] sob pena de responsabilização solidária pelas penalidades impostas e suas reincidências até a data do efetivo registro da comunicação de venda."
- **Escolha da modalidade** — Art. 36, § 2º: "É vedado aos órgãos ou entidades executivos de trânsito dos Estados e do Distrito Federal restringir, impedir ou criar embaraços à utilização das modalidades ou soluções de transferência eletrônica e transferência eletrônica custodiada previstas nesta Resolução."
- **Tipos de assinatura** — Art. 44: "Nos processos de transferência eletrônica de propriedade de veículos previstos nesta Resolução, serão admitidas exclusivamente: I - assinatura eletrônica avançada; e II - assinatura eletrônica qualificada." Art. 45, § 1º: qualificadas seguem ICP-Brasil; § 2º: avançadas seguem o Anexo II e padrões do Decreto 10.543/2020.
- **Soluções autorizadas sem homologação** — Art. 47: "I - as soluções de assinatura eletrônica disponibilizadas pelo Governo Federal; II - as soluções de assinatura eletrônica qualificada credenciadas ou homologadas no âmbito da Infraestrutura de Chaves Públicas Brasileira - ICP-Brasil [...]; III - as soluções de assinatura eletrônica avançada ou qualificada disponibilizadas pelos serviços notariais e de registro, diretamente ou por intermédio de suas entidades representativas, desde que a atividade esteja compreendida nas atribuições legais da respectiva especialidade ou seja autorizada pelo Conselho Nacional de Justiça - CNJ [...]; e IV - as soluções de assinatura eletrônica avançada ou qualificada disponibilizadas diretamente pelos órgãos ou entidades executivos de trânsito dos Estados e do Distrito Federal."
- **Despachante** — Art. 52: "A atuação do despachante documentalista em nome e por conta do interessado observará o mandato presumido previsto em lei, devendo, nos processos eletrônicos disciplinados nesta Resolução, ser assegurada a identificação do vínculo entre o interessado, o despachante documentalista e o respectivo processo." (§ 1º: vínculo por contrato eletrônico assinado, consentimento eletrônico em sistema integrado, ou "instrumento particular físico").
- **Transição** — Art. 58: "Os órgãos ou entidades que desempenham atividades relacionadas ao objeto desta Resolução terão o prazo de noventa dias, contados da data de publicação desta Resolução, para se adequarem às suas disposições." § 1º: "Durante o prazo de que trata o caput, permanecerão válidos e produzirão efeitos jurídicos os credenciamentos, autorizações, integrações e procedimentos operacionais regularmente instituídos sob a regulamentação anterior [...]". § 2º: "Não poderão ser iniciados novos processos nem praticados novos atos em desconformidade com esta Resolução, ressalvados os prazos específicos de adequação nela previstos e em seus Anexos e o disposto nos §§ 4º e 5º." Art. 59, § 2º: o CRV em papel e a ATPV nele constante "permanecerão válidos enquanto não ocorrer hipótese que determine sua substituição, cancelamento ou desmaterialização".
- Art. 60: "Ficam revogadas as Resoluções: I - nº 809, de 15 de dezembro de 2020; II - nº 817, de 17 de março de 2021; e III - nº 999, de 14 de setembro de 2023." Art. 61: "Esta Resolução entra em vigor na data de sua publicação."
- Não há na Res. 1.027 dispositivo que preveja "ATPV-e impressa" assinada à mão com firma reconhecida (busquei por "impress", "manuscrit", "meio físico"): as únicas assinaturas manuscritas previstas são na ATPV do verso do CRV em papel. **Conclusão (inferência minha):** após o prazo de adequação, o caminho "imprimir ATPV-e e reconhecer firma" tende a deixar de existir para veículos com CRV-e; **a prática dos DETRANs após ≈16/11/2026 não está confirmada.**

#### 1.1.4 Lei 15.153/2025 (CTB, art. 123, § 4º) — síntese
Fonte: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/L15153.htm. O § 4º permite a transferência "integralmente por meio eletrônico" pela SENATRAN ou DETRANs; inciso I: contrato com "assinaturas eletrônicas qualificadas ou avançadas, na forma da Lei nº 14.063 [...] e das normas regulamentares do Contran"; inciso II: contrato assinado perante a SENATRAN "terá validade em todo o território nacional"; inciso III (promulgado após derrubada de veto): assinatura avançada "por meio de plataforma de assinatura homologada"; inciso V: vistoria eletrônica a critério do DETRAN. (Texto literal completo: ver Seção 3.) A lei **não trata especificamente de vendedor PJ**; quem trata é a Res. 1.027, art. 28, § 7º.

#### 1.1.5 Lei 14.063/2020 — nada específico para veículos
Fonte: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14063.htm
- Não há menção a "veículo" na lei (busca no texto). A assinatura qualificada é obrigatória, entre outros, "IV - nos atos de transferência e de registro de bens imóveis [...]" (art. 5º, § 2º) — **não** para veículos; logo, para veículos a avançada é admissível (a Res. 1.027, art. 44, admite avançada ou qualificada).
- Art. 4º define: simples; "II - assinatura eletrônica avançada: a que utiliza certificados não emitidos pela ICP-Brasil ou outro meio de comprovação da autoria e da integridade [...]"; "III - assinatura eletrônica qualificada: a que utiliza certificado digital, nos termos do § 1º do art. 10 da Medida Provisória nº 2.200-2 [...]".

#### 1.1.6 Portaria SENATRAN nº 1.137/2023 (ARPEN — Registro Civil)
Fonte: https://www.gov.br/transportes/pt-br/assuntos/transito/arquivos-senatran/portarias/2023/Portaria11372023.pdf
- Art. 1º: credencia a ARPEN Brasil "para prestar o serviço de disponibilização e assinatura da Autorização para Transferência de Propriedade do Veículo em meio digital (ATPV-e)". Parágrafo único: "O serviço de que trata o caput é um canal de atendimento aos cidadãos facultativo, de livre escolha dos vendedores e compradores de veículos, em âmbito nacional."
- Anexo, item 3: dados acessíveis incluem "Número de documento do proprietário do veículo (pessoa física ou pessoa jurídica)". **Mas o Prov. CNJ 252/2026 vedou o atendimento a PJ (abaixo).**
- Portarias DENATRAN/SENATRAN específicas que regulamentassem a assinatura gov.br da ATPV-e na CDT (2021–2023): **não localizadas** (não confirmado). O serviço federal cita apenas a Res. 809/2020.

#### 1.1.7 CNJ — Provimento nº 252/2026 (Registro Civil e ATPV-e) — PJ VEDADA
Fonte: https://atos.cnj.jus.br/files/original124648202608206a86f73893e30.pdf (assinado em 19/08/2026)
- Considerando (literal): "CONSIDERANDO que a plataforma oficial de venda digital de veículos mantida pelo Governo Federal não admite a transferência por pessoas jurídicas, justamente em razão da inviabilidade de verificação automatizada e segura de poderes societários, impondo-se, por simetria e prudência regulatória, idêntica restrição ao serviço prestado pelas serventias".
- Considerando: "a prestação do serviço a pessoas jurídicas sem a prévia e adequada qualificação da existência, da regularidade e da representação societária expõe o tráfego jurídico ao risco concreto de alienações nulas ou ineficazes, na forma dos arts. 47 e 115 a 120 do Código Civil [...]".
- Considerando: "os órgãos executivos de trânsito não dispõem de estrutura jurídica de atendimento destinada ao exame de atos constitutivos, deliberações e limitações estatutárias de alçada [...]".
- Art. 3º, parágrafo único: "A prestação do serviço não importa reconhecimento de firma, autenticação ou outro ato privativo do Tabelião de Notas, nem juízo sobre a validade, a eficácia ou o conteúdo do negócio jurídico ou sobre a regularidade do veículo."
- Art. 4º: "O serviço somente poderá ser prestado quando todas as partes do negócio jurídico forem pessoas naturais, civilmente capazes, atuando em nome próprio."
- Art. 5º: "A aposição de assinatura eletrônica avançada será recusada quando: I – figurar pessoa jurídica, empresário individual ou microempreendedor individual em qualquer dos polos da relação negocial, seja como alienante, seja como adquirente, inclusive na condição de credor fiduciário, arrendador ou administrador de consórcio; e II – figurar ente despersonalizado ou universalidade, tais como espólio, massa falida, condomínio edilício ou grupo de consórcio." Parágrafo único: "A vedação prevista no inciso I incide ainda que a pessoa jurídica compareça por meio de representante legal ou estatutário regularmente identificado pelo IdRC."
- Art. 6º: na recusa, orientação "quanto à necessidade de instrumentalização do negócio perante o Tabelião de Notas ou o órgão executivo de trânsito competente".
- Art. 10: vedações "aplicam-se de imediato". Contexto: o CNJ havia restabelecido em 02/07/2026 a autorização do serviço do Registro Civil, antes suspensa (https://www.arpensp.org.br/noticia/cnj-restabelece-autorizacao-para-cartorios-de-registro-civil-realizarem-transferencia-digital-de-veiculos — data e ato da suspensão anterior: não confirmados).

#### 1.1.8 CNJ — Código Nacional de Normas (Prov. 149/2023): e-Notariado e reconhecimento de firma
Fonte (texto consolidado no portal de atos do CNJ): https://atos.cnj.jus.br/atos/detalhar/5243
- Art. 285, II: "certificado digital notarizado: identidade digital de uma pessoa física ou jurídica, identificada presencialmente por um notário a quem se atribui fé pública".
- Art. 306: "Compete, exclusivamente, ao tabelião de notas: [...] III - reconhecer as assinaturas eletrônicas apostas em documentos digitais, ato que terá a mesma força jurídica de um reconhecimento de firma; e (redação dada pelo Provimento n. 178, de 15.8.2024) IV — realizar o reconhecimento da firma como autêntica no documento físico, devendo ser confirmadas, por videoconferência, a identidade. a capacidade daquele que assinou e a autoria da assinatura a ser reconhecida." § 1º: "Tratando-se de documento atinente a veículo automotor, será competente para o reconhecimento de firma, de forma remota, o tabelião de notas do município de emplacamento do veículo ou de domicílio do adquirente indicados no Certificado de Registro de Veículo (CRV) ou na Autorização para Transferência de Propriedade de Veículo (ATPV)."
- Art. 308: no reconhecimento eletrônico por autenticidade deve constar "que a assinatura foi aposta no documento, perante o tabelião, seu substituto ou escrevente, em procedimento de videoconferência."
- Art. 353-A (incluído pelo Prov. 183/2024; capítulo de registro de imóveis): quando o título "proceder de ente coletivo, será exigido o reconhecimento de firma apenas do representante" (https://www.irib.org.br/provimento-cn-cnj-n-183-de-12-de-novembro-de-2024/).

---

### 1.2 Vendedor PJ: quem assina e por quais meios

#### 1.2.1 Quem assina
- Juridicamente, quem "vende" é a PJ; assina **a pessoa natural que a representa** (administrador/diretor com poderes, ou procurador). O cartório reconhece a firma **da pessoa física do representante**, não "da PJ": CGJ-TJMG, Decisão 6788/2020 — "não sendo possível o reconhecimento de firma de pessoa jurídica, mas apenas de um ou mais de seus representantes legais" (https://bd-login.tjmg.jus.br/jspui/handle/tjmg/11258).
- **O reconhecimento de firma, por si, não prova poderes**: Código de Normas do TJSC, art. 1.270, § 1º — o tabelião é responsável "unicamente pela análise da assinatura constante do documento a ele apresentado, não lhe competindo verificar a natureza do ato ou contrato, sua legalidade, validade, existência, eficácia ou a representação das partes"; § 2º — "A requerimento, no reconhecimento de firma de signatário, poderá ser certificado que o signatário assina em representação de pessoa jurídica ou outra pessoa física, desde que haja a conferência dos respectivos poderes nos atos constitutivos ou procurações." (https://www.tjsc.jus.br/web/codigo-de-normas/extrajudicial/livro-iii/titulo-vi/capitulo-vii-reconhecimento-de-firma — texto obtido via extração da página; é norma de SC, usada aqui como ilustração do princípio). O DETRAN-MG aceita "CRV/ATPV-e com reconhecimento de firma por pessoa jurídica" como alternativa aos atos constitutivos — provavelmente essa certificação de representação pelo tabelião (**interpretação provável; não confirmada**).
- Na via eletrônica nacional, a prova de poderes passa a ser exigência expressa (Res. 1.027, art. 28, § 7º — ver 1.1.3), mas o procedimento da SENATRAN **não foi localizado**.

#### 1.2.2 (i) Assinatura eletrônica gov.br — vale para PJ?
- "A conta gov.br apenas pode ser criada para Pessoa Física. Quando um serviço ou sistema integrado ao login do gov.br permitir o acesso de Pessoa Jurídica, será necessário vincular o CNPJ desejado à uma conta gov.br de Pessoa Física. Este processo é feito usando um Certificado Digital de Pessoa Jurídica (e-CNPJ)." Pontos: "É necessário um e-CNPJ registrado no mesmo CPF da conta gov.br desejada"; "Apenas são aceitos certificados digitais A1 ou A3, certificados em nuvem não serão identificados"; "Não será possível vincular a empresa desejada utilizando um certificado digital de pessoa física"; acesso também por "colaboradores cadastrados". Fonte: https://www.gov.br/governodigital/pt-br/acessibilidade-e-usuario/atendimento-gov.br/duvidas-na-conta-gov.br/duvidas-na-vinculacao-de-cnpj-no-gov.br
- Exemplo de vínculo baseado no cadastro da Receita (não no contrato social): PGFN/Regularize (17/09/2026) — "é necessário estar registrado como responsável pela empresa perante a Receita Federal do Brasil" (https://www.gov.br/pgfn/pt-br/assuntos/noticias/2026/novo-acesso-ao-regularize-para-representantes-de-empresas). **Alerta para o agente:** o "responsável perante a RFB" (um por CNPJ) não é necessariamente quem tem poderes de alienação segundo o contrato social, e vice-versa.
- **Venda digital federal (CDT/CNH do Brasil): só pessoa física** (ver 1.4). Logo, na prática atual, a assinatura gov.br da ATPV-e **não atende vendedor PJ** no canal federal. Exceção estadual: SP (TDV), via CPF do representante legal + procuração eletrônica (ver 1.3.2).
- Pela Res. 1.027, art. 47, I, soluções de assinatura do Governo Federal são aceitas sem homologação; para PJ, exige-se a comprovação de poderes do art. 28, § 7º — **implementação não confirmada**.

#### 1.2.3 (ii) Certificado ICP-Brasil (e-CNPJ ou e-CPF do representante)
- Base: Res. 809/2020, art. 20, I, "b" (histórico); Res. 1.027/2026, arts. 44, 45, § 1º, e 47, II (vigente): assinatura qualificada ICP-Brasil é aceita sem homologação específica.
- Para PJ, a Res. 1.027 exige ainda prova eletrônica de poderes (art. 28, § 7º). Usar e-CNPJ identifica a empresa e seu responsável perante a RFB, mas **não prova** que o contrato social dá a essa pessoa poder para alienar bens (inferência; não há norma que equipare e-CNPJ a prova de poderes).
- Aceitação concreta de ATPV-e assinada com ICP-Brasil por vendedor PJ: **DETRAN-RJ** aceita ATPV-e "assinados digitalmente, conforme requisitos definidos pela Resolução Contran nº 809/2020" e credencia plataformas com assinatura qualificada (ICP-Brasil) e/ou avançada (Portaria DETRAN-RJ SEI nº 6834/2025, art. 1º, IV — https://www2.detran.rj.gov.br/portal/pdfs/2025/27062025_Portaria6834.pdf); **DETRAN-CE: não confirmado**; **DETRAN-MG**: digital só PF (ver 1.3.4); **DETRAN-SP**: via TDV/e-Notariado (ver 1.3.2). DETRAN-SC tem norma própria (Portaria Normativa nº 2/2026) que, segundo resumo do LegisWeb, aceita ICP-Brasil na ATPV-e — **texto literal não conferido** (https://www.legisweb.com.br/legislacao/?id=490189).

#### 1.2.4 (iii) Cartório
- **Tabelionato de Notas — reconhecimento por autenticidade (papel):** obrigatório na ATPV do verso do CRV físico (Res. 1.027, arts. 20, § 1º, II, e 26). Na ATPV-e impressa era exigido pela Res. 809, art. 17 (revogada); os DETRANs ainda o descrevem na transição (ver 1.3). Assina o representante; o tabelião não verifica poderes salvo pedido de certificação da representação (TJSC art. 1.270, § 2º, acima). O que o cartório exige do representante da PJ para o reconhecimento por autenticidade: em regra, ficha de firma/cartão de autógrafos, comparecimento pessoal e documento de identidade (no CE, o registro fotográfico era exigido pelo Prov. 17/2024, art. 1º, IV, mas esse provimento foi revogado pelo Prov. 05/2025/CGJCE; se a exigência persiste por outra norma: não confirmado); **não localizei norma nacional nem de CE/SP/RJ/MG que obrigue o tabelião a exigir atos constitutivos da PJ** para reconhecer a firma do representante (não confirmado) — a conferência de poderes pelo tabelião só ocorre se pedida a certificação da representação (ex.: TJSC, art. 1.270, § 2º).
- **e-Notariado:** assinatura eletrônica notarizada/certificado digital notarizado (pode ser de pessoa física **ou jurídica** — CNN art. 285, II) e reconhecimento remoto (CNN art. 306, § 1º). Em SP, o módulo e-Not Assina para ATPV-e (lançado em 2022) informava: "Nesta fase apenas pessoas físicas poderão assinar eletronicamente o ATPV-e", vedada assinatura híbrida (https://cnbsp.org.br/2022/10/17/cnb-sp-e-cnb-cf-lancam-modulo-de-assinatura-de-documento-de-transferencia-de-veiculos-de-sp-atpv-e-via-e-not-assina/). Situação atual para PJ no e-Notariado/ATPV-e: **não confirmada**.
- **Registro Civil (ARPEN/IdRC):** **vedado para PJ, EI e MEI** (Prov. CNJ 252/2026, arts. 4º e 5º).

---

### 1.3 Documentos para provar poderes do representante — exemplos por DETRAN

#### 1.3.1 CEARÁ (prioridade)
**a) DETRAN-CE — serviço "Solicitar transferência de propriedade de veículo"** (Ceará Digital, serviço 2403; "last_publication_date: 08/05/2026"; dados obtidos da API pública do portal que alimenta https://cearadigital.ce.gov.br/servicos/2403):
- Requisitos: "O veículo deve ser aprovado na vistoria de identificação veicular." / "Deve haver intenção de venda assinada pelo comprador e vendedor, com reconhecimento em cartório."
- Informação: "O vendedor deve registrar a intenção de venda antes da transferência."
- Documentos (literal): "Se Pessoa Jurídica (CNPJ): Contrato Social, Documento de Identificação Oficial com foto do representante legal da empresa (CNH ou RG e CPF) e Comprovante Situação Cadastral do CNPJ (validade 30 dias)".
- "Se REPRESENTANTE LEGAL (terceiro): documento oficial com foto do representante (CNH ou RG e CPF); Comprovante de residência do representante e Procuração pública e específica para o fim que se destina".
- "Se compra e venda: Documento de intensão de venda assinad pelo comprador e vendedor reconhecida em cartório" (sic).
- "Se DESPACHANTE: Carteira profissional, Documento oficial com foto (CNH ou RG e CPF) e RPS assinado pelo proprietário do veículo em favor do despachante com reconhecimento de firma em cartório".
- Observação: a página fala apenas em "Contrato Social" — **não menciona** "última alteração", "consolidação" nem "certidão simplificada da Junta" (exigência de certidão simplificada pelo DETRAN-CE: **não confirmada**).

**b) DETRAN-CE no gov.br (Serviços Estaduais) — "Solicitar Transferência Veicular nos Postos do DETRAN/CE"** (Latest Modified: 12/04/2025): "Who can use this service? O proprietário do veículo, no caso de pessoa física; 2. Representante legal, no caso de pessoa jurídica; 3. Procurador por instrumento de procuração pública e específica para o ato (com validade de até 01 ano da data de expedição); 4. Despachante documentalista credenciado pelo DETRAN/CE." Fonte: https://www.gov.br/en/state-services/servico_estadual?id=20880

**c) Corregedoria-Geral da Justiça do Ceará: Provimento nº 05/2025/CGJCE (vigente) e Provimento nº 17/2024/CGJCE (REVOGADO)**
- **Correção de consolidação (conferida no PDF oficial em 17/10/2026):** o Prov. 17/2024 foi revogado expressamente pelo **Provimento nº 05/2025/CGJCE** (DJEA ed. 3596, 01/08/2025; vigência 50 dias após a publicação). Art. 7º: "revogando-se as disposições em contrário, em especial o Provimento nº 17/2024/CGJCE". Fonte: https://portal.tjce.jus.br/uploads/2025/08/Provimento-no-05-2025-CGJCE.pdf
- Prov. 05/2025, art. 4º (vigente): as serventias de Notas, "ao receberem a Autorização para Transferência de Propriedade de Veículo (APTV ou ATPV-e), procederão ao reconhecimento de ﬁrma do(a) signatário(a), vendedor(a) ou comprador(a), por autenticidade, com as cautelas exigidas no Código de Normas do Serviço Extrajudicial, utilizando o selo do tipo 14 no formato digital."
- Art. 5º: se a firma do vendedor foi reconhecida em outra UF, o tabelião "deverá reconhecer o sinal público, por semelhança, do(a) tabelião(ã) anterior".
- Art. 6º, §§ 1º e 2º: o usuário pode usar o DUT Eletrônico (facultativo). Se não usar, o tabelião o orienta "a providenciar o registro da APTV e a comunicação de venda junto a uma serventia de Registro de Títulos e Documentos de sua escolha, antes de apresentar ao Departamento de Trânsito [...] em cumprimento à Lei Estadual nº 14.605/2010."
- *Histórico, não vigente:* Prov. 17/2024/CGJCE (DJe-Adm 15/10/2024) — https://portal.tjce.jus.br/uploads/2024/10/PROVIMENTO-17-2024.pdf. O texto que segue fica só como referência.
- (Revogado) Art. 1º: "Definir que o processamento da autorização para transferência de propriedade de veículo automotor exigirá: I - o comparecimento pessoal do(a) vendedor(a) e do(a) comprador(a), simultâneo ou em momentos distintos, perante um(a) Tabelião(ã) de Notas ou substituto(a) legal, para o reconhecimento de firma, por autenticidade; II - a utilização de selo tipo 14, um para cada assinatura reconhecida; III - a captura da imagem do documento de transferência, Certificado de Registro de Veículos (CRV) ou da via impressa da Autorização para Transferência de Propriedade de Veículos (APTV-e), devidamente preenchido e selado; IV - o registro fotográfico do(a) vendedor(a) e do(a) comprador(a) [...]; V - o registro da operação por Cartório de Registro de Títulos e Documentos; VI - a comunicação ao DETRAN, para os fins do art. 134 da Lei nº 9.503 [...]."
- (Revogado) Art. 12: "É admitida a aquisição e alienação de veículo por procurador(a) constituído(a) por instrumento público, que deve ser exibido, conferida a autenticidade e ter uma cópia armazenada na serventia." § 1º: no documento figura "o nome do(a) mandante, como vendedor(a) ou comprador(a) [...] mas deverá ser assinado pelo(a) mandatário(a), cuja firma deverá ser reconhecida por autenticidade". (O provimento **não trata** de representante estatutário de PJ — não há artigo específico.)
- (Revogado; regra equivalente no art. 5º do Prov. 05/2025) Art. 5º: firma do vendedor reconhecida em outra UF → reconhecimento do "sinal público, por semelhança" do tabelião anterior.

**d) CGJCE — Ofício Circular nº 396/2026 (10/07/2026) + Parecer nº 1120/2026** — https://portal.tjce.jus.br/uploads/2026/07/OFICIO-396-1784047052.pdf
- Plataforma "DUT Eletrônico" (SINOREDI-CE) é facultativa; o cartório deve "promover o reconhecimento de firma por autenticidade (002021) e ao entregar o documento ao usuário, instruí-lo a dirigir-se a um cartório de RTD, de sua livre escolha, para requerer o registro, informando que a ausência do registro obstará a recepção do documento pelo DETRAN e a concretização da transferência do veículo."
- Parecer: "O lançamento de assinaturas (digitais) do comprador e do vendedor, para veículos com registro eletrônico, pode ser feito através do aplicativo Carteira Digital de Trânsito, pela plataforma gov.br, ambos utilizando uma conta perfil ouro, situação que dispensa ida ao cartório para reconhecimento das firmas por autenticidade." / "Quando não utilizado o gov.br, o reconhecimento das firmas do vendedor e do comprador deve ser feito em cartório de notas, por autenticidade."
- Lei Estadual CE nº 14.605/2010, art. 16 (citada no parecer): "Ficam os Cartórios de Títulos de documentos obrigados a registrar e informar eletronicamente operações de venda e compra ou qualquer forma de transferência de propriedade de veículos ao órgão de trânsito do Estado do Ceará."
- Selo tipo 14 migrou para digital em 30/03/2026 (o parecer cita ora "Provimento nº 05/2026/CGJCE", ora "Provimento nº 05/2025/CGJCE"; o link aponta para https://portal.tjce.jus.br/uploads/2025/08/Provimento-no-05-2025-CGJCE.pdf). O ato correto é o Provimento nº 05/2025/CGJCE, conferido no PDF oficial. Ele dá 50 dias a partir de 01/08/2025 para a migração. A data de 30/03/2026 citada no parecer não foi conferida; pode ter havido prorrogação (não confirmado).

**e) Transferência digital do DETRAN-CE (Balcão Digital)** — Ceará Digital, serviço 3284 (26/02/2026): requisito "Comprador e vendedor devem ser pessoas físicas habilitadas no Ceará."; "Possuir documento do veículo no formato digital (CRLV-e)"; FAQ: "Preciso ir ao cartório? Se você estiver dentro do requisitos da transferência digital, não precisa. [...] a sua assinatura é substituída pelo reconhecimento facial."; "Fiz a comunicação de venda no cartório, posso dar continuidade pela transferência digital? Não." (https://cearadigital.ce.gov.br/servicos/3284 ; portal: https://balcao.detran.ce.gov.br/servicosdigitais/login). **Não atende PJ.**

#### 1.3.2 SÃO PAULO
**a) Detran-SP/Poupatempo — "Transferir Propriedade de Veículo Registrado em São Paulo"** (Última atualização: 08/10/2026) — https://www.poupatempo.sp.gov.br/carta/859FFA63-4EEB-472A-843B-F9595D5AAA32 (mesmo conteúdo em https://servicos.sp.gov.br/fcarta/859FFA63-4EEB-472A-843B-F9595D5AAA32)
- Etapa 2: "Vá ao cartório para reconhecer firma no documento de venda. Se o documento foi emitido a partir de 2021, preencha também a ATPV-e [...]".
- "Pessoa jurídica como proprietária anterior: Se quem assinou o CRV for o representante legal: Contrato Social atualizado ou Certificado da Condição de Microempreendedor ou Estatuto Social e ata de eleição da diretoria (para sociedades por ações, associações ou fundações). [...] Se quem assinou for procurador do representante legal: Documentos acima e Procuração com: - Instrumento público com poderes específicos, ou - Instrumento particular com poderes específicos, identificação do veículo (placa ou chassi) e firma reconhecida por autenticidade."
- "Comprador e/ou vendedor representado por procurador apresentar: Procuração com assinatura eletrônica (nato digital) ou digitalizado com firma reconhecida por autenticidade. Para advogado apresentar OAB Não é necessário reconhecimento de firma."
- "Veículo registrado em nome de pessoa jurídica inativa (empresa baixada): Alvará judicial (digitalizado). Atenção: MEI, ME e produtor rural (pessoa física) podem transferir o veículo mesmo com cadastro baixado, sem necessidade de autorização judicial."
- "Reconhecimento de firma realizado fora do Estado de São Paulo: É necessário apresentar o Sinal Público."
- Prazo de validade da documentação societária (contrato "atualizado") **não definido em dias** na página.

**b) Detran-SP — "Gerenciar Procurador para Serviços de Veículos"** (procuração eletrônica) — https://servicos.sp.gov.br/fcarta/E1D0F0ED-684A-4496-B716-F56FFE1D253A
- Tipos: "Pessoa física para pessoa física; Pessoa física para pessoa jurídica; Pessoa jurídica para pessoa física; Pessoa jurídica para pessoa jurídica." Documentação PJ: "CNPJ e dados do representante legal (nome e CPF)."
- Condições: "Ter conta no Gov.br com nível prata ou ouro." / "Ser o proprietário do veículo (pessoa física) ou o representante legal da empresa proprietária do veículo (pessoa jurídica) para criar ou editar a procuração." / "A procuração tem prazo de validade definido no momento do cadastro e pode ser revogada a qualquer momento [...]". Serviço disponível: "Realizar Transferência Digital".
- Como o Detran-SP verifica quem é o "representante legal" da PJ (Receita/QSA vs. contrato social): **não confirmado**.

**c) Agência SP (12/02/2026) — TDV com procuração e PJ** — https://www.agenciasp.sp.gov.br/transferencia-digital-de-veiculos-avanca-para-cartorios-e-pessoas-juridicas-em-sp/
- "Num primeiro momento, a TDV via procuração permitirá a transação entre pessoas físicas e a transferência de um veículo usado de uma pessoa jurídica (por meio do CPF de seu representante legal) a uma pessoa física. Num segundo momento, a procuração abarcará também a transferência inversa, de uma pessoa física a uma pessoa jurídica e entre duas pessoas jurídicas (sempre na figura de seu representante legal)." (Implantação do "segundo momento": não confirmada.)
- Fluxo cartorário: após o reconhecimento das firmas, "caberá ao cartório enviar as informações sobre a transação para a Secretaria da Fazenda (SEFAZ), no prazo de 72h", que repassa ao Detran-SP para conclusão via TDV.

#### 1.3.3 RIO DE JANEIRO
**DETRAN-RJ — Transferência de Propriedade** — https://www.detran.rj.gov.br/todos-os-servicos/servicos-drv/transferencia-de-propriedade.html (versão antiga: https://www5.detran.rj.gov.br/_documento.asp?cod=2170; data de atualização não exibida)
- "Original do Certificado de Registro de Veículo (CRV) [...] cujas firmas serão reconhecidas por autenticidade [...]; Ou ATPV-e devidamente preenchido e assinado por comprador e vendedor, com firmas reconhecidas por autenticidade, ou assinados digitalmente, conforme requisitos definidos pela Resolução Contran nº 809/2020".
- "Cópia autenticada em cartório do contrato social que possibilite confirmar se a pessoa que assinou a autorização para a transferência tem poderes para tal ato, quando o vendedor for pessoa jurídica [...] (Lei Estadual nº 5.069/07)".
- "Cópia autenticada em cartório do estatuto e da ata da última assembléia ou dos atos constitutivos, conforme o tipo de empresa (Lei Estadual nº 5.069/07)".
- "Certidão Negativa de Débito (CND) ou Certidão Positiva de Débitos com Efeitos de Negativa (CPD-EN), do INSS, quando o vendedor for pessoa jurídica e o valor do veículo ultrapassar o limite estabelecido em portaria [...]".
- "Os reconhecimentos de firmas por cartórios de outras UFs terão de conter o sinal público de um tabelião do estado do Rio de Janeiro."
- Leasing (vendedor arrendatário): "Cópia autenticada em cartório de procuração por instrumento público, citando os mesmos nomes dos representantes que assinaram o [...] CRV como vendedores".
- Recomendação: reconhecimento de firma "em até 8 dias antes da data do atendimento" (prazo para o TJ disponibilizar a validação do selo eletrônico).
- **Portaria DETRAN-RJ SEI nº 6834/2025 (27/06/2025)** — credenciamento de "multiplataforma" de venda digital: art. 3º, § 2º: a plataforma "deverá possuir funcionalidade que permita que o Proprietário Vendedor outorgue procuração que conceda poderes para que um terceiro possa representá-lo como vendedor para efeito de assinatura do ATPV-e"; § 4º: "sendo inválido o emprego de assinatura física e eletrônica no mesmo documento". Regra específica para vendedor PJ na plataforma: **não há** (não confirmado como é tratada).

#### 1.3.4 MINAS GERAIS
**a) DETRAN-MG — "Documentos necessários para pessoa física e jurídica"** — https://www.transito.mg.gov.br/veiculos/transferencias/documentos-necessarios-para-atendimento-presencial
- "Vendedor é pessoa jurídica — Com reconhecimento de firma por pessoa jurídica: Certidão Negativa de Débitos (CND) da pessoa jurídica alienante/vendedor, expedida [...] caso valor da venda seja superior a R$ 87.493,73, conforme portaria interministerial MPS/MF nº 13, de 9 de janeiro de 2026; CRV/ATPV-e com reconhecimento de firma por pessoa jurídica."
- "Com reconhecimento de firma por pessoa física: Certidão Negativa de Débitos (CND) [...] caso valor da venda seja superior a R$ 87.493,73 [...]; Cópia autenticada do documento constitutivo da empresa vendedora; ou Contrato Social ou da última Alteração Contratual, se houver; ou cópia autenticada da Estatuto e Ata; ou original de Nota Fiscal eletrônica; ou original ou cópia autentica de Procuração Pública; ou cópia autenticada da Certidão/Requerimento de Microempreendedor Individual; ou cópia autenticada do documento equivalente."
- Procurador: "Original ou cópia autenticada da procuração por instrumento público, se procurador for pessoa física; Original ou cópia autenticada da procuração por instrumento público e do Contrato social atualizado, se procurador for pessoa jurídica." Advogado: "Procuração por instrumento particular dispensado o reconhecimento de firma em cartório".
- Comprador PJ: "Cartão CNPJ com menos de 90 dias constando situação da empresa ativa [...]".
- CRV/ATPV-e "devem estar com firma reconhecida por autenticidade/verdadeira".

**b) MG.gov.br — "Transferir propriedade de veículo (comprador)"** (Atualizado em: 08/06/2026) — https://www.mg.gov.br/servico/transferir-propriedade-de-veiculo
- "A transferência de veículos presencial é uma opção para veículos com Certificado de Registro de Veículo (CRV) físico, pessoa jurídica ou para proprietários(as) de veículos que escolham essa forma de atendimento."
- "É proibido o reconhecimento de firma por abono ou semelhança no ATPV-e. É proibida a utilização de assinatura digital e física ao mesmo tempo na ATPV-e."
- Prazo: concluir "no prazo máximo de 30 dias, a contar da assinatura da ATPV-e".

**c) DETRAN-MG — "Realizar a venda de um veículo (vendi meu veículo)"** — https://www.transito.mg.gov.br/veiculos/transferencias/realizar-a-venda-de-um-veiculo-vendi-meu-veiculo
- "A Transferência de veículos digital está disponível apenas para Pessoas Físicas que têm veículos com o Certificado de Registro de Veículo (CRV) digital emitido a partir de janeiro de 2021."
- "Acessar o aplicativo CNH do Brasil (antiga Carteira Digital de Trânsito - CDT)"; "A Transferência Digital iniciada no aplicativo CNH do Brasil não está disponível para veículos que possuem coproprietários."
- Comunicação de venda virtual: "a pessoa vendedora precisa ser pessoa física".

#### 1.3.5 Base legal da CND exigida por MG e RJ para PJ vendedora
Lei 8.212/1991, art. 47 (texto compilado do Planalto): "É exigida Certidão Negativa de Débito-CND, fornecida pelo órgão competente, nos seguintes casos: I - da empresa: [...] c) na alienação ou oneração, a qualquer título, de bem móvel de valor superior a Cr$ 2.500.000,00 (dois milhões e quinhentos mil cruzeiros) incorporado ao ativo permanente da empresa;" — https://www.planalto.gov.br/ccivil_03/leis/l8212cons.htm (valor atualizado por portaria interministerial; MG cita R$ 87.493,73 pela Portaria Interministerial MPS/MF nº 13/2026). Relevante: incide sobre veículo do **ativo permanente/imobilizado**, não sobre estoque de revenda (inferência a partir do texto legal).

#### 1.3.6 Certidão simplificada da Junta Comercial — prazo de validade
- **IN DREI nº 81/2020** (texto atualizado oficial): art. 96: "A Certidão Simplificada constitui-se de extrato de informações atualizadas, constantes de atos arquivados e/ou de arquivos eletrônicos [...]"; art. 99, § 1º: "Os atos arquivados nas juntas comerciais revestidos das formalidades legais produzem efeitos perante terceiros, os quais não podem alegar desconhecimento (eficácia erga omnes) [...]"; **art. 101, § 2º: "As certidões devem ficar disponíveis pelo prazo de 30 (trinta) dias, sendo certo que o seu download pelo usuário poderá ser realizado quantas vezes se fizerem necessárias durante este período, sem cobrança de novo preço."** (incluído pela IN DREI 01/2024). Não localizei nos arts. 95–102 qualquer **prazo de validade** da certidão. Fonte: https://www.gov.br/empresas-e-negocios/pt-br/drei/legislacao/instrucoes-normativas/arquivos-instrucoes-normativas-em-vigor/in-drei-81_atualizada_link.pdf
- **JUCEC** (Ceará Digital, serviço 142, publicação 22/06/2026): "O documento emitido é autenticado digitalmente e tem validade jurídica para todos os fins." — sem prazo em dias; preço "Certidão Simplificada - R$ 71,14" (https://cearadigital.ce.gov.br/servicos/142 ; portal: https://portalservicos.jucec.ce.gov.br/certidaoweb).
- **JUCESP** (servicos.sp.gov.br, 06/11/2024): "A certidão simplificada é um documento com validade jurídica com um extrato de informações atualizadas com base no último arquivamento registrado na JUCESP [...]" — sem prazo (https://servicos.sp.gov.br/fcarta/45719f85-04e8-40ab-b179-201459e43b52).
- **JUCERJA**: oferece "Validar Certidão" online para terceiros (https://www.jucerja.rj.gov.br/Transparencia/PerguntasFrequentes) — prazo de validade da simplificada não informado.
- **JUCEMG**: prazo de validade não localizado (não confirmado).
- Se a certidão traz prazo de validade impresso: **não confirmado** para JUCEC/JUCESP/JUCERJA/JUCEMG (não obtive modelo de certidão real).
- **Prazos fixados pelo órgão receptor (exemplos):** DETRAN-CE — "Comprovante Situação Cadastral do CNPJ (validade 30 dias)" (é o comprovante da RFB, não a certidão da Junta); DETRAN-MG — "Cartão CNPJ com menos de 90 dias" (comprador PJ); DETRAN-AL (Portaria GDP/DETRAN/AL nº 746/2011, segundo o LegisWeb — vigência não confirmada): contrato social e alterações "serão considerados atualizados até o prazo de 01 (um) ano"; depois, certidão da Junta com validade de 30 dias (https://www.legisweb.com.br/legislacao/?id=118512).

---

### 1.4 Transferência digital pela CDT (hoje "CNH do Brasil") e PJ

- **Serviço federal "Vender veículos digitalmente pela Carteira Digital de Trânsito (ATPV-e)"** (Última Modificação: 15/12/2025) — https://www.gov.br/pt-br/servicos/vender-veiculos-digitalmente-pela-carteira-digital-de-transito-atpv-e
  - "A nova funcionalidade permite que a transferência de veículos seja realizada sem a necessidade de reconhecer firma, possibilitando que a comunicação de venda do veículo seja realizada usando apenas o aplicativo."
  - **"Quem pode utilizar este serviço? Pessoa física proprietária ou futura proprietária de veículo moradora de um estado da federação que já tenha aderido ao sistema."**
  - "Atualmente 22 (vinte e dois) Estados aderiram" — a lista exibida tem 23 UFs: AC, AL, AM, BA, CE, GO, MG, MT, MS, PA, PB, PR, PE, PI, RJ, RN, RR, RO, RS, SE, SP, TO, ES (inconsistência da própria página).
  - "Atenção: O documento do veículo (antigo CRV/DUT) deve ter sido emitido a partir de 4 de janeiro de 2021."
  - Acesso "com a conta gov.br com selo de confiabilidade prata ou ouro"; "a assinatura digital é feita com biometria facial" (comprador e vendedor); "Após a assinatura, o vendedor não conseguirá mais acessar o CRLV-e do veículo."; depois, o comprador vai ao DETRAN para vistoria e conclusão; serviço gratuito.
- **Renomeação:** o app CDT passou a se chamar "CNH do Brasil" — página oficial de MG: "aplicativo CNH do Brasil (antiga Carteira Digital de Trânsito - CDT)" (link em 1.3.4-c); Serpro: https://www.serpro.gov.br/menu/noticias/noticias-2025/cnh-do-brasil (data de lançamento informada em buscas: 09/12/2025 — não conferida no texto da página).
- **Disponibilidade para PJ: NÃO** — (1) página federal acima (só pessoa física); (2) MG ("apenas para Pessoas Físicas"); (3) CE Balcão Digital ("pessoas físicas habilitadas no Ceará"); (4) CNJ Prov. 252/2026 (considerando: a plataforma federal "não admite a transferência por pessoas jurídicas").
- **Futuro fluxo da Res. 1.027 no app:** "a Secretaria Nacional de Trânsito (Senatran) trabalha na implementação da funcionalidade que permitirá realizar a transferência eletrônica de veículos usados entre pessoas físicas pelo aplicativo CNH do Brasil." (Agência Gov, 20/08/2026 — https://agenciagov.ebc.com.br/noticias/202608/transferencia-de-veiculos-vai-ser-feita-pelo-celular-saiba-como-vai-funcionar ; original: https://www.gov.br/transportes/pt-br/assuntos/noticias-/2026/08/contran-regulamenta-transferencia-eletronica-de-veiculos). Data de entrada em operação: não divulgada (não confirmado).
- **Apps/portais estaduais com assinatura digital da ATPV-e:** DETRAN-CE Balcão Digital (reconhecimento facial; só PF); Detran-SP TDV (gov.br prata/ouro + biometria; PJ→PF via procuração eletrônica e CPF do representante, desde 02/2026); DETRAN-RJ multiplataforma credenciada (Portaria 6834/2025; tratamento de PJ não confirmado); DETRAN-MG via CNH do Brasil (só PF).
- **Revendedora (art. 330 CTB)**: fluxo próprio via Renave, com integração às assinaturas eletrônicas da Res. 1.027 prevista para 09–20/11/2026 (Circular SENATRAN 2/2026; Res. 1.027, art. 28, § 6º, e art. 37, VI) — ver Seção 4.

---

### 1.5 Lacunas / pontos NÃO confirmados
1. Regulamentação da SENATRAN para o art. 28, § 7º, da Res. 1.027 (como provar eletronicamente poderes de PJ): não localizada.
2. Como cada DETRAN tratará a "ATPV-e impressa com firma reconhecida" após o fim do prazo de adequação (≈16/11/2026): não confirmado.
3. DETRAN-CE: aceitação de ATPV-e assinada com ICP-Brasil (e-CNPJ/e-CPF) ou via e-Notariado por vendedor PJ: não confirmada. Exigência de certidão simplificada ou de "última alteração/consolidação": não confirmada (a página pede "Contrato Social").
4. Se certidões simplificadas de JUCEC/JUCESP/JUCERJA/JUCEMG trazem prazo de validade impresso: não confirmado.
5. Significado exato de "reconhecimento de firma por pessoa jurídica" no DETRAN-MG: provável certificação da representação pelo tabelião (não confirmado).
6. Como o Detran-SP identifica o "representante legal" da PJ na procuração eletrônica (cadastro RFB vs. contrato social): não confirmado.
7. Portarias DENATRAN/SENATRAN de 2021–2023 que regulamentaram a assinatura gov.br da ATPV-e na CDT: não localizadas.

---

### 1.6 Regras codificáveis (Seção 1)
- R1.1 — Norma de referência: se data da operação ≥ 18/08/2026 → Res. CONTRAN 1.027/2026; Res. 809/2020 só para histórico/atos anteriores (Res. 1.027, arts. 59 e 60).
- R1.2 — Identificar o suporte: CRV em papel (emitido até 31/12/2020) → ATPV do verso + firma por autenticidade de vendedor e comprador em Tabelionato (Res. 1.027, arts. 20 e 26). CRV-e (desde 04/01/2021) → ATPV-e com assinatura eletrônica avançada ou qualificada; manuscrita vedada (art. 28, § 1º) — mas aceitar "ATPV-e impressa + firma por autenticidade" enquanto o DETRAN da UF ainda a aceitar (transição, art. 58; SP/MG/CE ainda descrevem esse fluxo) e sinalizar risco após ≈16/11/2026.
- R1.3 — Firma sempre **por autenticidade** (MG proíbe abono/semelhança; CE exige selo digital tipo 14); nunca misturar assinatura física e digital na mesma ATPV-e (MG, RJ; SP/e-Not 2022).
- R1.4 — Vendedor PJ + canal federal CDT/CNH do Brasil → **inelegível** (só PF). Vendedor PJ + Registro Civil (ARPEN/IdRC) → **inelegível** (Prov. CNJ 252/2026, também EI e MEI). Vendedor PJ + SP TDV → possível via CPF do representante legal + procuração eletrônica (Detran-SP).
- R1.5 — Assinatura eletrônica de PJ exige **prova de poderes do signatário** (Res. 1.027, art. 28, § 7º): o agente deve verificar outorgante, outorgado, poderes, prazo e revogação; gov.br (PF) ou e-CNPJ, isoladamente, **não** provam poderes.
- R1.6 — Reconhecimento de firma prova autoria, **não** poderes (TJSC art. 1.270, § 1º); poderes vêm do contrato social/estatuto+ata/procuração.
- R1.7 — Pacote documental do representante estatutário (mínimo comum CE/SP/RJ/MG): contrato social (SP: "atualizado"; MG: contrato social "ou última Alteração Contratual"; RJ: cópia autenticada que permita confirmar poderes) ou estatuto + ata de eleição (S.A.) ou CCMEI; documento oficial com foto e CPF do signatário; comprovante de situação cadastral do CNPJ (CE: validade 30 dias).
- R1.8 — Procurador da PJ: CE → só procuração **pública** e específica (validade ≤ 1 ano da expedição, segundo o DETRAN-CE no gov.br); O Prov. CGJCE 17/2024, que só previa procurador por instrumento público, foi revogado pelo Prov. 05/2025, mas a exigência de procuração pública continua na página do DETRAN-CE. MG → **pública** (procurador PF; se procurador PJ, pública + contrato social atualizado). SP → pública com poderes específicos **ou** particular com poderes específicos + identificação do veículo (placa ou chassi) + firma reconhecida por autenticidade (ou nato-digital). RJ (leasing) → pública com os mesmos nomes dos signatários do CRV. Advogado: SP e MG dispensam reconhecimento de firma (OAB).
- R1.9 — Ceará: além da firma por autenticidade, exigir **registro no RTD** (Lei CE 14.605/2010, art. 16); sem ele o DETRAN-CE não processa (Ofício Circular CGJCE 396/2026).
- R1.10 — Firma reconhecida em outra UF: SP exige sinal público; RJ exige sinal público de tabelião fluminense; CE reconhece sinal público por semelhança + firma do comprador por autenticidade.
- R1.11 — CND da PJ vendedora quando o veículo for do ativo permanente e o valor superar o limite (MG: R$ 87.493,73 em 2026; RJ: CND/CPD-EN) — Lei 8.212/1991, art. 47, I, "c".
- R1.12 — PJ baixada/inativa (SP): exigir alvará judicial, salvo MEI, ME e produtor rural.
- R1.13 — Validade de certidões: não há prazo legal nacional para a certidão simplificada (IN DREI 81, art. 101, § 2º = 30 dias de download). Usar parâmetro por órgão: padrão 30 dias; MG 90 dias (cartão CNPJ); DETRAN-AL: contrato/alteração até 1 ano, depois certidão ≤ 30 dias.
- R1.14 — Uma só ATPV-e ativa por veículo; após comunicação de venda, cancelamento só por decisão judicial, fraude/erro material em processo administrativo ou distrato com assinaturas eletrônicas avançadas/qualificadas (Res. 1.027, arts. 27, § 5º, e 29, § 2º).
- R1.15 — Comunicação de venda: a assinatura eletrônica das duas partes gera a comunicação automaticamente (Res. 1.027, art. 28, § 4º); no papel, se o comprador não transferir em 30 dias, o vendedor deve comunicar em até 60 dias (art. 26, §§ 2º–4º; CTB art. 134).

---

## 2. Procuração para venda/transferência de veículo

Pesquisa feita entre 16 e 17/10/2026. Legenda usada abaixo:
- **[N]** norma vigente (lei, portaria, provimento);
- **[P]** prática administrativa (página oficial de serviço);
- **[J]** jurisprudência ou decisão administrativa;
- **[D]** doutrina ou enunciado.

Quando o texto de um artigo do Código Civil já está na Seção 3, ele só é referenciado aqui. "Não confirmado" quer dizer que não achei fonte que sustente o ponto.

---

### 2.0 Resumo da Seção 2


1. **Forma da procuração de venda.** Não existe regra nacional única: a forma é fixada por cada DETRAN.
   - **Exigem instrumento PÚBLICO quando a procuração é física:**
     - DETRAN-CE: "pública e específica para o ato", válida por até 1 ano da expedição;
     - DETRAN-MG;
     - DETRAN-SC (PN 02/2026, art. 9º). Em SC, a alternativa é a procuração eletrônica com assinatura ICP-Brasil qualificada.
   - **Aceitam PÚBLICA ou PARTICULAR com firma reconhecida POR AUTENTICIDADE:**
     - DETRAN-SP (Portaria 1.680/2014, art. 8º, VI);
     - DETRAN-PR (Portaria 660/2025);
     - DETRAN-GO (Portaria 130/2021).
   - Firma reconhecida por semelhança não é aceita em nenhum dos estados verificados. MG proíbe expressamente semelhança ou abono no ATPV-e.
2. **Poderes.** É preciso ter poder especial e expresso de "vender/alienar" (art. 661, §1º, CC).
   - Para o DETRAN-PR, a cláusula "representar" não autoriza a venda.
   - Enunciado 183/CJF: a procuração com poderes especiais "deve conter a identificação do objeto".
   - O STJ (REsp 1.814.643/SP) recusou poder genérico sobre "quaisquer imóveis". O caso é de imóvel, mas a lógica vale para veículos.
   - GO e RS exigem identificação do veículo na procuração particular (GO) ou em toda procuração (RS). O PR, ao contrário, presume poderes sobre todos os veículos quando não há identificação.
3. **Prazo e recência.**
   - A lei não fixa prazo de validade (CN-CE, art. 924).
   - O CNJ (PCA 0007885-89.2023, 13/06/2025) declarou ilegal a exigência genérica de procuração com "prazo máximo de expedição" sem fundamentação idônea.
   - Ainda assim, há prazos administrativos e notariais:
     - DETRAN-CE: 1 ano;
     - DETRAN-PR: 3 anos, se a procuração não tiver prazo;
     - tabeliães do CE e de SP: 90 dias para traslado ou certidão de procuração e substabelecimento usados em escrituras.
   - Revogações de procuração pública devem ser comunicadas ao notário de origem (CNN, art. 272, §4º). Por isso, uma certidão atualizada da procuração é o meio prático de verificar se ela ainda vale.
4. **Substabelecimento.**
   - O art. 655 do CC permite substabelecimento particular de procuração pública.
   - O Enunciado 182/CJF limita isso aos casos em que a forma pública é facultativa.
   - Prática dos DETRANs: GO e RS aceitam só 1 substabelecimento; o PR admite substabelecimento salvo vedação expressa.
5. **Procuração em causa própria.** Não é título translativo de propriedade (STJ, REsp 1.345.170/RS, 2021). Funciona como autorização irrevogável para o procurador transferir o bem a si mesmo (arts. 685 e 117 do CC).


### 2.1 Forma exigida (pública ou particular) por estado

#### Ceará (prioridade)

- **[P] DETRAN-CE, gov.br Serviços Estaduais, "Solicitar Transferência Veicular nos Postos do DETRAN/CE" (última modificação: 12/04/2025).** Em "Quem pode utilizar este serviço?":
  > "O proprietário do veículo, no caso de pessoa física; 2. Representante legal, no caso de pessoa jurídica; 3. Procurador por instrumento de procuração pública e específica para o ato (com validade de até 01 ano da data de expedição); 4. Despachante documentalista credenciado pelo DETRAN/CE."

  Fonte: https://www.gov.br/pt-br/servicos-estaduais/servico_estadual?id=20880
  - A mesma fórmula aparece nos serviços "Solicitar Novo Documento do Veículo" (https://www.gov.br/en/state-services/servico_estadual?id=20930) e "Solicitar Licenciamento Anual" (https://www.gov.br/en/state-services/servico_estadual?id=20870).
- **[P] Ceará Digital, serviço 2403, "Solicitar transferência de propriedade de veículo" (data de publicação: 08/05/2026).** Lista de documentos, transcrita literalmente, com os erros de digitação do original:
  > "Se REPRESENTANTE LEGAL (terceiro): documento oficial com foto do representante (CNH ou RG e CPF); Comprovante de residência do representante e Procuração pública e específica para o fim que se destina"

  > "Se Pessoa Jurídica (CNPJ): Contrato Social, Documento de Identificação Oficial com foto do representante legal da empresa (CNH ou RG e CPF) e Comprovante Situação Cadastral do CNPJ (validade 30 dias)"

  > "Se compra e venda: Documento de intensão de venda assinad pelo comprador e vendedor reconhecida em cartório"

  Fonte: https://servicos.ce.gov.br/servicos/2403. A página é uma aplicação JavaScript; o conteúdo foi lido pela API pública que ela usa: `https://baoxyfada7.execute-api.sa-east-1.amazonaws.com/prod/service/get/active/2403`.
  - Exigência de recência do contrato social ou de certidão da Junta: **não consta** nesta página. Recência exigida: só os 30 dias do comprovante de situação cadastral do CNPJ.
- **[N] Cartórios do CE (CGJ-CE).**
  - O **Provimento nº 17/2024/CGJCE**, art. 12, dizia:
    > "É admitida a aquisição e alienação de veículo por procurador(a) constituído(a) por instrumento público, que deve ser exibido, conferida a autenticidade e ter uma cópia armazenada na serventia."

    Fonte: https://portal.tjce.jus.br/uploads/2024/10/PROVIMENTO-17-2024.pdf
  - **Esse provimento foi revogado** pelo **Provimento nº 05/2025/CGJCE**, art. 7º, que entrou em vigor 50 dias após 01/08/2025: "revogando-se as disposições em contrário, em especial o Provimento nº 17/2024/CGJCE". O art. 4º do mesmo provimento manda reconhecer a firma do signatário do ATPV/ATPV-e:
    > "por autenticidade, com as cautelas exigidas no Código de Normas do Serviço Extrajudicial, utilizando o selo do tipo 14 no formato digital."

    Fonte: https://portal.tjce.jus.br/uploads/2025/08/Provimento-no-05-2025-CGJCE.pdf
  - **Consequência:** não achei, depois de 2025, regra cartorial específica do CE sobre a forma da procuração do signatário do ATPV (**não confirmado**). Na prática, prevalece a exigência do DETRAN-CE de procuração pública e específica.
- **[N] Código de Normas Extrajudicial do CE (Provimento 04/2023/CGJCE, versão atualizada até 2026).**
  - Art. 960, §5º, sobre veículos:
    > "se impossibilitado o reconhecimento autêntico [...] o Tabelião poderá fazer o reconhecimento por semelhança [...] exceto em se tratando de veículos automotores, em que se impõe o reconhecimento autêntico."
  - Art. 962:
    > "Impõe-se o reconhecimento autêntico de firma nas transferências de veículos automotores, devendo o Tabelião de Notas exigir que o signatário assine o livro a que se refere."
  - Art. 960, §3º:
    > "O reconhecimento da razão social declarará a firma lançada e o nome de quem a lançou, e far-se-á somente mediante comprovação do prévio registro do ato constitutivo da sociedade e da representação, cuja comprovação poderá ser feita mediante a apresentação da certidão simplificada da Junta Comercial ou do Registro Civil das Pessoas Jurídicas"
  - Art. 963, §5º:
    > "Admite-se o reconhecimento de pessoa física que esteja relacionada a pessoa jurídica, quando não for lançado o nome da pessoa jurídica no reconhecimento, mas tão somente o nome da pessoa física que a lançou, desde que se faça menção de que o reconhecimento não comprova os poderes de representação."

  Fonte: https://portal.tjce.jus.br/uploads/2022/07/Codigo-de-Normas-Extrajudial-Versao-Atualizada-1789148558.pdf (página-índice: https://www.tjce.jus.br/corregedoria/codigo-de-normas-extrajudicial/)
- **[N/P] Ofício Circular nº 396/2026-CGJUCGJ (10/07/2026), com o Parecer 1120/2026.**
  - No CE, quando a firma é reconhecida em cartório, o documento de transferência precisa ainda ser **registrado em cartório de RTD**, por força do art. 16 da Lei Estadual 14.605/2010:
    > "a ausência do registro obstará a recepção do documento pelo DETRAN e a concretização da transferência do veículo."
  - A assinatura das duas partes pela CDT/gov.br nível ouro "dispensa ida ao cartório".

  Fonte: https://portal.tjce.jus.br/uploads/2026/07/OFICIO-396-1784047052.pdf

#### São Paulo

- **[N] Portaria DETRAN-SP nº 1.680/2014, art. 8º.** Documentos exigidos na transferência:
  > "VI - procuração pública ou particular com reconhecimento de firma por autenticidade, quando o Certificado de Registro de Veículo - CRV for assinado por procurador"

  §1º:
  > "o documento [...] deverá ser preenchido em nome do comprador e assinado, com reconhecimento de firma por autenticidade, pelo vendedor e pelo comprador."

  O inciso V do mesmo artigo exige, de pessoa jurídica, "atos constitutivos". O art. 4º remete à Portaria DETRAN 1288/2011 para "representação de terceiros perante este Departamento"; o texto da 1288/2011 não foi localizado.

  Fonte, texto reproduzido pela ARPEN-SP: https://arpensp.org.br/noticia/21542
  - A Portaria 1.680/2014 **não aparece** na lista de normas revogadas pela Portaria Normativa DETRAN-SP 12/2023 (https://www.normasbrasil.com.br/norma/portaria-normativa-12-2023-sp_451885.html). Vigência em 2026 **não confirmada** de forma positiva.
- **[J] 2ª Vara de Registros Públicos de SP, Proc. 1009916-08.2018.8.26.0100 (DJe de 10/04/2019).** Exige-se:
  > "indistintamente, a apresentação de procuração pública ou particular com reconhecimento firma reconhecida"

  A decisão afasta a "procuração simples" mesmo quando o procurador é advogado.

  Fonte: https://portaldori.com.br/2019/04/11/2avrpsp-para-transferencia-do-veiculo-ha-necessidade-de-procuracao-publica-ou-procuracao-particular-com-firma-reconhecida-por-autenticidade/
- **[P] Procuração digital do DETRAN-SP (fevereiro de 2026, fonte de imprensa).**
  - A procuração é criada no portal, em "Gerenciar Procurador de Serviços de Veículos", com login gov.br e "prova de vida".
  - Na primeira fase, cobre transações entre pessoas físicas e a venda de usado de **PJ (pelo CPF do representante legal) para PF**.
  - Na segunda fase, cobrirá PF→PJ e PJ→PJ.

  Fontes: https://revistacarro.com.br/detran-sp-amplia-transferencia-digital-de-veiculos-e-inclui-procuracao-e-cartorios/ (12/02/2026) e https://www.correiodamanha.com.br/nacional/sudeste/2026/02/259339-transferencia-digital-de-veiculos-avanca-para-cartorios.html. A portaria que regulamenta essa procuração digital **não foi localizada**.

#### Minas Gerais

- **[P] transito.mg.gov.br, "Documentos necessários para pessoa física e jurídica".**
  > "Se representada por Procurador: Original e cópia do documento de identificação oficial atualizado com foto e CPF do procurador. Original ou cópia autenticada da procuração por instrumento público, se procurador for pessoa física; Original ou cópia autenticada da procuração por instrumento público e do Contrato social atualizado, se procurador for pessoa jurídica."

  > "Se representada por Advogado: Procuração por instrumento particular dispensado o reconhecimento de firma em cartório"

  Fonte: https://www.transito.mg.gov.br/veiculos/transferencias/documentos-necessarios-para-atendimento-presencial
- **[P] mg.gov.br, "Transferir propriedade de veículo (comprador)".**
  > "É proibido o reconhecimento de firma por abono ou semelhança no ATPV-e."

  > "É proibida a utilização de assinatura digital e física ao mesmo tempo na ATPV-e."

  A página também fixa prazo de 30 dias "a contar da assinatura da ATPV-e" para concluir a transferência.

  Fonte: https://www.mg.gov.br/servico/transferir-propriedade-de-veiculo

#### Paraná (norma recente e detalhada, útil como modelo de regras)

- **[N] Portaria DETRAN-PR nº 660/2025 (DOE nº 11.959, de 06/08/2025), "outorga e o recebimento de procurações".**
  - Art. 1º, objeto:
    > "II - Assinar, na qualidade de vendedor, o Certificado de Registro de Veículo – CRV ou a Autorização para Transferência de Propriedade de Veículo – ATPV‐e; III - Substabelecer poderes para esses atos."
  - Art. 2º, definições:
    > "I - Procuração pública: aquela lavrada em Tabelionato de Notas; II - Procuração particular: instrumento particular subscrito pelo outorgante, com reconhecimento de firma por autenticidade ou semelhança, conforme exigido nesta Portaria"
  - Art. 4º:
    > "A pessoa física ou jurídica poderá outorgar procuração pública ou particular. § 1º. O reconhecimento de firma por autenticidade é obrigatório, salvo quando a procuração for outorgada exclusivamente a advogado regularmente inscrito na Ordem dos Advogados do Brasil – OAB [...]. § 2º. A ausência de identificação de veículo(s) na procuração confere poderes de administração sobre todos os veículos registrados em nome do outorgante (CPF ou CNPJ). § 3º. Na falta de prazo expresso, a procuração terá validade de 3 (três) anos contados da data de sua assinatura."
  - Art. 5º:
    > "O procurador constituído por procuração cujos poderes incluam 'vender' poderá assinar o CRV ou a ATPV‐e e praticar todos os demais atos junto ao DETRAN/PR. § 1º. A cláusula 'representar' autoriza todos os processos junto ao DETRAN/PR, excetuados aqueles que impliquem na venda do veículo."
  - Art. 6º, mais de um outorgado: "Aplicar‐se‐á o art. 672 do Código Civil".
  - Art. 7º:
    > "É admitido o substabelecimento dos poderes outorgados, salvo se houver cláusula expressa de vedação, observado o art. 655 do Código Civil."

  Fonte: https://www.legislacao.pr.gov.br/legislacao/listarAtosAno.do?action=exibir&codAto=368093
- **[N] Portaria DETRAN-PR nº 661/2025 (DOE de 06/08/2025), assinaturas digitais.** Pertence mais à Seção 1, mas afeta procurações.
  - Art. 2º, §1º, I: a assinatura ICP-Brasil qualificada "é válida para todos os documentos exigidos pelo DETRAN/PR, incluindo procurações com poderes de venda, a [...] ATPV-e".
  - §2º: e-Notariado aceito "para os mesmos fins".
  - §3º: gov.br é "válida para todos documentos, exceto ATPV-e e procuração que outorgue poderes de venda".
  - §5º, I: no ATPV-e, aceita-se a CDT/gov.br prata ou ouro quando ambas as partes assinam digitalmente.
  - Art. 3º:
    > "Não serão aceitas, em qualquer hipótese, assinaturas digitais realizadas com certificado digital do tipo e-CNPJ"

    §2º do mesmo artigo:
    > "Ainda que o contrato social [...] exija a assinatura de mais de um sócio ou representante legal para a prática de atos de disposição patrimonial, tais atos deverão ser firmados exclusivamente por meio de certificados digitais individuais (e-CPF)"

  Fonte: https://www.legislacao.pr.gov.br/legislacao/listarAtosAno.do?action=exibir&codAto=368123
- **[P] Página "Transferir propriedade de veículo" do DETRAN-PR.**
  > "Procuração Particular: exige firma reconhecida por autenticidade/verdadeira do outorgante [...] A validade da Procuração será de 3 anos, se não houver informação de prazo no documento"

  Quando o vendedor é PJ: "Comprovante de poderes do vendedor" e "Certidão Negativa de Débitos (CND) do INSS".

  Fonte: https://www.detran.pr.gov.br/servicos/Veiculo/Compra-e-venda/Transferir-propriedade-de-veiculo-ERrZE36k

#### Goiás

- **[N] Portaria DETRAN-GO nº 130/2021 (02/02/2021).**
  - Art. 1º, II:
    > "pelo procurador, devidamente constituído, munido de instrumento de procuração pública ou particular com firma reconhecida por autenticidade."
  - Art. 2º:
    > "O mandato procuratório público deverá outorgar no mínimo, poderes amplos e gerais [...] dispensando a identificação do automotor: I - o mandato em termos gerais só confere poderes de administração; e II - para alienar (vender) [...] depende a procuração de poderes especiais e expressos."
  - Art. 3º:
    > "O mandato procuratório particular deverá discriminar as características do veículo (placa ou chassi) e os poderes específicos [...] bem como o reconhecimento de firma da assinatura do outorgante, por autenticidade"
  - Art. 7º:
    > "Permitir apenas um substabelecimento de procuração [...] tanto para pessoa física como pessoa jurídica, ressalvando os agentes financeiros. Parágrafo único. Ainda quando se outorgue mandato por instrumento público, pode substabelecer-se mediante instrumento particular."

  Fonte: https://goias.gov.br/detran/wp-content/uploads/sites/8/2023/08/20210208-130-2021-1.pdf. A página atual "Serviços com Procuração" repete essas regras: https://goias.gov.br/detran/sobre-servicos-com-procuracao/

#### Santa Catarina

- **[N] Portaria Normativa DETRAN-SC nº 02/2026 (28/01/2026; DOE-SC de 29/01/2026).**
  - Art. 9º:
    > "A procuração de Venda de veículos, quando em sua versão física, deverá ser pública, com fins especiais e expressos, nos termos do art. 661, § 1º do código civil. Parágrafo único. A exigência havida no caput deste artigo não se aplica quando se tratar de procuração eletrônica, com assinatura eletrônica qualificada que dispõe de consulta pública junto ao instituto de Tecnologia da Informação - ITI"
  - Art. 2º, II: ICP-Brasil para "procuração eletrônica de venda de veículos, especificados os dados do veículo e com poderes expressos para finalidade de venda".
  - Art. 3º: gov.br só no ATPV-e via CDT, com as duas partes em nível ouro.
  - Art. 3º-A: gov.br vale para "outorga de procuração para protocolo de entrada e retirada de processos e documentos". Isso não abrange venda.
  - Art. 7º: ATPV-e impresso com assinatura física exige "reconhecimento de firma por autenticidade".

  Fonte, reprodução LegisWeb: https://www.legisweb.com.br/legislacao/?id=490189. O PDF oficial em mtsp.detran.sc.gov.br recusou conexão nos testes.

#### Rio Grande do Sul

- **[N] Portaria DETRAN/RS nº 449/2016, alterada pela Portaria nº 1/2017.** Trata da abertura de processo de transferência com procuração em causa própria.
  - Aceita-se o CRV com firmas reconhecidas e "no máximo, 01 (uma) procuração conferida a terceiro".
  - As procurações devem ser "individualizada[s] para cada veículo, assim como conter reconhecimento de firma em Tabelionato, por autenticidade". Ficam dispensadas da individualização instituições financeiras, seguradoras, concessionárias e locadoras.
  - "A procuração poderá autorizar 01 (um) único substabelecimento."

  Fonte: https://www.normasbrasil.com.br/norma/portaria-1-2017-rs_334987.html. Vigência em 2026 **não confirmada**.

#### Rio de Janeiro

- **[N] Portaria DETRAN-RJ SEI nº 6834/2025 (27/06/2025), multiplataforma digital do ATPV-e.**
  - Art. 3º:
    > "A [...] ATPV-e será expedida mediante o preenchimento pelo proprietário vendedor ou por seu procurador, do formulário eletrônico para registro da Intenção de Venda"
  - §2º:
    > "A multiplataforma [...] deverá possuir funcionalidade que permita que o Proprietário Vendedor outorgue procuração que conceda poderes para que um terceiro possa representá-lo como vendedor para efeito de assinatura do ATPV-e."
  - §4º veda misturar assinatura física e eletrônica no mesmo documento.

  Fonte: https://www2.detran.rj.gov.br/portal/pdfs/2025/27062025_Portaria6834.pdf
- **[N, histórico] Portaria DETRAN-RJ 2.936/2002.** Para vendedor PJ, exige "1 (uma) cópia do documento que confere poderes àquele que assinou o" CRV.

  Fonte: https://www.contabeis.com.br/legislacao/20705/portaria-detran-2936-2002/. Vigência **não confirmada**.
- A regra atual do DETRAN-RJ sobre a forma (pública ou particular) da procuração física para assinar ATPV é **não confirmada**: não localizei página oficial de 2025 ou 2026.

#### Outros estados

- **[N] DETRAN-PE, Portaria nº 9275/2025 (05/09/2025).** Art. 4º: a plataforma digital deve permitir que o proprietário vendedor "outorgue procuração" para a assinatura do ATPV-e; assinatura com nível mínimo "avançada" (art. 27).

  Fonte, reprodução LegisWeb: https://www.legisweb.com.br/legislacao/?id=483141. O texto literal completo não foi conferido.
- **[N] DETRAN-AL, Portaria 746/2011.** Para PJ, "Contratos Sociais e alterações contratuais [...] serão considerados atualizados até o prazo de 01 (um) ano"; "A certidão da Junta Comercial terá a validade de 30 dias a contar da data de sua expedição."

  Fonte: https://www.legisweb.com.br/legislacao/?id=118512. Vigência **não confirmada**.

### 2.2 Conteúdo da procuração: poderes especiais e identificação do veículo

- **[N]** Art. 661, §1º, do CC: alienar exige "poderes especiais e expressos" (texto na Seção 3).
- **[D] Enunciado 183 da III Jornada de Direito Civil (CJF):**
  > "Para os casos em que o parágrafo primeiro do art. 661 exige poderes especiais, a procuração deve conter a identificação do objeto."

  Fonte: https://www.cjf.jus.br/enunciados/enunciado/343
- **[J] STJ, REsp 1.814.643/SP (3ª Turma, rel. Min. Nancy Andrighi, j. 22/10/2019).**
  - A outorga de poderes para alienar "quaisquer imóveis em todo o território nacional" não supre a especialidade exigida pelo art. 661, §1º.
  - Poderes **expressos** dizem explicitamente qual é o poder (por exemplo, vender). Poderes **especiais** individualizam o negócio (por exemplo, vender tal bem).

  Fontes: https://informativos.trilhante.com.br/julgados/stj-resp-1814643-sp e https://www.migalhas.com.br/Quentes/17,MI313608,61044-Procuracao+que+concede+poder+de+alienacao+deve+individualizar+bens
- **[P/N] Como os DETRANs tratam o ponto:**
  - **PR:** sem identificação, a procuração vale para todos os veículos do CPF ou CNPJ (art. 4º, §2º, Port. 660/2025). Só a cláusula "vender" permite assinar CRV ou ATPV-e (art. 5º).
  - **GO:** a procuração pública dispensa identificação do veículo; a particular deve ter placa ou chassi (arts. 2º e 3º).
  - **SC:** a procuração eletrônica deve trazer os dados do veículo e poderes expressos de venda; a física deve ser pública, "com fins especiais e expressos".
  - **RS:** procuração individualizada por veículo.
  - **CE:** pede "pública e específica para o ato"; exigência expressa de placa, RENAVAM ou chassi **não confirmada**.
  - **MG:** não explicita a identificação.

### 2.3 Recência e validade da procuração

- **[N]** O Código Civil não fixa prazo de validade. CN-CE, art. 924:
  > "A procuração, salvo cláusula expressa, não tem prazo de validade."

  Fonte: o PDF do CN-CE citado em 2.1.
- **[J] CNJ, PCA 0007885-89.2023.2.00.0000 (rel. Cons. Marcello Terto e Silva, Plenário Virtual, 13/06/2025, unânime).** Tese:
  > "A exigência genérica de que toda procuração deva ter prazo máximo de expedição de 30 (trinta) dias não encontra amparo na legislação vigente e caracteriza ato ilegal, salvo nas hipóteses excepcionalmente previstas em lei ou quando houver fundamentação idônea que a justifique."

  A decisão vale para as serventias de MG; o art. 183, §7º, do Provimento Conjunto 93/2020-TJMG previa 30 dias. Ela foi comunicada "a todos os Tribunais de Justiça". Também afirma que tabeliães "podem exigir nova procuração ou termo de validade para a procuração pública".

  Fonte: Comunicado CG 527/2025, reproduzido em https://www.26notas.com.br/blog/?p=20260
- **[N] CNN/CNJ (Provimento 149/2023), art. 150:**
  > "Os notários deverão, antes da lavratura de ato notarial, verificar a atualidade dos poderes de uma procuração, abstendo-se da sua prática caso tenham conhecimento de que tenham eles sido revogados ou modificados."

  Fonte: https://atos.cnj.jus.br/atos/detalhar/5243
- **[N/P] Prazos administrativos e notariais encontrados:**
  - **DETRAN-CE:** procuração pública "com validade de até 01 ano da data de expedição" (2.1).
  - **DETRAN-PR:** 3 anos quando a procuração não tem prazo (Port. 660/2025, art. 4º, §3º).
  - **DETRAN-GO:** só para liberar veículo apreendido, a procuração vale 180 dias; "vencido o prazo, será exigido a certidão, quando pública" (Port. 130/2021, art. 6º).
  - **CN-CE (escrituras), art. 803:** o tabelião deve "examinar a procuração e substabelecimento observando a validade de 90 (dias) da data de sua expedição". Art. 932: exige "traslados atualizados da procuração e substabelecimento, com prazo de 90 (noventa) dias da data de sua expedição" quando não lavrados no próprio cartório.
  - **NSCGJ-SP, Cap. XVI, item 42, "c":** limite de "90 (noventa) dias, a contar de sua emissão" para procurações, no contexto de escrituras. A decisão do Juízo Corregedor Permanente de SP de 13/08/2025 manteve a regra. Fonte: https://cnbsp.org.br/2025/08/14/dje-processo-1045693-54-2025-8-26-0053-prazo-de-validade-das-procuracoes-publicas-e-dever-do-tabeliao-de-observar-as-nscgj-sp/. O texto literal integral do item **não foi obtido**.
  - Não achei regra federal ou estadual que exija procuração "recente" para reconhecer firma do procurador no ATPV (**não confirmado**).
- **[N] Ferramentas para checar revogação:**
  - **CNN, art. 272, §4º:**
    > "será obrigatória a comunicação da lavratura de escritura pública de revogação de procuração [...] ao notário que houver lavrado a escritura de procuração revogada [...] com a realização das anotações remissivas correspondentes".

    Na prática, a **certidão atualizada** emitida pelo cartório de origem mostra a revogação.
  - **CNN, art. 273** (redação do Provimento 194, de 26/05/2025; §1º com redação do Provimento 209, de 19/11/2025): qualquer interessado com certificado ICP-Brasil ou notarizado pode consultar o CNB/CF sobre a "existência ou não de escrituras e procurações" de um CPF ou CNPJ. A resposta traz serventia, data, livro e folhas, e é "vedado o detalhamento" do negócio. **Não informa revogação.**

    Fontes: https://atos.cnj.jus.br/atos/detalhar/5243 e a decisão do CNJ no PP 0003263-30.2024: https://cnbsp.org.br/wp-content/uploads/2025/05/Decisao-CNJ-Liberacao-Acesso-CEP.pdf
  - **CN-CE, art. 926:** o tabelião anota a revogação à margem do ato e comunica por malote digital ao cartório que lavrou o instrumento revogado. O §4º diz que a revogação só se torna oponível ao mandatário depois de notificá-lo.

### 2.4 Substabelecimento

- **[N]** Arts. 655 e 667 (§§1º a 4º) do CC (texto na Seção 3). Art. 117, parágrafo único, do CC, transcrito literalmente com a grafia do original:
  > "Para esse efeito, tem-se como celebrado pelo representante o negócio realizado por aquele em quem os poderes houverem sido subestabelecidos."

  Fonte: https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm
- **[D] Enunciado 182 da III Jornada de Direito Civil (CJF):**
  > "O mandato outorgado por instrumento público previsto no art. 655 do Código Civil somente admite substabelecimento por instrumento particular quando a forma pública for facultativa e não integrar a substância do ato."

  Fonte: https://www.cjf.jus.br/enunciados/enunciado/340
  - Aplicação a veículos (inferência): a lei não exige forma pública para vender bem móvel, então o substabelecimento particular é válido pelo direito civil. Mas onde o **DETRAN** exige procuração pública (CE, MG e SC para procuração física), é provável que recuse substabelecimento particular. Regra expressa sobre isso nesses três estados **não confirmada**.
- **[N] CNN, art. 307:**
  > "Em todas as escrituras e procurações em que haja substabelecimento ou revogação de outro ato deverá ser devidamente informado o notário, o livro e as folhas, o número de protocolo e a data do ato substabelecido ou revogado."
- **[N/P] DETRANs:**
  - **PR:** admite substabelecimento, salvo vedação expressa (art. 7º, Port. 660/2025).
  - **GO:** "apenas um substabelecimento" e aceita a forma particular (art. 7º, Port. 130/2021).
  - **RS:** "01 (um) único substabelecimento".
  - **CE (cartório, escrituras):** traslados atualizados em até 90 dias (CN-CE, art. 932).

### 2.5 Procuração em causa própria (art. 685 do CC)

- **[J] STJ, REsp 1.345.170/RS (4ª Turma, rel. Min. Luis Felipe Salomão, j. 04/05/2021):**
  > "A procuração em causa própria não é — nem pode vir a ser — título translativo de propriedade"

  E ainda:
  > "a rigor não se transmite o direito objeto do negócio jurídico, outorga-se o poder de transferi-lo"

  A procuração é irrevogável, não se extingue com a morte das partes e dispensa prestação de contas.

  Fonte: https://cnbsp.org.br/2021/08/02/conjur-procuracao-em-causa-propria-nao-equivale-a-titulo-translativo-de-propriedade-diz-stj/
- **[N] CN-CE, arts. 894 e 922.** A procuração em causa própria, regulada para imóveis, "deverão conter os mesmos requisitos da compra e venda (a coisa, o preço e forma de pagamento [...])". Art. 894, §2º:
  > "Ausentes qualquer dos requisitos [...] a procuração não será classificada como sendo em causa própria, ainda que por meio dela sejam outorgados poderes para transferência de bem para o próprio outorgado".
- **[N] Arts. 117 e 1.267 do CC:**
  > "Art. 117. Salvo se o permitir a lei ou o representado, é anulável o negócio jurídico que o representante, no seu interesse ou por conta de outrem, celebrar consigo mesmo."

  > "Art. 1.267. A propriedade das coisas não se transfere pelos negócios jurídicos antes da tradição."

  Fonte: planalto, link acima. Para veículos, o domínio passa pela tradição; o registro no DETRAN é ato administrativo (ver Seção 5).
- **[N/P] DETRAN-RS:** a Portaria 449/2016 disciplina a "abertura de processo de transferência de propriedade de veículo com procuração outorgada em causa própria" e limita a cadeia a 1 procuração a terceiro (ver 2.1). Regra equivalente nos DETRANs do CE, SP, MG e RJ: **não confirmada**.
- **[N] Sinal de alerta de prevenção à lavagem de dinheiro (CNN, art. 171):**
  > "poderá ser considerada suspeita [...] a lavratura de procuração que outorgue plenos poderes de gestão empresarial, conferida em caráter irrevogável ou irretratável ou quando isenta de prestação de contas, independentemente de ser em causa própria"

  Fonte: https://atos.cnj.jus.br/atos/detalhar/5243

### 2.6 Procuração outorgada por PJ: como comprovar que quem outorgou tinha poderes

- **[N] Limites da outorga.**
  - Art. 1.018 do CC: o administrador pode "constituir mandatários da sociedade, especificados no instrumento os atos e operações" (Seção 3).
  - Na S.A., o art. 144, parágrafo único, da LSA exige que o instrumento especifique os atos e **a duração do mandato** (Seção 3).
  - Manual de Registro de Sociedade Limitada do DREI (Anexo IV da IN 81/2020), item 4.5:
    > "As funções de administração não podem ser delegadas a representante ou terceiros."

    Fonte: https://www.gov.br/empresas-e-negocios/pt-br/drei/legislacao/instrucoes-normativas/arquivos-instrucoes-normativas-em-vigor/anexo-iv-limitada_link.pdf
- **[J] A validade é aferida na data da outorga.** No AgInt no REsp 1.997.964/SC, o STJ disse que a procuração vale desde que "outorgada em nome da sociedade empresária e regularmente assinada por quem de direito à época do negócio jurídico" (ver 7.2).
- **[P] O que os DETRANs pedem:**
  - **MG**, quando a firma do vendedor PJ é reconhecida como pessoa física:
    > "Cópia autenticada do documento constitutivo da empresa vendedora; ou Contrato Social ou da última Alteração Contratual, se houver; ou cópia autenticada da Estatuto e Ata; ou original de Nota Fiscal eletrônica; ou original ou cópia autentica de Procuração Pública"

    Se a firma for reconhecida "por pessoa jurídica" (o tabelião verifica a representação), basta o "CRV/ATPV-e com reconhecimento de firma por pessoa jurídica". Procurador PJ: procuração pública e contrato social atualizado. Fonte: a página de MG citada em 2.1.
  - **CE:** contrato social e situação cadastral do CNPJ (30 dias).
  - **PR:** "Comprovante de poderes do vendedor".
  - **AL (2011):** contrato social atualizado em até 1 ano, ou certidão da Junta de até 30 dias.
  - Exigência expressa de que o DETRAN confira o contrato social **vigente na data da outorga**: **não confirmada** em nenhum DETRAN.
- **[N] No cartório (CE):** o "reconhecimento da razão social" exige certidão simplificada da Junta ou do RCPJ (art. 960, §3º). O reconhecimento só da pessoa física "não comprova os poderes de representação" (art. 963, §5º).

### Regras codificáveis (Seção 2)

- `forma_procuracao_venda[UF]`:
  - CE = PÚBLICA, específica, validade ≤ 1 ano;
  - MG = PÚBLICA (exceto advogado);
  - SC = PÚBLICA se física, ou ELETRÔNICA com ICP-Brasil;
  - SP, PR, GO = PÚBLICA ou PARTICULAR com firma POR AUTENTICIDADE;
  - RJ = não confirmado; usar política conservadora (pública ou particular com autenticidade e alerta).
- Rejeitar firma reconhecida **por semelhança** ou abono em procuração de venda e em ATPV ou ATPV-e.
- Exigir o verbo **"vender/alienar"** (e, de preferência, "assinar CRV/ATPV-e"). "Representar perante o DETRAN" ou "poderes gerais de administração" não bastam (art. 661, §1º; PR, art. 5º).
- Identificação do veículo: exigir placa, RENAVAM e chassi quando a procuração for particular ou o estado for GO, RS ou SC (eletrônica). Se faltar identificação, marcar alerta ("procuração genérica"); o PR aceita.
- Prazo: usar o prazo expresso da procuração, se houver. Sem prazo, aplicar o limite do estado (CE 1 ano da expedição; PR 3 anos da assinatura). Fora disso, não bloquear só pela idade, mas exigir **certidão atualizada** do cartório de origem quando a procuração for pública e antiga (critério recomendado de ≤ 90 dias, por analogia com CN-CE e NSCGJ-SP; não é exigência legal).
- Assinatura digital: ICP-Brasil qualificada (e-CPF) ou e-Notariado → aceitar. gov.br em procuração de venda → rejeitar (PR, art. 2º, §3º; SC, art. 3º-A). e-CNPJ → rejeitar no PR.
- Substabelecimento: permitido salvo vedação (art. 667, §3º → sem efeito, salvo ratificação). Limitar a 1 nível em GO e RS. Se a procuração original é pública e o estado exige forma pública (CE, MG, SC), exigir substabelecimento público (política conservadora). Os poderes substabelecidos não podem exceder os originais.
- Causa própria: tratar como poder irrevogável de transferir a si mesmo. Exigir identificação do veículo; preço e forma de pagamento são recomendados. Não equivale a transferência já ocorrida.
- Procuração outorgada por PJ: validar os poderes do signatário **na data da outorga**, pelo contrato ou alteração arquivada naquela data, e conferir se o instrumento especifica atos (art. 1.018). Para S.A., exigir prazo de duração (art. 144, parágrafo único, LSA). Marcar alerta se a procuração tiver "plenos poderes de gestão" com cláusula irrevogável ou sem prestação de contas (CNN, art. 171).

---

## 3. Textos legais literais (vigentes em 16/10/2026)

**Método.** Os textos abaixo foram baixados diretamente do Planalto em 16/10/2026 (páginas HTML oficiais) e extraídos por script, preservando a redação literal. Onde o Planalto exibe redação anterior riscada, ela aparece separada, em itálico/riscado, com a marcação "NÃO citar como vigente". Únicas normalizações feitas: espaçamento de "§ 1º" (o HTML do Planalto alterna "§1º"/"§ 1o"), "§ 3ºdo" → "§ 3º do" (art. 1.072, § 2º), "mandatojudicial" → "mandato judicial" (LSA, art. 144, p.u.), remoção dos rótulos de link "Vigência"/"(Produção de efeitos)" e, no caput do art. 1.076, inclusão dos dois-pontos finais que constam do texto oficial da Lei 13.792/2019 (https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2019/lei/L13792.htm) e foram omitidos na compilação. Ressalva do próprio Planalto: "Este texto não substitui o publicado no DOU".

### 3.0 Quadro das alterações relevantes (o que mudou e o que foi revogado)

| Lei | Data / DOU / vigência | O que fez nos dispositivos pesquisados | Fonte |
|---|---|---|---|
| Lei 13.792/2019 | 03/01/2019, DOU 04/01/2019; vigência na publicação (art. 5º) | Nova redação do § 1º do art. 1.063 (destituição do sócio administrador nomeado no contrato: de "dois terços" para "mais da metade do capital social") e do caput do art. 1.076 (retirou a ressalva ao § 1º do art. 1.063). | https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2019/lei/L13792.htm |
| Lei 13.874/2019 (Liberdade Econômica) | 20/09/2019, DOU 20/09/2019 (ed. extra-B); vigência na publicação (art. 20, II) | Art. 7º: incluiu os §§ 1º e 2º do art. 1.052 (sociedade limitada unipessoal), substituindo o parágrafo único que havia sido incluído pela MP 881/2019. (Também incluiu os §§ 1º e 2º do art. 32 da Lei 8.934/1994.) | https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2019/lei/l13874.htm |
| Lei 14.195/2021 | 26/08/2021, DOU 27/08/2021; a revogação do art. 1.015, p.u., produz efeitos na publicação (art. 58, V) | Art. 57, XXIX, "c": **revogou o parágrafo único do art. 1.015** (e, na alínea "d", o inciso IV do caput e o parágrafo único do art. 1.033). Incluiu §§ 3º e 4º no art. 138 da LSA (o § 3º com efeitos em 360 dias — art. 58, II). A nova redação que o PLV 15/2021 dava ao **art. 1.053 foi vetada** (Mensagem nº 415/2021), por isso o art. 1.053 mantém a redação original. | https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14195.htm ; veto: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/Msg/VEP/VEP-415.htm |
| Lei 14.451/2022 | 21/09/2022, DOU 22/09/2022; vigência "após decorridos 30 (trinta) dias de sua publicação oficial" (art. 4º) — pelo critério do art. 8º, § 1º, da LC 95/1998, a partir de 22/10/2022 (cálculo nosso) | Nova redação do art. 1.061 (administrador não sócio: 2/3 dos sócios antes da integralização; mais da metade do capital depois) e do inciso II do art. 1.076; **revogou o inciso I do art. 1.076** (quórum de 3/4 para alteração contratual etc.). | https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2022/lei/l14451.htm |
| LC 182/2021 (Marco Legal das Startups) | 01/06/2021, DOU 02/06/2021 (retificado em 04/06/2021); vigência 90 dias após a publicação (art. 19) | Nova redação do caput do art. 143 da LSA (diretoria com "1 (um) ou mais membros"). | https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp182.htm ; https://www.planalto.gov.br/ccivil_03/leis/l6404consol.htm#art143 |
| Lei 14.071/2020 | 13/10/2020, DOU 14/10/2020; vigência 180 dias após a publicação (art. 7º) | Nova redação do art. 134 do CTB (comunicação de venda em 60 dias contados do fim do prazo de 30 dias do art. 123, § 1º; comprovante eletrônico "com assinatura eletrônica válida") e do art. 233. | https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14071.htm |
| **Lei 15.153/2025** | 26/06/2025, DOU 27/06/2025; o art. 3º (vigência imediata) foi vetado — razões do veto: "o vacatio legis desta lei será o período determinado pela [LINDB] ... de 45 dias após a sua publicação oficial"; inciso III do § 4º do art. 123 vetado e depois promulgado após derrubada do veto em 09/12/2025 (DOU 10/12/2025); o inciso IV continua vetado | **Incluiu o § 4º no art. 123 do CTB**: transferência de propriedade "integralmente por meio eletrônico", com contrato de compra e venda com "assinaturas eletrônicas qualificadas ou avançadas, na forma da Lei nº 14.063/2020"; assinatura avançada em "plataforma de assinatura homologada" (SENATRAN ou DETRAN), conforme regulamentação do Contran. O inciso IV vetado proibia empresas do setor de compra/venda/financiamento de veículos de serem provedoras da plataforma. | https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/L15153.htm ; veto: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/Msg/Vep/VEP-812-25.htm |

**Observações para codificação (Seção 3):**
- **Art. 1.015, parágrafo único — REVOGADO** (Lei 14.195/2021). Não use mais as três hipóteses de "excesso oponível a terceiros" (registro da limitação, conhecimento do terceiro, operação estranha ao objeto) como texto vigente. Depois da revogação, a oponibilidade das limitações de poderes passa a ser discutida a partir dos arts. 47, 1.154 (efeito do registro perante terceiros) e da teoria da aparência/boa-fé. Isso é leitura interpretativa; ver Seção 7.
- **Art. 1.015, caput**: a parte final ("a oneração ou a venda de bens imóveis depende do que a maioria dos sócios decidir") fala só de **imóveis**. Veículo é bem móvel (art. 82).
- **Art. 1.013, caput** (aplicável à limitada pelo art. 1.053): se o contrato não diz nada, a administração "compete separadamente a cada um". **Art. 1.014**: se a competência for conjunta, todos precisam concorrer, salvo urgência.
- **Art. 1.063**: o cargo cessa "pelo término do prazo se, fixado no contrato ou em ato separado, não houver recondução". O § 4º do art. 150 da LSA (prorrogação até a investidura dos novos administradores) existe só na LSA. A aplicação à limitada depende de regência supletiva (art. 1.053, p.u.) ou de interpretação; ver Seção 7.
- **Art. 1.018 / art. 144, p.u., LSA**: o administrador pode constituir mandatários da sociedade "especificados no instrumento os atos e operações". A LSA exige ainda a "duração do mandato".
- **Art. 661, § 1º**: para "alienar" a procuração precisa de "poderes especiais e expressos". **Art. 657**: a forma da procuração segue a forma exigida para o ato. A compra e venda de veículo (móvel) não tem forma especial em lei (arts. 107 e 1.267). Por isso não existe exigência legal de instrumento público; exigências de forma vêm de normas administrativas e de cartório (ver Seções 1 e 2).
- **CTB art. 134**: o vendedor tem 60 dias, **contados do término dos 30 dias do art. 123, § 1º**, para comunicar a venda. O comprovante pode ser eletrônico "com assinatura eletrônica válida".

### 3.1 Código Civil (Lei nº 10.406/2002) — Parte Geral e Mandato

Fonte: https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm (versão com redações anteriores riscadas: https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm). Texto extraído em 16/10/2026.

#### Art. 47 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art47

> Art. 47. Obrigam a pessoa jurídica os atos dos administradores, exercidos nos limites de seus poderes definidos no ato constitutivo.

#### Art. 653 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art653

> Art. 653. Opera-se o mandato quando alguém recebe de outrem poderes para, em seu nome, praticar atos ou administrar interesses. A procuração é o instrumento do mandato.

#### Art. 654 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art654

> Art. 654. Todas as pessoas capazes são aptas para dar procuração mediante instrumento particular, que valerá desde que tenha a assinatura do outorgante.
>
> § 1º O instrumento particular deve conter a indicação do lugar onde foi passado, a qualificação do outorgante e do outorgado, a data e o objetivo da outorga com a designação e a extensão dos poderes conferidos.
>
> § 2º O terceiro com quem o mandatário tratar poderá exigir que a procuração traga a firma reconhecida.

#### Art. 655 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art655

> Art. 655. Ainda quando se outorgue mandato por instrumento público, pode substabelecer-se mediante instrumento particular.

#### Art. 657 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art657

> Art. 657. A outorga do mandato está sujeita à forma exigida por lei para o ato a ser praticado. Não se admite mandato verbal quando o ato deva ser celebrado por escrito.

#### Art. 660 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art660

> Art. 660. O mandato pode ser especial a um ou mais negócios determinadamente, ou geral a todos os do mandante.

#### Art. 661 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art661

> Art. 661. O mandato em termos gerais só confere poderes de administração.
>
> § 1º Para alienar, hipotecar, transigir, ou praticar outros quaisquer atos que exorbitem da administração ordinária, depende a procuração de poderes especiais e expressos.
>
> § 2º O poder de transigir não importa o de firmar compromisso.

#### Art. 662 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art662

> Art. 662. Os atos praticados por quem não tenha mandato, ou o tenha sem poderes suficientes, são ineficazes em relação àquele em cujo nome foram praticados, salvo se este os ratificar.
>
> Parágrafo único. A ratificação há de ser expressa, ou resultar de ato inequívoco, e retroagirá à data do ato.

#### Art. 667 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art667

> Art. 667. O mandatário é obrigado a aplicar toda sua diligência habitual na execução do mandato, e a indenizar qualquer prejuízo causado por culpa sua ou daquele a quem substabelecer, sem autorização, poderes que devia exercer pessoalmente.
>
> § 1º Se, não obstante proibição do mandante, o mandatário se fizer substituir na execução do mandato, responderá ao seu constituinte pelos prejuízos ocorridos sob a gerência do substituto, embora provenientes de caso fortuito, salvo provando que o caso teria sobrevindo, ainda que não tivesse havido substabelecimento.
>
> § 2º Havendo poderes de substabelecer, só serão imputáveis ao mandatário os danos causados pelo substabelecido, se tiver agido com culpa na escolha deste ou nas instruções dadas a ele.
>
> § 3º Se a proibição de substabelecer constar da procuração, os atos praticados pelo substabelecido não obrigam o mandante, salvo ratificação expressa, que retroagirá à data do ato.
>
> § 4º Sendo omissa a procuração quanto ao substabelecimento, o procurador será responsável se o substabelecido proceder culposamente.

#### Art. 672 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art672

> Art. 672. Sendo dois ou mais os mandatários nomeados no mesmo instrumento, qualquer deles poderá exercer os poderes outorgados, se não forem expressamente declarados conjuntos, nem especificamente designados para atos diferentes, ou subordinados a atos sucessivos. Se os mandatários forem declarados conjuntos, não terá eficácia o ato praticado sem interferência de todos, salvo havendo ratificação, que retroagirá à data do ato.

#### Art. 682 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art682

> Art. 682. Cessa o mandato:
>
> I - pela revogação ou pela renúncia;
>
> II - pela morte ou interdição de uma das partes;
>
> III - pela mudança de estado que inabilite o mandante a conferir os poderes, ou o mandatário para os exercer;
>
> IV - pelo término do prazo ou pela conclusão do negócio.

#### Art. 684 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art684

> Art. 684. Quando a cláusula de irrevogabilidade for condição de um negócio bilateral, ou tiver sido estipulada no exclusivo interesse do mandatário, a revogação do mandato será ineficaz.

#### Art. 685 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art685

> Art. 685. Conferido o mandato com a cláusula "em causa própria", a sua revogação não terá eficácia, nem se extinguirá pela morte de qualquer das partes, ficando o mandatário dispensado de prestar contas, e podendo transferir para si os bens móveis ou imóveis objeto do mandato, obedecidas as formalidades legais.

#### Art. 686 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art686

> Art. 686. A revogação do mandato, notificada somente ao mandatário, não se pode opor aos terceiros que, ignorando-a, de boa-fé com ele trataram; mas ficam salvas ao constituinte as ações que no caso lhe possam caber contra o procurador.
>
> Parágrafo único. É irrevogável o mandato que contenha poderes de cumprimento ou confirmação de negócios encetados, aos quais se ache vinculado.

#### Art. 687 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art687

> Art. 687. Tanto que for comunicada ao mandatário a nomeação de outro, para o mesmo negócio, considerar-se-á revogado o mandato anterior.

#### Art. 689 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art689

> Art. 689. São válidos, a respeito dos contratantes de boa-fé, os atos com estes ajustados em nome do mandante pelo mandatário, enquanto este ignorar a morte daquele ou a extinção do mandato, por qualquer outra causa.

### 3.2 Código Civil — Sociedade simples (administração) e Sociedade limitada

Fonte: https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm (versão com redações anteriores riscadas: https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm). Texto extraído em 16/10/2026.

#### Art. 1.010 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1010

> Art. 1.010. Quando, por lei ou pelo contrato social, competir aos sócios decidir sobre os negócios da sociedade, as deliberações serão tomadas por maioria de votos, contados segundo o valor das quotas de cada um.
>
> § 1º Para formação da maioria absoluta são necessários votos correspondentes a mais de metade do capital.
>
> § 2º Prevalece a decisão sufragada por maior número de sócios no caso de empate, e, se este persistir, decidirá o juiz.
>
> § 3º Responde por perdas e danos o sócio que, tendo em alguma operação interesse contrário ao da sociedade, participar da deliberação que a aprove graças a seu voto.

#### Art. 1.011 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1011

> Art. 1.011. O administrador da sociedade deverá ter, no exercício de suas funções, o cuidado e a diligência que todo homem ativo e probo costuma empregar na administração de seus próprios negócios.
>
> § 1º Não podem ser administradores, além das pessoas impedidas por lei especial, os condenados a pena que vede, ainda que temporariamente, o acesso a cargos públicos; ou por crime falimentar, de prevaricação, peita ou suborno, concussão, peculato; ou contra a economia popular, contra o sistema financeiro nacional, contra as normas de defesa da concorrência, contra as relações de consumo, a fé pública ou a propriedade, enquanto perdurarem os efeitos da condenação.
>
> § 2º Aplicam-se à atividade dos administradores, no que couber, as disposições concernentes ao mandato.

#### Art. 1.012 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1012

> Art. 1.012. O administrador, nomeado por instrumento em separado, deve averbá-lo à margem da inscrição da sociedade, e, pelos atos que praticar, antes de requerer a averbação, responde pessoal e solidariamente com a sociedade.

#### Art. 1.013 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1013

> Art. 1.013. A administração da sociedade, nada dispondo o contrato social, compete separadamente a cada um dos sócios.
>
> § 1º Se a administração competir separadamente a vários administradores, cada um pode impugnar operação pretendida por outro, cabendo a decisão aos sócios, por maioria de votos.
>
> § 2º Responde por perdas e danos perante a sociedade o administrador que realizar operações, sabendo ou devendo saber que estava agindo em desacordo com a maioria.

#### Art. 1.014 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1014

> Art. 1.014. Nos atos de competência conjunta de vários administradores, torna-se necessário o concurso de todos, salvo nos casos urgentes, em que a omissão ou retardo das providências possa ocasionar dano irreparável ou grave.

#### Art. 1.015 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1015

> Art. 1.015. No silêncio do contrato, os administradores podem praticar todos os atos pertinentes à gestão da sociedade; não constituindo objeto social, a oneração ou a venda de bens imóveis depende do que a maioria dos sócios decidir.
>
> Parágrafo único. (Revogado pela Lei nº 14.195, de 2021)

*Redação(ões) anterior(es)/revogada(s) — exibida(s) riscada(s) no Planalto; NÃO citar como vigente:*

- ~~Parágrafo único. O excesso por parte dos administradores somente pode ser oposto a terceiros se ocorrer pelo menos uma das seguintes hipóteses: (Revogado pela Lei nº 14.195, de 2021)~~
- ~~I - se a limitação de poderes estiver inscrita ou averbada no registro próprio da sociedade; (Revogado pela Lei nº 14.195, de 2021)~~
- ~~II - provando-se que era conhecida do terceiro; (Revogado pela Lei nº 14.195, de 2021)~~
- ~~III - tratando-se de operação evidentemente estranha aos negócios da sociedade. (Revogado pela Lei nº 14.195, de 2021)~~

#### Art. 1.018 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1018

> Art. 1.018. Ao administrador é vedado fazer-se substituir no exercício de suas funções, sendo-lhe facultado, nos limites de seus poderes, constituir mandatários da sociedade, especificados no instrumento os atos e operações que poderão praticar.

#### Art. 1.052 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1052

> Art. 1.052. Na sociedade limitada, a responsabilidade de cada sócio é restrita ao valor de suas quotas, mas todos respondem solidariamente pela integralização do capital social.
>
> § 1º A sociedade limitada pode ser constituída por 1 (uma) ou mais pessoas. (Incluído pela Lei nº 13.874, de 2019)
>
> § 2º Se for unipessoal, aplicar-se-ão ao documento de constituição do sócio único, no que couber, as disposições sobre o contrato social. (Incluído pela Lei nº 13.874, de 2019)

*Redação(ões) anterior(es)/revogada(s) — exibida(s) riscada(s) no Planalto; NÃO citar como vigente:*

- ~~Parágrafo único. A sociedade limitada pode ser constituída por uma ou mais pessoas, hipótese em que se aplicarão ao documento de constituição do sócio único, no que couber, as disposições sobre o contrato social. (Incluído pela Medida Provisória nº 881, de 2019)~~

#### Art. 1.053 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1053

> Art. 1.053. A sociedade limitada rege-se, nas omissões deste Capítulo, pelas normas da sociedade simples.
>
> Parágrafo único. O contrato social poderá prever a regência supletiva da sociedade limitada pelas normas da sociedade anônima.

#### Art. 1.060 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1060

> Art. 1.060. A sociedade limitada é administrada por uma ou mais pessoas designadas no contrato social ou em ato separado.
>
> Parágrafo único. A administração atribuída no contrato a todos os sócios não se estende de pleno direito aos que posteriormente adquiram essa qualidade.

#### Art. 1.061 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1061

> Art. 1.061. A designação de administradores não sócios dependerá da aprovação de, no mínimo, 2/3 (dois terços) dos sócios, enquanto o capital não estiver integralizado, e da aprovação de titulares de quotas correspondentes a mais da metade do capital social, após a integralização. (Redação dada pela Lei nº 14.451, de 2022)

*Redação(ões) anterior(es)/revogada(s) — exibida(s) riscada(s) no Planalto; NÃO citar como vigente:*

- ~~Art. 1.061. Se o contrato permitir administradores não sócios, a designação deles dependerá de aprovação da unanimidade dos sócios, enquanto o capital não estiver integralizado, e de dois terços, no mínimo, após a integralização.~~
- ~~Art. 1.061. A designação de administradores não sócios dependerá de aprovação da unanimidade dos sócios, enquanto o capital não estiver integralizado, e de 2/3 (dois terços), no mínimo, após a integralização. (Redação dada pela Lei nº 12.375, de 2010)~~

#### Art. 1.062 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1062

> Art. 1.062. O administrador designado em ato separado investir-se-á no cargo mediante termo de posse no livro de atas da administração.
>
> § 1º Se o termo não for assinado nos trinta dias seguintes à designação, esta se tornará sem efeito.
>
> § 2º Nos dez dias seguintes ao da investidura, deve o administrador requerer seja averbada sua nomeação no registro competente, mencionando o seu nome, nacionalidade, estado civil, residência, com exibição de documento de identidade, o ato e a data da nomeação e o prazo de gestão.

#### Art. 1.063 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1063

> Art. 1.063. O exercício do cargo de administrador cessa pela destituição, em qualquer tempo, do titular, ou pelo término do prazo se, fixado no contrato ou em ato separado, não houver recondução.
>
> § 1º Tratando-se de sócio nomeado administrador no contrato, sua destituição somente se opera pela aprovação de titulares de quotas correspondentes a mais da metade do capital social, salvo disposição contratual diversa. (Redação dada pela Lei nº 13.792, de 2019)
>
> § 2º A cessação do exercício do cargo de administrador deve ser averbada no registro competente, mediante requerimento apresentado nos dez dias seguintes ao da ocorrência.
>
> § 3º A renúncia de administrador torna-se eficaz, em relação à sociedade, desde o momento em que esta toma conhecimento da comunicação escrita do renunciante; e, em relação a terceiros, após a averbação e publicação.

*Redação(ões) anterior(es)/revogada(s) — exibida(s) riscada(s) no Planalto; NÃO citar como vigente:*

- ~~§ 1º Tratando-se de sócio nomeado administrador no contrato, sua destituição somente se opera pela aprovação de titulares de quotas correspondentes, no mínimo, a dois terços do capital social, salvo disposição contratual diversa.~~

#### Art. 1.064 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1064

> Art. 1.064. O uso da firma ou denominação social é privativo dos administradores que tenham os necessários poderes.

#### Art. 1.071 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1071

> Art. 1.071. Dependem da deliberação dos sócios, além de outras matérias indicadas na lei ou no contrato:
>
> I - a aprovação das contas da administração;
>
> II - a designação dos administradores, quando feita em ato separado;
>
> III - a destituição dos administradores;
>
> IV - o modo de sua remuneração, quando não estabelecido no contrato;
>
> V - a modificação do contrato social;
>
> VI - a incorporação, a fusão e a dissolução da sociedade, ou a cessação do estado de liquidação;
>
> VII - a nomeação e destituição dos liquidantes e o julgamento das suas contas;
>
> VIII - o pedido de concordata.

#### Art. 1.072 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1072

> Art. 1.072. As deliberações dos sócios, obedecido o disposto no art. 1.010, serão tomadas em reunião ou em assembléia, conforme previsto no contrato social, devendo ser convocadas pelos administradores nos casos previstos em lei ou no contrato.
>
> § 1º A deliberação em assembléia será obrigatória se o número dos sócios for superior a dez.
>
> § 2º Dispensam-se as formalidades de convocação previstas no § 3º do art. 1.152, quando todos os sócios comparecerem ou se declararem, por escrito, cientes do local, data, hora e ordem do dia.
>
> § 3º A reunião ou a assembléia tornam-se dispensáveis quando todos os sócios decidirem, por escrito, sobre a matéria que seria objeto delas.
>
> § 4º No caso do inciso VIII do artigo antecedente, os administradores, se houver urgência e com autorização de titulares de mais da metade do capital social, podem requerer concordata preventiva.
>
> § 5º As deliberações tomadas de conformidade com a lei e o contrato vinculam todos os sócios, ainda que ausentes ou dissidentes.
>
> § 6º Aplica-se às reuniões dos sócios, nos casos omissos no contrato, o disposto na presente Seção sobre a assembléia.

#### Art. 1.076 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1076

> Art. 1.076. Ressalvado o disposto no art. 1.061, as deliberações dos sócios serão tomadas: (Redação dada pela Lei nº 13.792, de 2019)
>
> I - (revogado); (Redação dada pela Lei nº 14.451, de 2022)
>
> II - pelos votos correspondentes a mais da metade do capital social, nos casos previstos nos incisos II, III, IV, V, VI e VIII do caput do art. 1.071 deste Código; (Redação dada pela Lei nº 14.451, de 2022)
>
> III - pela maioria de votos dos presentes, nos demais casos previstos na lei ou no contrato, se este não exigir maioria mais elevada.

*Redação(ões) anterior(es)/revogada(s) — exibida(s) riscada(s) no Planalto; NÃO citar como vigente:*

- ~~Art. 1.076. Ressalvado o disposto no art. 1.061 e no § 1º do art. 1.063, as deliberações dos sócios serão tomadas:~~
- ~~I - pelos votos correspondentes, no mínimo, a três quartos do capital social, nos casos previstos nos incisos V e VI do art. 1.071; (Revogado pela Lei nº 14.451, de 2022)~~
- ~~II - pelos votos correspondentes a mais de metade do capital social, nos casos previstos nos incisos II, III, IV e VIII do art. 1.071;~~

### 3.3 Código Civil — Registro

Fonte: https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm (versão com redações anteriores riscadas: https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm). Texto extraído em 16/10/2026.

#### Art. 1.151 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1151

> Art. 1.151. O registro dos atos sujeitos à formalidade exigida no artigo antecedente será requerido pela pessoa obrigada em lei, e, no caso de omissão ou demora, pelo sócio ou qualquer interessado.
>
> § 1º Os documentos necessários ao registro deverão ser apresentados no prazo de trinta dias, contado da lavratura dos atos respectivos.
>
> § 2º Requerido além do prazo previsto neste artigo, o registro somente produzirá efeito a partir da data de sua concessão.
>
> § 3º As pessoas obrigadas a requerer o registro responderão por perdas e danos, em caso de omissão ou demora.

#### Art. 1.154 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1154

> Art. 1.154. O ato sujeito a registro, ressalvadas disposições especiais da lei, não pode, antes do cumprimento das respectivas formalidades, ser oposto a terceiro, salvo prova de que este o conhecia.
>
> Parágrafo único. O terceiro não pode alegar ignorância, desde que cumpridas as referidas formalidades.

### 3.4 Código Civil — dispositivos complementares úteis (não pedidos, incluídos para o parecer)

Fonte: https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm (versão com redações anteriores riscadas: https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm). Texto extraído em 16/10/2026.

#### Art. 79 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art79

> Art. 79. São bens imóveis o solo e tudo quanto se lhe incorporar natural ou artificialmente.

#### Art. 82 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art82

> Art. 82. São móveis os bens suscetíveis de movimento próprio, ou de remoção por força alheia, sem alteração da substância ou da destinação econômico-social.

#### Art. 107 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art107

> Art. 107. A validade da declaração de vontade não dependerá de forma especial, senão quando a lei expressamente a exigir.

#### Art. 108 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art108

> Art. 108. Não dispondo a lei em contrário, a escritura pública é essencial à validade dos negócios jurídicos que visem à constituição, transferência, modificação ou renúncia de direitos reais sobre imóveis de valor superior a trinta vezes o maior salário mínimo vigente no País.

#### Art. 1.226 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1226

> Art. 1.226. Os direitos reais sobre coisas móveis, quando constituídos, ou transmitidos por atos entre vivos, só se adquirem com a tradição.

#### Art. 1.267 — https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm#art1267

> Art. 1.267. A propriedade das coisas não se transfere pelos negócios jurídicos antes da tradição.
>
> Parágrafo único. Subentende-se a tradição quando o transmitente continua a possuir pelo constituto possessório; quando cede ao adquirente o direito à restituição da coisa, que se encontra em poder de terceiro; ou quando o adquirente já está na posse da coisa, por ocasião do negócio jurídico.

### 3.5 Lei nº 8.934/1994 (Registro Público de Empresas Mercantis)

Fonte: https://www.planalto.gov.br/ccivil_03/leis/l8934.htm (versão com redações anteriores riscadas: https://www.planalto.gov.br/ccivil_03/leis/l8934.htm). Texto extraído em 16/10/2026.

#### Art. 32 — https://www.planalto.gov.br/ccivil_03/leis/l8934.htm#art32

> Art. 32. O registro compreende:
>
> I - a matrícula e seu cancelamento: dos leiloeiros, tradutores públicos e intérpretes comerciais, trapicheiros e administradores de armazéns-gerais;
>
> II - O arquivamento:
>
> a) dos documentos relativos à constituição, alteração, dissolução e extinção de firmas mercantis individuais, sociedades mercantis e cooperativas;
>
> b) dos atos relativos a consórcio e grupo de sociedade de que trata a Lei nº 6.404, de 15 de dezembro de 1976;
>
> c) dos atos concernentes a empresas mercantis estrangeiras autorizadas a funcionar no Brasil;
>
> d) das declarações de microempresa;
>
> e) de atos ou documentos que, por determinação legal, sejam atribuídos ao Registro Público de Empresas Mercantis e Atividades Afins ou daqueles que possam interessar ao empresário e às empresas mercantis;
>
> III - a autenticação dos instrumentos de escrituração das empresas mercantis registradas e dos agentes auxiliares do comércio, na forma de lei própria.
>
> § 1º Os atos, os documentos e as declarações que contenham informações meramente cadastrais serão levados automaticamente a registro se puderem ser obtidos de outras bases de dados disponíveis em órgãos públicos. (Incluído pela Lei nº 13.874, de 2019)
>
> § 2º Ato do Departamento Nacional de Registro Empresarial e Integração definirá os atos, os documentos e as declarações que contenham informações meramente cadastrais. (Incluído pela Lei nº 13.874, de 2019)

#### Art. 36 — https://www.planalto.gov.br/ccivil_03/leis/l8934.htm#art36

> Art. 36. Os documentos referidos no inciso II do art. 32 deverão ser apresentados a arquivamento na junta, dentro de 30 (trinta) dias contados de sua assinatura, a cuja data retroagirão os efeitos do arquivamento; fora desse prazo, o arquivamento só terá eficácia a partir do despacho que o conceder.

### 3.6 Lei nº 6.404/1976 (Lei das S.A.)

Fonte: https://www.planalto.gov.br/ccivil_03/leis/l6404consol.htm (versão com redações anteriores riscadas: https://www.planalto.gov.br/ccivil_03/leis/l6404consol.htm). Texto extraído em 16/10/2026.

#### Art. 138 — https://www.planalto.gov.br/ccivil_03/leis/l6404consol.htm#art138

> Art. 138. A administração da companhia competirá, conforme dispuser o estatuto, ao conselho de administração e à diretoria, ou somente à diretoria.
>
> § 1º O conselho de administração é órgão de deliberação colegiada, sendo a representação da companhia privativa dos diretores.
>
> § 2º As companhias abertas e as de capital autorizado terão, obrigatoriamente, conselho de administração.
>
> § 3º É vedada, nas companhias abertas, a acumulação do cargo de presidente do conselho de administração e do cargo de diretor-presidente ou de principal executivo da companhia. (Incluído pela Lei nº 14.195, de 2021)
>
> § 4º A Comissão de Valores Mobiliários poderá editar ato normativo que excepcione as companhias de menor porte previstas no art. 294-B desta Lei da vedação de que trata o § 3º deste artigo. (Incluído pela Lei nº 14.195, de 2021)

*Redação(ões) anterior(es)/revogada(s) — exibida(s) riscada(s) no Planalto; NÃO citar como vigente:*

- ~~§ 3º É vedada, nas companhias abertas, a acumulação do cargo de presidente do conselho de administração e do cargo de diretor-presidente ou de principal executivo da companhia. (Incluído pela Medida Provisória nº 1.040, de 2021)~~
- ~~§ 4º A Comissão de Valores Mobiliários poderá excepcionar a vedação de que trata o § 3º para as companhias com menor faturamento, nos termos de sua regulamentação. (Incluído pela Medida Provisória nº 1.040, de 2021)~~

#### Art. 142 — https://www.planalto.gov.br/ccivil_03/leis/l6404consol.htm#art142

> Art. 142. Compete ao conselho de administração:
>
> I - fixar a orientação geral dos negócios da companhia;
>
> II - eleger e destituir os diretores da companhia e fixar-lhes as atribuições, observado o que a respeito dispuser o estatuto;
>
> III - fiscalizar a gestão dos diretores, examinar, a qualquer tempo, os livros e papéis da companhia, solicitar informações sobre contratos celebrados ou em via de celebração, e quaisquer outros atos;
>
> IV - convocar a assembléia-geral quando julgar conveniente, ou no caso do artigo 132;
>
> V - manifestar-se sobre o relatório da administração e as contas da diretoria;
>
> VI - manifestar-se previamente sobre atos ou contratos, quando o estatuto assim o exigir;
>
> VII - deliberar, quando autorizado pelo estatuto, sobre a emissão de ações ou de bônus de subscrição; (Vide Lei nº 12.838, de 2013)
>
> VIII – autorizar, se o estatuto não dispuser em contrário, a alienação de bens do ativo não circulante, a constituição de ônus reais e a prestação de garantias a obrigações de terceiros; (Redação dada pela Lei nº 11.941, de 2009)
>
> IX - escolher e destituir os auditores independentes, se houver.
>
> § 1º Serão arquivadas no registro do comércio e publicadas as atas das reuniões do conselho de administração que contiverem deliberação destinada a produzir efeitos perante terceiros. (Redação dada pela Lei nº 10.303, de 2001)
>
> § 2º A escolha e a destituição do auditor independente ficará sujeita a veto, devidamente fundamentado, dos conselheiros eleitos na forma do art. 141, § 4º, se houver. (Incluído pela Lei nº 10.303, de 2001)

*Redação(ões) anterior(es)/revogada(s) — exibida(s) riscada(s) no Planalto; NÃO citar como vigente:*

- ~~VIII - autorizar, se o estatuto não dispuser em contrário, a alienação de bens do ativo permanente, a constituição de ônus reais e a prestação de garantias a obrigações de terceiros;~~
- ~~VIII - autorizar, se o estatuto não dispuser em contrário, a alienação de bens do ativo não-circulante, a constituição de ônus reais e a prestação de garantias a obrigações de terceiros; (Redação dada pela Medida Provisória nº 449, de 2008)~~
- ~~Parágrafo único. Serão arquivadas no registro do comércio e publicadas as atas das reuniões do conselho de administração que contiverem deliberação destinada a produzir efeitos perante terceiros.~~

#### Art. 143 — https://www.planalto.gov.br/ccivil_03/leis/l6404consol.htm#art143

> Art. 143. A Diretoria será composta por 1 (um) ou mais membros eleitos e destituíveis a qualquer tempo pelo conselho de administração ou, se inexistente, pela assembleia geral, e o estatuto estabelecerá: (Redação dada pela Lei Complementar nº 182, de 2021)
>
> I - o número de diretores, ou o máximo e o mínimo permitidos;
>
> II - o modo de sua substituição;
>
> III - o prazo de gestão, que não será superior a 3 (três) anos, permitida a reeleição;
>
> IV - as atribuições e poderes de cada diretor.
>
> § 1º Os membros do conselho de administração, até o máximo de 1/3 (um terço), poderão ser eleitos para cargos de diretores.
>
> § 2º O estatuto pode estabelecer que determinadas decisões, de competência dos diretores, sejam tomadas em reunião da diretoria.

*Redação(ões) anterior(es)/revogada(s) — exibida(s) riscada(s) no Planalto; NÃO citar como vigente:*

- ~~Art. 143. A Diretoria será composta por 2 (dois) ou mais diretores, eleitos e destituíveis a qualquer tempo pelo conselho de administração, ou, se inexistente, pela assembléia-geral, devendo o estatuto estabelecer:~~

#### Art. 144 — https://www.planalto.gov.br/ccivil_03/leis/l6404consol.htm#art144

> Art. 144. No silêncio do estatuto e inexistindo deliberação do conselho de administração (artigo 142, n. II e parágrafo único), competirão a qualquer diretor a representação da companhia e a prática dos atos necessários ao seu funcionamento regular.
>
> Parágrafo único. Nos limites de suas atribuições e poderes, é lícito aos diretores constituir mandatários da companhia, devendo ser especificados no instrumento os atos ou operações que poderão praticar e a duração do mandato, que, no caso de mandato judicial, poderá ser por prazo indeterminado.

#### Art. 150 — https://www.planalto.gov.br/ccivil_03/leis/l6404consol.htm#art150

> Art. 150. No caso de vacância do cargo de conselheiro, salvo disposição em contrário do estatuto, o substituto será nomeado pelos conselheiros remanescentes e servirá até a primeira assembléia-geral. Se ocorrer vacância da maioria dos cargos, a assembléia-geral será convocada para proceder a nova eleição.
>
> § 1º No caso de vacância de todos os cargos do conselho de administração, compete à diretoria convocar a assembléia-geral.
>
> § 2º No caso de vacância de todos os cargos da diretoria, se a companhia não tiver conselho de administração, compete ao conselho fiscal, se em funcionamento, ou a qualquer acionista, convocar a assembléia-geral, devendo o representante de maior número de ações praticar, até a realização da assembléia, os atos urgentes de administração da companhia.
>
> § 3º O substituto eleito para preencher cargo vago completará o prazo de gestão do substituído.
>
> § 4º O prazo de gestão do conselho de administração ou da diretoria se estende até a investidura dos novos administradores eleitos.

### 3.7 CTB (Lei nº 9.503/1997)

Fonte: https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm (versão com redações anteriores riscadas: https://www.planalto.gov.br/ccivil_03/leis/l9503.htm). Texto extraído em 16/10/2026.

#### Art. 123 — https://www.planalto.gov.br/ccivil_03/leis/l9503.htm#art123

> Art. 123. Será obrigatória a expedição de novo Certificado de Registro de Veículo quando:
>
> I - for transferida a propriedade;
>
> II - o proprietário mudar o Município de domicílio ou residência;
>
> III - for alterada qualquer característica do veículo;
>
> IV - houver mudança de categoria.
>
> § 1º No caso de transferência de propriedade, o prazo para o proprietário adotar as providências necessárias à efetivação da expedição do novo Certificado de Registro de Veículo é de trinta dias, sendo que nos demais casos as providências deverão ser imediatas.
>
> § 2º No caso de transferência de domicílio ou residência no mesmo Município, o proprietário comunicará o novo endereço num prazo de trinta dias e aguardará o novo licenciamento para alterar o Certificado de Licenciamento Anual.
>
> § 3º A expedição do novo certificado será comunicada ao órgão executivo de trânsito que expediu o anterior e ao RENAVAM.
>
> § 4º A transferência de propriedade referida no inciso I do caput deste artigo poderá ser realizada integralmente por meio eletrônico pelo órgão máximo executivo de trânsito da União ou pelos órgãos executivos de trânsito dos Estados e do Distrito Federal, observadas as seguintes regras: (Incluído pela Lei nº 15.153, de 2025)
>
> I - no caso de transferência de propriedade realizada em meio eletrônico, o contrato de compra e venda de veículo deverá conter as assinaturas eletrônicas qualificadas ou avançadas, na forma da Lei nº 14.063, de 23 de setembro de 2020, e das normas regulamentares do Contran; (Incluído pela Lei nº 15.153, de 2025)
>
> II - o contrato de compra e venda de veículo em meio digital, quando assinado eletronicamente pelo comprador e pelo vendedor do veículo perante o órgão máximo executivo de trânsito da União, terá validade em todo o território nacional e deverá ser obrigatoriamente acatado por todos os órgãos de trânsito dos Estados e do Distrito Federal; (Incluído pela Lei nº 15.153, de 2025)
>
> III - a assinatura eletrônica avançada do contrato de compra e venda de veículo deverá ser realizada por meio de plataforma de assinatura homologada pelo órgão máximo executivo de trânsito da União ou pelos órgãos executivos de trânsito dos Estados e do Distrito Federal, conforme regulamentação do Contran; (Incluído pela Lei nº 15.153, de 2025)
>
> IV - (VETADO); (Incluído pela Lei nº 15.153, de 2025)
>
> V - a vistoria de transferência da propriedade poderá ser realizada em formato eletrônico a critério do órgão executivo de trânsito dos Estados e do Distrito Federal. (Incluído pela Lei nº 15.153, de 2025)

#### Art. 124 — https://www.planalto.gov.br/ccivil_03/leis/l9503.htm#art124

> Art. 124. Para a expedição do novo Certificado de Registro de Veículo serão exigidos os seguintes documentos:
>
> I - Certificado de Registro de Veículo anterior;
>
> II - Certificado de Licenciamento Anual;
>
> III - comprovante de transferência de propriedade, quando for o caso, conforme modelo e normas estabelecidas pelo CONTRAN;
>
> IV - Certificado de Segurança Veicular e de emissão de poluentes e ruído, quando houver adaptação ou alteração de características do veículo;
>
> V - comprovante de procedência e justificativa da propriedade dos componentes e agregados adaptados ou montados no veículo, quando houver alteração das características originais de fábrica;
>
> VI - autorização do Ministério das Relações Exteriores, no caso de veículo da categoria de missões diplomáticas, de repartições consulares de carreira, de representações de organismos internacionais e de seus integrantes;
>
> VII - certidão negativa de roubo ou furto de veículo, expedida no Município do registro anterior, que poderá ser substituída por informação do RENAVAM;
>
> VIII - comprovante de quitação de débitos relativos a tributos, encargos e multas de trânsito vinculados ao veículo, independentemente da responsabilidade pelas infrações cometidas; (Vide ADIN 2998)
>
> IX - (Revogado pela Lei nº 9.602, de 1998)
>
> X - comprovante relativo ao cumprimento do disposto no art. 98, quando houver alteração nas características originais do veículo que afetem a emissão de poluentes e ruído;
>
> XI - comprovante de aprovação de inspeção veicular e de poluentes e ruído, quando for o caso, conforme regulamentações do CONTRAN e do CONAMA.
>
> Parágrafo único. Os veículos cuja transferência de propriedade seja resultado de apreensão ou de confisco por decisão judicial, leilão de veículo recolhido em depósito ou de doação a órgãos ou entidades da administração pública são dispensados do cumprimento do disposto no inciso VIII do caput deste artigo, e os débitos existentes devem ser cobrados do proprietário anterior. (Redação dada pela Lei nº 14.440, de 2022)

*Redação(ões) anterior(es)/revogada(s) — exibida(s) riscada(s) no Planalto; NÃO citar como vigente:*

- ~~IX - Registro Nacional de Transportadores Rodoviários, no caso de veículos de carga; (Revogado pela Lei nº 9.602, de 1998)~~
- ~~Parágrafo único. O disposto no inciso VIII do caput deste artigo não se aplica à regularização de bens apreendidos ou confiscados na forma da Lei nº 11.343, de 23 de agosto de 2006. (Incluído pela Lei nº 13.886, de 2019)~~

#### Art. 134 — https://www.planalto.gov.br/ccivil_03/leis/l9503.htm#art134

> Art. 134. No caso de transferência de propriedade, expirado o prazo previsto no § 1º do art. 123 deste Código sem que o novo proprietário tenha tomado as providências necessárias à efetivação da expedição do novo Certificado de Registro de Veículo, o antigo proprietário deverá encaminhar ao órgão executivo de trânsito do Estado ou do Distrito Federal, no prazo de 60 (sessenta) dias, cópia autenticada do comprovante de transferência de propriedade, devidamente assinado e datado, sob pena de ter que se responsabilizar solidariamente pelas penalidades impostas e suas reincidências até a data da comunicação. (Redação dada pela Lei nº 14.071, de 2020)
>
> Parágrafo único. O comprovante de transferência de propriedade de que trata o caput deste artigo poderá ser substituído por documento eletrônico com assinatura eletrônica válida, na forma regulamentada pelo Contran. (Redação dada pela Lei nº 14.071, de 2020)

*Redação(ões) anterior(es)/revogada(s) — exibida(s) riscada(s) no Planalto; NÃO citar como vigente:*

- ~~Art. 134. No caso de transferência de propriedade, o proprietário antigo deverá encaminhar ao órgão executivo de trânsito do Estado dentro de um prazo de trinta dias, cópia autenticada do comprovante de transferência de propriedade, devidamente assinado e datado, sob pena de ter que se responsabilizar solidariamente pelas penalidades impostas e suas reincidências até a data da comunicação.~~
- ~~Parágrafo único. O comprovante de transferência de propriedade de que trata o caput poderá ser substituído por documento eletrônico, na forma regulamentada pelo Contran. (Incluído pela Lei nº 13.154, de 2015)~~

#### Art. 233 — https://www.planalto.gov.br/ccivil_03/leis/l9503.htm#art233

> Art. 233. Deixar de efetuar o registro de veículo no prazo de trinta dias, junto ao órgão executivo de trânsito, ocorridas as hipóteses previstas no art. 123:
>
> Infração - média; (Redação dada pela Lei nº 14.071, de 2020)
>
> Penalidade - multa; (Redação dada pela Lei nº 14.071, de 2020)
>
> Medida administrativa - remoção do veículo. (Redação dada pela Lei nº 14.071, de 2020)

*Redação(ões) anterior(es)/revogada(s) — exibida(s) riscada(s) no Planalto; NÃO citar como vigente:*

- ~~Infração - grave;~~
- ~~Penalidade - multa;~~
- ~~Medida administrativa - retenção do veículo para regularização.~~

### 3.8 Lei nº 14.063/2020 (assinaturas eletrônicas em interações com entes públicos)

Fonte: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14063.htm (versão com redações anteriores riscadas: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14063.htm). Texto extraído em 16/10/2026.

#### Art. 4 — https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14063.htm#art4

> Art. 4º Para efeitos desta Lei, as assinaturas eletrônicas são classificadas em:
>
> I - assinatura eletrônica simples:
>
> a) a que permite identificar o seu signatário;
>
> b) a que anexa ou associa dados a outros dados em formato eletrônico do signatário;
>
> II - assinatura eletrônica avançada: a que utiliza certificados não emitidos pela ICP-Brasil ou outro meio de comprovação da autoria e da integridade de documentos em forma eletrônica, desde que admitido pelas partes como válido ou aceito pela pessoa a quem for oposto o documento, com as seguintes características:
>
> a) está associada ao signatário de maneira unívoca;
>
> b) utiliza dados para a criação de assinatura eletrônica cujo signatário pode, com elevado nível de confiança, operar sob o seu controle exclusivo;
>
> c) está relacionada aos dados a ela associados de tal modo que qualquer modificação posterior é detectável;
>
> III - assinatura eletrônica qualificada: a que utiliza certificado digital, nos termos do § 1º do art. 10 da Medida Provisória nº 2.200-2, de 24 de agosto de 2001.
>
> § 1º Os 3 (três) tipos de assinatura referidos nos incisos I, II e III do caput deste artigo caracterizam o nível de confiança sobre a identidade e a manifestação de vontade de seu titular, e a assinatura eletrônica qualificada é a que possui nível mais elevado de confiabilidade a partir de suas normas, de seus padrões e de seus procedimentos específicos.
>
> § 2º Devem ser asseguradas formas de revogação ou de cancelamento definitivo do meio utilizado para as assinaturas previstas nesta Lei, sobretudo em casos de comprometimento de sua segurança ou de vazamento de dados.

#### Art. 5 — https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14063.htm#art5

> Art. 5º No âmbito de suas competências, ato do titular do Poder ou do órgão constitucionalmente autônomo de cada ente federativo estabelecerá o nível mínimo exigido para a assinatura eletrônica em documentos e em interações com o ente público. (Regulamento)
>
> § 1º O ato de que trata o caput deste artigo observará o seguinte:
>
> I - a assinatura eletrônica simples poderá ser admitida nas interações com ente público de menor impacto e que não envolvam informações protegidas por grau de sigilo;
>
> II - a assinatura eletrônica avançada poderá ser admitida, inclusive:
>
> a) nas hipóteses de que trata o inciso I deste parágrafo;
>
> b) (VETADO);
>
> c) no registro de atos perante as juntas comerciais;
>
> III - a assinatura eletrônica qualificada será admitida em qualquer interação eletrônica com ente público, independentemente de cadastramento prévio, inclusive nas hipóteses mencionadas nos incisos I e II deste parágrafo.
>
> § 2º É obrigatório o uso de assinatura eletrônica qualificada:
>
> I - nos atos assinados por chefes de Poder, por Ministros de Estado ou por titulares de Poder ou de órgão constitucionalmente autônomo de ente federativo;
>
> II - (VETADO);
>
> III - nas emissões de notas fiscais eletrônicas, com exceção daquelas cujos emitentes sejam pessoas físicas ou Microempreendedores Individuais (MEIs), situações em que o uso torna-se facultativo;
>
> IV - nos atos de transferência e de registro de bens imóveis, ressalvado o disposto na alínea “c” do inciso II do § 1º deste artigo;
>
> V – (VETADO);
>
> VI - nas demais hipóteses previstas em lei.
>
> § 3º (VETADO).
>
> § 4º O ente público informará em seu site os requisitos e os mecanismos estabelecidos internamente para reconhecimento de assinatura eletrônica avançada.
>
> § 5º No caso de conflito entre normas vigentes ou de conflito entre normas editadas por entes distintos, prevalecerá o uso de assinaturas eletrônicas qualificadas.
>
> § 6º As certidões emitidas por sistema eletrônico da Justiça Eleitoral possuem fé pública e, nos casos dos órgãos partidários, substituem os cartórios de registro de pessoas jurídicas para constituição dos órgãos partidários estaduais e municipais, dispensados quaisquer registros em cartórios da circunscrição do respectivo órgão partidário.

---

## 4. RENAVE (Registro Nacional de Veículos em Estoque)

Pesquisa feita em 16/10/2026. Os textos normativos foram baixados das fontes oficiais (gov.br/transportes, planalto.gov.br, DETRANs) e convertidos para texto. As citações literais estão entre aspas. Onde algo não pôde ser confirmado, está escrito "não confirmado".


### 4.1 O que é e qual a norma vigente

**Norma vigente: Resolução CONTRAN nº 1.026, de 26 de junho de 2026**, que "Institui o Registro Nacional de Veículos em Estoque - Renave e altera a Resolução Contran nº 807, de 2020."
- Página do DOU impressa (PDF no gov.br): "Seção 1 - Edição Extra", "Nº 120-C, terça-feira, 30 de junho de 2026" — https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/Resoluo1026.pdf
- A versão em texto no gov.br traz o cabeçalho "Publicado em: 01/07/2026 | Edição: 121-B | Seção: 1 - Extra B | Página: 11" — https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/resolucao10262026n.pdf (há também a versão `resolucao10262026c.pdf`, com texto idêntico). **Há divergência sobre a data de publicação (30/06 ou 01/07/2026).** A imprensa e o prazo final de 28/09/2026 são coerentes com 30/06/2026. Qual das duas é a data oficial: não confirmado.
- Vigência: "Art. 36. Esta Resolução entra em vigor na data de sua publicação."
- Revogações: "Art. 35. Ficam revogadas as Resoluções Contran nº 797, de 2 de setembro de 2020, e nº 818, de 17 de março de 2021."

Texto literal (Res. 1.026/2026):
- "Art. 1º Esta Resolução institui o Registro Nacional de Veículos em Estoque - Renave, sistema eletrônico cuja finalidade é registrar as movimentações de entrada e saída de veículos, novos ou usados, bem como o uso de placas de experiência, pelos estabelecimentos de que trata o art. 330 da Lei nº 9.503, de 23 de setembro de 1997 - Código de Trânsito Brasileiro, com o objetivo de conferir maior celeridade, eficiência, padronização e integridade aos processos de comercialização de veículos."
- "§ 1º O Renave é o único meio eletrônico admitido para realizar a escrituração eletrônica de entrada e saída de veículos, novos ou usados, substituindo os livros de registros físicos, conforme disposto no art. 330, § 6º, do Código de Trânsito Brasileiro."
- "§ 2º Não constituem escopo do Renave a efetivação da transferência de propriedade do veículo de que trata o art. 123, inciso I, do Código de Trânsito Brasileiro, incluindo a formalização do contrato de compra e venda, a coleta de assinaturas eletrônicas, bem como os procedimentos de apontamento, registro de contrato e constituição de gravame relacionados às garantias de alienação fiduciária, os quais observarão o disposto em regulamentação específica."
- "§ 3º O Renave será organizado e mantido pelo órgão máximo executivo de trânsito da União, e constitui subsistema informatizado do Registro Nacional de Veículos Automotores - Renavam."
- Art. 2º, definições:
  - "I - estabelecimento: pessoa jurídica regularmente constituída e representada que execute reformas ou recuperação de veículos ou que exerça atividade de compra e venda ou desmonte de veículos automotores, novos ou usados;"
  - "VII - veículo em estoque: veículo novo ou usado adquirido pelo estabelecimento para fins de comercialização, com correspondente registro eletrônico de entrada ativo no Renave;"
  - "VIII - veículo consignado: veículo entregue ao estabelecimento para fins de comercialização, pelo proprietário, por meio de contrato eletrônico de consignação, sem a transferência da propriedade;"
  - "XI - termo de entrega de veículo para entrada em estoque: documento eletrônico emitido pelo Renave que registra a intenção de entrada imediata do veículo no estoque do estabelecimento, e que somente será emitido mediante assinatura eletrônica do proprietário, nos termos de regulamentação específica; e"
  - "XII - termo de entrega de veículo para saída de estoque: documento eletrônico emitido pelo Renave para indicar a saída imediata do veículo de estoque, informando os dados do comprador adquirente, e que somente será emitido mediante assinatura eletrônica do proprietário, nos termos de regulamentação específica."

Base legal no CTB (Lei 9.503/1997), art. 330 (texto do planalto, https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm):
- "Art. 330. Os estabelecimentos onde se executem reformas ou recuperação de veículos e os que comprem, vendam ou desmontem veículos, usados ou não, são obrigados a possuir livros de registro de seu movimento de entrada e saída e de uso de placas de experiência, conforme modelos aprovados e rubricados pelos órgãos de trânsito."
- "§ 5º A falta de escrituração dos livros, o atraso, a fraude ao realizá-lo e a recusa de sua exibição serão punidas com a multa prevista para as infrações gravíssimas, independente das demais cominações legais cabíveis."
- "§ 6o Os livros previstos neste artigo poderão ser substituídos por sistema eletrônico, na forma regulamentada pelo Contran. (Incluído pela Lei nº 13.154, de 2015)"

### 4.2 Histórico normativo (todas as normas anteriores estão revogadas)

| Norma | Ementa (resumo) | Situação | Fonte |
|---|---|---|---|
| Deliberação CONTRAN 144, de 28/08/2015 | 1ª instituição do RENAVE | revogada pela Res. 584/2016 (art. 10) | https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/deliberacoes/deliberacao144.pdf |
| Res. CONTRAN 584, de 23/03/2016 | "Estabelece o registro nacional de veículos em estoque – RENAVE" | revogada pela Res. 655 (art. 40) | https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/resolucao5842016.pdf |
| Res. CONTRAN 655, de 10/01/2017 | "Estabelece o Registro Nacional de Veículos em Estoque – RENAVE e dá outras providências" | revogada pela Res. 678 (art. 39) | https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/resolucao6552016.pdf |
| Res. CONTRAN 678, de 21/06/2017 | idem | revogada pela Res. 797 (art. 21) | https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/resolucao6782017.pdf |
| Res. CONTRAN 797, de 02/09/2020 (em vigor desde 01/10/2020) | institui o RENAVE e trata da compra e venda de veículos novos e usados nos estabelecimentos do art. 330 | **revogada pela Res. 1.026/2026** | https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/resolucao797-2020.pdf/@@download/file |
| Res. CONTRAN 818, de 17/03/2021 | altera a Res. 797 | **revogada pela Res. 1.026/2026** | https://www.legisweb.com.br/legislacao/?id=411459 |
| **Res. CONTRAN 1.026, de 26/06/2026** | institui o Renave (regime atual) | **vigente** | links em 4.1 |

Ato complementar: **Circular SENATRAN nº 2, de 30/09/2026** (DOU de 30/09/2026, Edição 185-C, Seção 1 – Extra C, p. 18). Ela fixa o cronograma de implantação da Res. 1.026, com base no art. 33, § 4º (ver 4.4) — https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/circular022026.pdf

### 4.3 Quem é obrigado

- **Todo estabelecimento do art. 330 do CTB que comercializa veículos.** Texto: "Art. 5º Compete ao estabelecimento: ... III - registrar todas as operações de entrada, saída, transferência entre estabelecimentos e consignação de veículos destinados à comercialização no Renave, por meio de integradora autorizada pelo órgão máximo executivo de trânsito da União;" (Res. 1.026/2026).
- **Adesão por CNAE.** Texto: "Art. 7º Os estabelecimentos de que trata esta Resolução deverão solicitar sua adesão ao Renave cadastrando sua solicitação junto ao órgão máximo executivo de trânsito da União, por meio do sistema Credencia, devendo apresentar em seu objeto social e na Classificação Nacional de Atividades Econômicas - CNAE atividade econômica principal compatível com uma das seguintes atividades: I - compra e venda de veículos automotores novos ou usados; II - atividade de instituição credora, quando relacionada a operações com veículos automotores, sendo a adesão facultativa; ou III - outras atividades econômicas definidas pelo órgão máximo executivo de trânsito da União diretamente associadas às atividades previstas no art. 330 do Código de Trânsito Brasileiro."
- **Veículos novos: obrigatório em todo o país.** Texto: "§ 2º A adesão ao Renave por estabelecimentos que comercializem veículos novos é obrigatória em todo o território nacional, vedados o registro, o licenciamento e o emplacamento de veículos novos sem o prévio registro eletrônico de entrada em estoque no Renave." (art. 7º).
- **Veículos usados:** a obrigação resulta do art. 5º, III (registrar "todas as operações"), do art. 1º, § 1º ("único meio eletrônico admitido") e do art. 20, § 1º (consignação "vedada a realização de venda ou intermediação comercial sem o correspondente registro eletrônico prévio"). A imprensa especializada informa obrigatoriedade nacional a partir de 28/09/2026 (ver 4.4).
- **Certificado digital:** "Art. 10. Os estabelecimentos e as integradoras deverão possuir certificado digital e-CNPJ, padrão ICP-Brasil, válido ..." e "Art. 30. O acesso ao Renave será realizado mediante utilização de certificado digital e-CNPJ, padrão ICP-Brasil, válido, sendo vedado o acesso ao sistema com certificado expirado, suspenso ou revogado ...".
- **Sanções:** "Art. 25. A falta de escrituração dos livros de registro de entrada e saída de veículos, físicos ou eletrônicos, o atraso em sua realização, a fraude na escrituração ou a recusa de sua exibição à autoridade competente sujeitam o estabelecimento à aplicação da multa prevista para infração gravíssima, nos termos do art. 330, § 5º, do Código de Trânsito Brasileiro ...". Pelo § 2º, a integradora responde solidariamente se a infração decorrer de ação ou omissão dela. O art. 26 permite cancelar a adesão em caso de reincidência, com bloqueio de 180 dias para novo pedido.
- **Casos ainda não confirmados:**
  - Desmontes e oficinas de reforma estão no conceito de "estabelecimento" (art. 2º, I), mas a adesão é feita por CNAE de compra e venda (art. 7º). O art. 1º, § 4º remete à SENATRAN os procedimentos para veículos em reforma ou recuperação. Se a obrigação já alcança desmontes e oficinas na prática: não confirmado.
  - Leiloeiros não aparecem como obrigados na Res. 1.026. A Res. 1.027/2026, art. 37, III, diz apenas que transferências decorrentes de leilão serão "processadas preferencialmente por meio de transferência eletrônica".
  - Montadoras fazem o pré-cadastro do veículo novo no Renavam (art. 12). Não são "estabelecimento" para fins de estoque.

### 4.4 Estados, cronograma e situação em 2026

**Antes de 2026** (adesão estado a estado, sob a Res. 797/2020):
- Em outubro de 2024, a imprensa listava como estados que já implementavam o Renave de usados "Espírito Santo, Goiás, Mato Grosso do Sul, Mato Grosso, Santa Catarina, Sergipe e Paraná", e São Paulo tornando-o obrigatório desde 1º/10/2024 (Garagem360, 03/10/2024) — https://garagem360.com.br/renave-para-carros-usados-passa-a-ser-obrigatorio-em-sp-entenda. Outra fonte da mesma época cita também Pernambuco entre os nove estados aderentes (resultado de busca; não conferido no texto original).
- **SP:** a Portaria Normativa DETRAN-SP nº 32, de 12/08/2024 (DOE 13/08/2024), diz: "Art. 3º As pessoas jurídicas a que se refere o artigo 2º desta Portaria Normativa deverão realizar a escrituração de entrada e saída de veículos obrigatoriamente por intermédio do RENAVE." E: "Art. 7º Esta Portaria Normativa entra em vigor em 1º de outubro de 2024." — https://www.legisweb.com.br/legislacao/?id=470090
- **PR:** a Portaria nº 1091 – DP/DETRAN regulamenta o "RENAVE Usados" com vigência em 31/07/2023. O documento traz "Curitiba, 25 de julho de 2022" no fecho, mas foi assinado eletronicamente em 26/07/2023 — https://www.detran.pr.gov.br/sites/default/arquivos_restritos/files/documento/2023-07/PORT_1091_RENAVE_USADO.pdf
- **BA:** a Portaria DETRAN/BA nº 613, de 09/10/2024 (DOE 10/10/2024), entra em vigor 30 dias após a publicação. Texto: "Art. 3º Os estabelecimentos a que se refere o art. 2º desta Portaria devem realizar a escrituração de entrada e saída de veículos obrigatoriamente por intermédio do RENAVE." — https://www.legisweb.com.br/legislacao/?id=466173
- **ES:** citado pela SENATRAN como experiência de referência, com "100% das operações dentro do sistema" em 2023 e "quase 1.700 lojas cadastradas" (Portal do Trânsito, matéria de 14/08/2026) — https://www.portaldotransito.com.br/noticias/mobilidade-e-tecnologia/veiculos/novo-renave-promete-fechar-brechas-para-fraudes-na-compra-e-venda-de-veiculos/
- **CE (prioridade do usuário):** não localizei portaria do DETRAN-CE sobre o Renave. A situação do Ceará antes da Res. 1.026/2026 não está confirmada. Hoje a obrigação decorre diretamente da norma nacional.

**Nacionalização (2026):**
- Prazo de adequação: "Art. 33. Os estabelecimentos de que trata o art. 330 do Código de Trânsito Brasileiro, as integradoras e os órgãos ou entidades executivos de trânsito terão o prazo de 90 dias, contados da data de publicação desta Resolução, para se adequarem às suas disposições." O § 1º mantém válidos os credenciamentos e procedimentos anteriores durante esse prazo. O § 4º permite à SENATRAN prorrogar prazos.
- A imprensa registra a obrigatoriedade nacional desde 28/09/2026: "Desde hoje, dia 28 de setembro, o RENAVE (Registro Nacional de Veículos em Estoque) passa a ser obrigatório em todo o país" e "O RENAVE é uma obrigação das revendas, e não do comprador" (Portal do Trânsito, 28/09/2026) — https://www.portaldotransito.com.br/noticias/renave-torna-se-obrigatorio-nacionalmente-saiba-o-que-muda-para-lojistas-e-consumidores/amp/. No mesmo sentido: Vrum, 23/09/2026 — https://www.vrum.com.br/mercado/2026/09/7506809-renave-agora-e-obrigatorio-o-que-muda-na-compra-e-venda-de-carros.html; e NaPista, 19/09/2026, atualizada em 03/10/2026 — https://napista.com.br/radar/?p=2953
- **Circular SENATRAN nº 2/2026 (30/09/2026): implantação escalonada.** Ainda não está concluída na data desta pesquisa. Datas literais:
  - "Etapa B - Operação assistida para comercialização de veículos de propriedade de concessionárias e lojistas: entre 12 e 23 de outubro de 2026."
  - "Etapa C - Operação assistida para comercialização de veículos consignados em concessionárias e lojistas: entre 15 e 30 de outubro de 2026."
  - "Etapa D - ... com intermediação financeira ...: entre 30 de outubro e 10 de novembro de 2026."
  - "Etapa E - Controle de conformidade dos apontamentos das garantias relacionadas a veículos comercializados em desconformidade com a Resolução CONTRAN nº 1.026, de 2026: a partir de 20 de novembro de 2026."
  - "FASE 3 - Integração do Renave com processos de transferência e assinatura eletrônicas, conforme disposto na Resolução CONTRAN nº 1.027, de 17 de agosto de 2026." Etapas: "Integração das etapas de registro de intenção e de comunicação de venda: entre 9 e 13 de novembro de 2026"; "Integração das assinaturas eletrônicas ao Renave: entre 9 e 13 de novembro de 2026"; "Integração da etapa de transferência de propriedade do veículo ao Renave: entre 16 e 20 de novembro de 2026."

### 4.5 Como muda a venda e o ATPV-e quando o vendedor é revendedora

**(a) Revenda compra veículo usado (entrada em estoque).** Res. 1.026/2026:
- "Art. 14. Na compra de veículos usados, o estabelecimento deve: I - emitir a respectiva NF-e de compra; e II - assinar a Autorização para Transferência de Propriedade do Veículo em Meio Digital, conforme regulamentação específica."
- O art. 15 lista os dados mínimos do registro de compra, entre eles: "VIII - a data de reconhecimento de firma da assinatura do vendedor ou a data e hora da assinatura eletrônica avançada ou qualificada, nos termos do art. 123, § 4º, incisos I e II, do Código de Trânsito Brasileiro, da Lei nº 14.063, de 23 de setembro de 2020, e de regulamentação específica."
- "Art. 11. O registro eletrônico de estoque de entrada no Renave implica a anotação informativa de 'veículo em estoque' ou a restrição 'veículo em estoque vinculado' no cadastro do veículo no sistema Renavam." E: "§ 2º Os registros eletrônicos de estoque somente serão realizados em relação a veículos que não possuam restrições impeditivas ou débitos não liquidados."
- Termo de entrega para entrada em estoque: só é emitido "mediante assinatura eletrônica do proprietário" (art. 2º, XI).
- **Consequência para o agente:** quando uma PJ (não revendedora) vende seu veículo a uma revenda aderente ao Renave, a PJ vendedora ainda precisa assinar, como proprietária, a ATPV-e ou o termo de entrega. Por isso a revenda continua precisando conferir os poderes de quem assina pela PJ. Exemplo concreto do regime anterior (Res. 797/2020), na Portaria DETRAN-PR nº 1091/2023, para entrada de veículo de terceiros: "Se o vendedor é pessoa jurídica deverá anexar: - Comprovante de Poderes"; "Inserir a Procuração quando o CRV / ATPV-e for assinado por um terceiro"; "O estabelecimento deverá entregar ao DETRAN/PR o CRV ou ATPV-e devidamente preenchidos e com o reconhecimento de firma do vendedor." — https://www.detran.pr.gov.br/sites/default/arquivos_restritos/files/documento/2023-07/PORT_1091_RENAVE_USADO.pdf

**(b) Revenda vende veículo usado (saída de estoque).** Res. 1.026/2026, art. 18:
- O inciso II exige "a identificação do veículo, incluindo o número do Certificado de Registro de Veículo e o respectivo código de segurança".
- "§ 1º Para fins do registro eletrônico de estoque de saída, considera-se comprador a pessoa identificada como destinatária do veículo na operação de venda, independentemente da conclusão da transferência de propriedade."
- "§ 2º A formalização da operação de venda de veículo usado dar-se-á mediante a emissão da NF-e de saída, acompanhada da Autorização para Transferência de Propriedade do Veículo em Meio Digital assinada eletronicamente, nos termos de regulamentação específica."
- "§ 3º O proprietário que adquirir de estabelecimento veículo usado registrado no Renave deverá, para fins de circulação, providenciar a transferência de propriedade do veículo usado, por meio do registro, do licenciamento e do emplacamento, quando for o caso, junto ao órgão ou entidade executivo de trânsito competente, conforme regulamentação específica."
- "§ 4º A expedição de novo Certificado de Registro de Veículo em nome do comprador será informada ao estabelecimento vendedor por meio do Renave."
- **Comunicação de venda automática.** Res. CONTRAN 1.027/2026, art. 28, § 6º: "Para os processos envolvendo os estabelecimentos de que trata o art. 330 do Código de Trânsito Brasileiro, a comunicação de venda poderá ser realizada automaticamente mediante integração sistêmica entre o Renave e as plataformas de transferência e assinatura eletrônicas homologadas pelo órgão máximo executivo de trânsito da União, observados os requisitos e procedimentos por ele estabelecidos." — https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/resolucao10272026.pdf
- **Preferência pela transferência eletrônica.** Res. 1.027/2026, art. 37: "Serão processadas preferencialmente por meio de transferência eletrônica as transferências de propriedade decorrentes de: ... VI - comercialização de veículos em que participe estabelecimento aderente ao Renave."
- **Regime anterior (revogado), útil para entender práticas estaduais ainda em transição.** Res. 797/2020, art. 15, § 3º: "Com a emissão da NF-e de saída, fica dispensado o reconhecimento de firma por autenticidade por parte do estabelecimento vendedor e do proprietário comprador." Art. 14, § 1º: "Para o estabelecimento comprador, a assinatura da ATPV deve ser realizada por meio de certificado digital nos padrões estabelecidos pelo governo brasileiro." Art. 14, § 2º: "Para o vendedor, a assinatura da ATPV pode ser realizada por meio de assinatura eletrônica nos padrões estabelecidos pelo governo brasileiro ou por reconhecimento de firma em cartório ou por outro meio oficialmente válido."
  - O DETRAN-PR (Portaria 1091/2023) dizia: "para o processo de transferência de propriedade de veículos oriundos de estabelecimentos credenciados, fica dispensado a assinatura e o reconhecimento de firma no ATPV-e pelo comprador e vendedor, apresentando nota fiscal de venda junto com o ATPV-e."
  - O DETRAN-BA (Portaria 613/2024, art. 8º, § 2º) dizia: "Com a emissão da NF-e de saída, fica dispensado o reconhecimento de firma por autenticidade por parte do estabelecimento vendedor e do proprietário comprador no ATPV-e."
  - Atenção: essas portarias estaduais se apoiam na Res. 797/2020, hoje revogada. Se já foram adaptadas às Res. 1.026 e 1.027/2026 (que exigem ATPV-e assinada eletronicamente): não confirmado.

**(c) Consignação (revenda vende veículo de terceiro, inclusive de PJ).** Res. 1.026/2026, art. 20:
- "§ 1º A consignação de veículo para fins de comercialização por estabelecimento integra a escrituração obrigatória prevista no art. 330 do Código de Trânsito Brasileiro, e deverá, necessariamente, ser formalizada por meio de contrato eletrônico registrado no Renave, vedada a realização de venda ou intermediação comercial sem o correspondente registro eletrônico prévio."
- "§ 2º O contrato eletrônico de consignação deverá ser firmado digitalmente pelo estabelecimento e pelo consignante proprietário por meio de seu sistema de integração, observadas as seguintes regras: I - o estabelecimento deverá utilizar certificado digital e-CNPJ válido; II - o consignante, quando pessoa jurídica, deverá utilizar certificado digital e-CNPJ válido; e III - o consignante, quando pessoa física, poderá utilizar assinatura eletrônica qualificada ou avançada, nos termos do art. 123, § 4º, incisos I e II, do Código de Trânsito Brasileiro, da Lei nº 14.063, de 23 de setembro de 2020 e de regulamentação específica."
- "§ 6º A transferência de propriedade do veículo consignado somente ocorrerá após a assinatura da Autorização para Transferência de Propriedade do Veículo em Meio Digital, conforme regulamentação específica, pelo proprietário consignante."
- "§ 7º Caso o proprietário consignante não assine a Autorização para Transferência de Propriedade do Veículo em Meio Digital no prazo de 30 dias, ou cancele o contrato eletrônico de consignação, a venda será cancelada ..."
- Pelo caput, o estabelecimento é consignatário "até a saída do veículo por venda ou distrato contratual, respondendo pelas infrações de trânsito cometidas nesse período".

**(d) Transferência entre revendas.** Art. 19: só entre estabelecimentos aderentes. O registro se conclui após confirmação do comprador. A entrada em nome do comprador é "exclusivamente em meio digital" e, depois disso, "deverá ser providenciada a correspondente transferência de propriedade" (§ 3º).

**(e) Financiamento.** O art. 34 altera a Res. 807/2020 (art. 5º, § 5º): "O apontamento não poderá ser realizado quando: I - o beneficiário do financiamento for estabelecimento de que trata o art. 330 do Código de Trânsito Brasileiro; e II - o veículo, novo ou usado, objeto do financiamento não estiver registrado no estoque do estabelecimento no Registro Nacional de Veículos em Estoque - Renave ...".

**(f) O Renave não substitui a transferência.** Ver art. 1º, § 2º, acima. A imprensa repete: "o RENAVE não substitui a transferência de propriedade, que continua sendo necessária após a compra" (Portal do Trânsito, 28/09/2026).

### 4.6 Regras codificáveis (Renave)

- **R4.1** Se o vendedor tem CNAE principal de compra e venda de veículos e o veículo está "em estoque" no Renavam, o fluxo é o do Renave: NF-e de saída mais ATPV-e assinada eletronicamente (Res. 1.026, art. 18, § 2º). Nesse caso, o agente deve pedir o e-CNPJ da revenda e não o reconhecimento de firma do representante.
- **R4.2** Acesso ao Renave e assinatura do contrato de consignação pela revenda exigem e-CNPJ ICP-Brasil válido. Certificado expirado, suspenso ou revogado bloqueia o acesso (arts. 10, 20, § 2º, I e 30).
- **R4.3** Consignante PJ assina o contrato de consignação somente com e-CNPJ (art. 20, § 2º, II). Consignante PF pode usar assinatura avançada (gov.br) ou qualificada.
- **R4.4** Veículo consignado: a propriedade continua com o consignante, que deve assinar a ATPV-e em até 30 dias, sob pena de cancelamento da venda (art. 20, §§ 6º e 7º). Para o agente, quem tem de ter poderes é o representante do consignante, e não a revenda.
- **R4.5** Venda de PJ comum para revenda (entrada em estoque): continua exigindo assinatura do proprietário PJ (ATPV-e ou termo de entrega) e comprovação de poderes do signatário. A Res. 1.027, art. 28, § 7º, exige "comprovação eletrônica dos poderes do signatário" (ver nota cruzada).
- **R4.6** Registro de estoque só para veículo sem restrições impeditivas ou débitos (art. 11, § 2º). Checar antes.
- **R4.7** O Renave não transfere propriedade: o comprador final ainda faz a transferência (art. 18, § 3º). A emissão do novo CRV é informada à revenda via Renave (§ 4º).
- **R4.8** Datas: obrigação nacional desde 28/09/2026 (fim dos 90 dias do art. 33). Integração com assinatura e transferência eletrônica prevista para 09 a 20/11/2026 (Circular SENATRAN 2/2026). Até lá, procedimentos estaduais anteriores podem coexistir (art. 33, § 1º, durante o prazo de adequação; depois disso, não confirmado).
- **R4.9** Portarias estaduais baseadas na Res. 797/2020 (dispensa de firma "com a NF-e de saída", ATPV em papel com firma do vendedor) podem estar desatualizadas. Tratar como "verificar vigência".

---

## 5. Fraude e risco (casos mais úteis)

### 5.1 Comunicação de venda e responsabilidade do vendedor (art. 134 CTB)

- **Súmula 132/STJ** (aprovada em 26/04/1995, DJ 05/05/1995): "A ausência de registro da transferência não implica a responsabilidade do antigo proprietário por dano resultante de acidente que envolva o veículo alienado." — https://arquivocidadao.stj.jus.br/index.php/sumula-132
- **Súmula 585/STJ** (aprovada em 14/12/2016, DJe 01/02/2017): "A responsabilidade solidária do ex-proprietário, prevista no art. 134 do Código de Trânsito Brasileiro CTB, não abrange o IPVA incidente sobre o veículo automotor, no que se refere ao período posterior à sua alienação." — https://arquivocidadao.stj.jus.br/index.php/sumula-585
- **STJ, AREsp 369.593 (1ª Turma, Rel. Min. Benedito Gonçalves; notícia de 16/06/2021):** a solidariedade do ex-proprietário por multas não é afastada só pela prova da venda. Sem a comunicação, ele responde pelas infrações posteriores. A mitigação vale apenas para o IPVA — https://cnbsp.org.br/2021/06/16/stj-antigo-dono-que-nao-comunicou-venda-de-veiculo-responde-solidariamente-por-infracoes/
- **Regra para o agente:** a PJ vendedora deve garantir a comunicação de venda. Na ATPV-e, ela é gerada automaticamente após as duas assinaturas (Res. 1.027, art. 28, § 4º). No ATPV em papel, há os prazos de 30/60 dias (Res. 1.027, art. 26, §§ 2º a 4º).

### 5.2 Responsabilidade por reconhecimento de firma falso (cartório e Estado)

- **STF, Tema 777 (RE 842.846/SC, Rel. Min. Luiz Fux, Plenário, j. 27/02/2019), tese:** "O Estado responde, objetivamente, pelos atos dos tabeliães e registradores oficiais que, no exercício de suas funções, causem dano a terceiros, assentado o dever de regresso contra o responsável, nos casos de dolo ou culpa, sob pena de improbidade administrativa."
  - Fontes: CNB-SP (artigo de Kümpel e Sóller, 07/10/2025) — https://cnbsp.org.br/2025/10/07/artigo-responsabilidade-civil-dos-notarios-e-registradores-apos-o-tema-777-por-vitor-frederico-kumpel-e-natalia-soller/ — e https://tesesesumulas.com.br/newsletter/37-direito-de-regresso. O portal do STF respondeu 403, então o texto foi conferido em fontes secundárias concordantes.
- **Lei 8.935/1994, art. 22 (redação da Lei 13.286/2016):** "Os notários e oficiais de registro são civilmente responsáveis por todos os prejuízos que causarem a terceiros, por culpa ou dolo, pessoalmente, pelos substitutos que designarem ou escreventes que autorizarem, assegurado o direito de regresso." Parágrafo único: "Prescreve em três anos a pretensão de reparação civil, contado o prazo da data de lavratura do ato registral ou notarial." — https://www.planalto.gov.br/ccivil_03/leis/l8935.htm
  - Redações anteriores, que aparecem tachadas no planalto: a original ("responderão pelos danos que eles e seus prepostos causem a terceiros ...") e a da Lei 13.137/2015.
- **Res. CONTRAN 1.027/2026, art. 26, § 8º** (comunicação de venda eletrônica feita pelo tabelionato): "O Tabelionato de Notas e a pessoa jurídica responsável pela plataforma de transferência eletrônica responderão, no âmbito de suas respectivas atuações, pelas informações e pelos registros relacionados à comunicação de venda eletrônica ...".

### 5.3 DETRAN responde por transferência com procuração revogada ou sem poderes e firma falsificada

- **TJDFT, 4ª Vara da Fazenda Pública do DF, proc. 0702589-63.2021.8.07.0018 (sentença noticiada em 01/02/2024; cabia recurso).**
  - Fatos: o ex-companheiro transferiu o veículo da autora usando procuração que "excluía a venda" dos seus poderes e que havia sido revogada, com falsificação da assinatura e do selo cartorial (laudo pericial). Pediu 2ª via do documento de transferência.
  - Resultado: nulidade da transferência, retificação do registro e R$ 10 mil de dano moral contra o DETRAN-DF. Fundamento: o DETRAN "falhou na adoção dos procedimentos e precauções" para conferir a validade da procuração e das assinaturas. A defesa de que a procuração atribuía ao procurador os ônus do ato foi rejeitada.
  - Fonte: https://www.lex.com.br/detran-df-deve-indenizar-mulher-vitima-de-fraude-em-transferencia-de-veiculo/
- **TJDFT, 2º Juizado Especial da Fazenda Pública (notícia de 20/01/2025; nº do processo não informado na fonte):** veículo registrado em nome de terceiro com assinaturas falsificadas. Fundamento: "os riscos da atividade de conferência de documentação devem ser imputados ao órgão de trânsito, por constituir fortuito interno". DETRAN-DF e DF condenados a R$ 5 mil — https://www.lex.com.br/df-e-detran-sao-condenados-por-transferencia-fraudulenta-de-veiculo/

### 5.4 Representação de PJ: teoria da aparência e excesso de poderes (STJ)

- **REsp 887.277/SC (4ª Turma, Rel. Min. Luis Felipe Salomão; notícia de 19/11/2010).** Aditivo assinado por gerente sem poderes estatutários foi considerado válido. Ele assinou "na sede da Portobello", "no exercício ordinário de suas atribuições, ostentando a nítida aparência de que representava a empresa", e "não há qualquer indício de má-fé" da contraparte — https://www2.oabrs.org.br/jornalDaOrdem/empresa-nao-consegue-invalidar-aditivo-contratual-assinado-por-seu-funcionario/20080
  - Uso para o agente: a aparência protege o terceiro de boa-fé em atos rotineiros praticados na sede. Isso não serve de base para um parecer favorável. O agente deve exigir prova formal de poderes. A aparência é argumento de litígio, não de compliance.
- **REsp 704.546/DF (4ª Turma, Rel. Min. Luis Felipe Salomão, j. 01/06/2010, DJe 08/06/2010).** A teoria ultra vires foi afastada porque as garantias prestadas por sócio em excesso dos limites contratuais "retornaram, direta ou indiretamente, em proveito dos demais sócios da sociedade fiadora". Prevaleceram a boa-fé e a aparência — fonte secundária: https://jus.com.br/artigos/40360/teoria-ultra-vires-societatis-uma-analise-na-perspectiva-do-atual-entendimento-doutrinario-e-jurisprudencial
  - Contexto: a Lei 14.195/2021 revogou o parágrafo único do art. 1.015 do CC, que tinha as hipóteses de oponibilidade do excesso a terceiros (texto literal na Seção 3).

### 5.5 Alteração contratual ainda não arquivada × procuração ou alienação (caso Empi, STJ)

- **STJ, 3ª Turma, Rel. Min. Nancy Andrighi (notícia de 17/01/2014; nº do REsp não confirmado).**
  - Fatos: a sociedade outorgou procuração para dar seis imóveis em pagamento a ex-sócio. A procuração foi assinada pelos dois sócios em 04/06/1990 e lavrada em 20/06/1990. No mesmo 04/06/1990 foi assinada alteração contratual que passou a exigir três administradores para alienar bens. A alteração foi levada à Junta em 28/06/1990, dentro de 30 dias.
  - Tese: a alteração arquivada em até 30 dias retroage à data da assinatura (então art. 39 da Lei 4.726/65; regra hoje equivalente ao art. 36 da Lei 8.934/94, ver Seção 3). Logo, "no momento da lavratura da procuração, a sociedade não era mais integrada pelos mesmos sócios que a outorgaram".
  - O vício foi qualificado como "de presentação (e não propriamente de representação)".
  - O TJBA havia preservado as alienações a terceiros adquirentes de boa-fé.
  - Fonte: https://portaldori.com.br/2014/01/20/efeito-retroativo-de-alteracao-em-contrato-social-invalida-procuracao-que-permitiu-alienacao-de-imoveis/
  - Regra para o agente: existe uma **janela de risco de 30 dias**. Uma alteração assinada e ainda não arquivada pode retroagir e retirar os poderes de quem assina hoje. Certidão simplificada recente e pergunta expressa sobre "alterações assinadas e não arquivadas" mitigam o risco.

### 5.6 Fraudes operacionais recentes com documentos de transferência

- **DETRAN-GO, "Operação Ousadia" (publicada em 22/08/2023).**
  - Fatos: dono de revenda e assistente administrativa presos ao tentar transferir veículo com procuração adulterada. "A procuração ... era adulterada"; "possuía selo 'adulterado/falsificado'"; "O reconhecimento de firma da assinatura do proprietário do veículo no documento também tinha sido falsificado."
  - Como foi detectado: o servidor consultou o selo no TJ e a firma no cartório.
  - Fonte: https://goias.gov.br/detran/operacao-ousadia-duas-pessoas-sao-presas-por-documentos-falsos/
- **PCPR (04/03/2023).** Mercado paralelo de senhas de despachantes credenciados, usadas para transferências fraudulentas para "laranjas". Prejuízo de "mais de R$ 3,5 milhões"; 10 presos — https://www.portaldotransito.com.br/noticias/mobilidade-e-tecnologia/veiculos/policiais-prendem-dez-pessoas-em-esquema-que-burlava-sistema-de-transferencias-de-veiculos/
- **Polícias Civis de RS, SC e RJ (notícia de 07/05/2025).** Um integrante "invadia a conta Gov.br do proprietário original do veículo para ter acesso à documentação veicular". A vítima, compradora de veículo clonado, recebia "normalmente o documento de Autorização para Transferência de Propriedade de Veículo (ATPV-e)". 17 presos; cerca de R$ 100 mil por fraude — https://www.baguete.com.br/noticias/grupo-invade-contas-gov-br-para-vender-veiculos-clonados
- **O Povo (CE), coluna de Boris Feldman (11/02/2025).** Quadrilha usa dados de veículos em pátio de concessionária para emitir NF falsas e "APTVe" em outros estados e obter falso financiamento. A coluna diz que a digitalização "extremamente facilitou" a fraude — https://mais.opovo.com.br/colunistas/boris-feldman/2025/02/11/dut-eletronico-modernizacao-trouxe-uma-fraude-a-reboque.html
- **Canaltech (19/12/2025).** Alerta de especialistas sobre a transferência digital da Lei 15.153/2025: "A descentralização pode deixar a população mais vulnerável a fraudes e falsificações" — https://canaltech.com.br/carros/transferencia-digital-de-veiculos-e-aprovada-mas-acende-alerta-sobre-golpes/

### 5.7 Lições codificáveis (risco)

- **F1** Procuração revogada, com poderes que excluem a venda ou com selo ou firma falsificados é a causa típica de nulidade da transferência. O agente deve:
  - checar se os poderes cobrem expressamente "alienar/vender/transferir" (art. 661, § 1º, CC);
  - conferir o selo de fiscalização e a autenticidade junto ao TJ ou cartório;
  - no caso de procuração pública, consultar a CENSEC/CEP (ver 6.14).
- **F2** Alteração contratual assinada há até 30 dias pode retroagir (Lei 8.934/94, art. 36). O agente deve exigir declaração de inexistência de alteração pendente e certidão recente.
- **F3** Conta gov.br pode ser invadida (assinatura avançada). Em operações de PJ, preferir assinatura qualificada (e-CNPJ/e-CPF ICP-Brasil) e validar os poderes do signatário (Res. 1.027, art. 28, § 7º).
- **F4** A teoria da aparência (REsp 887.277) e a boa-fé (REsp 704.546) protegem terceiros em litígio, mas não substituem a verificação formal de poderes no parecer.
- **F5** Garantir a comunicação de venda (Súmula 585 e AREsp 369.593): sem ela, a PJ vendedora segue solidária pelas multas.

---

## 6. Mercado: análise de poderes, leitura de contrato social com IA, KYB, consulta a Juntas

A confirmação se cada empresa faz especificamente "análise de poderes de representação" com IA foi feita só no próprio site ou em notícia. Quando não houve confirmação, está indicado.

| # | Produto/serviço | O que comprovadamente oferece | Análise de poderes com IA? |
|---|---|---|---|
| 6.1 | **Aarin** (techfin do grupo Bradesco) | Agentes de IA (Amazon Bedrock) no onboarding PJ processam "contratos sociais, alterações societárias, procurações", extraem dados, validam cláusulas e detectam inconsistências; até −90% no tempo de análise (notícia de 15/09/2026) — https://www.letsmoney.com.br/noticias/aarin-onboarding-90-agentes-ia/ | **Sim (uso interno)**; não é produto vendido a terceiros (não confirmado) |
| 6.2 | **Kronoos** | "Transformamos dados, IA e evidências em decisões auditáveis para KYC, KYB, Background Check, Due Diligence e PLD/FT" — https://www.kronoos.com/ | KYB com IA sim; poderes: não confirmado |
| 6.3 | **Certta (ex-CAF – Combate à Fraude)** | Site diz "Caf is now Certta"; "Caf KYB" com "government databases, PEP and sanctions lists" — https://www.caf.io/ e https://www.certta.ai/resource/caf-kyb-a-global-solution-for-verifying-business-clients | KYB sim; poderes: não confirmado |
| 6.4 | **idwall** | "Verificação de documentos & Background Check" via API, com consulta a dados públicos — https://idwall.co/ | KYB e poderes: não confirmado (a página /kyb/ retorna "Página não encontrada") |
| 6.5 | **BigDataCorp** | Dados de empresas, "além de dados exclusivos, como faturamento presumido e relacionamento dos sócios"; verticais "PLD, KYC e Compliance" — https://bigdatacorp.com.br/ | Poderes: não confirmado |
| 6.6 | **Neoway (B3)** | "Diligências de PF e PJ automatizadas (KYC, KYE, KYP e KYS)" com IA e analytics — https://www.neoway.com.br/ | Poderes: não confirmado |
| 6.7 | **Serasa Experian** | Consulta CNPJ, autenticação e prevenção à fraude, soluções de cadastro/KYC — https://www.serasaexperian.com.br/ e https://www.serasaexperian.com.br/solucoes/cadastro-kyc/ | KYB PJ com poderes: não confirmado |
| 6.8 | **Direct Data** | "Acesse +300 fontes de dados públicos com APIs ... para risco, crédito e compliance" (CNPJ, CPF, Sintegra) — https://www.directd.com.br/ | Poderes: não confirmado |
| 6.9 | **Infosimples** | API "Junta Comercial / SP / Certidão Simplificada" (JUCESP): consulta por CPF/NIRE/nome e retorno de dados como capital, endereço, participantes e filiais — https://infosimples.com/consultas/junta-comercial-sp-simplifica/ | Não faz análise de poderes (fornece o dado). Outras Juntas na mesma página: não confirmado |
| 6.10 | **Linkana** | SRM de fornecedores: "A Linkana lê e valida os documentos por você e aprova o fornecedor conforme a categoria e a criticidade de fornecimento" — https://www.linkana.com/ | Poderes: não confirmado |
| 6.11 | **MonitorCNPJ** (Codecortex Tecnologia) | QSA, beneficiário final, monitoramento de mudanças societárias, API — https://monitorcnpj.com.br/artigos/kyb-kyc/ | Leitura de contrato social ou poderes: não confirmado |
| 6.12 | **Projuris Empresas** | Gestão de procurações: monitoramento, "alertas automáticos para renovação", relatórios de "quais procurações vão vencer nos próximos seis meses" — https://www.projuris.com.br/blog/o-que-e-procuracao/ | Controle de vencimento sim; IA para poderes: não confirmado |
| 6.13 | **Incode eKYB Brazil** (estrangeira) | Usa a "Brazilian government CNPJ database"; documentação diz "Directors are not currently supported for Brazil" — https://devhub.omnihub.incode.com/general-reference/ekyb-verification-reference-brazil/ | Não; mostra a lacuna de mercado |
| 6.14 | **Busca CEP / CENSEC** (Colégio Notarial do Brasil; fonte oficial, não é produto comercial) | Consulta pública da Central de Escrituras e Procurações desde 14/07/2025 (Provimento CN-CNJ nº 194/2025): mostra "nome do Tabelionato, número do livro, folhas do registro e o tipo do ato"; exige certificado ICP-Brasil ou notarizado — https://www.irib.org.br/noticias/detalhes/cnb-abre-consulta-publica-para-informacoes-de-milhoes-de-escrituras-e-procuracoes | Fonte para validar procuração pública. Se a consulta pública mostra revogação: não confirmado |
| 6.15 | **JUCEG** (Junta Comercial de Goiás; projeto público) | Ferramenta de IA que identifica inconsistências entre contrato social, Ficha Cadastral (FC) e DBE (sem data na página) — https://goias.gov.br/juceg/?p=39212 | Leitura de contrato social com IA no registro; não analisa poderes para terceiros |

Sinal de demanda: o **desafio Sebrae/PR IAS25CF01 (2026)** busca solução que verifique "autoridade do signatário com base em dados confiáveis (ex.: poderes de representação, procurações, cargos)", integrada a assinatura eletrônica e com alertas. O texto do desafio diz que hoje o processo depende de "validações manuais para conferir a atribuição de poderes para firmar os compromissos" — https://sebraepr.com.br/?p=292208

Conclusão de mercado: não encontrei produto brasileiro comercial que venda, de forma explícita e documentada, "decisão de quem pode assinar o ATPV-e" a partir de contrato social, procurações e substabelecimentos. O mais próximo é uso interno de banco (Aarin). Bureaus e KYB fornecem QSA e dados de Junta, mas a interpretação de cláusulas de administração e procurações não aparece documentada em nenhum deles.

> Nota de consolidação: os trechos sobre a Res. CONTRAN 1.027/2026 e a Lei 15.153/2025 estão nas Seções 1.1.3 e 3.0/3.7. Ponto que estava em aberto nesta seção e foi conferido no Planalto: no § 4º do art. 123 do CTB, o veto ao **inciso III** foi derrubado. O inciso foi promulgado em 09/12/2025 (DOU 10/12/2025). O **inciso IV** continua vetado. Fontes: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/L15153.htm e https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/Msg/Vep/VEP-812-25.htm

---

## 7. Doutrina e prática

### 7.0 Resumo da Seção 7

- (a) Contrato com dois administradores que não diz se atuam isolada ou conjuntamente: prevalece a atuação isolada (art. 1.013, aplicado supletivamente). Não achei precedente do STJ específico.
- (b) A procuração da PJ sobrevive à saída do administrador que a assinou. O STJ decidiu isso para o caso de morte do sócio signatário (AgInt no REsp 1.997.964/SC, 2024).
- (c) Prazo de mandato vencido sem recondução: o exercício do cargo cessa (art. 1.063). Na S.A., o mandato se estende até a posse do sucessor (art. 150, §4º, LSA). Na Ltda, isso só vale por regência supletiva da LSA, e a posição é controvertida (jurisprudência não confirmada).
- (d) Venda de veículo por quem é administrador: para revendedora, é o próprio objeto social; para bem do ativo imobilizado, cabe nos poderes de gestão do art. 1.015 se o contrato for omisso (há voz notarial mais cautelosa). Para mandatário, a venda sempre exige poder especial. Na S.A. com conselho de administração, a alienação de ativo não circulante depende do conselho, salvo disposição estatutária em contrário (art. 142, VIII, LSA).
- (e) Restrição contratual limitada a "bens imóveis" não alcança veículos, que são bens móveis (arts. 79 e 82 do CC).


### 7.1 (a) Dois administradores, sem regra sobre atuação isolada ou conjunta

- **[N]** Arts. 1.013, 1.014, 1.053 e 1.060 do CC (Seção 3). A Ltda aplica supletivamente as regras da sociedade simples (art. 1.053). O art. 1.013 manda que a administração, "nada dispondo o contrato social, compete separadamente a cada um". Atuação conjunta (art. 1.014) só existe quando há "atos de competência conjunta" previstos.
- **[D] Posição dominante:** se o contrato é omisso, cada administrador atua isoladamente (administração disjuntiva). Os demais podem impugnar a operação (art. 1.013, §1º).
  - Fonte educacional (Trilhante), em paráfrase: quando omisso o contrato, a lei determina que os poderes serão exercidos de forma isolada; e "No caso de o poder ser exercido conjuntamente, a ação a ser tomada precisa da anuência de todos os administradores." https://trilhante.com.br/trilha/direito-empresarial/curso/sociedade-limitada/aula/administracao-da-sociedade-1
  - O Manual de Registro de Ltda do DREI (item 4.5) **não trata** do ponto: só diz que "A administração da sociedade será exercida por uma ou mais pessoas designadas no contrato ou em ato separado". Precedente do STJ específico: **não localizado**.
- **[N/P] Indícios de como os DETRANs tratam o tema:**
  - PR, Portaria 661/2025, art. 3º, §2º: se o contrato exigir mais de uma assinatura para disposição patrimonial, cada representante deve assinar com seu e-CPF. Ou seja, o DETRAN respeita a exigência de assinatura conjunta quando ela existe.
  - PR, Portaria 660/2025, art. 6º: para vários procuradores no mesmo instrumento, aplica o art. 672 do CC (cada um pode agir, salvo se declarados conjuntos).
- **Regra codificável:**
  - Contrato com ≥2 administradores e sem cláusula de forma → `isolada = true`, com confiança média e registro do fundamento (art. 1.013 c/c art. 1.053).
  - Marcar revisão humana quando o texto for ambíguo, por exemplo: "em conjunto ou isoladamente", "sempre em conjunto", "dois a dois", "um sócio e um diretor", alçadas por valor ou por tipo de ato, ou exigência de "assinatura de dois administradores para alienação de bens".

### 7.2 (b) A procuração da PJ continua válida se o administrador que a assinou sai da administração?

- **[J] STJ, AgInt no REsp 1.997.964/SC (2ª Turma, rel. Min. Afrânio Vilela, j. 12/11/2024, DJe 18/11/2024).**
  - Tese: "A personalidade jurídica da sociedade empresária é distinta da personalidade jurídica de seus sócios e representantes legais. Portanto, a procuração outorgada pela pessoa jurídica não perde validade com o falecimento do sócio ou representante que assinou o mandato."
  - O mandato vale "até que ocorra sua revogação, renúncia, extinção da pessoa jurídica ou mudança de estado que impeça a atuação do mandatário".
  - Fundamentos: art. 6º, §1º, da LINDB e art. 682, I a IV, do CC.

  Fontes: https://informativos.trilhante.com.br/julgados/stj-agint-no-resp-1997964-sc e https://cnbsp.org.br/2024/12/12/migalhas-stj-assegura-validade-de-procuracao-assinada-por-socio-falecido/
  - Aplicação à saída do administrador (inferência por argumento *a fortiori*): se nem a morte do signatário extingue o mandato, a simples saída dele também não. A outorgante é a PJ, e o art. 682 não lista essa hipótese. A nova administração pode revogar o mandato.
- **[J] DREI, Decisão de Recurso SEI 14021.079493/2025-33 (assinada em 23/02/2026), caso JUCEG.** Adota o art. 686 do CC: a revogação "comunicada apenas ao mandatário não é oponível a terceiros de boa-fé". Admite a ratificação com efeito retroativo (art. 662, parágrafo único).

  Fonte: https://www.gov.br/empresas-e-negocios/pt-br/drei/pareceres-drei/arquivos/2026/recurso-sei-14021-079493-2025-33/@@download/file
- **[N]** Arts. 686 e 689 do CC (Seção 3) protegem o terceiro de boa-fé. O CNN, art. 150, obriga o notário a "verificar a atualidade dos poderes".
- **Prática de bancos e cartórios de exigir "ratificação" da procuração pela nova administração:** **não confirmada** em norma. Parece ser política interna de risco.
- **Regra codificável:**
  - Procuração da PJ válida se: (i) assinada por quem tinha poderes na data da outorga; (ii) sem revogação conhecida, arquivada ou anotada; (iii) dentro do prazo, se houver; (iv) PJ não extinta.
  - A saída do administrador signatário → **não** invalida, mas gera alerta e recomendação de certidão atualizada (se pública) ou confirmação pela administração atual.

### 7.3 (c) Administrador de Ltda com prazo de mandato vencido, sem recondução

- **[N]** Art. 1.063, caput e §2º, do CC (o exercício cessa ao fim do prazo, se não houver recondução; a cessação deve ser averbada em 10 dias). Arts. 1.151 e 1.154 (Seção 3). Pelo art. 1.154, parágrafo único, o terceiro não pode alegar ignorância de ato registrado. Se o prazo consta do contrato arquivado, o término do mandato é público.
- **[N/D] DREI, Manual de Ltda, item 4.5:**
  > "Não há obrigatoriedade de previsão de prazo do mandato de administrador nomeado no contrato, que, não estando previsto, entender-se-á ser de prazo indeterminado."

  Fonte: o Anexo IV citado em 2.6.
  - Atenção: o mesmo item 4.5.2 ainda menciona quórum de "unanimidade" ou "dois terços" para nomear administrador não sócio. Esse texto parece **desatualizado** em relação à Lei 14.451/2022. Prevalece o art. 1.061 vigente (Seção 3).
- **[N] LSA, art. 150, §4º (só S.A.):**
  > "O prazo de gestão do conselho de administração ou da diretoria se estende até a investidura dos novos administradores eleitos."

  Fonte: https://www.planalto.gov.br/ccivil_03/leis/l6404consol.htm
  - Aplicação à Ltda: em tese, só se o contrato adotar a regência supletiva da LSA (art. 1.053, parágrafo único) ou tiver cláusula própria de prorrogação. Doutrina ou jurisprudência que confirme ou rejeite a analogia: **não localizada**, portanto não confirmada.
- **[D] Teoria da aparência.** Enunciado 11 da I Jornada de Direito Comercial (CJF):
  > "A regra do art. 1.015, parágrafo único, do Código Civil deve ser aplicada à luz da teoria da aparência e do primado da boa-fé objetiva, de modo a prestigiar a segurança do tráfego negocial. As sociedades se obrigam perante terceiros de boa-fé."

  Fonte: https://www.dpd.ufv.br/wp-content/uploads/2019/08/I-Jornada-de-Direito-Comercial.pdf
  - O enunciado é anterior à revogação do art. 1.015, parágrafo único, pela Lei 14.195/2021. Para a doutrina posterior à revogação, ver 7.4.
  - Contrapeso: como o prazo do mandato está registrado, a aparência de poderes de quem tem mandato vencido é fraca diante do art. 1.154, parágrafo único.
- **Regra codificável:**
  - Prazo de mandato vencido e sem recondução arquivada → `poder = AUSENTE`, com bloqueio e revisão humana.
  - Exceções que levam à revisão em vez de bloqueio: (i) cláusula contratual de permanência "até a posse do sucessor"; (ii) regência supletiva pela LSA; (iii) S.A. (aplicar art. 150, §4º → poder mantido até a investidura dos novos administradores).
  - Conferir também na certidão simplificada o campo "Observações", onde aparece "instrumento de renúncia de administrador" (IN DREI 81/2020, art. 96, §1º, "c", item 6, na redação da IN DREI 01/2024): https://www.gov.br/empresas-e-negocios/pt-br/drei/legislacao/instrucoes-normativas/arquivos-instrucoes-normativas-em-vigor/in-drei-81_atualizada_link.pdf
  - A IN DREI 81/2020 (art. 96) **não fixa prazo de validade** da certidão simplificada.

### 7.4 (d) Venda de veículo do ativo imobilizado ou do estoque de revenda: é ato de gestão ordinária?

- **[N]** Art. 1.015, caput, do CC (Seção 3). No silêncio do contrato, os administradores praticam "todos os atos pertinentes à gestão". Só a venda ou oneração de **imóveis** que não sejam objeto social depende da maioria dos sócios. O parágrafo único foi revogado pela Lei 14.195/2021.
- **[D] Enunciado 219 da III Jornada de Direito Civil (CJF), redigido sob o parágrafo único hoje revogado:**
  > "Está positivada a teoria ultra vires no Direito brasileiro, com as seguintes ressalvas: (a) o ato ultra vires não produz efeito apenas em relação à sociedade; (b) sem embargo, a sociedade poderá, por meio de seu órgão deliberativo, ratificá-lo; (c) o Código Civil amenizou o rigor da teoria ultra vires, admitindo os poderes implícitos dos administradores para realizar negócios acessórios ou conexos ao objeto social, os quais não constituem operações evidentemente estranhas aos negócios da sociedade; (d) não se aplica o art. 1.015 às sociedades por ações, em virtude da existência de regra especial de responsabilidade dos administradores (art. 158, II, Lei n. 6.404/76)."

  Fonte: https://www.cjf.jus.br/enunciados/enunciado/430
- **[D] Depois da Lei 14.195/2021.** Marco Aurélio Cunha (Capital Aberto, 29/11/2021) vê na revogação "uma escolha legislativa de preferência à proteção do ambiente negocial em detrimento da proteção à empresa individualmente". Segundo ele, atuar fora do objeto seria "um problema de representação da pessoa jurídica (uma questão com efeito interna corporis) e não de capacidade desta".

  Fonte: https://capitalaberto.com.br/artigos/efeitos-da-revogacao-do-paragrafo-unico-do-artigo-1-015-do-codigo-civil/
- **[D] Visão notarial cautelosa: José Flávio Bueno Fischer (2014, antes da Lei 14.195/2021).**
  > "muito embora o texto legal em exame se refira expressa e exclusivamente a 'bens imóveis', quando a venda ou oneração de bens móveis não constitui objeto social ou ato de gestão, a análise dos dispositivos contratuais de administração deve se pautar por critérios semelhantes àqueles aplicados aos imóveis"

  E um exemplo:
  > "Para uma empresa, por exemplo, que comercializa vestuário e acessórios, cujo contrato seja silente em relação à venda ou oneração de bens, a venda de um imóvel ou mesmo de um veículo excede os meros poderes de gestão, não constituindo objeto social."

  Fonte: https://portaldori.com.br/2014/12/30/artigo-artigo-1-015-codigo-civil-e-venda-de-bens-por-jose-flavio-bueno-fischer/
- **[N] Ativo permanente: exigência de CND.** Lei 8.212/1991, art. 47, I, "c", exige CND:
  > "na alienação ou oneração, a qualquer título, de bem móvel de valor superior a Cr$ 2.500.000,00 (dois milhões e quinhentos mil cruzeiros) incorporado ao ativo permanente da empresa"

  Fonte: https://www.planalto.gov.br/ccivil_03/leis/l8212cons.htm
  - O valor é atualizado por portaria interministerial. O DETRAN-MG cita **R$ 87.493,73** pela "portaria interministerial MPS/MF nº 13, de 9 de janeiro de 2026" (página de MG em 2.1). O DETRAN-PR também exige CND do INSS de vendedor PJ.
  - A regra vale para bem do imobilizado, não para estoque de revenda.
- **[N] S.A., LSA art. 142, VIII (redação da Lei 11.941/2009):** compete ao conselho de administração:
  > "autorizar, se o estatuto não dispuser em contrário, a alienação de bens do ativo não circulante, a constituição de ônus reais e a prestação de garantias a obrigações de terceiros"

  Fonte: planalto LSA, link em 7.3.
- **[N] Mandatário:** art. 661, §1º. Alienar sempre exige poder especial e expresso, mesmo que, para a sociedade, a venda seja rotineira (estoque). O DETRAN-PR (art. 5º) só aceita a cláusula "vender".
- **Regra codificável:**
  - **Revendedora**, com objeto social que inclui comércio de veículos, vendendo veículo de **estoque** → ato do objeto social. Basta administrador com poderes gerais de gestão. Ver RENAVE na Seção 4.
  - **Imobilizado**, contrato omisso → dentro dos poderes do administrador (art. 1.015 só restringe imóveis). Marcar alerta de baixa severidade (corrente notarial cautelosa) e verificar CND se o valor passar do limite.
  - **S.A. com conselho** → exigir ata do conselho autorizando a venda ou cláusula estatutária que dispense a autorização (art. 142, VIII).
  - **Procurador** → exigir poder especial de "vender" (art. 661, §1º), mesmo para estoque.

### 7.5 (e) Restrição contratual a "alienação de bens imóveis" não alcança veículos

- **[N] Arts. 79 e 82 do CC:**
  > "Art. 79. São bens imóveis o solo e tudo quanto se lhe incorporar natural ou artificialmente."

  > "Art. 82. São móveis os bens suscetíveis de movimento próprio, ou de remoção por força alheia, sem alteração da substância ou da destinação econômico-social."

  Fonte: planalto CC. O veículo automotor é bem móvel, com "movimento próprio".
- **[N] Art. 113 do CC (§1º incluído pela Lei 13.874/2019):** a interpretação deve corresponder à boa-fé, aos usos e às práticas de mercado, e ser "mais benéfico à parte que não redigiu o dispositivo, se identificável" (inciso IV). O próprio art. 1.015 do CC só restringe imóveis.
- **[D] Interpretação estrita de cláusulas que limitam poderes:** é princípio doutrinário geral de que exceções se interpretam restritivamente. Não localizei acórdão específico sobre cláusula "imóveis" × veículo (**não confirmado**). Em sentido mais cauteloso, ver Fischer em 7.4.
- **Regra codificável:**
  - Restrição que menciona só "imóveis" → **não** bloqueia venda de veículo.
  - Procurar no contrato outras cláusulas que alcancem veículos: "bens móveis", "ativo imobilizado/permanente/não circulante", "quaisquer bens", "bens de valor superior a R$ X", "veículos", "atos de disposição patrimonial", "alienação de bens do ativo", "dependerá de aprovação dos sócios / assinatura conjunta".
  - Se qualquer dessas cláusulas existir → aplicar a restrição (exigir anuência ou assinatura conjunta) e marcar revisão.


---

## Anexo A — Conferências feitas diretamente na fonte oficial (16–17/10/2026)

As normas abaixo foram baixadas da fonte oficial e lidas no texto integral (PDF ou HTML). Não foram aceitas só com base em resumo ou notícia.

| Norma / documento | O que foi conferido | Fonte |
|---|---|---|
| Res. CONTRAN 1.027/2026 (DOU 18/08/2026, Ed. 155-B, Seção 1 – Extra B, p. 10) | Arts. 26, 27, 28 (§§ 1º, 4º, 6º e 7º), 44 a 47, 49, 52, 58, 59, 60 e 61. Em todo o texto, "pessoa jurídica" como proprietária aparece só no art. 28, § 7º. A palavra "procuração" não aparece; o art. 28, § 7º, usa "instrumento de outorga verificável". | https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/resolucao10272026.pdf |
| Provimento CNJ 252/2026 | Considerandos (inclusive o que trata da plataforma federal e de PJ), arts. 4º, 5º, 6º, 7º, 10 e 11 | https://atos.cnj.jus.br/files/original124648202608206a86f73893e30.pdf |
| Res. CONTRAN 1.026/2026 (RENAVE) | Página do DOU "Nº 120-C, terça-feira, 30 de junho de 2026" e a existência dos arts. 33, 35 e 36. Os dispositivos sobre e-CNPJ aparecem no texto. | https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/Resoluo1026.pdf |
| Provimento CGJCE nº 05/2025 | Arts. 4º a 7º, inclusive a revogação expressa do Prov. 17/2024 | https://portal.tjce.jus.br/uploads/2025/08/Provimento-no-05-2025-CGJCE.pdf |
| Código Nacional de Normas – Foro Extrajudicial (Prov. CNJ 149/2023, consolidado) | Art. 150 (verificar "a atualidade dos poderes de uma procuração"); art. 171 (procuração com "plenos poderes de gestão empresarial" como possível operação suspeita); art. 272, § 4º (comunicação da revogação ao notário de origem); art. 306, § 1º (reconhecimento remoto de firma em documento de veículo) | https://atos.cnj.jus.br/atos/detalhar/5243 |
| DETRAN-CE no gov.br (serviço estadual 20880) | "Procurador por instrumento de procuração pública e específica para o ato (com validade de até 01 ano da data de expedição)" | https://www.gov.br/en/state-services/servico_estadual?id=20880 |
| Lei 15.153/2025 e Mensagem de veto nº 812/2025 | Texto do § 4º do art. 123 do CTB; veto do art. 3º, cujas razões dizem que "o vacatio legis desta lei será [...] de 45 dias após a sua publicação oficial"; promulgação do inciso III em 09/12/2025 (DOU 10/12/2025); inciso IV continua vetado | https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/L15153.htm ; https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/Msg/Vep/VEP-812-25.htm |
| Lei 14.195/2021 e Mensagem de veto nº 415/2021 | Art. 57, XXIX, "c" (revogação do art. 1.015, p.u.); art. 58 (efeitos); veto da nova redação do art. 1.053 do CC | https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14195.htm ; https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/Msg/VEP/VEP-415.htm |
| Leis 13.792/2019, 13.874/2019, 14.451/2022, 14.071/2020, 14.063/2020 e LC 182/2021 | Dispositivos que alteraram os artigos da Seção 3 e cláusulas de vigência | links na Seção 3.0 |
| Todos os links do documento | 147 URLs únicas testadas em 17/10/2026: todas responderam HTTP 200 | — |

As demais afirmações das Seções 1, 2 e 4 a 7 vêm das fontes citadas em cada item. Páginas de serviço de DETRAN e portarias estaduais foram lidas no site oficial ou em reprodução indicada (por exemplo, LegisWeb), e isso está dito junto de cada citação.

## Anexo B — Lista consolidada do que NÃO foi confirmado

1. **SENATRAN / Res. 1.027, art. 28, § 7º:** como será feita a "comprovação eletrônica dos poderes do signatário" de PJ (bases oficiais, instrumento verificável). Nenhuma regulamentação foi localizada.
2. **Transição:** como os DETRANs tratarão a "ATPV-e impressa + firma por autenticidade" depois do prazo de adequação (~16/11/2026), ou se haverá prorrogação (art. 58, § 3º).
3. **DETRAN-CE:**
   - aceitação de ATPV-e de PJ assinada com ICP-Brasil (e-CNPJ/e-CPF) ou via e-Notariado;
   - exigência de certidão simplificada, última alteração ou consolidação (a página pede só "Contrato Social");
   - exigência de identificação do veículo na procuração;
   - data real da migração para o selo 14 digital (o parecer cita 30/03/2026);
   - existência de ato estadual sobre o RENAVE antes de 2026.
4. **Certidão simplificada:** se JUCEC, JUCESP, JUCERJA ou JUCEMG imprimem prazo de validade.
5. **DETRAN-MG:** sentido exato de "reconhecimento de firma por pessoa jurídica". O provável é certificação da representação pelo tabelião.
6. **Detran-SP:**
   - como identifica o "representante legal" da PJ na procuração eletrônica (cadastro da RFB ou contrato social);
   - vigência atual da Portaria 1.680/2014. A página do Poupatempo, atualizada em 08/10/2026, é coerente com ela;
   - implantação da 2ª fase da transferência digital (PF→PJ e PJ→PJ).
7. **DETRAN-RJ:** forma exigida para a procuração física do vendedor comum.
8. **Substabelecimento:** se DETRANs que exigem procuração pública (CE, MG, SC) recusam substabelecimento particular.
9. **Procuração em causa própria:** tratamento específico nos DETRANs de CE, SP, MG e RJ.
10. **Doutrina e jurisprudência:**
    - aplicação analógica do art. 150, § 4º, da LSA à Ltda;
    - precedente do STJ específico sobre contrato omisso quanto à atuação isolada ou conjunta;
    - acórdão específico afirmando que cláusula restrita a "imóveis" não alcança veículo;
    - norma que obrigue a ratificação da procuração pela nova administração (parece ser só política interna de bancos e cartórios).
11. **Caso Empi (STJ, 3ª Turma):** número do REsp.
12. **RENAVE:**
    - data oficial de publicação da Res. 1.026/2026 (30/06 ou 01/07/2026);
    - adaptação das portarias estaduais anteriores (SP, PR, BA) às Res. 1.026 e 1.027/2026;
    - situação de desmontes, oficinas e leiloeiros.
13. **Mercado:** se os fornecedores de KYB listados fazem, de fato, análise de poderes de representação com IA. A única confirmação é o uso interno da Aarin (Bradesco).
14. **CDT e assinatura gov.br:** portarias DENATRAN/SENATRAN de 2021–2023 que regulamentaram a assinatura gov.br da ATPV-e na CDT. Não foram localizadas; a página federal ainda cita a Res. 809/2020.
