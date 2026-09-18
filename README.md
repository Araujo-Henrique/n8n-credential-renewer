# n8n Credential Renewer

## Problema identificado
Identifiquei um fluxo no n8n que se conectava com uma conta google que estava em fase teste no Google Cloude e não podia ser publicada. Aplicações em fase teste do Google Cloude possuem tokens que expiram em 7 dias. O código utiliza a biblioteca Playwright do python para acessar o chrome em modo de depuração remota, em seguida acessa o n8n com as credenciais e por fim desconecta e conecta novamente a conta, o que renova os tokens por mais 7 dias. Inicialmente o fluxo foi feito para rodar no agendador de tarefas da máquina. Próximos ajustes serão feitos para colocar o sistema para rodar na rede.

## Pré-requisitos

- **Conta no n8n**
- **Programa criado em fase teste no Google Console**
- **Credenciais da conta google (client ID e Client Secret) registradas na plataforma do n8n**

## Configurações iniciais

### Setup do ambiente de desenvolvimento

1. Crie o ambiente virtual:
   ```powershell
   python -m venv venv
   ```
2. Ative:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
3. Instale as dependências:
   ```powershell
   python -m pip install -r requirements.txt
   ```

### Conectar Playwright e Chrome aberto com depuração remota

Foi necessário prosseguir com o método abaixo porque o google costuma bloquear o acesso da biblioca Playwright para fazer login em contas. Com esse desafio em mente foi necessário conectar a biblioteca playwright no chrome aberto em modo de depuração remota e fazer o primeiro login na conta manualmente. Após isso a automação poderá guarda os dados de login em uma pasta que escolher (utilizei o nome chrome-debug).

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\caminho_escolhido\da_pasta\chrome-debug"
```

E no Python você conecta com:

```python
browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
```

## Registro de execução (observabilidade)
Ao final de cada execução o programa dispara um log de aviso para reportar se o programa rodou por completo, quebrou no meio do caminho ou se encontrou alguma barreira que resultou em erro. Ese disparo é feito com a integração com o bot do telegram. Não é um passo orbigatório para o projeto, mas permite que o processo possa ser acompanhado tendo em vista que o programa é para rodar com headless True