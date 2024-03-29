# Release Process Documentation

## Table of Contents
- [Release Process Documentation](#release-process-documentation)
  - [Table of Contents](#table-of-contents)
  - [Versioning](#versioning)
  - [Development Workflow](#development-workflow)
  - [Release Branch Creation](#release-branch-creation)
  - [UAT Deployment](#uat-deployment)
  - [Tagging Convention](#tagging-convention)
  - [Production Deployment](#production-deployment)
  - [Hotfixes and Bugfixes](#hotfixes-and-bugfixes)
    - [Hotfix Process for Immediate Production Deployment:](#hotfix-process-for-immediate-production-deployment)
    - [Bugfix Process with UAT Validation:](#bugfix-process-with-uat-validation)
    - [Notes on Process](#notes-on-process)
  - [Rollback Procedures](#rollback-procedures)
  - [Release Communication](#release-communication)
  - [Naming Conventions](#naming-conventions)
  - [Automation](#automation)
  - [Security Practices for Deployment](#security-practices-for-deployment)

This document outlines the steps and conventions we follow for releasing software in this project. As a solo developer, this process is streamlined but designed to accommodate growth and collaboration in the future.

## Versioning

- We adhere to Semantic Versioning (`MAJOR.MINOR.PATCH`) for clarity and consistency in release management.

## Development Workflow

- All development work and minor changes are committed directly to the `develop` branch.
- Significant features should be developed in separate branches and merged into `develop` upon completion.

## Release Branch Creation

- When ready for a new release, create a release branch from `develop` named `release/vX.Y.Z`, where `X.Y.Z` follows [Semantic Versioning](https://semver.org/) guidelines.

## UAT Deployment

- Merge the `release/vX.Y.Z` branch into `UAT` and tag the merge commit with `vX.Y.Z-rc` and a brief annotation about the release candidate.
- This tag will trigger a GitHub Actions workflow to deploy the release candidate to the UAT environment on Google Cloud Platform (GCP), accessible via Cloud Run.
- Gather feedback during UAT and incorporate necessary changes:
  - Minor changes can be made directly in the `UAT` branch and redeployed with the same `-rc` tag.
  - Significant changes may require creating a new `-rc` version and restarting the UAT process.

## Tagging Convention

- **Pre-release tags** for UAT: Tagged with `-rc` suffix, e.g., `v1.0.0-rc`.
- **Production release tags**: Semantic versioning without `-rc`, e.g., `v1.0.0`.

## Production Deployment

- If the release candidate (`-rc`) passes UAT:
    - Tag the commit from the UAT branch that's been tested and approved with the production semantic version (e.g., `v1.0.0`).
    - This tag will trigger a GitHub Actions workflow to deploy the final version to the production environment on GCP, accessible via Cloud Run.

## Hotfixes and Bugfixes

- **Bugfixes**: Address issues discovered during the development cycle or in UAT. These fixes are applied to the `develop` branch, merged into `main`, tagged with `-rc` for UAT deployment, and then deployed to production upon approval.

- **Hotfixes**: Address urgent issues in production. These are immediately fixed, merged into `main` and `develop`, and deployed to production without the `-rc` phase, given their critical nature.

### Hotfix Process for Immediate Production Deployment:

1. **Identify Critical Issue**: When a production issue requires an urgent hotfix (e.g., `v2.5.3`).

2. **Create and Apply Hotfix**:
   1. Create a new branch for the hotfix, incrementing the patch version (e.g., `v2.5.4`):
      ```bash
      git checkout -b hotfix/v2.5.4 main
      ```
   2. Apply necessary changes and commit:
      ```bash
      git commit -am "Apply urgent hotfix for issue XYZ"
      ```

3. **Deploy Hotfix to Production**:
   1. Merge the hotfix into `main` and deploy:
      ```bash
      git checkout main
      git merge hotfix/v2.5.4
      git tag -a v2.5.4 -m "Hotfix v2.5.4"
      git push origin main --tags
      ```
   2. This tag triggers the production deployment.

4. **Sync Hotfix with Develop**:
   1. Merge the hotfix into the `develop` branch:
      ```bash
      git checkout develop
      git merge hotfix/v2.5.4
      git push origin develop
      ```

### Bugfix Process with UAT Validation:

1. **Apply Bugfix in Develop**: Address non-critical bugs in the `develop` branch.

2. **Prepare for UAT**:
   1. Merge fixes into a release branch and then into `main`.
   2. Tag the merge in `main` with `-rc` to indicate readiness for UAT testing:
      ```bash
      git tag -a v1.2.1-rc -m "Release candidate for bugfixes"
      git push origin v1.2.1-rc
      ```

3. **UAT and Production Deployment**:
   1. Upon successful UAT, tag the commit without `-rc` and deploy to production:
      ```bash
      git tag -a v1.2.1 -m "Final release for bugfix v1.2.1"
      git push origin v1.2.1
      ```
   2. Merge the fixes back into the `develop` branch:
      ```bash
      git checkout develop
      git merge main
      git push origin develop
      ```

### Notes on Process

- **Direct Deployment for Hotfixes**: Given their urgency, hotfixes bypass the `-rc` phase to expedite deployment to production, addressing critical issues promptly.

- **UAT for Bugfixes**: Bugfixes are validated through UAT to ensure stability and prevent regressions, following the standard `-rc` to production tag progression.

By distinguishing between the immediacy of hotfixes and the structured deployment of bugfixes, this process ensures both critical production issues and less urgent bugs are managed effectively, maintaining the stability and integrity of the production environment.

## Rollback Procedures

In case of issues with a new release, follow these steps to revert to a previous stable version:

1. Identify the last stable version (e.g., `v1.2.0`).
2. Check out the `main` branch and reset it to the last stable version:
   ```bash
   git checkout main
   git reset --hard v1.2.0
   git push --force origin main
   ```
   **Note**: Be cautious when using `git push --force`, as it overwrites the remote history. Ensure that you have communicated with your team (if applicable) before proceeding, as this action can affect other collaborators.
3. Redeploy the last stable version to the production environment using the appropriate deployment process.
4. Investigate and address the issues that caused the rollback before attempting a new release.

## Release Communication

- Prepare release notes and change logs detailing the changes, fixes, and new features included in each release.
- Share the release notes with stakeholders and users through appropriate channels (e.g., email, project management tools, or release announcements).
- Include any relevant instructions or migration steps required for users to update to the new version.

## Naming Conventions

- **Branch Names**: Use lowercase and hyphens for separators (e.g., `feature/add-user-authentication`, `bugfix/fix-login-issue`).
- **Commit Messages**: Write clear and concise commit messages that describe the changes made. Use the imperative mood and present tense (e.g., "Add feature X", "Fix bug Y").
- **Pull Request Titles**: Follow a similar format to commit messages, providing a brief summary of the changes included in the pull request.

## Automation

- **GitHub Actions** automates the deployment process to both UAT and production environments based on tagging conventions.
- Workflows are defined in the `.github/workflows/` directory and include steps for deployment to GCP Cloud Run.

## Security Practices for Deployment

- Ensure that production secrets and sensitive credentials are securely stored and managed, using tools like Google Secret Manager or Hashicorp Vault.
- Use the principle of least privilege when configuring IAM roles and permissions for the CI/CD pipeline, ensuring that only necessary access is granted.
- Regularly rotate and update credentials used in the deployment process to maintain security.
- Implement security scanning and vulnerability checks as part of the CI/CD pipeline to identify and address potential security issues before deployment.

By following these practices and continuously monitoring and improving the deployment process, we can ensure a secure and reliable release workflow.