# LESA Token & Dispatch API

This project is a FastAPI-based backend service that provides a secure and configurable API for generating [LiveKit](https://livekit.io/) access tokens and dispatching LiveKit LESA agent. It's designed to to use interface for managing LiveKit sessions and agent interactions.

## Features

- **Token Generation:** Securely generate LiveKit JWTs with customizable permissions, including room name, participant identity, and time-to-live (TTL).
- **Agent Dispatch:** Dispatch agents to specific rooms with custom metadata.
- **Configuration Management:** Uses Pydantic for robust and type-safe settings management via environment variables or a `.env` file.
- **Structured Logging:** Utilizes `structlog` for structured, easy-to-parse JSON logs.
- **Middleware:** Includes middleware for logging, security headers, trusted hosts, and CORS.
- **Health Checks:** A dedicated health check endpoint for monitoring the service's status.
- **Backward Compatibility:** Includes a legacy `/status` endpoint for older clients.

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Authentication & Tokens

- **`POST /auth/token`**: Generates a LiveKit access token.
  - **Request Body:**
    - `room`: The name of the room to join.
    - `identity`: The identity of the participant.
    - `name` (optional): The display name of the participant.
    - `ttl_minutes` (optional): The time-to-live for the token in minutes.
    - `mic_only` (optional): If true, the participant can only publish their microphone.
    - `dispatch_agent` (optional): If true, an agent will be dispatched to the room.
  - **Response:** A JSON object containing the generated token, WebSocket URL, and other metadata.

### Agent Management

- **`POST /agent/dispatch`**: Dispatches an agent to a room.
  - **Request Body:**
    - `room`: The name of the room to dispatch the agent to.
    - `agent_name` (optional): The name of the agent to dispatch.
    - `metadata` (optional): Custom metadata to pass to the agent.
  - **Response:** A JSON object containing the dispatch ID and other details.

### Health & Monitoring

- **`GET /health`**: Returns the health status of the service.

## Configuration

The application is configured using environment variables or a `.env` file. The following variables are available:

| Variable                      | Description                                     | Default         |
| ----------------------------- | ----------------------------------------------- | --------------- |
| `ENVIRONMENT`                 | The application environment                       | `development`   |
| `DEBUG`                       | Enable or disable debug mode                    | `False`         |
| `HOST`                        | The host to bind the server to                  | `0.0.0.0`       |
| `PORT`                        | The port to bind the server to                  | `8000`          |
| `LIVEKIT_WS_URL`              | The WebSocket URL for your LiveKit server       | **Required**    |
| `LIVEKIT_URL`                 | The API URL for your LiveKit server             | **Required**    |
| `LIVEKIT_API_KEY`             | Your LiveKit API key                            | **Required**    |
| `LIVEKIT_API_SECRET`          | Your LiveKit API secret                         | **Required**    |
| `AGENT_NAME`                  | The default name for the agent                  | `py-agent`      |
| `TRUSTED_HOSTS`               | A comma-separated list of trusted hosts         | `*`             |
| `MAX_TOKEN_TTL_MINUTES`       | The maximum TTL for a token in minutes          | `1440`          |
| `DEFAULT_TOKEN_TTL_MINUTES`   | The default TTL for a token in minutes          | `60`            |
| `CORS_ALLOW_ORIGINS`          | A comma-separated list of allowed CORS origins  | `*`             |
| `CORS_ALLOW_CREDENTIALS`      | Allow credentials for CORS requests             | `True`          |
| `CORS_ALLOW_METHODS`          | A comma-separated list of allowed CORS methods  | `*`             |
| `CORS_ALLOW_HEADERS`          | A comma-separated list of allowed CORS headers  | `*`             |
| `DISPATCH_CACHE_TTL_SECONDS`  | The TTL for the dispatch cache in seconds       | `3`             |
| `MAX_ROOM_NAME_LENGTH`        | The maximum length for a room name              | `100`           |
| `MAX_IDENTITY_LENGTH`         | The maximum length for a participant identity   | `100`           |

## Running the Application

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Create a `.env` file** in the root of the project and add the required environment variables (see the Configuration section).

3.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```

The API will be available at `http://localhost:8000`.

## Dependencies

This project uses the following major dependencies:

- [FastAPI](https://fastapi.tiangolo.com/): A modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.
- [Pydantic](https://pydantic-docs.helpmanual.io/): Data validation and settings management using Python type annotations.
- [LiveKit API](https://github.com/livekit/python-sdks/tree/main/livekit-api): The official Python SDK for the LiveKit API.
- [Uvicorn](https://www.uvicorn.org/): An ASGI server, for running the FastAPI application.
- [Structlog](https://www.structlog.org/en/stable/): Structured logging for Python.

For a full list of dependencies, see `requirements.txt`.
