# Docker Multi-Architecture Build Guide

## Overview

The `build.sh` script allows you to build and push Docker images for multiple architectures (amd64, arm64, arm/v7) to Docker Hub without using Docker Compose.

## Quick Start

### 1. Configure the Script

Edit `build.sh` and update these variables:

```bash
# REQUIRED: Your Docker Hub username
DOCKER_USERNAME="your-dockerhub-username"

# OPTIONAL: Customize these if needed
IMAGE_NAME="yorku-multi-db-api"
IMAGE_TAG="latest"
ADDITIONAL_TAGS="v1.0.0"
PLATFORMS="linux/amd64 linux/arm64"
PUSH_TO_HUB=true
```

### 2. Run the Build

```bash
./build.sh
```

The script will:
1. Validate your configuration
2. Login to Docker Hub (if pushing)
3. Create/use a multi-architecture builder
4. Build for all specified platforms
5. Push to Docker Hub (if enabled)

## Configuration Options

### Docker Hub Settings

```bash
# Your Docker Hub username (REQUIRED)
DOCKER_USERNAME="myusername"

# Image name (will be: myusername/image-name)
IMAGE_NAME="yorku-multi-db-api"
```

### Versioning

```bash
# Primary tag
IMAGE_TAG="latest"

# Additional tags (space-separated)
ADDITIONAL_TAGS="v1.0.0 v1.0 stable"
```

This will create:
- `myusername/yorku-multi-db-api:latest`
- `myusername/yorku-multi-db-api:v1.0.0`
- `myusername/yorku-multi-db-api:v1.0`
- `myusername/yorku-multi-db-api:stable`

### Platform Selection

```bash
# Build for specific platforms (space-separated)
PLATFORMS="linux/amd64 linux/arm64"
```

#### Available Platforms

| Platform | Description | Common Use Cases |
|----------|-------------|------------------|
| `linux/amd64` | 64-bit x86 | Most servers, cloud instances |
| `linux/arm64` | 64-bit ARM | Apple M1/M2, AWS Graviton, Raspberry Pi 4 (64-bit) |
| `linux/arm/v7` | 32-bit ARM | Raspberry Pi 3/4 (32-bit), older ARM devices |
| `linux/386` | 32-bit x86 | Legacy systems (rarely needed) |

#### Common Combinations

**For most deployments:**
```bash
PLATFORMS="linux/amd64 linux/arm64"
```

**For maximum compatibility:**
```bash
PLATFORMS="linux/amd64 linux/arm64 linux/arm/v7"
```

**For x86 only:**
```bash
PLATFORMS="linux/amd64"
```

**For ARM only:**
```bash
PLATFORMS="linux/arm64 linux/arm/v7"
```

### Push Settings

```bash
# Push to Docker Hub (true/false)
PUSH_TO_HUB=true
```

- `true`: Build and push to Docker Hub
- `false`: Build locally only (for testing)

## Usage Examples

### Example 1: Build and Push to Docker Hub

```bash
#!/bin/bash
# Edit build.sh:
DOCKER_USERNAME="johndoe"
IMAGE_NAME="yorku-multi-db-api"
IMAGE_TAG="v1.0.0"
ADDITIONAL_TAGS="latest stable"
PLATFORMS="linux/amd64 linux/arm64"
PUSH_TO_HUB=true

# Run:
./build.sh
```

Result:
- `johndoe/yorku-multi-db-api:v1.0.0`
- `johndoe/yorku-multi-db-api:latest`
- `johndoe/yorku-multi-db-api:stable`

All built for amd64 and arm64, pushed to Docker Hub.

### Example 2: Build Locally (Testing)

```bash
#!/bin/bash
# Edit build.sh:
DOCKER_USERNAME="johndoe"
IMAGE_NAME="yorku-multi-db-api"
IMAGE_TAG="test"
PLATFORMS="linux/amd64"  # Single platform for faster testing
PUSH_TO_HUB=false        # Don't push

# Run:
./build.sh
```

Result: Local image built for testing, not pushed to Docker Hub.

### Example 3: Release Build

```bash
#!/bin/bash
# Edit build.sh:
DOCKER_USERNAME="mycompany"
IMAGE_NAME="yorku-multi-db-api"
IMAGE_TAG="2.1.0"
ADDITIONAL_TAGS="2.1 2 latest"
PLATFORMS="linux/amd64 linux/arm64 linux/arm/v7"
PUSH_TO_HUB=true

# Run:
./build.sh
```

Result: Production release with semantic versioning, all platforms.

## Prerequisites

### 1. Docker with Buildx

**Check if you have buildx:**
```bash
docker buildx version
```

**If not available:**
- Update Docker to version 19.03+ (buildx is included)
- Or install Docker Desktop (includes buildx)

### 2. Docker Hub Account

