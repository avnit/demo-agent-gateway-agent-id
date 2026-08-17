```markdown
# demo-agent-gateway-agent-id Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill provides guidance on developing and maintaining the `demo-agent-gateway-agent-id` Python codebase. It covers the project's coding conventions, how to structure files and imports, and how to write and run tests. The repository does not use a specific framework, focusing instead on clean Python code and consistent project structure.

## Coding Conventions

### File Naming
- Use **snake_case** for all Python files.
  - Example: `agent_handler.py`, `user_utils.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .utils import get_agent_id
    ```

### Export Style
- Use **named exports** (explicitly define what is exported from a module).
  - Example:
    ```python
    __all__ = ['AgentHandler', 'get_agent_id']
    ```

### Commit Messages
- Freeform style, no strict prefixes.
- Average commit message length: ~86 characters.
  - Example: `Add agent ID validation logic and update handler to use new util`

## Workflows

### Adding a New Module
**Trigger:** When introducing new functionality or logical grouping.
**Command:** `/add-module`

1. Create a new Python file using snake_case (e.g., `new_feature.py`).
2. Implement the required classes or functions.
3. Use relative imports to access shared utilities or components.
4. Define `__all__` for named exports if needed.
5. Write corresponding tests in a file named `new_feature.test.py`.

### Writing and Running Tests
**Trigger:** When adding or updating code that requires validation.
**Command:** `/run-tests`

1. Create test files using the pattern `*.test.py` (e.g., `agent_handler.test.py`).
2. Write test functions using standard Python `assert` statements or your preferred test framework.
3. Run tests using your chosen Python test runner (e.g., `pytest`, `unittest`).
   - Example command: `pytest .` (if using pytest)

### Refactoring Imports
**Trigger:** When reorganizing code or modules.
**Command:** `/refactor-imports`

1. Update import statements to use relative imports within the package.
   - Example: Change `from utils import get_agent_id` to `from .utils import get_agent_id`
2. Ensure all modules use consistent import style.
3. Run tests to verify nothing is broken.

## Testing Patterns

- Test files are named using the pattern `*.test.py`.
  - Example: `agent_handler.test.py`
- The specific testing framework is not enforced; use your preferred Python test runner.
- Place test files alongside the modules they test or in a dedicated `tests/` directory.
- Example test:
  ```python
  def test_get_agent_id():
      assert get_agent_id('input') == 'expected_id'
  ```

## Commands
| Command         | Purpose                                      |
|-----------------|----------------------------------------------|
| /add-module     | Create a new module following conventions    |
| /run-tests      | Run all test files in the repository         |
| /refactor-imports | Update imports to use relative style       |
```
