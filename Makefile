# ========= Config (overridable: make VAR=value ...) =========
AWS_REGION ?= eu-west-3
REPO_NAME  ?= fastapi-inventory
DOCKER_PLATFORM ?= linux/amd64  

ACCOUNT_ID ?= $(shell aws sts get-caller-identity --query Account --output text 2>/dev/null)
ECR_URI    := $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(REPO_NAME)

GIT_SHA    := $(shell git rev-parse --short HEAD 2>/dev/null)
IMAGE_TAG  ?= $(if $(GIT_SHA),$(GIT_SHA),local)

PY         ?= python
PIP        ?= $(PY) -m pip

.DEFAULT_GOAL := help


help:
	@echo "\nTargets disponibles:\n"
	@grep -E '^[a-zA-Z0-9_-]+:.*?##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-26s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ================ Dev =================
deps:
	$(PIP) install -r requirements.txt

run: 
	uvicorn app.main:app --reload

test:
	pytest -q

env-copy: 
	@test -f .env || cp .env.example .env

clean-pyc: 
	find . -name "__pycache__" -type d -exec rm -rf {} +; \
	find . -name "*.pyc" -delete

clean-db: ## Remove SQLite local (dev.db)
	rm -f dev.db

# ============== Alembic ==============
alembic-up: ## Migrate DB a head
	alembic upgrade head

alembic-down: ## Reverse migration (downgrade -1)
	alembic downgrade -1

alembic-new: ## Create new migration: make alembic-new NAME="mensaje"
	@test -n "$(NAME)" || (echo "Uso: make alembic-new NAME=\"mensaje\""; exit 1)
	alembic revision -m "$(NAME)" --autogenerate

# ============== Docker / ECR ==============
print-ecr: ## Muestra variables calculates
	@echo "ACCOUNT_ID = $(ACCOUNT_ID)"
	@echo "AWS_REGION = $(AWS_REGION)"
	@echo "REPO_NAME  = $(REPO_NAME)"
	@echo "ECR_URI    = $(ECR_URI)"
	@echo "IMAGE_TAG  = $(IMAGE_TAG)"
	@echo "DOCKER_PLATFORM = $(DOCKER_PLATFORM)"

docker-build: ## Build docker image (platform=$(DOCKER_PLATFORM))
	docker build --platform=$(DOCKER_PLATFORM) -t $(REPO_NAME):$(IMAGE_TAG) .

docker-tag-latest: ## Etiqueta la imagen como :latest y con ECR URI
	@test -n "$(ACCOUNT_ID)" || (echo "ACCOUNT_ID vacío. ¿Configuraste aws cli?"; exit 1)
	docker tag $(REPO_NAME):$(IMAGE_TAG) $(ECR_URI):$(IMAGE_TAG)
	docker tag $(REPO_NAME):$(IMAGE_TAG) $(ECR_URI):latest

docker-push: ## Empuja la imagen a ECR (tag y latest)
	@test -n "$(ACCOUNT_ID)" || (echo "ACCOUNT_ID vacío. ¿Configuraste aws cli?"; exit 1)
	docker push $(ECR_URI):$(IMAGE_TAG)
	docker push $(ECR_URI):latest

ecr-create-repo: ## Crea el repositorio en ECR si no existe
	aws ecr create-repository --repository-name $(REPO_NAME) --region $(AWS_REGION) >/dev/null 2>&1 || true

ecr-login: ## Login de Docker en ECR
	@test -n "$(ACCOUNT_ID)" || (echo "ACCOUNT_ID vacío. Ejecuta 'aws configure' y repite."; exit 1)
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

ecr-push: ecr-create-repo ecr-login docker-build docker-tag-latest docker-push ## Build+push a ECR (sha y latest)
	@echo "Imagen publicada en: $(ECR_URI):$(IMAGE_TAG) y :latest"
