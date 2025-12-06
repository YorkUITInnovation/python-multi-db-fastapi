# Quick Reference: build.sh

## Setup (One-time)

```bash
# 1. Edit build.sh
DOCKER_USERNAME="your-dockerhub-username"  # REQUIRED

# 2. Make executable (if not already)
chmod +x build.sh
```

## Basic Usage

```bash
# Build and push to Docker Hub
./build.sh
```

## Common Configurations

### Production Release
```bash
# In build.sh:
IMAGE_TAG="1.0.0"
ADDITIONAL_TAGS="1.0 1 latest"
PLATFORMS="linux/amd64 linux/arm64"
PUSH_TO_HUB=true
```

### Development/Testing
```bash
# In build.sh:
IMAGE_TAG="dev"
ADDITIONAL_TAGS=""
PLATFORMS="linux/amd64"
PUSH_TO_HUB=false
```

### ARM-only Build
```bash
# In build.sh:
IMAGE_TAG="arm-latest"
PLATFORMS="linux/arm64 linux/arm/v7"
PUSH_TO_HUB=true
```

## Platform Options

| Platform | Description |
|----------|-------------|
| `linux/amd64` | x86-64 (Intel/AMD servers, cloud) |
| `linux/arm64` | ARM 64-bit (M1/M2, Graviton, Pi 4) |
| `linux/arm/v7` | ARM 32-bit (Pi 3, older devices) |

## Quick Tips

```bash
# Test build locally (don't push)
PUSH_TO_HUB=false ./build.sh

# Build single platform (faster)
PLATFORMS="linux/amd64" ./build.sh

# Override config from command line
IMAGE_TAG="test-$(date +%Y%m%d)" ./build.sh
```

## After Building

Your image is available at:
```bash
docker pull your-username/yorku-multi-db-api:latest
```

Use in docker-compose.yml:
```yaml
services:
  api:
    image: your-username/yorku-multi-db-api:latest
    # ... rest of config
```

## Troubleshooting

**Build fails on ARM:**
```bash
# Install QEMU (Linux)
sudo apt-get install -y qemu-user-static
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

**Login fails:**
```bash
# Use Docker Hub access token (not password)
docker login
# Username: your-username
# Password: [paste access token from hub.docker.com/settings/security]
```

**Check buildx:**
```bash
docker buildx version
# Should show: github.com/docker/buildx v0.x.x
```

## Full Documentation

See [BUILD_GUIDE.md](BUILD_GUIDE.md) for:
- Complete configuration options
- Advanced usage
- CI/CD integration
- Best practices
- Security tips

