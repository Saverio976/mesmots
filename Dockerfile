FROM python:3.13

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

ENV ENVIRON="production"
ENV HOST="0.0.0.0"
ENV PORT="7860"

COPY --chown=user ./uv.lock pyproject.toml /app/
RUN pip install --no-cache-dir --upgrade uv
RUN uv sync

COPY --chown=user mesmots /app/mesmots
COPY --chown=user datasets /app/datasets

WORKDIR /app/mesmots

CMD ["uv", "run", "."]
