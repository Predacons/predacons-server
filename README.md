# Predacons Server

## About

An openai api based server built on predacons to host any torch and hugging face llm model 

## Running Locally

To run the application locally, follow these steps:

### Prerequisites

* Docker installed on your system
* Docker Compose installed on your system

### Steps

1. Clone the repository:
bash
git clone (link unavailable)

1. Change into the project directory:

cd predacons-server

1. Build the Docker image:

docker-compose build

1. Start the containers:

docker-compose up

1. Access the application at:

http://localhost:8000

*Environment Variables*

You can configure environment variables in the `env` directory. For example, you can add a `.env` file with the following contents:

API_KEYS=your-api-key


*License*

This project is licensed under [LICENSE].

*Contributing*

Contributions are welcome! Please open a pull request to submit changes.


[LICENSE]: https://github.com/Predacons/predacons-server/blob/main/LICENSE-AGPL