# Component Tests — Autograder VectorDB

BDD component tests using [Behave](https://behave.readthedocs.io/) that spin up the API inside Docker and validate its HTTP behaviour end-to-end.

---

## Prerequisites

| Tool | Minimum version | Check |
|------|----------------|-------|
| Python | 3.11+ | `python3 --version` |
| Docker | 24+ | `docker --version` |
| Docker Compose v2 | 2.20+ | `docker compose version` |

> Make sure the Docker daemon is running before proceeding.

---

## Setup

```bash
cd component-tests
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Running the tests

All commands below assume you are inside the `component-tests/` directory with the virtualenv activated.

### Run all scenarios

```bash
behave
```

With elapsed time:

```bash
start=$(date +%s); behave; end=$(date +%s); echo "Total: $((end - start))s"
```

### Run a single feature

```bash
behave features/health.feature
```

### Run scenarios by tag

```bash
behave -t @smoke
```

### Verbose / debug output

```bash
behave --logging-level=DEBUG
```

---

## What happens when you run `behave`

1. **`before_all`** — Builds and starts the Docker Compose stack defined in `docker/docker-compose.yml`. The runner waits until the API container logs `Application startup complete.` (retries up to ~3 min).
2. **`before_scenario`** — Creates a fresh `ScenarioContext` so each scenario starts with clean HTTP state.
3. **Scenario steps execute** — Steps read request/response JSON files from `resources/`, make real HTTP calls to the containerised API, and assert on status codes and response bodies.
4. **`after_scenario`** — Destroys the scenario context.
5. **`after_all`** — Tears down the Docker Compose stack.

---

## Docker environment

The test infrastructure is defined in `docker/docker-compose.yml`:

| Service | Image | Host port | Purpose |
|---------|-------|-----------|---------|
| `tests-autograder-vectordb-api` | Built from `Dockerfile.api.component-tests` | `8000` | The API under test |

Environment variables for the API container live in `docker/docker-env/api.env`.

### ⚠️ Rebuilding containers after application changes

Docker images are built once and cached. **They are not rebuilt automatically between test runs.** This means that if you change anything in the application and run the tests again, they will still run against the old version of the code.

You **must** tear down the containers whenever you change:

- Any API source code (`api/app/**`)
- Python dependencies (`api/requirements.txt`)
- The Dockerfile (`docker/Dockerfile.api.component-tests`)
- Environment variables (`docker/docker-env/api.env`)

```bash
docker compose -f docker/docker-compose.yml down -v
```

After that, the next `behave` run will rebuild the image with your latest changes.

### Manually managing the stack

```bash
# Start
docker compose -f docker/docker-compose.yml up -d --build

# View logs
docker compose -f docker/docker-compose.yml logs -f tests-autograder-vectordb-api

# Stop and remove volumes
docker compose -f docker/docker-compose.yml down -v
```

---

## Project structure

```
component-tests/
├── docker/
│   ├── docker-compose.yml              # Test infrastructure
│   ├── docker-env/api.env              # API environment variables
│   └── Dockerfile.api.component-tests  # API container build
├── features/
│   ├── *.feature                       # Gherkin scenarios
│   ├── environment.py                  # Behave lifecycle hooks
│   ├── steps/                          # Step definitions
│   │   ├── __commons__http_steps.py    # Reusable HTTP steps
│   │   └── api_steps.py               # API-specific steps
│   └── src/
│       ├── commons/                    # Reusable layer
│       │   ├── context/                # Shared data classes
│       │   └── services/               # HTTP, Docker, JSON, file I/O
│       └── business/                   # Project-specific layer
│           ├── config/endpoint_enum.py # API endpoint URLs
│           └── context/                # Global + Scenario context
├── resources/                          # Test data per scenario
│   └── {scenario_name}/http/
│       ├── request/                    # Request payloads (.json)
│       └── response/                   # Expected responses (.json)
├── requirements.txt
├── ARCH.md                             # Architecture deep-dive
└── README.md                           # ← you are here
```

See **[ARCH.md](ARCH.md)** for architecture patterns and how to add new tests.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Docker compose file not found` | Run commands from inside `component-tests/` |
| Container never becomes ready | Check logs: `docker compose -f docker/docker-compose.yml logs` |
| Port 8000 already in use | Stop whatever is using it: `lsof -i :8000` |
| Tests fail after code changes | Rebuild: `docker compose -f docker/docker-compose.yml down -v` |
| `ModuleNotFoundError` | Activate the venv: `source venv/bin/activate` |