Create a free account at [hub.docker.com](https://hub.docker.com)

### 3. QEMU (for cross-platform builds)

**On Linux:**
```bash
# Install QEMU
sudo apt-get install -y qemu-user-static

# Register QEMU
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

**On macOS/Windows:**
Docker Desktop includes QEMU automatically.

## How It Works

### Build Process

1. **Validation**: Checks Docker, buildx, and configuration
2. **Authentication**: Logs into Docker Hub (if pushing)
3. **Builder Setup**: Creates or uses a multi-arch builder
4. **Build**: Builds for all specified platforms simultaneously
5. **Push**: Pushes all platform variants as a manifest list

### Multi-Architecture Magic

The script uses Docker Buildx to:
- Build for multiple architectures in one command
- Create a manifest list that points to all platform variants
- Users can `docker pull` on any platform and get the right image

Example:
```bash
# On AMD64 server
docker pull johndoe/yorku-multi-db-api:latest
# → Pulls the linux/amd64 variant

# On Apple M1
docker pull johndoe/yorku-multi-db-api:latest
# → Pulls the linux/arm64 variant

# On Raspberry Pi
docker pull johndoe/yorku-multi-db-api:latest
# → Pulls the linux/arm/v7 variant
```

## Workflow

### Development Workflow

```bash
# 1. Make code changes
# 2. Test locally
PUSH_TO_HUB=false ./build.sh

# 3. Tag and push when ready
IMAGE_TAG="v1.2.3" PUSH_TO_HUB=true ./build.sh
```

### Release Workflow

```bash
# 1. Update version in build.sh
IMAGE_TAG="1.5.0"
ADDITIONAL_TAGS="1.5 1 latest"

# 2. Build and push
./build.sh

# 3. Tag in git
git tag v1.5.0
git push origin v1.5.0
```

## Troubleshooting

### Build Fails on ARM Platform

**Issue**: Build fails when building for ARM on x86 machine

**Solution**: Install QEMU
```bash
# Linux
sudo apt-get install -y qemu-user-static
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

# macOS/Windows
Update Docker Desktop to latest version
```

### Docker Hub Login Fails

**Issue**: "unauthorized: incorrect username or password"

**Solution**: Use access token instead of password
1. Go to [Docker Hub Security](https://hub.docker.com/settings/security)
2. Create a new access token
3. Use token as password when logging in

### Image Not Found After Push

**Issue**: Can't pull image after pushing

**Solution**: Check repository visibility
1. Go to [Docker Hub Repositories](https://hub.docker.com/repositories)
2. Ensure repository is public or you're logged in
3. Verify image name: `docker pull username/imagename:tag`

### Build Too Slow

**Issue**: Multi-arch builds take too long

**Solutions**:
```bash
# 1. Build single platform for testing
PLATFORMS="linux/amd64" ./build.sh

# 2. Use caching
docker buildx build --cache-from=type=registry,ref=user/image:cache ...

# 3. Optimize Dockerfile (reduce layers, multi-stage builds)
```

### Buildx Not Available

**Issue**: `docker: 'buildx' is not a docker command`

**Solution**: Update Docker
```bash
# Check version
docker --version

# Should be 19.03+
# Update at https://docs.docker.com/engine/install/
```

## Advanced Usage

### Custom Dockerfile

```bash
# Edit build.sh:
DOCKERFILE="Dockerfile.custom"
```

### Custom Build Context

```bash
# Edit build.sh:
BUILD_CONTEXT="../"  # Parent directory
```

### Build Arguments

Modify the script to add build args:

```bash
# In build.sh, modify build_cmd:
build_cmd="$build_cmd --build-arg VERSION=1.0.0"
build_cmd="$build_cmd --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
```

### Cache Control

```bash
# No cache (clean build)
docker buildx build --no-cache ...

# Registry cache
docker buildx build \
  --cache-from=type=registry,ref=user/image:cache \
  --cache-to=type=registry,ref=user/image:cache ...
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Build and Push Docker Image

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v2
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}
      
      - name: Build and push
        run: |
          export IMAGE_TAG=${GITHUB_REF#refs/tags/v}
          ./build.sh
```

### GitLab CI

```yaml
build:
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD
  script:
    - ./build.sh
  only:
    - tags
```

## Best Practices

1. **Use Semantic Versioning**: `v1.2.3`, `v1.2`, `v1`, `latest`
2. **Tag Releases**: Always tag git commits when pushing images
3. **Test Before Pushing**: Set `PUSH_TO_HUB=false` first
4. **Document Changes**: Update CHANGELOG.md with each release
5. **Automate**: Use CI/CD for consistent builds
6. **Monitor Build Times**: Multi-arch builds can be slow
7. **Use Registry Cache**: Speed up subsequent builds

## Security

### Protect Docker Hub Credentials

```bash
# Never commit credentials
echo "*.env" >> .gitignore

# Use environment variables
export DOCKER_USERNAME="myusername"
./build.sh

# Or use Docker credential helpers
```

### Scan Images for Vulnerabilities

```bash
# After building, scan the image
docker scout cves myusername/yorku-multi-db-api:latest

# Or use Trivy
trivy image myusername/yorku-multi-db-api:latest
```

## Reference

### Full Configuration Example

```bash
DOCKER_USERNAME="mycompany"
IMAGE_NAME="yorku-multi-db-api"
IMAGE_TAG="1.0.0"
ADDITIONAL_TAGS="1.0 1 latest stable"
PLATFORMS="linux/amd64 linux/arm64 linux/arm/v7"
DOCKERFILE="Dockerfile"
BUILD_CONTEXT="."
PUSH_TO_HUB=true
```

### Platform Architectures

| Platform | CPU Architecture | Bits | Common Devices |
|----------|-----------------|------|----------------|
| linux/amd64 | x86-64 | 64-bit | Servers, PCs, Cloud VMs |
| linux/arm64 | ARMv8 | 64-bit | M1/M2 Macs, Graviton, Pi 4 |
| linux/arm/v7 | ARMv7 | 32-bit | Pi 3, Older ARM |
| linux/386 | x86 | 32-bit | Legacy systems |

## Support

- **Docker Buildx Docs**: https://docs.docker.com/buildx/
- **Multi-platform Images**: https://docs.docker.com/build/building/multi-platform/
- **Docker Hub**: https://hub.docker.com

## Summary

The `build.sh` script provides:
- ✅ Multi-architecture builds (amd64, arm64, arm/v7)
- ✅ Docker Hub integration
- ✅ Multiple tags support
- ✅ Easy configuration
- ✅ Production-ready
- ✅ No Docker Compose required

Simply update the configuration variables and run `./build.sh`!

