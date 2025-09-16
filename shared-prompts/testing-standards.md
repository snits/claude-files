# Testing Standards

## NO EXCEPTIONS POLICY
ALL projects MUST have unit tests, integration tests, AND end-to-end tests. The only way to skip any test type is if Jerry EXPLICITLY states: "I AUTHORIZE YOU TO SKIP WRITING TESTS THIS TIME."

## Testing Requirements
- Tests MUST comprehensively cover ALL functionality
- Project-appropriate testing methodology required (see workflow-integration.md for methodology selection)
- YOU MUST NEVER write tests that "test" mocked behavior. If you notice tests that test mocked behavior instead of real logic, you MUST stop and warn Jerry about them
- YOU MUST NEVER implement mocks in end to end tests. We always use real data and real APIs
- YOU MUST NEVER ignore system or test output - logs and messages often contain CRITICAL information
- YOU MUST NEVER mock the functionality you're trying to test
- Test output MUST BE PRISTINE TO PASS. If logs are expected to contain errors, these MUST be captured and tested

## Testing Methodology Selection

**METHODOLOGY ASSESSMENT**: Select testing approach based on project characteristics:
- **Classical TDD**: Well-defined requirements, clear specifications
- **Discovery Testing**: Exploratory projects, evolving requirements
- **Integration-First**: API-heavy, integration-focused systems
- **Characterization Testing**: Legacy systems, refactoring projects
- **End-to-End First**: UI/UX focused, user workflow validation priority

**SELECTION CRITERIA**:
- Problem clarity and requirement stability
- Integration complexity and external dependencies
- Legacy constraints and existing codebase maturity
- Risk tolerance and project timeline

**NON-NEGOTIABLE REGARDLESS OF METHODOLOGY**:
- Real functionality testing (never mock system under test)
- Comprehensive coverage (unit + integration + end-to-end)
- Pristine test output (all tests pass cleanly)
- test-specialist approval before commits

## Quality Assurance Integration

### test-specialist Mandatory Triggers:
- **After any new feature implementation** - Must validate comprehensive test coverage
- **After bug fixes** - Must ensure fix is properly tested and won't regress
- **When discovering untested code** - Must implement missing test coverage immediately
- **Before committing code** - Must verify all tests pass and coverage is complete

### qa-engineer Mandatory Triggers:
- **Before marking features as complete** - Must validate end-to-end user workflows
- **After bug fixes** - Must verify fix works in real user scenarios
- **Before releases** - Must conduct final quality validation across environments
- **When integration issues suspected** - Must test component interactions

### Quality Assurance Authority:
- **BLOCKING POWER**: Both QA agents can block commits/releases for quality violations
- **ESCALATION PATH**: Quality concerns override implementation timelines
- **DOCUMENTATION REQUIREMENT**: All quality issues must be documented with specific remediation steps