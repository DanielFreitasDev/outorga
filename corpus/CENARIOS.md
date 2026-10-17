# Cenários de avaliação (gabarito)

Gerado por `corpus/spec.py`. Dados fictícios.

| Caso | Cenário | Assinante(s) | Esperado | Faixa | Quem pode assinar |
|---|---|---|---|---|---|
| C01 | Administração 'indistintamente' — um sócio assina | João | PODE | VERDE | João ou Maria |
| C02 | Assinatura conjunta exigida — só um assina | Carlos | NAO_PODE | VERMELHO | Carlos + Luciana |
| C03 | Assinatura conjunta — os dois assinam | Carlos, Luciana | PODE | VERDE | Carlos + Luciana |
| C04 | Sócia quotista sem poder de administração assina | Ana | NAO_PODE | VERMELHO | Francisco |
| C05 | Administrador não sócio assina | Gustavo | PODE | VERDE | Gustavo |
| C06 | Sócio majoritário (70%) que não é administrador | Roberto | NAO_PODE | VERMELHO | Gustavo |
| C07 | Contrato omisso sobre a forma de atuação | Paula | PODE | AMARELO | Paula ou Ítalo |
| C08 | Alçada por valor — abaixo do limite | Josefa | PODE | VERDE | Antônio ou Josefa |
| C09 | Alçada por valor — acima do limite | Antônio | NAO_PODE | VERMELHO | Antônio + Josefa |
| C10 | Alçada por valor — valor não informado | Antônio | INDETERMINADO | AMARELO | — |
| C11 | Ativo não circulante (inclui veículos) sem deliberação | Valdir | INDETERMINADO | AMARELO | Valdir ou Márcia |
| C12 | Ativo não circulante com ata aprovando a venda | Márcia | PODE | VERDE | Valdir ou Márcia |
| C13 | Carro integralizado pelo sócio — o OUTRO sócio vende sozinho | Leonardo | NAO_PODE | VERMELHO | Marcos |
| C14 | Carro integralizado pelo sócio — ele mesmo vende | Marcos | PODE | VERDE | Marcos |
| C15 | Carro integralizado, mas o CRLV ainda está no CPF do sócio | Marcos | INDETERMINADO | AMARELO | Marcos |
| C16 | Procuração pública válida com poderes especiais | Pedro | PODE | VERDE | Francisco ou Pedro |
| C17 | Procuração só com poderes gerais de administração | Rodrigo | NAO_PODE | VERMELHO | Francisco |
| C18 | Procuração vencida | Kleber | NAO_PODE | VERMELHO | Carlos + Luciana |
| C19 | Procuração revogada | Fábio | NAO_PODE | VERMELHO | Antônio ou Josefa |
| C20 | Procuração outorgada por quem não tinha poder sozinho | Kleber | NAO_PODE | VERMELHO/AMARELO | Carlos + Luciana |
| C21 | Procuração do sócio em nome próprio (PF), não da empresa | Kleber | NAO_PODE | VERMELHO/AMARELO | João ou Maria |
| C22 | Procuração para OUTRO veículo específico | Ana | NAO_PODE | VERMELHO | Rafael |
| C23 | Substabelecimento com reserva, permitido | Ana | PODE | VERDE | Francisco ou Pedro ou Ana |
| C24 | Substabelecimento vedado na procuração | Kleber | NAO_PODE | VERMELHO | Rafael ou Igor |
| C25 | Substabelecimento sem reserva — o procurador original assina | Fábio | NAO_PODE | VERMELHO | Antônio ou Josefa ou Ana |
| C26 | Procuração particular sem firma reconhecida | Camila | PODE | AMARELO | Rafael ou Camila |
| C27 | Procuradores que devem agir em conjunto — só um assina | Sérgio | NAO_PODE | VERMELHO | Gustavo ou Sérgio + Bruna |
| C28 | Administrador que outorgou saiu da administração depois | Davi | PODE | VERDE/AMARELO | Lúcia ou Davi |
| C29 | Alteração contratual mudou de isolada para conjunta | Hélio | NAO_PODE | VERMELHO | Hélio + Regina |
| C30 | Administrador com mandato por prazo determinado vencido | Wagner | NAO_PODE | VERMELHO/AMARELO | ninguém (regularizar) |
| C31 | Sociedade limitada unipessoal — sócio único assina | Rafael | PODE | VERDE | Rafael |
| C32 | S.A. — um diretor sozinho | Marcelo | NAO_PODE | VERMELHO | Marcelo + Helena ou Marcelo + Tiago ou Helena + Tiago |
| C33 | S.A. — diretor + procurador com procuração válida | Tiago, Sérgio | PODE | VERDE | Marcelo + Helena ou Marcelo + Tiago ou Helena + Tiago ou Marcelo + Sérgio ou Helena + Sérgio ou Tiago + Sérgio |
| C34 | Empresário individual | Josué | PODE | VERDE | Josué |
| C35 | Revendedora: restrição a ativo imobilizado x estoque | Eduardo | PODE | AMARELO/VERDE | Eduardo |
| C36 | Procuração válida — documentos ESCANEADOS (OCR) | Pedro | PODE | VERDE/AMARELO | Francisco ou Pedro |
| C37 | Procuração antiga sem prazo (3 anos) | Bruna | PODE | AMARELO | Gustavo ou Bruna |
| C38 | Todos os sócios assinam (com exigência de deliberação) | Valdir, Márcia, Osvaldo | PODE | VERDE/AMARELO | Valdir ou Márcia |
| H01 | [cega] ‘De per si’ — um administrador assina | Otávio | PODE | VERDE | Raquel ou Otávio |
| H02 | [cega] Quaisquer dois dos três administradores — um assina | Renata | NAO_PODE | VERMELHO | Lucas + Renata ou Lucas + Caio ou Renata + Caio |
| H03 | [cega] Veículos da frota exigem os dois (sem valor) — um assina | Ivan | NAO_PODE | VERMELHO | Ivan + Solange |
| H04 | [cega] Procuração ‘pelo período de doze meses’ vencida | Nilton | NAO_PODE | VERMELHO | Ivan + Solange |
| H05 | [cega] ‘Sem direito de substabelecer’ e houve substabelecimento | Nilton | NAO_PODE | VERMELHO | Hugo ou Priscila |
| H06 | [cega] Procuração conjunta, veículo identificado, no prazo | Nilton | PODE | VERDE | Breno + Clarice ou Nilton |
| H07 | [cega] Antiga administradora assina depois da troca | Vera | NAO_PODE | VERMELHO | Jonas |
| H08 | [cega] Restrição a imóveis e participações; veículo de R$ 320 mil | Hugo | PODE | VERDE | Hugo |

