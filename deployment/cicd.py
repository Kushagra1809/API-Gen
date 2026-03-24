import json

def generate_pipeline_config(config: dict) -> dict:
    """
    Generate CI/CD pipeline configuration based on user input.
    Returns: {"pipeline_yaml": str, "dockerfile": str|null, "secrets": list, "instructions": str}
    """
    platform = config.get("platform", "github")
    project_name = config.get("project_name", "my_project")
    language = config.get("language", "python")
    framework = config.get("framework", "fastapi")
    package_manager = config.get("package_manager", "pip")
    test_command = config.get("test_command", "python -m pytest")
    build_command = config.get("build_command", "")
    port = config.get("port", "8000")
    needs_dockerfile = config.get("needs_dockerfile", False)
    deploy_targets = config.get("deploy_targets", [])
    cloud_config = config.get("cloud_config", {})
    registry = config.get("registry", "dockerhub")

    dockerfile_content = None
    if needs_dockerfile:
        dockerfile_content = _generate_dockerfile(language, package_manager, build_command, port)

    pipeline_yaml = ""
    secrets = []
    
    if platform == "github":
        pipeline_yaml, required_secrets = _generate_github_actions(config)
        secrets.extend(required_secrets)
    elif platform == "gitlab":
        pipeline_yaml, required_secrets = _generate_gitlab_ci(config)
        secrets.extend(required_secrets)
        
    instructions = _generate_instructions(platform, secrets)
    
    return {
        "pipeline_yaml": pipeline_yaml,
        "dockerfile": dockerfile_content,
        "secrets": list(set(secrets)),
        "instructions": instructions
    }

def _generate_dockerfile(language: str, pm: str, build_cmd: str, port: str) -> str:
    if language.lower() == "python":
        return f"""FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE {port}
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}"]
"""
    elif language.lower() in ["node.js", "javascript", "typescript"]:
        build_step = f"RUN {build_cmd}" if build_cmd else ""
        return f"""FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
{build_step}
EXPOSE {port}
CMD ["npm", "start"]
"""
    elif language.lower() == "go":
        return f"""FROM golang:1.20-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o main .

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/main .
EXPOSE {port}
CMD ["./main"]
"""
    elif language.lower() in ["java", "spring boot"]:
        return f"""FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE {port}
CMD ["java", "-jar", "app.jar"]
"""
    elif language.lower() in ["c#", "dotnet", "asp.net"]:
        return f"""FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY *.csproj ./
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE {port}
ENTRYPOINT ["dotnet", "App.dll"]
"""
    return f"""FROM ubuntu:latest
WORKDIR /app
COPY . .
EXPOSE {port}
CMD ["./start.sh"]
"""

