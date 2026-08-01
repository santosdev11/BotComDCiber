# ComDCiber Bot

Bot desenvolvido em Python para automatizar os processos administrativos do servidor ComDCiber. 
O sistema opera utilizando o conceito de *Discord-as-a-Database*, mas em vez de depender de comandos, ele funciona de forma orgânica lendo as mensagens diretamente nos canais.

## Como o sistema funciona
O bot monitora canais específicos aguardando o envio de relatórios de texto pelos militares.

- **Auto-Moderação:** Se um usuário comum enviar uma mensagem fora do padrão (sem as palavras-chave no título), o bot apaga a mensagem instantaneamente e envia um aviso temporário. Moderadores têm bypass nessa regra.
- **Integração Visual:** Mensagens válidas recebem uma reação de ⏳ (em análise) e são copiadas para um canal privado de Logs.
- **Aprovação Interativa:** Os administradores aprovam ou reprovam os relatórios na sala de Logs clicando em botões interativos (Views).
- **Feedback Automático:** Ao ser avaliado, o bot responde a mensagem original do soldado no canal público, troca a reação para ✅ ou ❌, entrega cargos temporários (no caso de Avais) e registra quem foi o avaliador.

## Stack
- Python 3
- `discord.py` (cogs, event listeners, ui)
- `python-dotenv`

## Como rodar

1. Baixe os arquivos e instale as dependências:
```bash
pip install discord python-dotenv

```

2. No arquivo chamado `.env` coloque o token do seu bot:

```env
DISCORD_TOKEN=seu_token

```

3. Abra o arquivo `config.py` e insira os IDs corretos do seu servidor (Canais, Cargos de Permissão e Cargos de Concessão).
4. Ligue o bot:

```bash
python main.py

```
Feito por [santosdev11](https://www.google.com/search?q=https://github.com/santosdev11)

```

```
