# 🎬 FiapX Video Processor 

##  Arquitetura da Solução 
![video_processor drawio (1)](https://github.com/user-attachments/assets/981f24c7-112a-46b5-86dc-29f090de2ea3)


## 📌 Visão Geral
Uma plataforma de processamento de vídeos que recebe arquivos, extrai os frames, gera um arquivo `.zip` com as imagens e disponibiliza para o usuário. O sistema foi reestruturado com foco em escalabilidade, segurança, resiliência e boas práticas de arquitetura.

---

## ✅ Funcionalidades
- Upload de vídeos via API
- Extração de frames do vídeo
- Geração automática de `.zip`
- Processamento assíncrono e escalável com RabbitMQ
- Registro e login com autenticação JWT
- Armazenamento dos arquivos e status por usuário
- Infraestrutura baseada em microsserviços com Docker Compose

---

## 🧱 Arquitetura Escolhida: Microsserviços com Mensageria

### ✨ Por que essa arquitetura?
| Requisito                             | Como atendemos                                            |
|--------------------------------------|------------------------------------------------------------|
| Processar vários vídeos ao mesmo tempo | Processamento paralelo via múltiplos workers RabbitMQ     |
| Não perder requisições em picos        | RabbitMQ com fila durável e suporte a retry               |
| Proteção por login/senha               | Auth Service com JWT e senhas com Bcrypt                  |
| Listagem de status por usuário        | Status-service com filtro por e-mail                      |
| Notificações em caso de erro          | Notification-service com envio de e-mail via SMTP         |
| Persistência de dados                 | PostgreSQL compartilhado com serviços                     |
| CI/CD e testes                        | Pipeline planejado com GitHub Actions                     |

### 📌 Componentes
- `auth-service`: login e registro com JWT
- `video-upload-service`: upload e envio para fila `video_to_process`
- `video-processing-service`: consome da fila, extrai frames, gera ZIP e atualiza status
- `status-service`: exibe status e permite download dos arquivos processados
- `notification-service`: envia notificações (email/logs)
- `RabbitMQ`: mensageria com filas dedicadas
- `PostgreSQL`: banco relacional para armazenar vídeos e status
- `Docker Compose`: orquestração local

---

## 🚀 Como rodar o projeto

### 🧩 Pré-requisitos:
- Docker
- Docker Compose

### 🛠️ Subir os serviços:
```bash
git clone https://github.com/ca-ayumi/fiapx-video-processor.git
cd fiapx-video-processor
docker-compose up --build
```

### 📦 Serviços disponíveis:
| Serviço              | URL                        | Porta |
|----------------------|-----------------------------|--------|
| Auth Service         | http://localhost:8001       | 8001   |
| Upload Service       | http://localhost:8002       | 8002   |
| Status Service       | http://localhost:8004       | 8004   |
| Notification Service | http://localhost:8005       | 8005   |
| RabbitMQ Dashboard   | http://localhost:15672      | 15672  |
| PostgreSQL           | localhost:5432              | 5432   |

---

## 🧪 Exemplos de uso com cURL

## 🧪 Exemplos de uso com cURL

### ▶️ Registro de usuário
```bash
curl -X POST http://localhost:8001/register \
    -H 'Content-Type: application/json' \
    -d '{"email":"user@fiapx.com", "password":"123456"}'
```

### 🔐 Login
```bash
curl -X POST http://localhost:8001/login \
    -H 'Content-Type: application/json' \
    -d '{"email":"user@fiapx.com", "password":"123456"}'
```

### 📤 Upload de vídeo
```bash
curl -X POST "http://localhost:8002/upload?user_email=user@fiapx.com" \
  -F "file=@exemplo_video.mp4"
```

### 📊 Verificar status
```bash
curl "http://localhost:8004/videos?user_email=user@fiapx.com"
```

### 📥 Fazer download
```bash
curl -O "http://localhost:8004/download/<nome_do_arquivo>.zip"
```

---

## 📁 Estrutura de Pastas
```
fiapx-video-processor/
├── auth-service/
├── video-upload-service/
├── video-processing-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── processor.py
│   │   ├── models.py
│   │   └── database.py
├── status-service/
├── notification-service/
├── docker-compose.yml
├── .env
└── README.md
```

---

## 🧾 Requisitos Técnicos Atendidos
- ✅ Processamento paralelo com fila RabbitMQ
- ✅ Resiliência a picos de requisição com RabbitMQ durável e DLQ
- ✅ Login e autenticação com JWT seguro
- ✅ Arquitetura escalável com Docker
- ✅ Persistência de dados com PostgreSQL
- ✅ Status por usuário 
- ✅ Em caso de erro, um usuário pode ser notificado com envio de e-mail no Notification Service
---

## 📌 Entregáveis
- [x] Documentação da arquitetura ✅
- [x] Script de infraestrutura (Docker Compose) ✅
- [x] Repositório no GitHub ✅
- [ ] Vídeo de até 10 minutos apresentando a solução 🎥

---

## 📚 Créditos
Projeto acadêmico desenvolvido para o Hackaton da FIAP.

---
