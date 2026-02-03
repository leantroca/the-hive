# The Hive

Local AI chat interface using Ollama and Open WebUI.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- (Optional) NVIDIA GPU with [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) for GPU acceleration

## Quick Start

1. **Start the services:**
   ```bash
   docker compose up -d
   ```

2. **Access Open WebUI:**
   Open http://localhost:3000 in your browser

3. **Create an account:**
   On first visit, create a local admin account

4. **Pull a model:**
   ```bash
   docker compose exec ollama ollama pull llama3
   ```

5. **Start chatting:**
   Select the model in Open WebUI and begin your conversation

## Available Models

Pull any model from the [Ollama library](https://ollama.com/library):

```bash
# Examples
docker compose exec ollama ollama pull llama3
docker compose exec ollama ollama pull mistral
docker compose exec ollama ollama pull codellama
docker compose exec ollama ollama pull phi3
```

List downloaded models:
```bash
docker compose exec ollama ollama list
```

## Configuration

### Without GPU

If you don't have an NVIDIA GPU, edit `docker-compose.yml` and remove the `deploy` section from the ollama service:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ./ollama-data:/root/.ollama
    restart: unless-stopped
```

### Change Ports

To use different ports, modify the `ports` section in `docker-compose.yml`:

```yaml
# Change Open WebUI port (default: 3000)
ports:
  - "8080:8080"  # Access at http://localhost:8080

# Change Ollama API port (default: 11434)
ports:
  - "11435:11434"  # API at http://localhost:11435
```

## Data Persistence

Data is stored in local directories:

- `./ollama-data/` - Downloaded models and Ollama configuration
- `./open-webui-data/` - User accounts, chat history, and settings

To reset everything, stop the services and delete these directories:
```bash
docker compose down
rm -rf ollama-data open-webui-data
```

## Common Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# View logs for a specific service
docker compose logs -f ollama
docker compose logs -f open-webui

# Restart services
docker compose restart

# Check service status
docker compose ps

# Pull latest images
docker compose pull
docker compose up -d
```

## Troubleshooting

### GPU not detected

Ensure nvidia-container-toolkit is installed:
```bash
# Ubuntu/Debian
sudo apt install nvidia-container-toolkit
sudo systemctl restart docker
```

Verify GPU access:
```bash
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

### Open WebUI can't connect to Ollama

1. Check if Ollama is running:
   ```bash
   docker compose ps
   ```

2. Check Ollama logs:
   ```bash
   docker compose logs ollama
   ```

3. Restart the services:
   ```bash
   docker compose restart
   ```

### Port already in use

Change the port in `docker-compose.yml` or stop the conflicting service:
```bash
# Find what's using port 3000
sudo lsof -i :3000
```
