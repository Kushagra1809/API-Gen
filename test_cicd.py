import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from deployment.cicd import generate_pipeline_config

# Case 1: Vercel deployment (should NOT have docker-push, but might mistakenly 'need' it)
config_vercel = {
    "platform": "github",
    "project_name": "test_vercel",
    "language": "python",
    "deploy_targets": ["vercel"],
    "registry": "dockerhub"
}

result = generate_pipeline_config(config_vercel)
print("--- Vercel Config ---")
print(result["pipeline_yaml"])

# Case 2: No targets (should NOT have deploy job at all)
config_no_targets = {
    "platform": "github",
    "project_name": "test_none",
    "language": "python",
    "deploy_targets": [],
    "registry": "dockerhub"
}
result_none = generate_pipeline_config(config_no_targets)
print("\n--- No Targets Config ---")
print(result_none["pipeline_yaml"])