def _generate_github_actions(config: dict) -> tuple[str, list[str]]:
    lang = config.get("language", "python").lower()
    pm = config.get("package_manager", "pip").lower()
    test_cmd = config.get("test_command", "python -m pytest")
    build_cmd = config.get("build_command", "")
    targets = config.get("deploy_targets", [])
    registry = config.get("registry", "dockerhub")
    
    secrets = []
    
    # Base setup
    yaml = [
        "name: CI/CD Pipeline",
        "",
        "on:",
        "  push:",
        "    branches: [ main ]",
        "  pull_request:",
        "    branches: [ main ]",
        "",
        "jobs:",
        "  test-and-build:",
        "    runs-on: ubuntu-latest",
        "    steps:",
        "      - name: Checkout Code",
        "        uses: actions/checkout@v3",
        ""
    ]
    
    # Language setup
    if lang == "python":
        yaml.extend([
            "      - name: Setup Python",
            "        uses: actions/setup-python@v4",
            "        with:",
            "          python-version: '3.10'",
            "          cache: 'pip'",
            "      - name: Install Dependencies",
            f"        run: {pm} install -r requirements.txt",
        ])
    elif lang in ["node.js", "javascript", "typescript"]:
        yaml.extend([
            "      - name: Setup Node.js",
            "        uses: actions/setup-node@v3",
            "        with:",
            "          node-version: '18'",
            f"          cache: '{'npm' if pm == 'npm' else 'yarn'}'",
            "      - name: Install Dependencies",
            f"        run: {pm} install",
        ])
    elif lang == "go":
        yaml.extend([
            "      - name: Setup Go",
            "        uses: actions/setup-go@v4",
            "        with:",
            "          go-version: '1.20'",
            "          cache: true",
        ])
    elif lang in ["java", "spring boot"]:
        yaml.extend([
            "      - name: Setup Java",
            "        uses: actions/setup-java@v3",
            "        with:",
            "          java-version: '17'",
            "          distribution: 'temurin'",
            "          cache: 'maven'",
        ])
        
    # Test & Build
    if test_cmd:
        yaml.extend([
            "      - name: Run Tests",
            f"        run: {test_cmd}"
        ])
        
    if build_cmd and lang not in ["python"]: # Python generally doesn't need a build step
        yaml.extend([
            "      - name: Build Application",
            f"        run: {build_cmd}"
        ])
        
    # Docker Push
    has_docker_push = False
    needs_docker = len(targets) > 0 and not all(t in ["vercel", "netlify", "railway"] for t in targets)
    
    if needs_docker:
        has_docker_push = True
        yaml.extend([
            "",
            "  docker-push:",
            "    needs: test-and-build",
            "    runs-on: ubuntu-latest",
            "    if: github.ref == 'refs/heads/main'",
            "    steps:",
            "      - uses: actions/checkout@v3",
        ])
        
        if registry == "dockerhub":
            secrets.extend(["DOCKER_USERNAME", "DOCKER_PASSWORD"])
            yaml.extend([
                "      - name: Log in to Docker Hub",
                "        uses: docker/login-action@v2",
                "        with:",
                "          username: ${{ secrets.DOCKER_USERNAME }}",
                "          password: ${{ secrets.DOCKER_PASSWORD }}",
                "      - name: Build and push Docker image",
                "        uses: docker/build-push-action@v4",
                "        with:",
                "          context: .",
                "          push: true",
                "          tags: ${{ secrets.DOCKER_USERNAME }}/app:${{ github.sha }},${{ secrets.DOCKER_USERNAME }}/app:latest"
            ])
        elif registry == "ghcr":
            yaml.extend([
                "      - name: Log in to GitHub Container Registry",
                "        uses: docker/login-action@v2",
                "        with:",
                "          registry: ghcr.io",
                "          username: ${{ github.actor }}",
                "          password: ${{ secrets.GITHUB_TOKEN }}",
                "      - name: Build and push Docker image",
                "        uses: docker/build-push-action@v4",
                "        with:",
                "          context: .",
                "          push: true",
                "          tags: ghcr.io/${{ github.repository }}/app:latest"
            ])
            
    # Deployments
    if len(targets) > 0:
        yaml.extend([
            "",
            "  deploy:",
            f"    needs: [test-and-build{', docker-push' if has_docker_push else ''}]",
            "    runs-on: ubuntu-latest",
            "    if: github.ref == 'refs/heads/main'",
            "    steps:",
            "      - uses: actions/checkout@v3",
        ])
        
        if "aws" in targets:
            aws_svc = config.get("cloud_config", {}).get("aws_service", "ec2")
            secrets.extend(["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"])
            yaml.extend([
                "      - name: Configure AWS credentials",
                "        uses: aws-actions/configure-aws-credentials@v2",
                "        with:",
                "          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}",
                "          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}",
                "          aws-region: ${{ secrets.AWS_REGION }}"
            ])
            if aws_svc == "ecs":
                yaml.extend([
                    "      - name: Deploy to Amazon ECS",
                    "        run: |",
                    "          aws ecs update-service --cluster my-cluster --service my-service --force-new-deployment"
                ])
                
        if "gcp" in targets:
            secrets.extend(["GCP_CREDENTIALS"])
            yaml.extend([
                "      - name: Authenticate to Google Cloud",
                "        uses: google-github-actions/auth@v1",
                "        with:",
                "          credentials_json: ${{ secrets.GCP_CREDENTIALS }}",
                "      - name: Deploy to Cloud Run",
                "        run: gcloud run deploy my-app --image=gcr.io/my-project/my-app:latest --region=us-central1"
            ])
            
        if "vercel" in targets:
            secrets.extend(["VERCEL_TOKEN", "VERCEL_PROJECT_ID", "VERCEL_ORG_ID"])
            yaml.extend([
                "      - name: Deploy to Vercel",
                "        uses: amondnet/vercel-action@v20",
                "        with:",
                "          vercel-token: ${{ secrets.VERCEL_TOKEN }}",
                "          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}",
                "          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}",
                "          vercel-args: '--prod'"
            ])

    return "\n".join(yaml), secrets