## Lote ATPV-e (vendendo ou comprando; todos os tipos de PJ)

| Caso | Cenário | Vendedor | Comprador | Esperado | Faixa |
|---|---|---|---|---|---|
| A01 | Comprador PJ: administrador assina compra abaixo da alçada | Nádia (PF) | COMERCIAL BOM JARDIM LTDA. — Gilberto | PODE | VERDE |
| A02 | Comprador PJ: compra acima da alçada com um só administrador | Nádia (PF) | COMERCIAL BOM JARDIM LTDA. — Gilberto | NAO_PODE | VERMELHO |
| A03 | Restrição de compra não alcança a venda | COMERCIAL BOM JARDIM LTDA. — Simone | Débora (PF) | PODE | VERDE |
| A04 | Comprador PJ por procurador com poder de compra | Nádia (PF) | LOCADORA JANGADA LTDA. — Elias | PODE | VERDE |
| A05 | Procuração só de venda usada para comprar | Nádia (PF) | LOCADORA JANGADA LTDA. — Pedro | NAO_PODE | VERMELHO |
| A06 | PJ dos dois lados: ambos com poder | TRANSPORTES SERTÃO VERDE LTD — João | COMERCIAL BOM JARDIM LTDA. — Simone | PODE | VERDE |
| A07 | PJ dos dois lados, assinaturas lidas da ATPV-e: comprador sem poder | CONSTRUTORA MANDACARU LTDA. — Carlos, Luciana | LOCADORA JANGADA LTDA. — Ana | NAO_PODE | VERMELHO |
| A08 | Cooperativa: Diretor-Presidente e Diretor Financeiro assinam | COOPERATIVA DE TRANSPORTE ES — Manoel, Expedito | Débora (PF) | PODE | VERDE |
| A09 | Cooperativa: Diretor-Presidente sozinho | COOPERATIVA DE TRANSPORTE ES — Manoel | Débora (PF) | NAO_PODE | VERMELHO |
| A10 | Associação compradora: Presidente eleita assina | Nádia (PF) | ASSOCIAÇÃO COMUNITÁRIA AMIGO — Maria | PODE | VERDE |
| A11 | MEI vende: o titular assina | 60.827.183 ROGERIO FERNANDES — Rogério | Débora (PF) | PODE | VERDE |
| A12 | MEI compra: a esposa do titular assina | Nádia (PF) | 60.827.183 ROGERIO FERNANDES — Cláudia | NAO_PODE | VERMELHO |
| A13 | EIRELI (hoje SLU) vende: o titular assina | OLIVEIRA SÁ ENGENHARIA EIREL — Wellington | Débora (PF) | PODE | VERDE |
| A14 | Sociedade simples: um sócio assina sozinho | PINHO & ARRUDA FISIOTERAPIA  — Larissa | Débora (PF) | NAO_PODE | VERMELHO |

