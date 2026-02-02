FROM python:3.13

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

ENV PYTHONUNBUFFERED="y"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONOPTIMIZE="2"

ENV ENVIRON="production"
ENV HOST="0.0.0.0"
ENV PORT="7860"

COPY --chown=user ./uv.lock pyproject.toml /app/
RUN pip install --no-cache-dir --upgrade uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0
RUN uv sync

COPY --chown=user mesmots /app/mesmots
COPY --chown=user dataset /app/dataset

WORKDIR /app/mesmots

CMD ["uv", "run", "."]
