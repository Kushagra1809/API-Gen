"""
REST API Generator Routes — analyze Python code and generate REST APIs.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import GeneratedProject, UserSettings
from schemas import (
    GenerateRequest, GenerateResponse, AnalysisResult, 
    CICDRequest, CICDResponse, GitHubPushRequest,
    GitHubSettings, GitHubSettingsUpdate
)
from generator.analyzer import analyze_project
from generator.rest_generator import (
    generate_endpoints, 
    generate_fastapi_code,
    generate_express_code,
    generate_spring_code,
    generate_express_ts_code,
    generate_gin_code,
    generate_aspnet_code
)
from generator.doc_generator import generate_openapi_spec, generate_example_requests
from deployment.generators import generate_all_deployment_configs
from gateway.gateway_gen import generate_gateway_config

router = APIRouter(prefix="/api", tags=["Generator"])


@router.post("/analyze")
def analyze_code(request: GenerateRequest):
    """
    🔬 Analyze Python code without generating REST API.

    Upload Python source files as {filename: source_code} and get
    detailed analysis: functions, classes, type hints, and framework recommendation.
    """
    analysis = analyze_project(request.project_name, request.files)
    return analysis


@router.post("/generate-pipeline", response_model=CICDResponse)
def generate_pipeline(request: CICDRequest, db: Session = Depends(get_db)):
    """
    🚀 Generate CI/CD Pipeline Configuration
    
    Creates a fully configured deployment pipeline for GitHub Actions or GitLab CI,
    along with a Dockerfile if requested, and provides setup instructions.
    """
    from deployment.cicd import generate_pipeline_config
    
    try:
        result = generate_pipeline_config(request.dict())
        
        # Persist to database if project_id is provided
        if request.project_id:
            project = db.query(GeneratedProject).filter_by(id=request.project_id).first()
            if project:
                if not project.deployment_configs:
                    project.deployment_configs = {}
                
                pipeline_filename = ".github/workflows/deploy.yml" if request.platform == "github" else ".gitlab-ci.yml"
                project.deployment_configs[pipeline_filename] = result["pipeline_yaml"]
                project.deployment_configs["CI/CD Instructions"] = result["instructions"]
                
                if result.get("dockerfile"):
                    project.deployment_configs["Dockerfile"] = result["dockerfile"]
                
                # Use flag_modified to ensure SQLAlchemy tracks the change to the JSON field
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(project, "deployment_configs")
                db.commit()

        return CICDResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate CI/CD pipeline: {str(e)}")


@router.post("/generate")
def generate_api(request: GenerateRequest, db: Session = Depends(get_db)):
    """
    🚀 Generate a complete REST API from Python source code.

    Upload Python source files and receive:
    - Auto-generated REST endpoints
    - Complete FastAPI application code
    - OpenAPI specification
    - Deployment configurations (Docker, K8s, AWS Lambda, etc.)
    - API gateway middleware
    """
    # Step 1: Analyze the project
    analysis = analyze_project(request.project_name, request.files)

    if not analysis.get("functions") and not analysis.get("classes"):
        raise HTTPException(
            status_code=400,
            detail="No public functions or classes found in the provided code."
        )

    # Step 2: Generate endpoint definitions
    endpoints = generate_endpoints(analysis)

    # Step 3: Determine framework
    framework = request.framework or analysis.get("framework_recommendation", "fastapi")

    # Step 4: Generate application code
    if framework == "express":
        generated_files = generate_express_code(
            project_name=request.project_name,
            endpoints=endpoints,
            original_files=request.files,
        )
    elif framework == "express_ts":
        generated_files = generate_express_ts_code(
            project_name=request.project_name,
            endpoints=endpoints,
            original_files=request.files,
        )
    elif framework == "gin":
        generated_files = generate_gin_code(
            project_name=request.project_name,
            endpoints=endpoints,
            original_files=request.files,
        )
    elif framework == "asp_net":
        generated_files = generate_aspnet_code(
            project_name=request.project_name,
            endpoints=endpoints,
            original_files=request.files,
        )
    elif framework == "spring_boot":
        generated_files = generate_spring_code(
            project_name=request.project_name,
            endpoints=endpoints,
            original_files=request.files,
        )
    else:
        generated_files = generate_fastapi_code(
            project_name=request.project_name,
            endpoints=endpoints,
            original_files=request.files,
        )

    # Step 5: Generate OpenAPI spec
    openapi_spec = generate_openapi_spec(request.project_name, endpoints)

    # Step 6: Generate deployment configs
    deployment_configs = generate_all_deployment_configs(request.project_name, framework)

    # Step 7: Generate gateway middleware
    gateway_files = generate_gateway_config(request.project_name)
    generated_files.update(gateway_files)

    # Step 8: Generate example requests
    examples = generate_example_requests(endpoints)

    # Step 9: Save to database
    project = GeneratedProject(
        project_name=request.project_name,
        original_files=request.files,
        analysis_result=analysis,
        framework=framework,
        generated_files=generated_files,
        openapi_spec=openapi_spec,
        deployment_configs=deployment_configs,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Prepare endpoint summaries
    endpoint_defs = [
        {
            "method": ep["method"],
            "path": ep["path"],
            "function_name": ep["function_name"],
            "summary": ep.get("summary", ""),
            "tags": ep.get("tags", []),
        }
        for ep in endpoints
    ]

    return {
        "project_id": project.id,
        "project_name": request.project_name,
        "framework": framework,
        "framework_reason": analysis.get("framework_reason", ""),
        "endpoints": endpoint_defs,
        "generated_files": generated_files,
        "openapi_spec": openapi_spec,
        "deployment_configs": deployment_configs,
        "examples": examples,
        "analysis": {
            "files_scanned": analysis.get("files_scanned", 0),
            "functions_found": len(analysis.get("functions", [])),
            "classes_found": len(analysis.get("classes", [])),
            "has_async": analysis.get("has_async", False),
            "has_db_models": analysis.get("has_db_models", False),
            "has_ml_models": analysis.get("has_ml_models", False),
        },
    }


@router.get("/generate/{project_id}")
def get_generated_project(project_id: int, db: Session = Depends(get_db)):
    """📦 Retrieve a previously generated project."""
    project = db.query(GeneratedProject).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "project_id": project.id,
        "project_name": project.project_name,
        "framework": project.framework,
        "generated_files": project.generated_files,
        "openapi_spec": project.openapi_spec,
        "deployment_configs": project.deployment_configs,
        "created_at": project.created_at.isoformat(),
    }


@router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    """📋 List all generated projects."""
    projects = db.query(GeneratedProject).order_by(GeneratedProject.created_at.desc()).all()
    return [
        {
            "id": p.id,
            "project_name": p.project_name,
            "framework": p.framework,
            "created_at": p.created_at.isoformat(),
            "file_count": len(p.generated_files or {}),
        }
        for p in projects
    ]


@router.post("/push-to-github")
def push_to_github(request: GitHubPushRequest, db: Session = Depends(get_db)):
    """🐙 Push a generated project to GitHub and configure Action secrets."""
    project = db.query(GeneratedProject).filter_by(id=request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    from deployment.github_integrator import get_or_create_repo, set_repo_secrets, push_files_to_repo

    try:
        # Create or fetch repo
        repo, created = get_or_create_repo(request.github_token, request.repo_name, request.is_private)
        
        # Set secrets
        set_repo_secrets(repo, request.secrets)
        
        # Collect all files (generated sources + deployment configs)
        all_files = {}
        if project.generated_files:
            all_files.update(project.generated_files)
            
        if project.deployment_configs:
            for k, v in project.deployment_configs.items():
                if k != "CI/CD Instructions":
                    all_files[k] = v
                    
        if project.openapi_spec:
            import json
            all_files["openapi.json"] = json.dumps(project.openapi_spec, indent=2)

        # Push files
        push_files_to_repo(repo, all_files, commit_message="Initial commit from API Gen Platform")
        
        return {
            "success": True, 
            "repo_url": repo.html_url,
            "created_new_repo": created
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings/github", response_model=GitHubSettings)
def get_github_settings(db: Session = Depends(get_db)):
    """Fetch saved GitHub credentials."""
    settings = db.query(UserSettings).first()
    if not settings:
        return GitHubSettings(github_token="", default_repo="")
    return GitHubSettings(
        github_token=settings.github_token or "",
        default_repo=settings.default_repo or ""
    )


@router.post("/settings/github")
def update_github_settings(settings_in: GitHubSettingsUpdate, db: Session = Depends(get_db)):
    """Update saved GitHub credentials."""
    settings = db.query(UserSettings).first()
    if not settings:
        settings = UserSettings()
        db.add(settings)
    
    settings.github_token = settings_in.github_token
    settings.default_repo = settings_in.default_repo
    db.commit()
    return {"success": True}