## Lote consulta por CPF (antes da ATPV-e; pessoa física e procuração)

| Caso | Cenário | Papel | Quem vai assinar | Esperado | Faixa |
|---|---|---|---|---|---|
| P01 | Pessoa física: o próprio dono vai assinar | vender | Raimunda Nonata Siqueira | PODE | VERDE |
| P02 | Procurador com procuração pública e específica | vender | Josué Lima Ferreira | PODE | VERDE |
| P03 | CPF diferente do dono, sem procuração | vender | Luana Castro Ribeiro | INDETERMINADO | AMARELO |
| P04 | Procuração só com poderes gerais (DETRAN, IPVA, multas) | vender | Patrícia Moura Leal | NAO_PODE | VERMELHO |
| P05 | Procuração de 6 meses, vencida | vender | Edvaldo Pinheiro Neto | NAO_PODE | VERMELHO |
| P06 | Procuração específica de outro veículo | vender | Josué Lima Ferreira | NAO_PODE | VERMELHO |
| P07 | Compradora pessoa física representada por procuradora | comprar | Patrícia Moura Leal | PODE | VERDE |
| P08 | Procuração revogada | vender | Edvaldo Pinheiro Neto | NAO_PODE | VERMELHO |
| P09 | Substabelecida pelo procurador, com reserva | vender | Patrícia Moura Leal | PODE | VERDE |
| P10 | Procuração particular com firma reconhecida | vender | Edvaldo Pinheiro Neto | NAO_PODE | VERMELHO |
| P11 | Procuração dada pela esposa, não pelo dono registral | vender | Josué Lima Ferreira | NAO_PODE | VERMELHO |
| P12 | Dona é empresa: CPF do administrador | vender | Francisco Wellington Rocha | PODE | VERDE |
| P13 | Dona é empresa: CPF de sócia sem poder, sem procuração | vender | Ana Beatriz Holanda | INDETERMINADO | AMARELO |
| P14 | Dona é empresa: CPF de procurador da empresa | vender | Pedro Henrique Lima | PODE | VERDE |
| P15 | Comprador é empresa: CPF do administrador, abaixo da alçada | comprar | Gilberto Araújo Nunes | PODE | VERDE |
