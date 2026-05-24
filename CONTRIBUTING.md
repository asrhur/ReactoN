# Contributing to ReactoN

Thank you for your interest in contributing to ReactoN!

## Current Status (May 2026)

ReactoN is currently in **private development** (TRL 4). 

**Public contributions will open after the August 2026 release.**

For now, contributions are limited to the ASRHÜR core team.

## For Team Members

### Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally.
3. Run tests: `pytest tests/`
4. Maintain a high code coverage ($\ge 90\%$).
5. Create a pull request with a clear description of the modifications, mathematical formulas used, or bug fixes.
6. A code review by at least one other team member is required before merging.

### Code Style

- Follow **PEP 8** style guidelines.
- Use explicit type hints for all public function signatures and class definitions.
- Include Google-style docstrings detailing arguments, returns, and raised exceptions.
- Add comments explaining complex chemical kinetics, thermodynamics, and pressure equations.

### Testing Requirements

- Write unit tests for all new core algorithms.
- Provide integration tests for combined system simulators (e.g., PID and PLC loops).
- Maintain robust validation benchmarks.

---

**Questions?** Contact: dogukan@asrhur.com
