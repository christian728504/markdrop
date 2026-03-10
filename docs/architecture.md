# Asynchronous Architecture & Security

This document details under-the-hood choices available in **Markdrop v4.0.0+**.

## ⚡ Asynchronous Pipeline

To drastically boost execution speed, the semantic description loop (`markdrop describe`) executes using Python's `asyncio` framework.

1. **`asyncio.gather`**: Images and tables discovered inside the Markdown are separated into distinct task jobs and spawned instantly as HTTP calls concurrently. 
2. **Event Loop Non-Blocking**: To ensure long-running synchronous local ML models (e.g. HuggingFace Transformers, Qwen, or Molmo vision models) don't freeze the async process, their heavy compute loads are delegated sideways into thread pools via `asyncio.to_thread`.
3. **Internal Handling**: If you are using Markdrop natively in your application as a library, `markdrop describe` is implemented using `asyncio.run(process_markdown(config))`. If your application already acts on an active loop, you can explicitly `await process_markdown(config)`.

## 🛡️ Security Posture

### Server Side Request Forgery (SSRF)
The `markdrop convert` command supports downloading PDFs from live internet URLs. Markdrop validates DNS records actively when capturing this URL stream. 

**Blocked Execution Paths:**
* Any resolution tracking back to `.localhost`, `[::1]`, `127.x.x.x`.
* Any resolution into Private IP Subnets (e.g., `192.168.x.x`, `10.x.x.x`).
* Broadcast / Multicast ranges.
* Non HTTP/HTTPS port allocations.

If the validation fails dynamically, the pipeline drops the connection before socket buffers occur, eliminating risk of internal network scanning attacks via malicious CLI executions.

### Path Traversal Protection
Because `markdrop describe` pulls explicit `![alt](file_path)` addresses straight from raw text to encode inside Base64 for OpenAI/Claude submissions, it is vulnerable to Directory Traversal (i.e. if the text maliciously contains `![alt](../../../../../etc/passwd)`).

Markdrop binds the scope rigidly to the exact `[project_directory]/output` root folder. It uses Python's `Path().resolve()` to evaluate bounds and rejects all external assets dynamically.

### Denial of Service Vectors
Network requests are explicitly governed by:
* 30.0 second max execution time.
* Max chunk-sum accumulation of 200MB.

If the file attempts to download infinity (e.g., gzip bombs) the file hook closes the stream completely and issues garbage disposal to clean up the partial temporary file.
