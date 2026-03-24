"""
Deployment Configuration Generators — Docker, Kubernetes, AWS Lambda, Cloud Run, Vercel, Railway.
"""
from config import DEFAULT_PYTHON_VERSION, DEFAULT_PORT


def generate_dockerfile(
    framework: str = "fastapi",
    python_version: str = DEFAULT_PYTHON_VERSION,
    port: int = DEFAULT_PORT,
) -> str:
    """Generate a production-ready Dockerfile."""
    return f"""# ─── Multi-stage production Dockerfile ───
FROM python:{python_version}-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:{python_version}-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PORT={port}

EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:{port}/health')"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "{port}"]
"""


def generate_docker_compose(
    project_name: str = "my-api",
    port: int = DEFAULT_PORT,
) -> str:
    """Generate docker-compose.yml with optional Redis and Postgres."""
    return f"""version: '3.8'

services:
  api:
    build: .
    container_name: {project_name}-api
    ports:
      - "{port}:{port}"
    environment:
      - PORT={port}
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/{project_name}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{port}/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:16-alpine
    container_name: {project_name}-db
    environment:
      POSTGRES_DB: {project_name}
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    container_name: {project_name}-redis
    ports:
      - "6379:6379"

volumes:
  postgres_data:
"""


def generate_kubernetes_manifests(
    project_name: str = "my-api",
    port: int = DEFAULT_PORT,
    replicas: int = 3,
) -> str:
    """Generate Kubernetes deployment, service, and ingress."""
    return f"""# ─── Kubernetes Deployment ───
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {project_name}
  labels:
    app: {project_name}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {project_name}
  template:
    metadata:
      labels:
        app: {project_name}
    spec:
      containers:
        - name: {project_name}
          image: {project_name}:latest
          ports:
            - containerPort: {port}
          env:
            - name: PORT
              value: "{port}"
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: {port}
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health
              port: {port}
            initialDelaySeconds: 5
            periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: {project_name}-svc
spec:
  selector:
    app: {project_name}
  ports:
    - port: 80
      targetPort: {port}
  type: LoadBalancer

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {project_name}-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: {project_name}.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {project_name}-svc
                port:
                  number: 80
"""


def generate_aws_lambda(project_name: str = "my-api") -> str:
    """Generate AWS SAM template for Lambda deployment."""
    return f"""# ─── AWS SAM Template ───
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: {project_name} - Auto-generated REST API

Globals:
  Function:
    Timeout: 30
    MemorySize: 256
    Runtime: python3.11

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.handler
      CodeUri: .
      Description: {project_name} API handler
      Events:
        Api:
          Type: HttpApi
          Properties:
            Path: /{{proxy+}}
            Method: ANY

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${{ServerlessHttpApi}}.execute-api.${{AWS::Region}}.amazonaws.com/"
"""


def generate_cloud_run(project_name: str = "my-api") -> str:
    """Generate Google Cloud Run service configuration."""
    return f"""# ─── Google Cloud Run ───
# Deploy with: gcloud run deploy {project_name} --source .

apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: {project_name}
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containerConcurrency: 80
      containers:
        - image: gcr.io/PROJECT_ID/{project_name}
          ports:
            - containerPort: 8000
          resources:
            limits:
              memory: 512Mi
              cpu: "1"
"""


def generate_vercel_config(project_name: str = "my-api") -> str:
    """Generate Vercel deployment configuration."""
    return f"""{{
  "version": 2,
  "name": "{project_name}",
  "builds": [
    {{
      "src": "app.py",
      "use": "@vercel/python"
    }}
  ],
  "routes": [
    {{
      "src": "/(.*)",
      "dest": "app.py"
    }}
  ]
}}"""


def generate_railway_config(project_name: str = "my-api") -> str:
    """Generate Railway deployment configuration."""
    return f"""# ─── Railway Configuration ───
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
"""


def generate_all_deployment_configs(
    project_name: str = "my-api",
    framework: str = "fastapi",
) -> dict[str, str]:
    """Generate all deployment configurations at once."""
    return {
        "Dockerfile": generate_dockerfile(framework),
        "docker-compose.yml": generate_docker_compose(project_name),
        "k8s-manifests.yml": generate_kubernetes_manifests(project_name),
        "aws-sam-template.yml": generate_aws_lambda(project_name),
        "cloud-run.yml": generate_cloud_run(project_name),
        "vercel.json": generate_vercel_config(project_name),
        "railway.toml": generate_railway_config(project_name),
    }
