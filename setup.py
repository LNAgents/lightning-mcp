from setuptools import setup, find_packages

setup(
    name="lightning-mcp",
    version="0.1.0",
    description="Bridge between Lightning Network and Model Context Protocol",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Nick Speer",
    author_email="nick@speer.ai",
    url="https://github.com/LNAgents/lightning-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastmcp>=0.1.0",  # MCP server implementation
        "grpcio>=1.54.0",  # gRPC for LND communication
        "grpcio-tools>=1.54.0",  # Tools for generating gRPC stubs
        "pydantic>=2.0.0",  # Data validation
        "fastapi>=0.100.0",  # REST API (optional)
        "uvicorn>=0.22.0",  # ASGI server (for FastAPI)
        "python-dotenv>=1.0.0",  # Environment variable management
        "cryptography>=41.0.0",  # For TLS/SSL handling
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.1",
            "pytest-asyncio>=0.21.0",
            "black>=23.3.0",
            "isort>=5.12.0",
            "mypy>=1.3.0",
            "flake8>=6.0.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lightning-mcp=lightning_mcp.server.mcp_server:main",
        ],
    },
)
