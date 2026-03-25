import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from deployment.cicd import generate_pipeline_config
from deployment.generators import generate_all_deployment_configs

# Case 1: Render deployment
config_render = {
    "platform": "github",
    "project_name": "test_render",
    "language": "python",
    "deploy_targets": ["render"],
    "registry": "dockerhub"
}

result = generate_pipeline_config(config_render)
print("--- Render Pipeline Config ---")
print(result["pipeline_yaml"])
print("\n--- Required Secrets ---")
print(result["secrets"])

print("\n--- Render Blueprint (render.yaml) ---")
configs = generate_all_deployment_configs("test_render")
print(configs.get("render.yaml", "NOT FOUND"))

