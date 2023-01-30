<h1 align="center">Alterador de Guias TISS</h1>

<p align="center">A ideia inicial desse projeto nasceu da necessidade de uma ferramenta capaz de realizar manutenções/alterações de 
dados eletrônicos em guias médicas (arquivos XML) no <b>padrão TISS</b> definido pela ANS, com propósito 
de otimizar o tempo gasto para essa tarefa que até então em meu trabalho era feita de forma manual através de editores de texto como 
++Notepad, bloco de notas, etc.</p>

<p align="center">
    <a href="#-projeto">Projeto</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
    <a href="#-funcionalidades">Funcionalidades</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
    <a href="#-tecnologias">Tecnologias</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
    <a href="#-licença">Licença</a>&nbsp;&nbsp;&nbsp;
</p>

todo --> Imagem ilustrativa do projeto

## 💻 Projeto

Realizar manutenção de dados eletrônicos em guias médicas no padrão TISS. Dentre os dados a serem
alterados estão:

* Código de procedimento;
* Tipo de tabela;
* Unidade de medida;
* Grau de participação;
* Código de despesa;
* Valor unitário;
* Valor total;

---

## ⚙ Funcionalidades

1. <a href="#-leitura-de-críticas">Leitura de críticas;</a>
2. <a>Alteração de dados;</a>
3. <a>Alteração de valores;</a>
4. <a>Gerar código hash;</a>
5. <a>Salvar arquivo;</a>

### 📖 Leitura de críticas

Para leitura das críticas/correções, é necessário a entrada dos dados a serem alterados em tabelas
que serão lidas pelo software.

Foi criado uma <a>planilha em formato XLSX</a> no repositório contendo tabelas padronizadas 
para duas categorias de alterações.

Abaixo estão as colunas das tabelas que representam os dados que serão alterados:

#### 🎲 Categoria de dados

| Número da guia | Código de procedimento (atual) | Código de procedimento (novo) | Tipo de tabela (atual) | Tipo de tabela (nova) | Grau de participação (atual) | Grau de participação (novo) | Código de despesa (atual) | Código de despesa (novo) | Unidade de Medida (atual) | Unidade de Medida (novo) |
|----------------|--------------------------------|-------------------------------|------------------------|-----------------------|------------------------------|-----------------------------|---------------------------|--------------------------|---------------------------|--------------------------|

<br>

#### 💰 Categoria de valores

| Número da guia | Código de procedimento | Valor unitário (atual) | Valor unitário (novo) |
|----------------|------------------------|------------------------|-----------------------|

<br>

Em ambas tabelas, a coluna número da guia pode ser preenchida para especificar uma guia a ser realizada alteração.
Quando vazia, irá realizar alteração no procedimento especificado em todas guias da conta.

Para informações mais técnicas sobre a leitura das tabelas recomendo a visualização da classe responsável:

```Python
class Tabela:
    ...
    ...
```

### ✍ Alterações

Na alteração de dados, o software interpreta cada linha das tabelas de alterações e busca pelo código de procedimento
especificado, caso encontre verifica se o dado (atual) é igual ao passado na tabela, se for realiza o de/para.







