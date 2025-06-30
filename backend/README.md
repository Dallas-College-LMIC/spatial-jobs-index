Build: nix build .#docker
Dev: uv run python -m uvicorn app.main:app --reload
