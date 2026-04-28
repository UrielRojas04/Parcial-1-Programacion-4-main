## ADDED Requirements

### Requirement: Prevent creation with duplicate names (active or inactive)
The system SHALL prevent the creation or modification of any element if another element with the same name already exists in the database, regardless of whether the existing element is active or logically deleted (soft deleted).

#### Scenario: User attempts to create element with name that exists as active
- **WHEN** user attempts to create a new element with a name that matches an active (non-deleted) element
- **THEN** system returns HTTP 409 Conflict with error code `DUPLICATE_NAME_ACTIVE` and message indicating the name is already in use

#### Scenario: User attempts to create element with name that exists as inactive
- **WHEN** user attempts to create a new element with a name that matches a logically deleted (inactive) element
- **THEN** system returns HTTP 409 Conflict with error code `DUPLICATE_NAME_INACTIVE` and message: "The name '{name}' is already in use (inactive). Please contact the administrator to resolve this conflict."

#### Scenario: User attempts to update element to a name that conflicts
- **WHEN** user attempts to rename an existing element to a name that conflicts with another element (active or inactive)
- **THEN** system returns HTTP 409 Conflict with appropriate error code and message

### Requirement: Validation occurs at multiple layers
The system SHALL validate name uniqueness at both the application layer and database layer using constraints.

#### Scenario: Database constraint prevents race condition
- **WHEN** two concurrent requests attempt to create elements with the same name
- **THEN** database constraint ensures only one succeeds; the second receives a constraint violation that is translated to appropriate application error

#### Scenario: Application layer validation provides user feedback
- **WHEN** user attempts an operation that would create a duplicate name
- **THEN** application validates before database call and returns descriptive error message

### Requirement: Error message guides user to administrator
The system SHALL provide clear communication when duplicate names are detected, including guidance to contact the administrator.

#### Scenario: User receives clear error for inactive duplicates
- **WHEN** system detects a duplicate name that is currently inactive
- **THEN** error response includes: (1) error code, (2) human-readable message mentioning the inactive status, (3) suggestion to contact administrator

#### Scenario: Administrator can identify and resolve duplicates
- **WHEN** administrator views system logs or error reports
- **THEN** logs include: element name, status of conflicting element (active/inactive), user who attempted the operation, timestamp

