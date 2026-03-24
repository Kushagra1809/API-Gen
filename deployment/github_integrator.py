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

    # Get the public key for the repository to encrypt secrets
    key = repo.get_public_key()
    
    for secret_name, secret_value in secrets_dict.items():
        if not secret_value:
            continue
        encrypted_value = encrypt_secret(key.key, secret_value)
        repo.create_secret(secret_name, encrypted_value, key.key_id)

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
