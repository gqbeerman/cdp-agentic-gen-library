# Agentic RAG Library - Automated Integration Suite

This document serves as the prompt payload for an agent checking if new features broke the application. An AI agent using Browser Automation should be able to execute these steps strictly.

## Prerequisites
1. Ensure the frontend is running (default: http://localhost:5173).
2. Ensure the backend is running (default: http://localhost:8000).
3. Use test credentials ONLY: 
   - **Email:** `test@agenticrag.com`
   - **Password:** `testpassword123`
   - **OpenRouter API Key:** `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`

---

## 🧪 Test 01: Authentication & App Shell Resilience
**Purpose:** Verifies that the Supabase auth flow and private routing are intact.
**Instructions:**
1. Navigate to the frontend URL.
2. If already logged in, click "Sign Out".
3. Clear the email and password inputs.
4. Input the test email and test password.
5. Click "Login".
**Acceptance Criteria:**
- The agent successfully authenticates and is redirected to the active Chat interface.
- No console errors related to `401 Unauthorized`.

---

## 🧪 Test 02: Chat Thread Lifecycle & Database Persistence
**Purpose:** Verifies the backend `chat_messages` and `user_threads` tables work, RLS operates correctly, and threads auto-name themselves.
**Instructions:**
1. Click the "New Chat" button in the sidebar.
2. In the chat input, send: "Respond with the word 'Verifying' nothing else."
3. Wait for the streaming response to stop.
4. Look at the Sidebar. The previously "New Chat" thread should now have a distinct title (e.g., "Verifying Response").
5. Click "New Chat" again, and verify the main interface clears of messages.
6. Click the newly titled thread from step 4 in the sidebar, and verify that the message history reappears correctly.
7. Click the trash icon next to that thread to delete it.
**Acceptance Criteria:**
- Streaming works without hanging.
- Thread titles change based on the prompt.
- Chat history persists across thread switching.
- Thread deletions immediately reflect in the UI.

---

## 🧪 Test 03: Provider Abstraction & Model Independence
**Purpose:** Verifies that OpenRouter passes authentication and models correctly bubble up errors if rate-limited.
**Instructions:**
1. Click the Settings icon/button.
2. Paste the OpenRouter API Key in the field.
3. In the "Add Custom Model" box, type: `google/gemma-2-9b-it:free` and click Add.
4. Select `google/gemma-2-9b-it:free (Custom)` from the Chat Model dropdown.
5. Close Settings.
6. Start a New Chat and send: "Testing the custom model router."
7. Wait 10 seconds for the response (or error).
**Acceptance Criteria:**
- The UI MUST display the response from the custom model, OR...
- It MUST display an explicit error string on the screen (e.g. `Error: Provider returned error`). It MUST NOT fail silently or fall back to the generic OpenAI ChatGPT responses.

---

## 🧪 Test 04: Document Ingestion UI & Storage Lifecycle
**Purpose:** Verifies Supabase Storage uploading and Realtime subscription inserts into the `documents` table.
**Instructions:**
1. Navigate to the "Documents" interface (if implemented via top navigation).
2. Upload a simple `.txt` file containing the word "testing" using the file upload zone.
3. Observe the newly added document in the list below the uploader.
**Acceptance Criteria:**
- The document appears with status `"uploaded"`.
- The UI updates instantly via Supabase Realtime without requiring a page refresh.
- Clicking delete removes the document from the list.

---

**Completion:** If the agent successfully validates all Acceptance Criteria, declare the validation suite PASSED. If any step fails, return a detailed breakdown of the failure in the test report.
