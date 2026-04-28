## Context

Currently, the system allows creation of elements with names that match logically deleted (soft-deleted) elements. This creates data ambiguity and integrity issues. Soft deletes are commonly implemented using `is_active` or `deleted_at` fields rather than physical deletion. The validation must operate across all tables that implement soft delete patterns without requiring schema changes.

## Goals / Non-Goals

**Goals:**
- Prevent duplicate names across active and inactive (logically deleted) elements
- Provide clear error messages distinguishing between active and inactive conflicts
- Implement validation at both application and database levels (defense in depth)
- Guide users to contact administrators when conflicts arise

**Non-Goals:**
- Physical deletion of records (system uses soft deletes only)
- Changes to existing data model schemas (use existing soft-delete columns)
- Hard constraints that prevent future recovery workflows (maintain flexibility for admin resolution)

## Decisions

### Decision 1: Multi-layer validation approach
**Choice**: Implement validation at both application and database layers

**Rationale**: 
- Application layer provides immediate, descriptive feedback to users
- Database layer prevents race conditions and ensures consistency
- Two layers create defense-in-depth

**Alternatives Considered**:
- Database only: Less user-friendly error messages; slower feedback
- Application only: Vulnerable to race conditions in concurrent scenarios
- Chose multi-layer for reliability + UX

### Decision 2: Name uniqueness includes soft-deleted records
**Choice**: Query that checks uniqueness includes both `is_active = true` AND `is_active = false` records

**Rationale**:
- Prevents name shadowing (same name exists but hidden)
- Maintains data integrity during recovery workflows
- Simplifies name management across lifecycle

**Implementation Pattern**:
```sql
-- Example for MySQL/PostgreSQL
SELECT COUNT(*) FROM table_name 
WHERE name = ? AND (is_active = true OR is_active = false)
-- or for soft-delete with timestamp
WHERE name = ? AND (deleted_at IS NULL OR deleted_at IS NOT NULL)
```

### Decision 3: Differentiate error messages by state
**Choice**: Return different error codes and messages for active vs. inactive conflicts

**Error Codes**:
- `DUPLICATE_NAME_ACTIVE`: "The name '{name}' is already in use."
- `DUPLICATE_NAME_INACTIVE`: "The name '{name}' is already in use (inactive). Please contact the administrator to resolve this conflict."

**Rationale**: 
- Users need to know why they can't use a name
- Inactive conflicts require admin intervention
- Clear messaging reduces support tickets

### Decision 4: Validation scope across all entities
**Choice**: Use a shared validation utility/service that can be applied to any repository

**Rationale**:
- Avoids code duplication across multiple repositories
- Ensures consistent behavior across all tables
- Easier to maintain and test

**Example Structure**:
- Abstract method in base repository: `validateNameUniqueness(name, id?)`
- Checks both active and inactive records
- Returns specific error code/message

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Performance impact on large tables with name lookups | Add database index on `name` column; consider partial index filtering by soft-delete status |
| Concurrent requests creating duplicates before validation | Database-level constraint (unique index conditional on soft-delete status) provides final safeguard |
| Administrators cannot easily re-activate duplicate-named records | Design a recovery workflow: archive old inactive record or allow explicit merge/resolution through admin interface |
| Message about "contact administrator" may confuse self-service users | Include clear documentation/FAQ; provide admin dashboard to view and resolve conflicts |

## Migration Plan

1. **Phase 1: Add validation logic** (no breaking changes)
   - Implement application-level validation in repositories
   - Deploy behind feature flag (default: enabled)
   - Monitor error logs

2. **Phase 2: Add database constraints** (optional hardening)
   - Create indexes on `name` column where applicable
   - Consider unique partial indexes: `UNIQUE (name) WHERE is_active = true`
   - Backwards compatible; prevents future violations

3. **Phase 3: Document and communicate**
   - Update API documentation with new error codes
   - Create admin guide for conflict resolution
   - Add metrics/dashboards for duplicate-name errors

## Open Questions

1. Which tables/entities need this validation? (Should identify all soft-delete tables)
2. Does the system have a standard soft-delete column name (`is_active`, `deleted_at`, etc.)?
3. Should admins be able to override/force-create duplicates for recovery purposes?
4. What's the preferred recovery workflow when conflicts are discovered?
