FROM python:3.13-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml chainlit.md sqlite.sql ./

RUN pip install -U pip && pip install .

COPY src/ ./src/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port Chainlit runs on
EXPOSE 8000

# Initialize database and run the application
CMD python src/init_db.py && chainlit run src/app.py --host 0.0.0.0 --port 8000
