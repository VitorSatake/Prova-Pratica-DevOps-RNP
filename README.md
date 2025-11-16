# Prova-Pratica-DevOps-RNP

> Projeto de demonstração/avaliação para a prova prática DevOps — RNP

Este repositório contém um stack de observabilidade simples com Prometheus e Grafana, um banco Postgres e dois *agents* (ping e http) que coletam métricas e as expõem para o Prometheus. Está montado para rodar via Docker Compose.

## Visão geral

- Prometheus: coleta métricas dos agentes e do próprio Prometheus.
- Grafana: painel com dashboards pré-configurados (provisionados automaticamente).
- Postgres: armazena métricas (inicialização via `db/init.sql`).
- ping-agent: executa pings periódicos para alvos e expõe RTT/perda em /metrics.
- http-agent: realiza requisições HTTP periódicas e expõe tempos de resposta e status em /metrics.

Estrutura principal do repositório:

```
docker-compose.yml
db/
	init.sql
grafana/
	dashboards/
	provisioning/
prometheus/
	prometheus.yml
ping-agent/
	ping_agent.py
	Dockerfile
	requirements.txt
http-agent/
	http_agent.py
	Dockerfile
	requirements.txt
```

## Requisitos

- Docker (recomendo a versão mais recente)
- Docker Compose (ou `docker compose` integrado)
- (Opcional) Python 3.8+ para executar os agentes localmente

No Windows PowerShell, confirme as versões:

```powershell
docker --version
docker compose version
```

## Como rodar (modo rápido)

Na raiz do projeto (PowerShell):

```powershell
# sobe todos os serviços em background (rebuild quando necessário)
# copie o arquivo de exemplo de variáveis de ambiente e ajuste valores sensíveis
copy .env.example .env

# sobe todos os serviços em background (rebuild quando necessário)
docker compose up --build -d

# verificar logs (exemplo para grafana)
docker compose logs -f grafana
```

Observações:
- O `docker-compose.yml` já contém builds para `ping-agent` e `http-agent` (diretórios `ping-agent` e `http-agent`).
- Se estiver usando uma versão antiga do Compose, troque por `docker-compose`.

## Serviços e portas expostas

- Postgres: 5432 (usuário: `monitor`, senha: `monitor123`, bd: `metrics` conforme `docker-compose.yml`).
- Prometheus: 9090
- Grafana: 3000 (usuário `admin`, senha padrão `admin` — altere em produção)
- ping-agent: expõe /metrics em 8000 dentro do container
- http-agent: expõe /metrics em 8001 dentro do container

> Atenção: as credenciais e senhas estão em texto plano no compose para fins demonstrativos — não use em produção.

## Arquivos importantes

- `docker-compose.yml` — define os serviços, volumes e dependências.
- `prometheus/prometheus.yml` — configuração do Prometheus (jobs para coletar os agentes).
- `grafana/provisioning/` — configura dashboards e datasource para provisionamento automático.
- `db/init.sql` — script de inicialização do banco (cria tabela(s) usadas pelos agents).
- `ping-agent/` e `http-agent/` — código dos agentes, Dockerfile e `requirements.txt`.
 - `.env.example` — exemplo das variáveis de ambiente usadas pelo `docker-compose` (copie para `.env`).
 - `.github/workflows/ci.yml` — workflow do GitHub Actions que valida o compose, roda lint em Python e valida YAMLs.

## Como desenvolver / executar agentes localmente

É possível executar os agentes sem Docker, num ambiente virtual Python:

```powershell
cd .\ping-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\ping_agent.py

# idem para http-agent
cd ..\http-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\http_agent.py
```

Os agentes expõem métricas no endpoint HTTP (porta definida no código/Dockerfile). Configure o Prometheus para apontar para esses endpoints (o compose já faz isso).

## Banco de dados

O arquivo `db/init.sql` é montado no container Postgres para inicializar a(s) tabela(s). Se quiser recriar o banco localmente:

```powershell
docker compose down -v
docker compose up --build -d
```

Isso removerá volumes e recriará os dados a partir do script de inicialização.

## Validando as configurações

- Validar Compose:

```powershell
docker compose -f .\docker-compose.yml config
```

- Validar Prometheus (usando promtool via container):

```powershell
docker run --rm -v ${PWD}\prometheus:/prometheus prom/prometheus promtool check config /prometheus/prometheus.yml
```

- Validar dashboards grafana: abra http://localhost:3000 e verifique os painéis (usuário: `admin`).

## Observabilidade e troubleshooting

- Para ver métricas do Prometheus: http://localhost:9090
- Para ver logs de um serviço:

```powershell
docker compose logs -f ping-agent
docker compose logs -f http-agent
```

- Se algo falhar ao iniciar, verifique se as portas estão livres e se os volumes foram criados corretamente.

## Boas práticas e segurança

- Não deixe senhas em texto plano: utilize Docker secrets ou variáveis de ambiente gerenciadas por um orquestrador.
- Restrinja o acesso ao Grafana/Prometheus para redes confiáveis ou adicione autenticação/role-based access.

## Testes e QA rápidos

- Teste local de sintaxe Python:

```powershell
python -m py_compile .\ping-agent\ping_agent.py
python -m py_compile .\http-agent\http_agent.py
```

- Teste de integração rápido: subir stack e acessar os endpoints `/metrics` dos agentes via curl:

```powershell
curl http://localhost:8000/metrics
curl http://localhost:8001/metrics
```

## Integração Contínua (CI)

Este repositório já inclui um workflow de CI em `.github/workflows/ci.yml`. O que ele faz:

- Faz checkout do código.
- Configura Python 3.10 e instala `flake8` e `yamllint`.
- Roda checagens rápidas de sintaxe Python para os agentes e executa `flake8` (configurado com tolerâncias mínimas).
- Linta arquivos YAML importantes (`prometheus`, `grafana/provisioning` e `docker-compose.yml`).
- Valida o `docker-compose.yml` com `docker compose config` e valida o `prometheus/prometheus.yml` com `promtool` (executado em container oficial do Prometheus).

## Nota sobre variáveis expostas

Você certamente notará que este repositório (no `docker-compose.yml` e no `.env.example`) contém exemplos de variáveis e valores — inclusive senhas em texto claro para facilitar a execução local e a avaliação do projeto. Isso foi feito intencionalmente para demonstrar o funcionamento do stack de forma rápida.

Importante: essa não é a melhor prática para ambientes reais. Em produção recomenda-se fortemente utilizar mecanismos de gerenciamento de segredos, por exemplo:

- Docker secrets (Swarm) ou secrets do orquestrador que você estiver usando (Kubernetes Secrets, HashiCorp Vault, AWS Secrets Manager, etc.).
- Variáveis de ambiente definidas fora do repositório (não comitadas), ou uso de um provider de secrets com rotação/controle de acesso.

# Links de Repositórios

Praticas de Terraform para infraestrutura em cloud (aws):
[Terraform](https://github.com/VitorSatake/Terraform) <br>
https://github.com/VitorSatake/Terraform

Repositório onde se enontram diversos laboratórios de particas de processo de formação DevOps:
[DevOps](https://github.com/VitorSatake/Processo-Formacao-DevOps) <br>
https://github.com/VitorSatake/Processo-Formacao-DevOps