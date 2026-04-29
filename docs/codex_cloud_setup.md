# Codex Cloud Setup

Codex Cloud environments are created in the web UI, not from this local checkout.

1. Create a private GitHub repository named `do-no-harm-retrieval-routing`.
2. Push this local repository to that private repository.
3. Open <https://chatgpt.com/codex>.
4. Connect the private GitHub repository.
5. Create a Cloud environment for the repository.
6. Enable network access.
7. Add secrets:
   - `HF_TOKEN`
   - `ANTHROPIC_API_KEY`
   - `GOOGLE_API_KEY`
8. Use `scripts/setup_cloud.sh` as the setup script.
9. Run Task 1 from `configs/codex_cloud_tasks.md`.

After the environment exists, submit tasks locally with:

```powershell
codex cloud exec --env <ENV_ID> --branch main "Run Task 1 from configs/codex_cloud_tasks.md"
```

The current local repository has no remote configured. After creating the private GitHub repo, run:

```powershell
git remote add origin <PRIVATE_REPO_URL>
git add .
git commit -m "Bootstrap do-no-harm retrieval routing experiments"
git push -u origin main
```

Do not commit `.env`, run caches, model weights, or generated full experiment outputs.
