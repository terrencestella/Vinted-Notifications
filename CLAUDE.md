# Claude Code Implementation Plan: Vinted Notifications Fork

## Project Context

We are setting up an automated workflow for a fork of the Vinted-Notifications repository. The goal is to add our own improvements (UV, Docker, automated deployment) on top of the original repository while automatically staying synchronized with upstream updates.

## Repository Information

- **Upstream Repository**: `https://github.com/Fuyucch1/Vinted-Notifications`
- **Project Type**: Python notification bot for Vinted listings
- **Current Features**: Web UI, Telegram notifications, RSS feeds, multi-country support
- **Original Installation**: `pip install -r requirements.txt` + `python vinted_notifications.py`

## Objectives

### Primary Goals
1. **Fork Management**: Automatic sync with upstream repository
2. **Modernize Dependencies**: Implement UV package manager
3. **Containerization**: Add Docker support
4. **CI/CD Pipeline**: Automated build and deployment via GitHub Actions
5. **Self-hosted Runner**: Deploy via own GitHub Actions runner

### Technical Requirements
- Python 3.11+
- UV package manager
- Docker containerization
- GitHub Container Registry (ghcr.io)
- Automated upstream sync
- Conflict detection and handling

## Implementation Plan

### Phase 1: Repository Setup
```bash
# Fork original repository via GitHub UI
# Clone your fork locally
git clone https://github.com/YOUR_USERNAME/Vinted-Notifications.git
cd Vinted-Notifications

# Setup upstream remote
git remote add upstream https://github.com/Fuyucch1/Vinted-Notifications.git
```

### Phase 2: UV Implementation
**Files to create:**

1. **pyproject.toml** - Modern Python project configuration
2. **uv.lock** - Lock file for reproducible builds
3. **Update existing requirements.txt dependencies**

### Phase 3: Docker Implementation  
**Files to create:**

1. **Dockerfile** - Using `ghcr.io/astral-sh/uv:python3.11-slim` base image
2. **docker-compose.yml** - For local development
3. **docker-compose.prod.yml** - For production deployment
4. **.dockerignore** - Optimize build context

### Phase 4: GitHub Actions Workflow
**Files to create:**

1. **.github/workflows/sync-and-deploy.yml** - Complete automation workflow

**Workflow Features:**
- Daily upstream sync (6:00 UTC)
- Automatic dependency updates
- Docker build and push to ghcr.io
- Deployment via self-hosted runner
- Manual trigger support
- Conflict detection

### Phase 5: Deployment Configuration
- Self-hosted runner setup
- Container deployment strategy
- Data persistence volumes
- Environment configuration

## File Structure Overview

```
Vinted-Notifications/
├── .github/
│   └── workflows/
│       └── sync-and-deploy.yml
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── docker-compose.yml  
├── docker-compose.prod.yml
├── .dockerignore
├── requirements.txt (existing)
└── [existing project files]
```

## Sync Process Explanation

### Conceptual Flow

1. **Detection Phase**
   - GitHub Actions checks upstream repository
   - Compares latest commit with our last sync point
   - Determines if updates are available

2. **Sync Phase** (if updates found)
   - Fetch latest changes from upstream
   - Attempt automatic merge into our main branch
   - Handle three scenarios:
     - Clean merge → Continue to build
     - Conflicts → Stop workflow, notify for manual resolution
     - No changes → Skip build phase

3. **Dependency Update Phase**
   - Parse requirements.txt for changes
   - Update pyproject.toml with new dependencies
   - Generate new uv.lock file
   - Commit changes if modifications occurred

4. **Build Phase**
   - Build Docker image with latest changes
   - Push to GitHub Container Registry
   - Tag with both `latest` and commit SHA

5. **Deploy Phase** 
   - Pull latest image on self-hosted runner
   - Stop existing container
   - Start new container with updated image
   - Cleanup old images

## Key Automation Features

### 1. Upstream Sync Logic
- **Trigger**: Daily cron job + manual dispatch + push events
- **Process**: Fetch upstream, detect changes, merge automatically
- **Conflict Handling**: Stop workflow, require manual intervention
- **Output**: Boolean flag for downstream jobs

### 2. Dependency Management
- **Detection**: Monitor requirements.txt changes
- **Update**: Automatically sync pyproject.toml
- **Lock**: Generate new uv.lock file  
- **Commit**: Auto-commit dependency updates

### 3. Docker Build Strategy
- **Base Image**: `ghcr.io/astral-sh/uv:python3.11-slim`
- **Optimization**: Multi-layer caching
- **Registry**: GitHub Container Registry (ghcr.io)
- **Tagging**: Latest + SHA-based tags

### 4. Deployment Process
- **Runner**: Self-hosted GitHub Actions runner
- **Strategy**: Docker container replacement
- **Persistence**: Volume mounting for data
- **Rollback**: Tagged images for recovery

## Expected Workflow Behavior

