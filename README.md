<h1 align="center">Alterador de Guias TISS</h1>

<p align="center">A ideia inicial desse projeto nasceu da necessidade de uma ferramenta capaz de realizar manutenções/alterações de 
dados eletrônicos em guias médicas (arquivos XML) no <b>padrão TISS</b> definido pela ANS, com propósito 
de otimizar o tempo gasto para essa tarefa que até então em meu trabalho era feita de forma manual através de editores de texto como 
++Notepad, bloco de notas, etc.</p>

<p align="center">
    <a href="#-tecnologias">Tecnologias</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
    <a href="#-projeto">Projeto</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
    <a href="#-funcionalidades">Funcionalidades</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
    <a href="#-licença">Licença</a>&nbsp;&nbsp;&nbsp;
</p>

todo --> Imagem ilustrativa do projeto

## 🚀 Tecnologias

Esse projeto foi desenvolvido com as seguintes tecnologias:

* Python;
* GitHub;

### 📚 Bibliotecas

* os;
* customtkinter;
* tkinter;
* sys;
* xml.etree;
* hashlib;

## 💻 Projeto

Realizar alteração de dados eletrônicos em guias médicas no padrão TISS. Dentre os dados a serem
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

1. <a href="#-leitura-de-tabelas">Leitura de tabelas;</a>
2. <a href="#-alteracoes-em-arquivo-xml">Alterações em arquivo XML;</a>
3. <a>Gerar código hash;</a>

### 📖 Leitura de tabelas

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

Em ambas tabelas, a coluna número da guia pode ser preenchida para especificar uma guia a ser feita as alterações.
Quando não estiver preenchida, o software entende que será realizada alteração no procedimento especificado em
todas guias da conta.

Para informações mais técnicas sobre a leitura das tabelas recomendo a visualização da classe responsável:

```Python
class Tabela:
    ...
    ...
```

### ✍ Alterações em arquivo XML

O software faz as alterações de acordo com a leitura das tabelas, para cada linha será feita uma busca dentro das guias
pelo código de procedimento passado e realizando alteração caso os dados a serem alterados estejam de acordo (de/para). 

Após realização das alterações, o software disponibiliza o botão de salvar que ao clicar, gera um novo arquivo XML com
as alterações.







