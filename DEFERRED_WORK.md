# Deferred Work Items

## Deferred from: Code Review (2026-05-06)

These items were identified during code review but deferred as they are pre-existing design decisions or operational concerns that don't block the current implementation:

### 21. No audit logging for admin actions
- **Issue**: Admin operations (create/delete users, courses) not logged
- **Impact**: No accountability, difficult to debug issues
- **Reason for deferring**: Pre-existing design decision, not introduced by this commit. Can be added as a future enhancement.

### 22. No backup/restore functionality
- **Issue**: No automated database backups
- **Impact**: Data loss risk
- **Reason for deferring**: Operational concern, not code issue. Should be handled at infrastructure level.

### 23. No health check endpoint
- **Issue**: No `/health` or `/readiness` endpoint for load balancers
- **Impact**: Deployment orchestration can't detect unhealthy instances
- **Reason for deferring**: Infrastructure concern, can be added later when deploying to production with load balancers.

### 24. No API versioning
- **Issue**: API endpoints not versioned (e.g., `/v1/auth/login`)
- **Impact**: Breaking changes require new deployment
- **Reason for deferring**: Design decision, acceptable for MVP. Can be added when API stability becomes a concern.

---

## Recommendations for Future Sprints

1. **Audit Logging**: Implement audit trail for all admin and doctor actions
2. **Backup Strategy**: Set up automated database backups (daily snapshots, point-in-time recovery)
3. **Health Checks**: Add `/health` and `/readiness` endpoints for Kubernetes/load balancer integration
4. **API Versioning**: Introduce `/v1/` prefix for all endpoints before public release
5. **Database Migrations**: Integrate Alembic for schema version control (partially addressed with current fixes)
