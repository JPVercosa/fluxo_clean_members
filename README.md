# Podio Members Management Script

Este repositório contém um script Python para gerenciar membros do Podio. O script automatiza a remoção de membros que não estão listados em uma planilha Excel fornecida. Este script foi desenvolvido por João Pedro Verçosa [GitHub](github.com/JPVercosa) para automatização de uma tarefa necessária pela [Fluxo Consultoria](https://fluxoconsultoria.poli.ufrj.br/). O repositório não possui manutenção, mas qualquer dúvida podem me contactar por [Email](mailto:jpkvqvercosa@gmail.com) ou [LinkedIn](https://www.linkedin.com/in/jpvercosa/).

## Requisitos

1. **Python**: Certifique-se de ter o Python instalado. Você pode baixá-lo em [python.org](https://www.python.org/) ou para usuários Windows pela [Microsoft Store](https://apps.microsoft.com/detail/9pjpw5ldxlz5?hl=pt-br&gl=BR).
2. **Ambiente Virtual**: É altamente recomendado utilizar um ambiente virtual para gerenciar dependências. Caso você possua o [Anaconda](https://www.anaconda.com/) (ou o Miniconda) instalado você pode utilizar o comando `conda` abaixo para criar um novo ambiente. Caso não possua o Anaconda a maneira mais simples de criar um ambiente virtual para gerenciamento de dependências é através do módulo `venv`, com o comando abaixo também. Esses códigos podem ser executados dentro do **PowerShell** ~~(ou CMD)~~.

### Criar um ambiente virtual com `conda`

```bash
conda create --name myenv
conda activate myenv
```

### Criar um ambiente virtual com `venv`

```bash
python -m venv myenv
source myenv/bin/activate  # No Windows, use `myenv\Scripts\activate`
```

> [!NOTE]
> No Windows ao tentar criar um novo ambiente pela primeira vez, pode ocorrer um erro devido as permissões para rodar o script necessário. Para resolvê-lo será necessário a alteração da política de execução de script para o usuário. Para isso dentro do PowerShell execute o seguinte comando: </br> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

3. **Instalar Dependências**: Após a ativação do ambiente virtual, instale as dependências listadas no arquivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

4. **Chrome Driver**: As versões mais recentes do Selenium fazem o download do Driver automaticamente para você. Então as instruções a baixo só devem ser seguidas caso algum erro como `The executable chromedriver needs to be available in the path.` ou `Unable to Locate Driver Error` surgirem.

<details>
  <summary>Ver instruções</summary>
  
O Selenium requer o ChromeDriver para controlar o navegador Chrome. Baixe o ChromeDriver compatível com sua versão do Chrome em [sites.google.com/chromium.org/driver](https://sites.google.com/chromium.org/driver). Para descobrir a sua versão atual do GoogleChrome abra uma nova guia e digite `chrome://version/`. Para versões mais atuais do chrome (115.X.XXXX.XXX+) é possível encontrar o link para Download (aqui)[https://googlechromelabs.github.io/chrome-for-testing/] procure por Stable e copie e cole a URL em uma nova guia de acordo com a sua plataforma (para Windows normalmente opte por escolher a `win64`) para versões mais antigas do Chrome procure pela sua versão [aqui](https://sites.google.com/chromium.org/driver/downloads).

O download será feito em uma pasta compactada. Abra a pasta compactada e coloque o executável no diretório junto do código e tente executar o script. Caso ainda não funcione será necessário adicionar o caminho do executável ao PATH do seu sistema.

#### Usuários Windows

Para isso na Barra de Pesquisa do Windows pesquise por Variáveis de Ambientes, e selecione a opção `Editar as Variáveis de Ambiente do Sistema`, caso tenha permissões de Administrador, ou `Editar as Variáveis de Ambiente da sua Conta` caso contrário. Clique em `Variáveis de Ambiente`. Selecione a Variável com nome `Path` e clique em `Editar`. Clique em `Novo` e adicione o caminho do executável do ChromeDriver. Não se esqueça de fazer a descompactação da pasta para algum diretório. Após isso clique em `OK` e feche todas as janelas.

#### Usuários Linux

Para isso abra um terminal e digite o seguinte comando:

```bash
export PATH=$PATH:/path/to/chromedriver
```

Substituindo `/path/to/chromedriver` pelo caminho do executável do ChromeDriver.

Para tornar essa mudança permanente adicione rode o código abaixo e reinicie o terminal.

```bash
echo 'export PATH=$PATH:/path/to/chromedriver' >> ~/.bash_profile
source ~/.bash_profile
```

Novamente substituindo pelo local em que se encontra o arquivo `chromedriver.exe`.

#### Usuários MacOS

Para isso abra um terminal e digite o seguinte comando:

```bash
export PATH=$PATH:/path/to/chromedriver
```

Substituindo `/path/to/chromedriver` pelo caminho do executável do ChromeDriver. Para tornar essa mudança permanente utilize o código:

```bash
echo 'export PATH=$PATH:/path/to/chromedriver' >> ~/.bash_profile
source ~/.bash_profile
```

</details>

5. **Planilha Excel**: Certifique-se de ter uma planilha Excel (`.xlsx`) com as colunas "MEMBROS" e "EMAIL" em maiúsculas.

## Configuração

1. **Credenciais**: Utilize o arquivo `secret.json` para adicionar suas credenciais de login do Podio:

```json
{
  "email": "seu_email@exemplo.com",
  "password": "sua_senha"
}
```

2. **Planilha de Membros**: Prepare a planilha Excel (`.xlsx`) com os nomes dos membros e seus respectivos e-mails. Certifique-se de que as colunas estão nomeadas exatamente como "MEMBROS" e "EMAIL". **Certifique-se que todos os membros que devem ser mantidos (membros ativos) estão na planilha.**

## Uso

Execute o script com o seguinte comando, substituindo `nomedoplanilha.xlsx` pelo nome da sua planilha:

```bash
python script.py --file nomedoplanilha.xlsx
```

> [!WARNING]
> Esse script é um script que vai remover membros do Podio, após a remoção de um membro para ele voltar ao Podio será necessário que ele faça todo o processo de criar uma conta de acesso ao Podio novamente. Não é possível restaurar o usuário após removê-lo. Áreas de Trabalho que só contém a pessoa inativa sendo removida também serão apagadas. Certifique-se de estar com a planilha correta de membros ativos e que os emails dos membros na planilha são os mesmos que eles utilizaram para se cadastrar na plataforma.

> [!NOTE]
> Antes de iniciar as remoções, o Script calcula se ele encontra todos os emails existentes na planilha no Podio se ele encontra emails que estão na Planilha e não estão no Podio, ele para a execução e gera um erro com a mensagem `Emails não encontrados no Podio` e imprime a lista de emails não encontrados, que devem ser alterados na planilha, para corresponderem ao email do usuário no Podio.

## Estrutura do Código

O script realiza as seguintes etapas:

1. Carrega as credenciais do arquivo `secret.json`.
2. Inicializa o ChromeDriver e abre o navegador.
3. Faz login no Podio.
4. Navega até a página de membros da organização.
5. Carrega a lista de membros do Podio e compara com a lista da planilha.
6. Remove membros do Podio que não estão presentes na planilha.

## Erros Conhecidos

### Erro de Timeout

O script é baseado em automatização, e algumas vezes o site do Podio pode demorar a responder após uma ação ser tomada. Caso o site demore mais que um determinado tempo (10 segundos) para trazer uma resposta após uma ação ser tomada pelo script, ele vai acusar um Timeout e vai parar a execução do script.

Nesse caso o script deve ser reinicializado e ele vai continuar funcionando corretamente, a partir do ponto que ele parou.

### Membros que não podem ser apagados

Alguns membros não podem ser apagados dentro do Podio. Logo esses membros, mesmo que inativos, devem permanecer na planilha, com seus devidos emails de cadastro no Podio.
