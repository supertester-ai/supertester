# Supertester

AI-driven software testing workflow for Continue.

## Overview

Supertester is a skill-based plugin that guides you through a complete testing lifecycle:
- Phase 1: Requirement Analysis
- Phase 2: Requirement Association
- Phase 3: Test Case Generation
- Phase 4: Automation Analysis
- Phase 5: Automation Scripting
- Phase 6: Test Reporting

## Usage

Run `/supertester` in Continue chat to start the testing workflow.

For specific tasks:
- `/supertester analyze requirements/auth-prd.md` - Parse requirements
- `/supertester generate tests` - Generate functional test cases
- `/supertester generate scripts` - Generate Playwright E2E scripts

## Workflow Files

All workflow state is persisted to `.supertester/` directory:
- `test_plan.md` - Phase tracking and decisions
- `findings.md` - Research findings
- `progress.md` - Session log
