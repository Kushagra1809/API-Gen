"""
Pydantic schemas for request / response validation.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ─── API Discovery ──────────────────────────────────────

class DiscoverRequest(BaseModel):
    idea: str = Field(..., min_length=3, description="Application idea description")


class APIRecommendation(BaseModel):
    name: str
    provider: str
    category: str
    description: str
    free_tier: bool
    pricing_model: str
    pricing_details: str
    auth_type: str
    documentation_url: str
    base_url: str
    sdk_languages: list[str]
    request_limit: str
    github_url: str
    composite_score: float
    popularity_score: float
    reliability_score: float
    alternatives: list[str]
    tags: list[str]


class FeatureBreakdown(BaseModel):
    feature: str
    category: str
    icon: str
    apis: list[APIRecommendation]


class DiscoverResponse(BaseModel):
    idea: str
    features: list[FeatureBreakdown]
    total_apis: int


# ─── API Catalog ────────────────────────────────────────

class APISummary(BaseModel):
    id: int
    name: str
    slug: str
    provider: str
    category: str
    free_tier: bool
    pricing_model: str
    composite_score: float
    is_active: bool
    tags: list[str]

    class Config:
        from_attributes = True


class APIDetail(APIRecommendation):
    id: int
    slug: str
    is_active: bool
    last_verified: Optional[datetime] = None
    last_response_ms: Optional[int] = None

    class Config:
        from_attributes = True


class CategoryOut(BaseModel):
    id: int
    name: str
    display_name: str
    description: str
    icon: str
    api_count: int


# ─── Health Check ───────────────────────────────────────

class HealthCheckResult(BaseModel):
    api_name: str
    is_reachable: bool
    status_code: Optional[int] = None
    response_ms: Optional[int] = None
    doc_reachable: bool
    error: str = ""
    checked_at: datetime


# ─── Code Analyzer ──────────────────────────────────────

class FunctionInfo(BaseModel):
    name: str
    docstring: str = ""
    parameters: list[dict]          # [{name, type, default}]
    return_type: str = "Any"
    is_async: bool = False
    decorators: list[str] = []
    file: str


class ClassInfo(BaseModel):
    name: str
    docstring: str = ""
    methods: list[FunctionInfo]
    file: str


class AnalysisResult(BaseModel):
    project_name: str
    files_scanned: int
    functions: list[FunctionInfo]
    classes: list[ClassInfo]
    has_async: bool
    has_db_models: bool
    has_ml_models: bool
    has_file_io: bool
    framework_recommendation: str
    framework_reason: str


# ─── REST Generator ────────────────────────────────────

class EndpointDef(BaseModel):
    method: str             # GET, POST, PUT, DELETE
    path: str
    function_name: str
    summary: str
    request_body: Optional[dict] = None
    response_schema: Optional[dict] = None
    tags: list[str] = []


class GenerateRequest(BaseModel):
    project_name: str = "my_project"
    files: dict[str, str]   # {filename: source_code}
    framework: Optional[str] = None   # auto-detect if None


class GenerateResponse(BaseModel):
    project_id: int
    project_name: str
    framework: str
    framework_reason: str
    endpoints: list[EndpointDef]
    generated_files: dict[str, str]
    openapi_spec: dict
    deployment_configs: dict[str, str]


# ─── Agent ──────────────────────────────────────────────

class AgentQuery(BaseModel):
    query: str = Field(..., min_length=3)
    auto_integrate: bool = False


class AgentResponse(BaseModel):
    query: str
    reasoning: str
    recommendations: list[APIRecommendation]
    integration_snippets: dict[str, str] = {}


# ─── CI/CD Generator ──────────────────────────────────────

class CICDRequest(BaseModel):
    platform: str = "github"
    project_name: str = "my_project"
    language: str = "python"
    framework: str = "fastapi"
    package_manager: str = "pip"
    test_command: str = ""
    build_command: str = ""
    port: str = "8000"
    needs_dockerfile: bool = False
    deploy_targets: list[str] = []
    cloud_config: dict = {}
    registry: str = "dockerhub"
    project_id: Optional[int] = None


class CICDResponse(BaseModel):
    pipeline_yaml: str
    dockerfile: Optional[str] = None
    secrets: list[str]
    instructions: str


class GitHubPushRequest(BaseModel):
    project_id: int
    github_token: str
    repo_name: str
    secrets: dict[str, str] = {}
    is_private: bool = True

class GitHubSettings(BaseModel):
    github_token: Optional[str] = None
    default_repo: Optional[str] = None

class GitHubSettingsUpdate(BaseModel):
    github_token: str
    default_repo: str


class ConfigureActionsRequest(BaseModel):
    """Request to configure GitHub Actions on a repository."""
    github_token: str
    repo_name: str
    is_private: bool = True
    # Pipeline configuration (same fields as CICDRequest)
    platform: str = "github"
    project_name: str = "my_project"
    language: str = "python"
    framework: str = "fastapi"
    package_manager: str = "pip"
    test_command: str = ""
    build_command: str = ""
    port: str = "8000"
    needs_dockerfile: bool = False
    deploy_targets: list[str] = []
    registry: str = "dockerhub"
    # Cloud credentials — key-value of secret name to value
    cloud_credentials: dict[str, str] = {}
