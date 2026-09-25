# Release Plan — 0.1.0

1. Run formatting, linting, strict typing, unit/integration/E2E tests, and coverage gate.
2. Build wheel and source distribution; inspect included files.
3. Run offline demo and independent release verification.
4. Run security/static review and secret scan.
5. Initialize public GitHub repository with protected `main` baseline.
6. Push implementation branch and open pull request.
7. Wait for all Python-version CI jobs to pass.
8. Merge without force-push and verify public `main` contents and repository visibility.
