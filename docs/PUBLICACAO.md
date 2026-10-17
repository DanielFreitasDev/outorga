# Demonstração on-line

**https://outorga.cepify.com.br** — demonstração pública com dados fictícios.

## O que funciona on-line (sem IA no servidor)

| Funciona | Por quê |
|---|---|
| Os 85 cenários da **Demonstração**, com o resultado real da IA local e o gabarito | resultados pré-calculados (`avaliacoes/`) |
| **Rodar agora** um cenário de exemplo | as leituras da IA para o corpus estão no cache versionado (`.cache/leituras/`) |
| **Consulta por CPF** sem documentos (veículos da base veicular simulada) | não precisa de IA: dono pela base + motor de regras |
| Simulação "e se…?", parecer em PDF, faixa intermediária, auditoria | o motor de regras roda no servidor |

| Desligado on-line | Por quê |
|---|---|
| Envio de documentos (novas análises com arquivos, leitura de ATPV-e) | o servidor não tem GPU nem IA; e uma demonstração pública não deve receber documentos reais |
| Mudar a política e registrar revisão humana | evitar que um visitante altere a configuração dos outros |
| Histórico das consultas de outros visitantes | privacidade: a consulta de cada visitante só é vista por quem tem o link |

Para ler documentos novos, rode o Outorga na sua máquina com uma IA local ou uma chave de API ([`IA.md`](IA.md)).

## Como foi publicada

- **Servidor:** uma VPS Linux ARM64 (Ubuntu 24.04, 2 vCPU, 12 GB de RAM), **sem GPU**.
- **Instalação nativa com systemd**, no mesmo padrão dos outros serviços da VPS:
  - usuário de sistema dedicado (`outorga`), código em `/opt/outorga` e configuração em `/etc/outorga/outorga.env`
    (root, 600);
  - serviço endurecido: sistema de arquivos só leitura, exceto `/opt/outorga/dados`; limite de 1 GB de memória e de
    1,5 CPU ([`scripts/deploy/outorga-demo.service`](../scripts/deploy/outorga-demo.service));
  - modo demonstração: `OUTORGA_MODO=demonstracao` e `OUTORGA_LLM=nenhum`.
- **Exposição na internet só pelo Cloudflare Tunnel.** A aplicação escuta apenas em `127.0.0.1:54325`; o túnel liga o
  hostname público a essa porta e cuida do HTTPS. Nenhuma porta nova foi aberta no servidor.
- **Atualizar:** `SERVIDOR=usuario@host ./scripts/deploy/publicar.sh` envia o commit atual e a interface compilada,
  instala as dependências e reinicia o serviço.
- **Consumo medido:** ~175 MB de memória em uso normal.

## Para produção (DETRAN-CE)

A demonstração não é uma instalação de produção. Para produção, seriam necessários:

- autenticação e controle de acesso;
- servidor com GPU, ou uma IA por chave de API contratada;
- integração com a base veicular (RENAVAM) e com o sistema de transferência;
- política de retenção dos documentos (LGPD).

Ver [`INTEGRACAO.md`](INTEGRACAO.md).
