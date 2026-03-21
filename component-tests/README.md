# Component Tests - Autograder VectorDB

## Requirements

```
cd component-tests
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Docker required:
```
docker --version
docker compose version
```

## Executing

Run all scenarios:
```
behave
```

Run a specific feature:
```
behave features/health.feature
```

## Development

See **[ARCH.md](ARCH.md)** for architecture details and how to add new tests.

## Troubleshooting

If tests fail after code changes, rebuild containers:
```
docker compose -f docker/docker-compose.yml down -v
```
