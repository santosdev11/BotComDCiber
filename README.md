# BotComDCiber

Bot desenvolvido em Python para automatizar processos do servidor da divisão ComDCiber. 
Em vez de um banco de dados externo, o bot usa os próprios canais do Discord para armazenar e registrar as logs

## Módulos
Tudo funciona via Slash Commands e formulários (Modais). Os administradores avaliam os pedidos por botões interativos nas mensagens.
- `/patrulha`: Envia relatório de patrulha para aprovação.
- `/aval`: Solicita licença/ausência. Se aprovado, entrega o cargo temporário automaticamente.
- `/meta`: Registra a conclusão de metas semanais.

## Stack
- Python 3
- `discord.py` (cogs, ui, app_commands)
- `python-dotenv`

## Como rodar

1. Baixe os arquivos e instale as dependências:
```bash
pip install discord python-dotenv
