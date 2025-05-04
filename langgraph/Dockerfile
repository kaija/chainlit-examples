FROM python:3.13-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml chainlit.md ./

RUN pip install -U pip && pip install .

COPY src/ ./src/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port Chainlit runs on
EXPOSE 8000

# Run the application
CMD ["chainlit", "run", "src/app.py", "--host", "0.0.0.0", "--port", "8000"]
