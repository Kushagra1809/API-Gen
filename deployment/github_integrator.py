import base64
import github
from github import Github, GithubException
from nacl import encoding, public

def get_or_create_repo(token: str, repo_name: str, private: bool = True):
    g = Github(token)
    user = g.get_user()
    
    # Check if the repo_name includes username, e.g. "username/repo"
    if "/" in repo_name:
        repo_name = repo_name.split("/")[1]
    
    try:
        # Check if repo exists
        repo = user.get_repo(repo_name)
        return repo, False
    except GithubException as e:
        if e.status == 404:
            # Repo doesn't exist, create it
            repo = user.create_repo(repo_name, private=private, auto_init=True)
            return repo, True
        raise

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key_bytes = base64.b64decode(public_key)
    sealed_box = public.SealedBox(public.PublicKey(public_key_bytes))
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def set_repo_secrets(repo, secrets_dict: dict):
    if not secrets_dict:
        return

    for secret_name, secret_value in secrets_dict.items():
        if not secret_value:
            continue
        repo.create_secret(secret_name, secret_value, "actions")

def configure_github_actions(token: str, repo_name: str, pipeline_config: dict,
                              cloud_credentials: dict, is_private: bool = True):
    """
    All-in-one: generate pipeline, commit workflow files to the repo, and set secrets.
    Returns dict with repo_url, secrets_set, files_committed.
    """
    from deployment.cicd import generate_pipeline_config

    # 1. Generate the pipeline
    result = generate_pipeline_config(pipeline_config)

    # 2. Get or create the repo
    repo, created = get_or_create_repo(token, repo_name, is_private)

    # 3. Prepare files to commit
    files_to_commit = {}

    platform = pipeline_config.get("platform", "github")
    if platform == "github":
        files_to_commit[".github/workflows/deploy.yml"] = result["pipeline_yaml"]
    else:
        files_to_commit[".gitlab-ci.yml"] = result["pipeline_yaml"]

    if result.get("dockerfile"):
        files_to_commit["Dockerfile"] = result["dockerfile"]

    # 4. Commit workflow files to the repo
    push_files_to_repo(repo, files_to_commit, commit_message="Configure CI/CD via API Gen Platform")

    # 5. Set cloud credentials as repo secrets
    if cloud_credentials:
        set_repo_secrets(repo, cloud_credentials)

    return {
        "success": True,
        "repo_url": repo.html_url,
        "created_new_repo": created,
        "files_committed": list(files_to_commit.keys()),
        "secrets_set": [k for k, v in cloud_credentials.items() if v],
        "pipeline_result": result,
    }


def push_files_to_repo(repo, files_dict: dict, commit_message: str = "Initial API Gen commit"):
    """
    Push a dictionary of files {filepath: content} to the repository.
    """
    try:
        # Try to get the ref for the main branch
        ref = repo.get_git_ref("heads/main")
    except GithubException:
        try:
            # Fallback to master if main doesn't exist
            ref = repo.get_git_ref("heads/master")
        except GithubException:
            # Repo is completely empty, no branches yet
            # Create a dummy initial commit to initialize main
            repo.create_file("README.md", "Initial commit", "# Generated API\n", branch="main")
            ref = repo.get_git_ref("heads/main")
        
    branch_sha = ref.object.sha
    base_tree = repo.get_git_tree(branch_sha)
    
    element_list = []
    for filepath, content in files_dict.items():
        # Create a blob for each file
        blob = repo.create_git_blob(content, "utf-8")
        element = github.InputGitTreeElement(filepath, "100644", "blob", sha=blob.sha)
        element_list.append(element)
        
    # Create the new tree
    tree = repo.create_git_tree(element_list, base_tree)
    
    # Create the commit
    parent = repo.get_git_commit(branch_sha)
    commit = repo.create_git_commit(commit_message, tree, [parent])
    
    # Update the reference
    ref.edit(commit.sha)