### Normal Operation
```
Day 1: Upstream has no updates → No action
Day 2: Upstream has new feature → Auto-sync + rebuild + deploy
Day 3: Upstream has dependency update → Auto-sync + update pyproject.toml + rebuild + deploy
```

### Conflict Scenarios
```
Scenario A: Clean merge → Automatic deployment
Scenario B: Merge conflict → Workflow stops, manual intervention required
Scenario C: Build failure → Notification sent, no deployment
```

## Configuration Requirements

### GitHub Repository Settings
- Fork the upstream repository
- Enable GitHub Actions
- Configure GitHub Container Registry access
- Set up self-hosted runner

### Required Files
- All files listed in "File Structure Overview"
- Proper permissions and access rights
- Environment-specific configurations

### Self-hosted Runner Requirements
- Docker installed and configured
- Access to deployment environment  
- Sufficient storage for container images
- Network access to ghcr.io
- Appropriate user permissions

## Success Criteria

### Technical Success
- [ ] Successful fork and sync setup
- [ ] UV package manager working correctly
- [ ] Docker container builds successfully  
- [ ] GitHub Actions workflow runs without errors
- [ ] Automated deployment functions properly
- [ ] Data persistence maintained across deployments

### Operational Success  
- [ ] Daily sync runs automatically
- [ ] New upstream features are picked up
- [ ] Deployment happens without downtime
- [ ] Manual intervention only required for conflicts
- [ ] Rollback capability available

## Risk Mitigation

### Potential Issues
1. **Merge Conflicts**: Manual resolution required
2. **Upstream Breaking Changes**: May break our additions  
3. **Docker Build Failures**: Dependency issues
4. **Runner Downtime**: Deployment failures
5. **Registry Access**: Authentication problems

### Mitigation Strategies
- Comprehensive testing in feature branches
- Backup and rollback procedures
- Monitoring and alerting setup
- Documentation for manual procedures
- Staged deployment approach

## Implementation Steps for Claude Code

### Step 1: Project Initialization
```bash
# Create local working directory
# Fork repository via GitHub
# Clone and setup remotes
# Verify upstream connectivity
```

### Step 2: UV Migration
```bash
# Analyze existing requirements.txt
# Create pyproject.toml with proper configuration
# Generate uv.lock file
# Test local installation with UV
```

### Step 3: Docker Implementation
```bash
# Create optimized Dockerfile
# Setup docker-compose files
# Create .dockerignore
# Test local container builds
```

### Step 4: GitHub Actions Setup
```bash
# Create workflow directory structure
# Implement sync-and-deploy.yml
# Configure job dependencies
# Test workflow triggers
```

### Step 5: Testing and Validation
```bash
# Test manual workflow trigger
# Validate Docker container functionality
# Verify sync behavior
# Test deployment on runner
```

## Docker Configuration Details

### Base Image Selection
- **Choice**: `ghcr.io/astral-sh/uv:python3.11-slim`
- **Rationale**: Pre-installed UV, smaller footprint, official support
- **Alternatives**: Standard python:3.11-slim + UV installation

### Container Architecture
- **Ports**: 8000 (Web UI), 8001 (RSS Feed)
- **Volumes**: Data persistence for database and configuration
- **Environment**: Production-ready configuration
- **Security**: Non-root user, minimal attack surface

### Deployment Strategy
- **Blue-Green**: Stop old container, start new one
- **Health Checks**: Ensure service availability
- **Persistence**: Maintain data across deployments
- **Monitoring**: Container health and application metrics

## Maintenance Considerations

### Regular Maintenance
- Monitor daily sync success rates
- Review dependency updates for security
- Update Docker base images periodically  
- Maintain runner infrastructure
- Handle merge conflicts promptly

### Monitoring Points
- Upstream sync frequency and success
- Build pipeline performance
- Deployment success rates
- Application health metrics
- Resource usage trends

## Troubleshooting Guide

### Common Issues
1. **Sync Failures**: Check upstream connectivity and conflicts
2. **Build Failures**: Verify dependency compatibility
3. **Deployment Failures**: Check runner status and permissions
4. **Container Issues**: Validate Docker configuration and resources

### Debug Procedures
- GitHub Actions logs analysis
- Container logs inspection  
- Runner connectivity testing
- Manual sync verification

---

## Claude Code Execution Notes

**Environment Requirements:**
- Access to GitHub CLI or web interface for forking
- Local Git installation
- Docker for testing
- UV package manager for local testing

**Execution Order:**
Execute phases sequentially, testing each phase before proceeding to the next. Focus on getting the basic sync working before adding complexity.

**Validation Steps:**
After each phase, verify functionality locally before committing to the workflow automation.

---

**Expected Implementation Time**: 6-8 hours total
**Complexity Level**: Intermediate to Advanced
**Prerequisites**: GitHub Actions experience, Docker knowledge, Python packaging familiarity