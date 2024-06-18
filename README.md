# Predacons Server

## About

An OpenAI API-based server built on Predacons to host any Torch and Hugging Face LLM model.

## Running Locally

To run the application locally, follow these steps:

### Prerequisites

- Docker installed on your system
- Docker Compose installed on your system

### Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/Predacons/predacons-server.git
    ```

2. Change into the project directory:

    ```bash
    cd predacons-server
    ```

3. Build the Docker image:

    ```bash
    docker-compose build
    ```

4. Start the containers:

    ```bash
    docker-compose up
    ```

5. Access the application at:

    [http://localhost:8000](http://localhost:8000)

*Environment Variables*

You can configure environment variables in the `env` directory. For example, you can add a `.env` file with the following contents:

API_KEYS=your-api-key


*License*

This project is licensed under multiple licenses:

- For **free users**, the project is licensed under the terms of the GNU Affero General Public License (AGPL). See  [`LICENSE-AGPL`](LICENSE-AGPL) for more details.

- For **paid users**, there are two options:
    - A perpetual commercial license. See [`LICENSE-COMMERCIAL-PERPETUAL`](LICENSE-COMMERCIAL-PERPETUAL) for more details.
    - A yearly commercial license. See [`LICENSE-COMMERCIAL-YEARLY`](LICENSE-COMMERCIAL-YEARLY) for more details.

Please ensure you understand and comply with the license that applies to you.

*Contributing*

Contributions are welcome! Please open a pull request to submit changes.
