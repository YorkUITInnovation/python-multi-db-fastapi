#!/bin/bash

# Docker Multi-Architecture Build and Push Script
# This script builds Docker images for multiple platforms and pushes to Docker Hub

set -e

# ============================================================================
# CONFIGURATION - Update these variables for your setup
# ============================================================================

# Docker Hub username (REQUIRED - update this!)
DOCKER_USERNAME="uitadmin"

# Image name (update if needed)
IMAGE_NAME="yorku-multi-db-api"

# Image tag/version (update as needed)
IMAGE_TAG="latest"

# Additional tags (optional, space-separated)
ADDITIONAL_TAGS="v1.0.0"

# Platforms to build for (space-separated)
# Options: linux/amd64, linux/arm64, linux/arm/v7
PLATFORMS="linux/amd64 linux/arm64"

# Dockerfile location
DOCKERFILE="Dockerfile"

# Build context (current directory)
BUILD_CONTEXT="."

# Push to Docker Hub (true/false)
PUSH_TO_HUB=true

# ============================================================================
# DO NOT MODIFY BELOW THIS LINE (unless you know what you're doing)
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed: $(docker --version)"
}

# Check if buildx is available
check_buildx() {
    if ! docker buildx version &> /dev/null; then
        print_error "Docker Buildx is not available. Please update Docker to a newer version."
        exit 1
    fi
    print_success "Docker Buildx is available: $(docker buildx version)"
}

# Validate configuration
validate_config() {
    if [ "$DOCKER_USERNAME" == "your-dockerhub-username" ]; then
        print_error "Please update DOCKER_USERNAME in the script!"
        print_info "Edit build.sh and set DOCKER_USERNAME to your Docker Hub username"
        exit 1
    fi

    if [ ! -f "$DOCKERFILE" ]; then
        print_error "Dockerfile not found: $DOCKERFILE"
        exit 1
    fi

    print_success "Configuration validated"
}

# Login to Docker Hub
docker_login() {
    if [ "$PUSH_TO_HUB" == "true" ]; then
        print_info "Logging in to Docker Hub..."
        if docker login; then
            print_success "Logged in to Docker Hub"
        else
            print_error "Failed to login to Docker Hub"
            exit 1
        fi
    fi
}

# Create or use buildx builder
setup_builder() {
    BUILDER_NAME="multiarch-builder"

    if docker buildx inspect "$BUILDER_NAME" &> /dev/null; then
        print_info "Using existing builder: $BUILDER_NAME"
        docker buildx use "$BUILDER_NAME"
    else
        print_info "Creating new buildx builder: $BUILDER_NAME"
        docker buildx create --name "$BUILDER_NAME" --use
        docker buildx inspect --bootstrap
    fi

    print_success "Builder ready: $BUILDER_NAME"
}

# Build and push the image
build_image() {
    local full_image_name="${DOCKER_USERNAME}/${IMAGE_NAME}"
    local platform_list=$(echo "$PLATFORMS" | tr ' ' ',')

    print_info "Building image: $full_image_name:$IMAGE_TAG"
    print_info "Platforms: $platform_list"

    # Build tags array
    local tags="-t ${full_image_name}:${IMAGE_TAG}"

    # Add additional tags
    if [ -n "$ADDITIONAL_TAGS" ]; then
        for tag in $ADDITIONAL_TAGS; do
            tags="$tags -t ${full_image_name}:${tag}"
            print_info "Additional tag: ${full_image_name}:${tag}"
        done
    fi

    # Build command
    local build_cmd="docker buildx build"
    build_cmd="$build_cmd --platform $platform_list"
    build_cmd="$build_cmd $tags"
    build_cmd="$build_cmd -f $DOCKERFILE"

    if [ "$PUSH_TO_HUB" == "true" ]; then
        build_cmd="$build_cmd --push"
    else
        build_cmd="$build_cmd --load"
    fi

    build_cmd="$build_cmd $BUILD_CONTEXT"

    print_info "Executing: $build_cmd"
    echo ""

    if eval "$build_cmd"; then
        print_success "Build completed successfully!"

        if [ "$PUSH_TO_HUB" == "true" ]; then
            print_success "Image pushed to Docker Hub: ${full_image_name}:${IMAGE_TAG}"

            echo ""
            print_info "Your image is now available at:"
            echo "  docker pull ${full_image_name}:${IMAGE_TAG}"

            if [ -n "$ADDITIONAL_TAGS" ]; then
                for tag in $ADDITIONAL_TAGS; do
                    echo "  docker pull ${full_image_name}:${tag}"
                done
            fi
        else
            print_success "Image built locally (not pushed)"
        fi
    else
        print_error "Build failed!"
        exit 1
    fi
}

# Display summary
show_summary() {
    echo ""
    echo "============================================================================"
    echo "                          BUILD SUMMARY"
    echo "============================================================================"
    echo "Docker Hub User:  $DOCKER_USERNAME"
    echo "Image Name:       $IMAGE_NAME"
    echo "Image Tag:        $IMAGE_TAG"
    if [ -n "$ADDITIONAL_TAGS" ]; then
        echo "Additional Tags:  $ADDITIONAL_TAGS"
    fi
    echo "Platforms:        $PLATFORMS"
    echo "Push to Hub:      $PUSH_TO_HUB"
    echo "============================================================================"
    echo ""
}

# Main function
main() {
    echo "============================================================================"
    echo "         Docker Multi-Architecture Build Script"
    echo "============================================================================"
    echo ""

    # Run checks
    check_docker
    check_buildx
    validate_config

    # Show summary
    show_summary

    # Ask for confirmation
    if [ "$PUSH_TO_HUB" == "true" ]; then
        read -p "This will build and push to Docker Hub. Continue? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_warning "Build cancelled by user"
            exit 0
        fi
    fi

    # Login to Docker Hub if needed
    docker_login

    # Setup builder
    setup_builder

    # Build the image
    build_image

    echo ""
    print_success "All done! 🚀"
    echo ""
}

# Run main function
main "$@"

