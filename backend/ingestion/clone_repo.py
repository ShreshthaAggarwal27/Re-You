import os
from git import Repo
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
REPO_URL = os.getenv("GITHUB_REPO_URL")
CLONE_DIR = "data/repo"

def clone_repo():
    if not ACCESS_TOKEN or not REPO_URL:
        raise ValueError("GitHub token or repo URL missing in .env")

    # Insert token into the repo URL for authentication
    if "https://" in REPO_URL:
        authed_url = REPO_URL.replace(
            "https://",
            f"https://{ACCESS_TOKEN}@"
        )
    else:
        raise ValueError("Invalid GitHub repo URL format")

    # Clone only if folder does not already exist
    if not os.path.exists(CLONE_DIR):
        print(f"Cloning repo into {CLONE_DIR}...")
        Repo.clone_from(authed_url, CLONE_DIR)
        print("✅ Cloning complete!")
    else:
        print("✅ Repo already cloned. Skipping.")

if __name__ == "__main__":
    clone_repo()
