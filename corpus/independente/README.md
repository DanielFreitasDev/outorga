# Casos independentes (I01–I10)

Dez cenários para testar às cegas o sistema que decide quem pode assinar a ATPV/ATPV-e na venda de veículo de pessoa jurídica no Ceará. O autor escreveu os casos sem consultar o código, as regras nem o corpus do sistema. Usou apenas `corpus/GUIA_REDACAO.md`, `docs/PESQUISA_JURIDICA.md` e conhecimento próprio de direito societário, notarial e de trânsito. Todos os dados são fictícios. CPF, CNPJ, placa, RENAVAM e chassi foram gerados por `outorga.ids` (semente 9090), e os dígitos verificadores foram conferidos de forma independente.

Cada caso fica em `IXX/` e tem três partes:

- `docs/`: documentos societários e notariais em Markdown. Não há CRLV, que deve ser gerado a partir de `crlv_proprietario`.
- `pedido.json`: dados da venda.
- `gabarito.json`: resposta esperada, com dois cenários:
  - `esperado`: só pelo Código Civil e pela legislação societária;
  - `esperado_ce`: com a política do DETRAN-CE (procurador só com procuração pública, específica para o ato e de até 1 ano da expedição). Fica `null` quando essa política não muda nem o veredito nem os conjuntos.

`conjuntos_minimos_cpf` lista todas as combinações mínimas de pessoas que poderiam assinar a ATPV daquele veículo, naquela data, obrigando a empresa. Os valores possíveis são:

- `[]`: ninguém pode assinar;
- `null`: os conjuntos não são determináveis com os documentos apresentados.

| Caso | Título | Veredito esperado | Faixas aceitáveis | Por quê |
|---|---|---|---|---|
| I01 | S.A. com Diretoria de mandato vencido, prorrogado por lei, e nova Diretoria eleita depois da venda | PODE | VERDE, AMARELO | O mandato venceu em 27/04/2026, mas o art. 150, § 4º, da LSA o estende até a posse dos sucessores, que só ocorreu em 22/09/2026, depois da venda. O estatuto exige dois Diretores, e o par pedido é válido. O "Diretor isolado perante repartições" não vale para alienação. A venda fica abaixo da alçada do Conselho. A procuração outorgada por um só Diretor é ineficaz. |
| I02 | Dois administradores assinam juntos, mas da mesma classe | NAO_PODE | VERMELHO | A cláusula exige um Administrador A **e** um Administrador B para alienar veículos do imobilizado, e os dois signatários são da classe A. O único Administrador B na data é EXPEDITO, porque a renúncia de VALDENIA foi arquivada antes da venda. A procuração existente é de outro veículo. |
| I03 | Procuração de venda revogada por nova procuração que só autoriza assinar "na qualidade de adquirente" | NAO_PODE | VERMELHO | A procuração de 2025, que dava poder de venda, foi revogada expressamente (livro e folhas). A de 2026 menciona "transferência" e "ATPV-e", mas só para veículos adquiridos pela empresa, e não traz poder de alienar (art. 661, § 1º). Só o administrador HÉLIO pode assinar. |
| I04 | Cadeia de substabelecimentos: o primeiro "sem reserva" e o último por instrumento particular | PODE (CE: NAO_PODE) | VERDE, AMARELO (CE: VERMELHO, AMARELO) | Ao substabelecer sem reserva, o procurador original perde os poderes. Pelo CC, o substabelecimento particular de procuração pública é válido (art. 655; Enunciado 182), e DIEGO pode assinar. No DETRAN-CE, que só aceita procuração pública, o elo particular não serve. |
| I05 | Procuração pública sem prazo, com mais de 1 ano, outorgada por administrador que depois saiu | PODE (CE: NAO_PODE) | VERDE, AMARELO (CE: VERMELHO, AMARELO) | A procuração da PJ sobrevive à saída do signatário (STJ, AgInt no REsp 1.997.964/SC), e o CC não fixa prazo. No DETRAN-CE, a procuração de 23/06/2025 ultrapassa 1 ano na venda de 12/08/2026, e só a administradora SUELI pode assinar. |
| I06 | Ata "aprovada por unanimidade dos presentes" e pela "maioria dos sócios", com só 55% do capital | NAO_PODE | VERMELHO | O contrato exige aprovação prévia de 2/3 do capital para alienar veículos, com votos contados por quotas. Os presentes somam 55%. O registro da ata não supre o quórum. Sem aprovação válida, ninguém pode assinar (`[]`). |
| I07 | Procuração outorgada por sócio cujo poder de administração depende de alterações não apresentadas | INDETERMINADO | AMARELO | A escritura invoca a Terceira Alteração, e a Quarta Alteração é anterior à outorga, mas nenhuma das duas está no dossiê. O contrato de 2016 mostra outro administrador, e a consolidação de 2026 não informa como CLÁUDIO atuava. É preciso exigir os atos faltantes (`null`). |
| I08 | Sócio único de SLU assina a venda, mas só foi nomeado administrador uma semana depois | NAO_PODE | VERMELHO | A administração cabia com exclusividade à administradora não sócia. Ser dono de 100% das quotas não dá poder de representação. A alteração que nomeou o sócio é posterior à venda (a retroação do art. 36 vai no máximo até a assinatura). A procuração particular de 6 meses já estava vencida. |
| I09 | Alçada de valor para assinatura conjunta, alterada no tempo, e venda sem valor informado | INDETERMINADO | AMARELO | A alçada vigente é de R$ 150.000,00 (Quarta Alteração), e ela alcança veículos. Sem o valor da operação, não se sabe se basta um administrador ou se são necessários os dois (`null`). |
| I10 | Ex-EIRELI com nome alterado: CRLV no nome antigo, restrição só para imóveis e revogação genérica | PODE | VERDE | O CRLV tem o mesmo CNPJ (transformação pela Lei 14.195/2021 e troca de nome registrada). O "ressalvado o § 1º" remete a uma restrição só para imóveis e "bens de raiz". A procuração de 2026 é válida e revoga genericamente a de 2024. |

Resumo da distribuição pelo Código Civil: 4 PODE (I01, I04, I05, I10), 4 NAO_PODE (I02, I03, I06, I08) e 2 INDETERMINADO (I07, I09). A política do DETRAN-CE muda o resultado em I04 e I05.

Armadilhas de leitura semântica:

- I02: "dois administradores" × "um A e um B";
- I03: "transferência" e "ATPV-e" na qualidade de adquirente;
- I04: "sem reserva de iguais poderes";
- I06: "unanimidade dos presentes" e "maioria dos sócios";
- I10: "ressalvado o disposto no § 1º", que só trata de imóveis;
- I01: exceção de "mero expediente perante repartições públicas", que exclui alienação.
