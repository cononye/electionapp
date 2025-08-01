# AGENTS.md: Election Results Tracking Platform

This document provides guidance for AI agents working on this codebase.

## 1. Project Overview

This project is a web-based platform for tracking election results in real-time. It allows authenticated party agents and the general public to submit results from polling units. The system then aggregates this data, flags discrepancies, and presents it on dashboards.

## 2. Architecture

-   **Backend**: Django
-   **API**: Django Rest Framework (DRF)
-   **Database**: SQLite (for development), PostgreSQL (for production)
-   **Core Components**:
    -   `election_tracker`: The main Django project.
    -   `results`: A Django app containing all core logic for models, views, and serializers related to the election results.

## 3. Getting Started

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Database Migrations**:
    ```bash
    python manage.py migrate
    ```

3.  **Create a Superuser** (for admin access):
    ```bash
    python manage.py createsuperuser
    ```

4.  **Start the Development Server**:
    ```bash
    python manage.py runserver
    ```

## 4. Key Components & Logic

### 4.1. Data Models (`results/models.py`)

-   `PollingUnit`: Stores details for each polling station.
-   `Party`: Represents a political party.
-   `Agent`: An authenticated party agent, linked to a Django `User`.
-   `ResultSubmission`: The core model for a single result upload. It links to a polling unit, contains the `scores` in a JSONField, and an image of the result form. It also tracks whether the submission is from an `Agent` or a public `User`.
-   `Discrepancy`: Logs conflicts between agent and public submissions for the same polling unit.

### 4.2. Agent Authentication

-   Agent authentication is handled via a custom backend: `results.authentication.AgentCodeBackend`.
-   Agents are identified by a unique code (`unique_code` field on the `Agent` model).
-   To authenticate as an agent, a request to a protected API endpoint must include the header `X-Agent-Code: <your_agent_code>`.
-   A management command is available to create agents:
    ```bash
    # First, create some parties in the Django admin or shell
    # Then, run the command:
    python manage.py create_agents <username> <password> <party_acronym>
    ```

### 4.3. Public User Authentication

-   Public users are standard Django `User` objects and can be authenticated using DRF's default authentication methods (e.g., Session or Token Authentication if configured).

## 5. API Endpoints

### Result Submission

-   **URL**: `/api/results/submit/`
-   **Method**: `POST`
-   **Permissions**: `IsAuthenticated`
-   **Description**: Submits election results for a polling unit. The system automatically detects if the submission is from an agent (via `X-Agent-Code` header) or a public user.
-   **Request Body** (`multipart/form-data`):
    -   `polling_unit_code` (string, required): The unique code of the polling unit.
    -   `scores` (JSON string, required): A JSON object mapping party acronyms to vote counts. Example: `{"APC": 150, "PDP": 120}`.
    -   `result_form_image` (file, required): An image file of the official result sheet.

## 6. Coding Conventions

-   Follow PEP 8 for Python code.
-   Keep models focused on data structure and relationships.
-   Place business logic in services or manager methods, not directly in views. (We can refactor to this pattern as the codebase grows).
-   Write clear and concise docstrings for all functions, classes, and methods.
-   Ensure all new API endpoints are documented in this file.
