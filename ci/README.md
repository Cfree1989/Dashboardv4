# CI Scripts and Configurations

This directory contains scripts, configurations, and other resources used by the continuous integration (CI) and continuous deployment (CD) workflows.

## Purpose

- **Reusable Scripts**: To store shell scripts (`.sh`), Node.js scripts (`.js`), or other executable files that automate testing, building, and deployment steps.
- **Configuration Files**: To hold environment-specific configurations or templates needed during the CI/CD process.
- **Separation of Concerns**: To keep the logic of CI/CD tasks separate from the workflow definitions in the `.github/workflows` directory. This makes both the workflows and the scripts easier to read, maintain, and reuse.

## Usage

Workflows defined in `.github/workflows/*.yml` can execute the scripts in this directory. For example, a workflow step might look like this:

```yaml
- name: Run E2E Tests
  run: ./ci/run-e2e-tests.sh
``` 