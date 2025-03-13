FROM python:3.10-slim

WORKDIR /app

# Install uv for package management
RUN pip install --upgrade pip && \
    pip install uv

# Copy just requirements first to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN uv pip install -r requirements.txt

# Copy the rest of the code
COPY . .

# Install the package
RUN uv pip install -e .

# Expose MCP server port
EXPOSE 8080

# Mount points for configuration and Lightning Network credentials
VOLUME ["/app/config", "/root/.lnd"]

# Environment variable for config path
ENV LIGHTNING_MCP_CONFIG=/app/config/config.json

# Run the server
CMD ["python", "-m", "lightning_mcp.server.mcp_server"] 