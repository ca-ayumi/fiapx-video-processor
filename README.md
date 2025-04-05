# 🎬 FiapX Video Processor 

##  Arquitetura da Solução 
![video_processor drawio](https://github.com/user-attachments/assets/768efcd6-ac83-4368-941c-d2fcdcab3ef1)


## 📌 Visão Geral
Uma plataforma de processamento de vídeos que recebe arquivos, extrai os frames, gera um arquivo `.zip` com as imagens e disponibiliza para o usuário. O sistema foi reestruturado com foco em escalabilidade, segurança, resiliência e boas práticas de arquitetura.

---

## ✅ Funcionalidades
- Upload de vídeos via API
- Extração de frames do vídeo
- Geração automática de `.zip`
- Processamento assíncrono e escalável
- Registro e login com autenticação JWT
- Armazenamento dos arquivos e status
- Infraestrutura baseada em microsserviços

---

## 🧱 Arquitetura Escolhida: Microsserviços com Mensageria

### ✨ Por que essa arquitetura?
| Requisito | Como atendemos |
|----------|----------------|
| Processar vários vídeos ao mesmo tempo | Processamento paralelo via RabbitMQ |
| Não perder requisições em picos | Mensageria garante buffer e retry |
| Proteção por login/senha | Auth Service + JWT |
| Listagem de status por usuário | (status-service - em progresso) |
| Notificações em caso de erro | (notification-service - em progresso) |
| Persistência de dados | PostgreSQL compartilhado |
| CI/CD e testes | Planejados com GitHub Actions |

### 📌 Componentes
- `auth-service`: login e registro com JWT
- `video-upload-service`: upload e envio para fila
- `video-processing-service`: consome da fila, processa e salva .zip
- `status-service`: exibe status do processamento (em desenvolvimento)
- `notification-service`: notifica usuários por email (em desenvolvimento)
- `RabbitMQ`: mensageria
- `PostgreSQL`: persistência de dados
- `Docker Compose`: orquestração local

---

## 🚀 Como rodar o projeto

### 🧩 Pré-requisitos:
- Docker
- Docker Compose

### 🛠️ Subir os serviços:
```bash
git clone https://github.com/seu-usuario/video-processor-platform.git
cd video-processor-platform
docker-compose up --build
```

### 📦 Serviços disponíveis:
| Serviço | URL | Porta |
|--------|-----|-------|
| Auth Service | http://localhost:8001 | 8001 |
| Upload Service | http://localhost:8002 | 8002 |
| Processing Service | (fila, sem rota HTTP) | - |
| RabbitMQ | http://localhost:15672 | 15672 (user: guest) |
| PostgreSQL | localhost:5432 | - |

---

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
curl -X POST http://localhost:8002/upload \
    -F "file=@video.mp4"
```

---

## 📁 Estrutura de Pastas
```
video-processor-platform/
├── auth-service/
├── video-upload-service/
├── video-processing-service/
├── status-service/ (em progresso)
├── notification-service/ (em progresso)
├── shared/
├── docker-compose.yml
├── .env
├── README.md
└── .github/workflows/ci.yml (em progresso)
```

---

## 🧾 Requisitos Técnicos Atendidos
- ✅ Processamento paralelo via fila
- ✅ Resiliência a picos de requisição (RabbitMQ)
- ✅ Login e autenticação com senha segura (JWT + Bcrypt)
- ✅ Arquitetura escalável com Docker + microsserviços
- ✅ Persistência de dados com PostgreSQL
- 🔄 Status por usuário (em progresso)
- 🔄 Notificações (em progresso)
- 🔄 Testes automatizados (planejado)
- 🔄 CI/CD com GitHub Actions (planejado)

---

## 📌 Entregáveis
- [x] Documentação da arquitetura ✅
- [x] Script de infraestrutura (Docker Compose) ✅
- [ ] Link do GitHub do projeto
- [ ] Vídeo de até 10 minutos apresentando a solução

---

## 📚 Créditos
Projeto acadêmico desenvolvido para a disciplina da FIAP X.

---

Se quiser, contribua com testes, melhorias e novas features via pull request! 💡

---

**Made with ❤️ for FIAP X**
