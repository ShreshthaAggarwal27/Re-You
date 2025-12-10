import os
from git import Repo
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

def clone_specific_repo(full_name: str, clone_dir: str):
    """
    Clone a GitHub repo (owner/repo) into the given directory.
    """

    if not ACCESS_TOKEN:
        raise ValueError("Missing GitHub access token")

    owner, repo = full_name.split("/")

    # Construct authenticated HTTPS URL
    authed_url = f"https://{ACCESS_TOKEN}:x-oauth-basic@github.com/{full_name}.git"

    # If directory exists, skip
    if os.path.exists(clone_dir):
        print(f"📂 Repo already exists at: {clone_dir}")
        return clone_dir

    print(f"⬇️ Cloning {full_name} into {clone_dir} ...")

    Repo.clone_from(authed_url, clone_dir)

    print(f"✅ Cloned {full_name}")
    return clone_dir