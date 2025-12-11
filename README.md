# **SolidGuard – Smart Contract Vulnerability Analyzer**

AI-powered real-time detection of Solidity smart contract vulnerabilities.

### Pre-Install

Install the required system tools for Taskfile, Python, Node, and Bun.

You can either run

``` bash
task setup
```

or you can look through the pre-install requirements below and do it yourself

------------------------------------------------------------------------

### **Pre-Install Requirements**

#### **uv (Python env manager)**

-   **Mac:** `brew install uv`
-   **Linux:** `curl -LsSf https://astral.sh/uv/install.sh | sh`

#### **Taskfile**

-   **Mac:** `brew install go-task/tap/go-task`
-   **Linux:** `sh -fsSL https://taskfile.dev/install.sh | sh`

#### **Python / pip**

-   **Mac:** `brew install python`
-   **Linux:** `sudo apt-get install python3 python3-pip -y`

#### **Node.js (18+)**

-   **Mac:** `brew install node`
-   **Linux:** `sudo apt-get install nodejs npm -y`

#### **Bun (Mac/Linux)**

-   `curl -fsSL https://bun.sh/install | bash`

------------------------------------------------------------------------

### Install dependencies

``` bash
task install
```

------------------------------------------------------------------------

## Environment Setup

Inside the **backend/** directory, create your `.env`:

``` bash
echo "OPENAI_API_KEY=your-api-key-here" > backend/.env
```

No quotes needed around the key itself.

------------------------------------------------------------------------

### Run backend + frontend together

(Always run this from the project root: `proj-02-extra-parliament`)

``` bash
task app
```

### Stop and clean all servers

(Required before restarting another session)

``` bash
clear
task end
```

------------------------------------------------------------------------

## Core Files You Should Know

```         
knowledge_store.jsonl   ← RAG knowledge base (stored at project root)
Taskfile.yml            ← Defines all commands (install, app, end, etc.)
backend/prompts/        ← Prompts for RAW + RAG analysis
backend/app.py          ← FastAPI backend
frontend/src/           ← React + TypeScript frontend
```

You do **not** need anything inside the `research/` directory to run the app.

------------------------------------------------------------------------

## Features

-   Real-time vulnerability detection
-   GPT-based classification (RAW + RAG modes)
-   Vulnerability highlighting in the editor
-   Contract generator (10 attack types)
-   Model selection (4.1-mini / 4.1 / GPT-5.1)

------------------------------------------------------------------------

## Notes for Developers

-   The **Taskfile** is the main interface for development. It provides the simplest commands to install, run, and stop everything.

-   To modify analysis behavior, edit the prompts in:

    ```         
    backend/prompts/
    ```

-   To modify the RAG knowledge, edit:

    ```         
    knowledge_store.jsonl
    ```

    Then restart:

    ``` bash
    task end
    task app
    ```

------------------------------------------------------------------------

## License

Cornell INFO 4940 (Fall 2025) — for educational use only.# solidguard
