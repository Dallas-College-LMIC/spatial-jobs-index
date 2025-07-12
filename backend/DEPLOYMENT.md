# Automated Deployment Setup

## Overview
This project now includes automated deployment to your VPS whenever you push code to the main branch.

## Required GitHub Secrets

You need to add these secrets to your GitHub repository:

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Add the following secrets:

### `VPS_HOST`
- **Value**: Your VPS IP address or hostname
- **Example**: `192.168.1.100` or `your-domain.com`

### `VPS_USER`
- **Value**: SSH username for your VPS
- **Example**: `root` or `ubuntu` or your custom username

### `VPS_SSH_KEY`
- **Value**: Private SSH key content for authentication
- **How to get**: Run `cat ~/.ssh/id_rsa` on your local machine (or the key you use to SSH to your VPS)
- **Format**: Copy the entire key including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`

## VPS Setup Requirements

1. **Docker Compose Location**: The deployment assumes your docker-compose.yml is located at `~/projects/spatial-jobs-index-api/`
   - If it's elsewhere, update the path in `.github/workflows/build.yml` line 44

2. **Docker Compose File**: Ensure your docker-compose.yml uses the correct image:
   ```yaml
   services:
     api:
       image: ghcr.io/dallas-college-lmic/spatial-jobs-index-api:latest
       # ... other configuration
   ```

3. **SSH Access**: Ensure your VPS accepts SSH connections from GitHub Actions

4. **Docker Group Access**: The deployment runs docker commands without sudo
   - **REQUIRED**: Add your SSH user to the docker group on your VPS:
     ```bash
     sudo usermod -aG docker $USER
     newgrp docker
     ```
   - **Verify**: Test that docker commands work without sudo:
     ```bash
     docker --version
     docker compose version
     ```

## How It Works

1. **Push to main branch** → GitHub Actions triggers
2. **Build Docker image** → Push to GitHub Container Registry
3. **Deploy to VPS** → SSH into VPS, pull latest image, restart containers
4. **Health check** → Verify API is responding at `http://localhost:8000/docs`

## Troubleshooting

- **SSH connection fails**: Check your SSH key and VPS firewall settings
- **Health check fails**: Verify your API starts correctly and is accessible on port 8000
- **Permission denied**: Ensure your SSH user has permission to run Docker commands

### Docker Permission Issues
If you see errors like "permission denied" or "Cannot connect to the Docker daemon" during deployment:

1. **Ensure user is in docker group**:
   ```bash
   groups $USER
   ```
   Should show "docker" in the list.

2. **If not in docker group, add user**:
   ```bash
   sudo usermod -aG docker $USER
   ```

3. **Apply group changes** (requires logout/login or):
   ```bash
   newgrp docker
   ```

4. **Test docker access**:
   ```bash
   docker ps
   docker compose version
   ```

5. **Restart Docker service if needed**:
   ```bash
   sudo systemctl restart docker
   ```

## Manual Deployment

If you need to deploy manually, you can still use the deployment script:
```bash
./deploy.sh
```

This script is also available on your VPS and performs the same deployment steps.
