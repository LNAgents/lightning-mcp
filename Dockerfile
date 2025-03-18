FROM python:3.10-slim

WORKDIR /app

# Install uv for package management
RUN pip install --upgrade pip && \
    pip install uv

# Create virtual environment with explicit path
ENV VIRTUAL_ENV=/app/.venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy just requirements first to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the code
COPY . .

# Install the package
RUN pip install -e .

# Expose MCP server port
EXPOSE 8080

# Mount points for configuration and Lightning Network credentials
VOLUME ["/app/config", "/root/.lnd"]

# Environment variable for config path
ENV LIGHTNING_MCP_CONFIG=/app/config/config.json

# Run the server using the virtual environment's Python
CMD ["python", "-m", "lightning_mcp.server.mcp_server"] 