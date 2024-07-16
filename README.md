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

# predacons-server
an openai api based server built on predacons to host any torch and hugging face llm model 


## Features
- **Model Hosting**: Easily host and manage PyTorch and Hugging Face models.
- **API Key Authentication**: Secure access through API key authentication for both free and paid users.
- **Scalable Architecture**: Designed to scale horizontally to handle increasing loads and concurrent requests.
- **Easy Integration**: Provides a straightforward REST API for integrating with existing applications or services.


## Getting Started

To get started with predacons-server, follow these steps:

1. Clone the repository to your local machine.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Set up your environment variables, including your API keys in a `.env` file.
4. Run the server using `uvicorn main:app --reload`.

For detailed instructions and documentation, please refer to our [Wiki](#) or [Getting Started Guide](#).

## Contribution

Contributions are welcome! If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## Support

If you encounter any issues or require assistance, please open an issue on our GitHub repository.

Thank you for considering predacons-server for your AI model hosting needs!
## License

This project is licensed under multiple licenses:

- For **free users**, the project is licensed under the terms of the GNU Affero General Public License (AGPL). See  [`LICENSE-AGPL`](LICENSE-AGPL) for more details.

- For **paid users**, there are two options:
    - A perpetual commercial license. See [`LICENSE-COMMERCIAL-PERPETUAL`](LICENSE-COMMERCIAL-PERPETUAL) for more details.
    - A yearly commercial license. See [`LICENSE-COMMERCIAL-YEARLY`](LICENSE-COMMERCIAL-YEARLY) for more details.

Please ensure you understand and comply with the license that applies to you.

