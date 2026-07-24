FROM python:3.14-slim AS builder

WORKDIR /src

COPY . .

RUN python -m pip install --no-cache-dir build \
    && python -m build --wheel


FROM python:3.14-slim

LABEL org.opencontainers.image.source="https://github.com/chin/hybrid-ai-quantum-platform"
LABEL org.opencontainers.image.description="Polymorphic hybrid optimization engine"
LABEL org.opencontainers.image.licenses="MIT"

COPY --from=builder /src/dist/*.whl /tmp/

RUN python -m pip install --no-cache-dir /tmp/*.whl \
    && rm -f /tmp/*.whl

ENTRYPOINT ["python", "-m", "optengine"]
CMD ["--help"]