# CLAUDE.md

RAG app with chat (default) and document ingestion interfaces. Config via env vars, no admin UI.

## Stack
- Frontend: React + Vite + Tailwind + shadcn/ui
- Backend: Python + FastAPI
- Database: Supabase (Postgres, pgvector, Auth, Storage, Realtime)
- LLM: OpenAI (Module 1), OpenRouter (Module 2+)
- Observability: LangSmith

## Rules
- Python backend must use a `venv` virtual environment
- No LangChain, no LangGraph - raw SDK calls only
- Use Pydantic for structured LLM outputs
- All tables need Row-Level Security - users only see their own data
- Stream chat responses via SSE
- Use Supabase Realtime for ingestion status updates
- Module 2+ uses stateless completions - store and send chat history yourself
- Ingestion is manual file upload only - no connectors or automated pipelines
- **MANDATORY:** Always run the validation suite located at `.agent/tests/integration-suite.md` using a browser subagent when verifying changes to ensure no regressions occur.
- **MANDATORY:** If you implement a new feature, you must update `.agent/tests/integration-suite.md` to include a new test validating your specific feature implementation.

## Planning
- Save all plans to `.agent/plans/` folder
- Naming convention: `{sequence}.{plan-name}.md` (e.g., `1.auth-setup.md`, `2.document-ingestion.md`)
- Plans should be detailed enough to execute without ambiguity
- Each task in the plan must include at least one validation test to verify it works
- Assess complexity and single-pass feasibility - can an agent realistically complete this in one go?
- Include a complexity indicator at the top of each plan:
  - ✅ **Simple** - Single-pass executable, low risk
  - ⚠️ **Medium** - May need iteration, some complexity
  - 🔴 **Complex** - Break into sub-plans before executing

## Development Flow
1. **Plan** - Create a detailed plan and save it to `.agent/plans/`
2. **Build** - Execute the plan to implement the feature
3. **Validate** - Test and verify the implementation works correctly. Use browser testing where applicable via an appropriate MCP
4. **Iterate** - Fix any issues found during validation

## Progress
Check PROGRESS.md for current module status. Update it as you complete tasks.

### Verify Services
- Backend health: `curl http://localhost:8000/health` should return `{"status":"ok"}`
- Frontend: Open http://localhost:5173 in browser

## Test Credentials
For browser testing and validation:
- **Email:** test@agenticrag.com
- **Password:** testpassword123
For OpenRouter API Key:
- **OpenRouter API Key:** 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
- **openrouter model:** z-ai/glm-4.5-air:free

## Testing Process
Never create a new user for testing purposes. Always use the test user credentials above.
- When entering credentials in the browser, first select "Login", not "Sign Up".
- Before entering credentials, clear the credential fields to ensure the correct credentials are used.
- Your primary testing mechanism should be the integration suite. After making significant code changes, **you MUST run `browser_subagent` following the instructions laid out in `.agent/tests/integration-suite.md`**.
- When you create new features (guided by documents in `.agent/plans/`), you must append a new test case to `.agent/tests/integration-suite.md` with explicit instructions and strictly defined Acceptance Criteria.

## Progress
Check PROGRESS.md for current module status. Update it as you complete tasks.

# Notes

The Python Virtual Environemtn is located in the folder /backend/venv/ NOT .venv