def _generate_gitlab_ci(config: dict) -> tuple[str, list[str]]:
    test_cmd = config.get("test_command", "pytest")
    build_cmd = config.get("build_command", "")
    targets = config.get("deploy_targets", [])
    registry = config.get("registry", "dockerhub")
    
    secrets = []
    
    yaml = [
        "stages:",
        "  - test",
        "  - build",
        "  - docker-push",
        "  - deploy",
        "",
        "test_job:",
        "  stage: test",
        "  script:",
        f"    - {test_cmd}",
        ""
    ]
    
    if build_cmd:
        yaml.extend([
            "build_job:",
            "  stage: build",
            "  script:",
            f"    - {build_cmd}",
            ""
        ])
        
    if registry == "dockerhub":
        secrets.extend(["DOCKER_USERNAME", "DOCKER_PASSWORD"])
        yaml.extend([
            "docker_build:",
            "  stage: docker-push",
            "  image: docker:20.10.16",
            "  services:",
            "    - docker:20.10.16-dind",
            "  script:",
            "    - docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD",
            "    - docker build -t $DOCKER_USERNAME/app:$CI_COMMIT_SHA .",
            "    - docker push $DOCKER_USERNAME/app:$CI_COMMIT_SHA",
            "  only:",
            "    - main",
            ""
        ])
        
    if "aws" in targets:
        secrets.extend(["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION"])
        yaml.extend([
            "deploy_aws:",
            "  stage: deploy",
            "  image: amazon/aws-cli",
            "  script:",
            "    - aws sts get-caller-identity # Verify auth",
            "    - echo 'Deploying to AWS...'",
            "  only:",
            "    - main",
            ""
        ])

    return "\n".join(yaml), secrets

def _generate_instructions(platform: str, secrets: list[str]) -> str:
    parts = []
    if platform == "github":
        parts.append("### Setup Instructions (GitHub Actions)")
        parts.append("1. Create `.github/workflows/deploy.yml` in your repository and paste the pipeline YAML.")
        if secrets:
            parts.append("2. Go to your GitHub Repository -> **Settings** -> **Secrets and variables** -> **Actions**.")
            parts.append("3. Click **New repository secret** and add the following secrets:")
            for s in sorted(list(set(secrets))):
                parts.append(f"   - `{s}`")
        parts.append(f"{'4' if secrets else '2'}. Push your code to the `main` branch to trigger the pipeline automatically.")
    else:
        parts.append("### Setup Instructions (GitLab CI/CD)")
        parts.append("1. Create `.gitlab-ci.yml` in the root of your repository and paste the pipeline YAML.")
        if secrets:
            parts.append("2. Go to your GitLab Repository -> **Settings** -> **CI/CD** -> **Variables**.")
            parts.append("3. Click **Add variable** and add the following required variables:")
            for s in sorted(list(set(secrets))):
                parts.append(f"   - `{s}`")
        parts.append(f"{'4' if secrets else '2'}. Push your code to the `main` branch to trigger the pipeline.")
        
    return "\n".join(parts)
