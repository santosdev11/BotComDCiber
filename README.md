# 🛡️ ComDCiber

Bot desenvolvido em Python para automatizar os processos administrativos, operacionais e punitivos do servidor **Comando de Defesa Cibernética**. 

O sistema opera utilizando o conceito inovador de **Discord-as-a-Database**[cite: 4]. Em vez de depender de bancos de dados externos (como SQL), ele funciona de forma orgânica lendo, processando e consultando as próprias mensagens de Log diretamente nos canais[cite: 4].

---

## ⚙️ Principais Funcionalidades

### 1. Sistema de Relatórios e Auto-Moderação
O bot monitora canais de subordinação aguardando o envio de relatórios de texto pelos militares[cite: 4].
*   **Filtro de Padrão:** Apaga instantaneamente mensagens de usuários comuns que não contenham o formato correto (ex: sem a palavra-chave "RELATÓRIO DE PATRULHAMENTO")[cite: 4].
*   **Integração Visual:** Relatórios válidos recebem a reação ⏳ e são espelhados na sala de Logs para a chefia[cite: 4].
*   **Aprovação Interativa (Views):** Administradores aprovam/reprovam os relatórios por botões[cite: 4], informando o motivo através de um painel Modal. O sistema avisa o soldado automaticamente e pode entregar cargos (ex: Aval Concedido).

### 2. Sistema Punitivo (Exílio e Blacklist)
Ferramentas avançadas para a Diretoria e Alto Comando manterem a ordem no servidor.
*   Gera relatórios impecáveis e padronizados de Exílio e Blacklist com anexação de provas (Links, Imagens ou Vídeos).
*   **Ação Direta:** Aplica a expulsão (Kick) ou Banimento automaticamente no Discord, dependendo do prazo selecionado.
*   **Ficha Criminal:** Os registros ficam salvos no banco de dados para consultas futuras.

### 3. Banco de Dados e Consultas (Slash Commands)
Comandos de barra integrados para puxar as informações operacionais de qualquer recruta ou militar.
*   Varredura inteligente que previne a "Amnésia de Histórico", buscando dados independentemente de quão antigos sejam.

### 4. 🛡️ Segurança e Proteções Anti-Crash (Blindagem)
*   **Trava de RAM:** Bloqueia o upload de vídeos/arquivos maiores que 8MB nos comandos, prevenindo o congelamento da hospedagem (Discloud).
*   **Tratamento de Limite de Caracteres:** Calcula matematicamente o espaço da mensagem ao avaliar relatórios. Se faltar espaço para o limite de 2000 do Discord, ele comprime a mensagem do soldado para garantir que o seu selo de aprovação seja publicado.
*   **Proteção de Usuário Fantasma:** O sistema não sofre Crash se o militar que enviou o relatório sair do servidor no meio do processo.
*   **Proteção de Rodapé:** Se os IDs de rastreio ocultos forem corrompidos, o bot invalida o relatório em vez de travar.

---

## 💻 Painel de Comandos

O bot utiliza *Slash Commands* (`/comando`), acessíveis mediante hierarquia:

| Comando | Descrição | Permissão |
| :--- | :--- | :--- |
| `/help` | Exibe o painel de ajuda e a lista de comandos. | Livre |
| `/patrulhamentos` | Puxa o total de patrulhas aprovadas de um militar. | Livre |
| `/infoexilio` | Busca a ficha de exílio de um usuário, incluindo provas. | Livre |
| `/infoblacklist` | Busca a ficha de blacklist de um usuário, incluindo provas. | Livre |
| `/exilar` | Registra o exílio e Bane/Expulsa o alvo do servidor. | [DR] Diretoria ou + |
| `/blacklist` | Registra a blacklist e Bane/Expulsa o alvo do servidor. | [DR] Diretoria ou + |

---

## 🛠️ Stack
*   **Linguagem:** Python 3[cite: 4]
*   **Bibliotecas Principais:** `discord.py` (Cogs, Event Listeners, UI/Modals, app_commands), `python-dotenv`[cite: 4]
*   **Arquitetura:** Modular (`main.py`, `config.py`, `components.py` e pasta `cogs/`)[cite: 4]

---

Feito por [santosdev11](https://github.com/santosdev11)
