# Guia de redação dos documentos sintéticos

Os documentos do corpus simulam peças reais (contratos sociais registrados na JUCEC, escrituras de
procuração, substabelecimentos, atas). Eles alimentam a avaliação do agente, então **fidelidade aos
fatos de `cenarios.json` é obrigatória** — o gabarito depende deles.

## Regras de ouro

1. **Fatos exatos.** Use exatamente os nomes, CPFs, RGs, CNPJ, NIRE, placas, RENAVAM, chassis, datas,
   percentuais e valores de `corpus/cenarios.json` (`pessoas`, `empresas`, `veiculos`, `documentos`).
2. **Frases obrigatórias literais.** Cada item de `frases_obrigatorias` deve aparecer **exatamente**
   como está (mesmas maiúsculas/minúsculas e acentos; só quebras de linha/espaços podem variar).
   Pode haver texto antes e depois da frase no mesmo período.
3. **Nada de regras extras.** Não invente regras sobre forma de assinatura, alçada de valor,
   alienação/oneração de bens, outorga de procuração ou aprovação de sócios além das pedidas.
   Cláusulas-padrão neutras são bem-vindas (dão realismo e testam a leitura semântica):
   denominação e sede, objeto, prazo, capital e quotas (tabela), responsabilidade limitada,
   pró-labore, exercício social e balanço, cessão de quotas com direito de preferência, falecimento
   ou incapacidade de sócio, declaração de desimpedimento, foro. A vedação-padrão de uso do nome
   empresarial "em atividades estranhas ao objeto social, especialmente em avais, fianças e endossos
   de favor" também é permitida.
4. **Datas por extenso no fecho**, por exemplo "Fortaleza/CE, 6 de maio de 2019", usando a `data` do
   documento. Datas no corpo podem ser numéricas.
5. **Tamanho** dentro de `palavras` (mín./máx.) do documento.
6. **Formato:** Markdown simples que pareça o documento real. Título centralizado em maiúsculas
   (pode usar `**...**`), cláusulas como `CLÁUSULA PRIMEIRA – DA DENOMINAÇÃO E SEDE`,
   "Parágrafo único.", "§ 1º". Nada de listas com marcadores, exceto em quadros/tabelas (quadro
   societário pode ser uma tabela Markdown). Sem comentários de bastidor, sem "(fictício)" no meio do
   texto, exceto no nome do cartório, que já vem com "(fictício)".
7. **Qualificação completa das partes** no preâmbulo: nome, nacionalidade, estado civil, profissão,
   CPF, RG e cidade de residência (invente rua e número).

## Por tipo de documento

- **Contrato social / alteração / consolidação / ato constitutivo de SLU:** preâmbulo com
  qualificação, cláusulas numeradas por extenso, fecho com local e data, assinaturas dos sócios
  (linhas com nome), visto de advogado fictício ("Visto: Fulano de Tal – OAB/CE nº 12.345") ou
  declaração de enquadramento ME/EPP. Ao final, quando o documento tiver `registro`, inclua o
  bloco de chancela:

  ```
  JUNTA COMERCIAL DO ESTADO DO CEARÁ – JUCEC
  Certifico o registro em DD/MM/AAAA sob o nº <registro.numero>
  Protocolo: <invente> | NIRE: <empresa.nire>
  Empresa: <razão social>
  Autenticação: <código hexadecimal inventado>
  ```

- **Alteração contratual:** "Os sócios abaixo qualificados resolvem alterar o contrato social
  mediante as cláusulas seguintes"; diga explicitamente quais cláusulas mudam e que as demais
  permanecem inalteradas.
- **Estatuto de S.A.:** artigos (Art. 1º…), capítulos (Capítulo I – Da Denominação…), Conselho de
  Administração e Diretoria. **Ata do Conselho:** cabeçalho com data, hora, local, quórum, mesa,
  ordem do dia, deliberações, encerramento, assinaturas.
- **Procuração pública:** cabeçalho com República Federativa do Brasil / Estado do Ceará / nome do
  cartório / Livro e Folhas; "SAIBAM quantos este público instrumento de procuração virem que...";
  comparecimento da outorgante (quando PJ, "neste ato representada por..." e menção ao contrato
  social ou estatuto que comprova os poderes, com registro na JUCEC); "nomeia e constitui seu
  bastante procurador..."; poderes; prazo; substabelecimento conforme o pedido (se "omisso", não
  diga nada sobre substabelecer); fecho do tabelião, emolumentos e selo digital fictícios, "TRASLADO".
- **Procuração particular:** OUTORGANTE / OUTORGADO / PODERES / prazo / local e data / assinatura.
  Reconhecimento de firma **somente** se o documento pedir.
- **Substabelecimento e revogação:** identifique com precisão a procuração de origem (data,
  cartório, livro, folhas) e as partes.
- **Requerimento de empresário:** formulário com campos rotulados (NOME CIVIL, CPF, NOME EMPRESARIAL,
  CNPJ, NIRE, ENDEREÇO, OBJETO, CAPITAL, DATA DE INÍCIO).

## Verificação

Depois de escrever, rode `uv run python corpus/verificar_docs.py <IDs>` na raiz do projeto e
corrija até passar.
