## 1. Research and Analysis

- [x] 1.1 Identify all tables in the database that use soft-delete patterns (is_active, deleted_at, etc.)
- [x] 1.2 Document current soft-delete column names and conventions per table
- [x] 1.3 Review existing repository/persistence layer architecture
- [x] 1.4 Map error handling and response structure conventions (how errors are returned in the API)

## 2. Application-Layer Validation

- [x] 2.1 Create base repository method `validateNameUniqueness(name, id, tableName)` that checks both active and inactive records
- [x] 2.2 Implement logic to distinguish between `DUPLICATE_NAME_ACTIVE` and `DUPLICATE_NAME_INACTIVE` errors
- [x] 2.3 Create custom exception classes for duplicate name errors with proper error codes
- [x] 2.4 Integrate validation into all repository create/update methods for entities with names
- [x] 2.5 Test validation logic with unit tests (active duplicates, inactive duplicates, no duplicates)

## 3. Database-Layer Constraints

- [x] 3.1 Create migration/script to add indexes on `name` columns where appropriate
- [ ] 3.2 (Optional) Create unique partial indexes that enforce uniqueness across soft-deleted records
- [ ] 3.3 Document database constraint rationale in schema documentation

## 4. API Error Response Handling

- [x] 4.1 Map custom exceptions to HTTP 409 Conflict responses
- [x] 4.2 Create error response DTOs with error codes and descriptive messages
- [x] 4.3 Add message template for `DUPLICATE_NAME_INACTIVE` that includes name and "contact administrator" guidance
- [ ] 4.4 Test error responses through API endpoints with integration tests

## 5. Logging and Monitoring

- [x] 5.1 Add structured logging to capture duplicate-name attempts (who, what, when, conflicting element state)
- [x] 5.2 Create metrics/counters for duplicate-name errors by type (active vs. inactive)
- [x] 5.3 Document metrics and logging format for administrative monitoring

## 6. Documentation and Testing

- [x] 6.1 Update API documentation with new HTTP 409 error codes and response formats
- [ ] 6.2 Create end-to-end tests verifying: create with active duplicate, create with inactive duplicate, update to conflict
- [x] 6.3 Write developer guide explaining the validation pattern and how to apply it to new entities
- [x] 6.4 Create admin documentation on how to identify and resolve duplicate-name conflicts

## 7. Deployment and Monitoring

- [x] 7.1 Plan rollout strategy (feature flag if applicable)
- [x] 7.2 Monitor error logs during first 48 hours of deployment for unexpected duplicate-name detections
- [x] 7.3 Create runbook for administrators handling duplicate-name conflict reports


