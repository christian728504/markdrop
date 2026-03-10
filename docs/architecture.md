# Internal Architecture & Security

This document outlines the critical infrastructural protections and runtime performance optimizations that dictate how Markdrop executes and validates complex PDF-to-Markdown manipulations under the hood.

---

## Phase 4 Performance: Asynchronous Parallel Execution

Converting unstructured, 100-page academic layouts laden with complex images, graphs, and tabular data into pure text has traditionally been a heavily constrained, synchronous processing pipeline. Markdrop eliminates this bottleneck by processing semantic reasoning simultaneously via `asyncio`.

When `markdrop describe` initiates:
1.  **Regex Identification:** Markdrop reads the raw sequence and builds a localized list of pattern-matched image links `![alt](path)` and ASCII representations of `| Tables |`.
2.  **Concurrency Generation:** Both lists map completely towards unique, detached coroutines (`_replace_image_match()` and `_replace_table_match()`).
3.  **Rest Dispatch:** All tasks dispatch inside giant `asyncio.gather(*tasks)` pools. This means if your document contains 45 complex graphics, 45 non-blocking API requests are fired almost immediately at the OpenAI/Google Gemini endpoints.
4.  **String Reconciliation:** The script yields control back to the event loop, waiting dynamically for the responses to return. As each description resolves, it incrementally validates and builds out the final enriched unstructured document block.

### Local GPU Workload Protection
Because local Hugging Face `transformers` models (like Qwen, or Molmo) process inference sequentially on the internal hardware (which relies on `torch.generate`), executing them directly within our async block would fundamentally deadlock the Python event loop, crippling application responsiveness.
*   **Resolution:** Within `models/responder.py`, these heavy procedural tasks are carefully wrapped inside parameterless functions and injected out of scope via `await asyncio.to_thread(_run_molmo)`.

---

## Security Defenses (v4.0.0 Refactor)

Markdrop interacts closely with the user's base operating system. It relies heavily on writing disk files, evaluating network paths, and downloading executables. Rigorous mitigations guard against common exploit vectors.

### 1. Server Side Request Forgery (SSRF) Mitigations
Markdrop allows users to pass an active URL to `markdrop convert` (e.g. `markdrop convert https://domain.com/paper.pdf`). A malicious user could provide `http://192.168.1.100/admin_secrets.pdf` prompting the Python server running Markdrop to scrape its own secure internal endpoints.

The `download_pdf()` utility natively protects against this payload:
*   The script uses `urllib.parse` and the `ipaddress` modulus to recursively validate the domain target. 
*   It explicitly blocks network connections routing back to `.localhost`, `[::1]`, and `127.x.x.x`.
*   It halts connections targeting Private IPv4 Subnets (e.g., `192.168.x.x`/16, `10.x.x.x`/8, `172.16.x.x`/12) and their IPv6 localized analogs.
*   It blocks Broadcast / Multicast ranges.
*   Only valid `http://` or `https://` schemas are allowed to run.

### 2. Path Traversal Sandbox (`../`) Containment
In `markdrop describe`, Markdrop dynamically reads the string `![alt](images/1.jpg)` via Regex and opens the visual asset on the filesystem to convert it to Base64 byte-streams to pass to the Vision algorithms.

A malicious text injection payload within an original PDF—for example, explicitly trying to inject a spoofed image matching `![alt](../../../../../etc/passwd)`—could trick Markdrop into Base64 encoding the host machine's root credentials and appending them directly into the output prompt stream.

**Resolution (`replace_image` method in `parse.py`):**
Markdrop calculates the exact working root environment where the original `.md` conversion initially took place using strict `absolute_path().resolve()`. Every Regex parsed linked structure must subsequently `str(target).startswith(str(root))` validating it remains strictly confined within the data output folder hierarchy. Assets targeting structures beyond this scope are logged dynamically as `"Blocked path traversal attempt:"` and immediately aborted from processing.

### 3. File Execution Handling & Race Conditions
*   **Denial of Service Guard:** Downloaded PDFs are governed aggressively by a hard `200MB` accumulation check loop inside the memory buffer and a `[30.second]` absolute max transfer TTL to prevent gzip bombs. All disconnected stream buffers immediately fire `cleanup_download_dir()` to permanently remove orphaned local data chunks.
*   **Temp File Descriptors:** `add_downloadable_tables()` relies on building actual internal `.xlsx` spreadsheet objects out of Pandas data. Historically it hardcoded these to `temp.xlsx` exposing system race conditions when processing huge document libraries dynamically. This is now fully normalized towards `tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")` guaranteeing absolute I/O collision isolation across multiprocessor pipelines.

### 4. Application Sandboxing (.env Guarding)
`markdrop setup` is the interactive key vault mechanism. Keys are dynamically inserted to `[Base_Dir]/.env`. To protect server credentials in shared UNIX architectures, the vault actively applies `os.chmod(env_path, 0o600)` immediately on execution. Standard operating system principles protect the file exclusively limiting read capacities simply exclusively to the system-process executor.
