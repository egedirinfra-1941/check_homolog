# Monitor de Possíveis Homologações no PNCP

## Descrição

Este projeto automatiza a identificação de possíveis homologações de processos licitatórios registrados no PLANINFRAWeb, realizando consultas no Portal Nacional de Contratações Públicas (PNCP) e enviando notificações por e-mail para análise da equipe responsável.

O script executa as seguintes etapas:

1. Obtém dados de uma planilha Google Sheets.
2. Filtra processos licitatórios que:

   * Estão com status **LIA**;
   * Não possuem data de licitação cadastrada;
   * Possuem data de entrega de propostas preenchida;
   * Já ultrapassaram a data de entrega das propostas.
3. Consulta o PNCP em busca de editais encerrados compatíveis com os registros.
4. Identifica possíveis correspondências utilizando:

   * Unidade responsável pela licitação;
   * Modalidade da licitação;
   * Município;
   * Número da licitação.
5. Gera uma lista de itens para conferência manual.
6. Envia um e-mail automático com os resultados encontrados.

---

## Arquitetura

```text
Google Sheets (PLANINFRAWeb)
           │
           ▼
    Leitura dos dados
           │
           ▼
   Filtros de seleção
           │
           ▼
      Consulta PNCP
           │
           ▼
  Identificação de editais
           │
           ▼
    Geração do relatório
           │
           ▼
      Envio de e-mail
```

---

## Dependências

Instale as bibliotecas necessárias:

```bash
pip install pandas numpy requests gspread oauth2client
```

---

## Variáveis de Ambiente

O script depende das seguintes variáveis de ambiente:

### Google Sheets

| Variável           | Descrição                                              |
| ------------------ | ------------------------------------------------------ |
| `GSHEET_KEY_SHEET` | ID da planilha Google Sheets                           |
| `JSON_KEY`         | Credenciais da conta de serviço Google em formato JSON |

### E-mail

| Variável          | Descrição                 |
| ----------------- | ------------------------- |
| `SENDER_EMAIL`    | E-mail remetente          |
| `EMAIL_PASSWORD`  | Senha do e-mail remetente |
| `RECEIVER_EMAIL`  | Destinatário principal    |
| `RECEIVER_EMAIL2` | Destinatário secundário   |
| `RECEIVER_EMAIL3` | Destinatário secundário   |
| `RECEIVER_EMAIL4` | Destinatário secundário   |

---

## Estrutura dos Dados

O script utiliza a aba **ACD** da planilha Google Sheets.

As seguintes colunas são obrigatórias:

* ID Planinfra
* Status
* Cidade
* Estado
* OM
* DESCRIÇÃO
* RESPONSÁVEL LICITAÇÃO
* DATA DA LICITAÇÃO
* DATA ENTREGA PROPOSTAS
* TIPO LICITACAO
* NUMERO LICITACAO

---

## Regras de Seleção

Somente serão analisados registros que atendam simultaneamente aos seguintes critérios:

```python
Status == "LIA"
DATA DA LICITAÇÃO == vazio
DATA ENTREGA PROPOSTAS != vazio
DATA ENTREGA PROPOSTAS < data atual
```

---

## Integração com o PNCP

As consultas são realizadas através da API pública de busca do PNCP:

```text
https://pncp.gov.br/api/search/
```

### Estratégia de Busca

#### Primeira tentativa

Busca por:

* Unidade responsável
* Modalidade
* Editais encerrados

#### Segunda tentativa

Caso não haja resultados:

* Município
* Modalidade
* Órgãos previamente definidos
* Editais encerrados

---

## Exemplo de Saída

### Console

```text
Checar ID 2026-2345 (Contratação de serviço XYZ)
no link https://pncp.gov.br/app/editais/...
```

### E-mail

```html
Prezados, bom dia!

Segue relação de itens de possíveis homologações a serem checadas:

• Checar ID 2026-2345 (Contratação de serviço XYZ)
  Clique aqui para abrir o edital

Respeitosamente,
Equipe ECCP
```

---

## Execução

Execute o script normalmente:

```bash
python monitor_homologacoes.py
```

---

## Tratamento de Erros

O sistema possui tratamento para:

* Falhas de acesso ao Google Sheets;
* Erros de comunicação com a API do PNCP;
* Erros de processamento dos dados;
* Falhas no envio de e-mails SMTP.

Os erros são registrados no console para posterior análise.

---

## Segurança

### Atenção

As seguintes informações **não devem ser versionadas**:

* Credenciais Google (`JSON_KEY`);
* Senhas de e-mail;
* IDs internos de planilhas sensíveis;
* Endereços de e-mail institucionais.

Recomenda-se armazenar todas as credenciais exclusivamente por meio de variáveis de ambiente ou serviços de gerenciamento de segredos.

---

## Manutenção

Sempre que houver:

* Inclusão de novas cidades;
* Inclusão de novas unidades licitantes;
* Alterações nas modalidades de licitação;
* Mudanças na API do PNCP;

Os dicionários de mapeamento e a lógica de busca deverão ser revisados.

---

## Autor

Equipe ECCP

