# Architecture - Component Tests

## Structure

```
component-tests/
├── docker/                     # Docker environment configs
│   ├── docker-env/             # Environment variable files
│   ├── docker-compose.yml      # Test infrastructure
│   └── Dockerfile.api.*        # API container build
├── features/                   # BDD test definitions
│   ├── steps/                  # Step implementations
│   ├── src/                    # Source code organized in layers
│   │   ├── commons/            # Reusable across projects
│   │   └── business/           # Project-specific logic
│   ├── environment.py          # Behave lifecycle hooks
│   └── *.feature               # Gherkin scenario files
├── resources/                  # Test data organized by scenario
│   ├── common/                 # Shared resources
│   └── {scenario_name}/        # Per-scenario resources
│       └── http/
│           ├── request/        # Request payloads
│           └── response/       # Expected responses
└── requirements.txt
```

## Patterns

### Context Pattern

- **GlobalContext**: Shared across all scenarios (Docker Compose lifecycle)
- **ScenarioContext**: Isolated per scenario (HTTP state between steps)

### Service Pattern

All services use Singleton pattern with `execute()` method.

### Layers

- **Commons**: Generic services (HTTP, Docker, JSON, file I/O)
- **Business**: Project-specific (endpoint config, scenario context)

## Adding New Tests

1. Create a `.feature` file in `features/`
2. Add step definitions in `features/steps/` (reuse commons steps when possible)
3. Add endpoint to `EndpointEnum` if needed
4. Create request/response JSON files in `resources/{scenario_name}/http/`
