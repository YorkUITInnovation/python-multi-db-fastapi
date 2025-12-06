# Docker Compose V2 Update

## Change Summary

All files have been updated to use Docker Compose V2 syntax:
- **Old**: `docker-compose` (hyphenated, legacy command)
- **New**: `docker compose` (space, integrated into Docker CLI)

## Files Updated

✅ `verify-docker-setup.sh` - Verification script  
✅ `Makefile` - All make commands  
✅ `docker-start.sh` - Quick start script  
✅ `DOCKER_DEPLOYMENT.md` - Documentation  
✅ `README.md` - Main readme  
✅ `DOCKER_SETUP_SUMMARY.md` - Setup summary  

## Why This Change?

Docker Compose V2 is now the official version and is integrated directly into the Docker CLI:
- ✅ Better integration with Docker
- ✅ Faster performance
- ✅ Improved compatibility
- ✅ Official supported version

## Compatibility

### Docker Compose V2 (Current - Recommended)
```bash
docker compose up -d
docker compose logs -f
docker compose down
```

### Docker Compose V1 (Legacy - Deprecated)
```bash
docker-compose up -d      # Still works but deprecated
docker-compose logs -f
docker-compose down
```

## Verification

Check your Docker Compose version:
```bash
docker compose version
```

Expected output:
```
Docker Compose version v2.x.x
```

## Installation

Docker Compose V2 comes bundled with Docker Desktop and recent Docker Engine installations.

If you need to install or upgrade:

### Linux
```bash
# Docker Compose V2 is included in Docker Engine 20.10+
docker --version

# If not available, install Docker Engine latest version
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### macOS/Windows
Docker Desktop includes Docker Compose V2 by default.

## Migration from V1 to V2

If you're still using V1:

### Option 1: Install V2 (Recommended)
Update Docker Engine or Docker Desktop to latest version.

### Option 2: Use V1 Compatibility
Docker Compose V2 provides a compatibility alias:
```bash
# Create alias (temporary)
alias docker-compose='docker compose'

# Or create permanent symlink (not recommended)
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```

However, we recommend using the native `docker compose` command.

## Testing

Run the verification script to confirm everything works:
```bash
./verify-docker-setup.sh
```

You should see:
```
✓ Docker Compose installed: Docker Compose version v2.x.x
✓ docker-compose.yml is valid
✓ docker-compose.prod.yml is valid
✓ docker-compose.dev.yml is valid
```

## All Commands Updated

### Quick Start
```bash
./docker-start.sh          # Uses docker compose
```

### Makefile Commands
```bash
make build                 # Uses docker compose
make up
make down
make logs
make dev-up
make dev-logs
```

### Manual Commands
```bash
# Production
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml down

# Development
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml logs -f
docker compose -f docker-compose.dev.yml down
```

## Benefits of V2

1. **Native Docker integration**: Part of Docker CLI
2. **Better performance**: Faster builds and operations
3. **GPU support**: Native GPU support for ML workloads
4. **Profiles**: Better environment management
5. **Watch mode**: Improved file watching
6. **Official support**: Active development and support

## Status

✅ **All files updated to Docker Compose V2**  
✅ **Backward compatible (V1 still works if installed)**  
✅ **Tested and verified**  
✅ **Documentation updated**  

## References

- [Docker Compose V2 Documentation](https://docs.docker.com/compose/cli-command/)
- [Migrating to V2](https://docs.docker.com/compose/migrate/)
- [Docker Compose GitHub](https://github.com/docker/compose)

