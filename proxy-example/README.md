# JupyterLab Deployment with Configurable HTTP Proxy and Nginx Reverse Proxy

## Introduction

This project extends the existing JupyterLab deployment by introducing a robust proxy setup using both Configurable HTTP Proxy and Nginx Reverse Proxy. This configuration enhances the flexibility and security of the deployment.

## Improvements

- Added **Configurable HTTP Proxy** for managing the internal routing of JupyterLab services.
- Integrated an **Nginx Reverse Proxy** layer for secure external access.
- Provided a sample Nginx configuration optimized for this setup.

## Deployment

The deployment is managed with `docker-compose`, ensuring ease of setup and consistency. The `docker-compose.yml` includes the following services:

- `hub`: The main JupyterHub service.
- `proxy`: The Configurable HTTP Proxy service.
- `reverse-proxy`: The Nginx Reverse Proxy service.

## Usage

To deploy the JupyterLab environment:

1. Clone this repository.
2. Navigate to the repository directory.
3. Run `docker-compose up -d`.
4. Once the deployment is complete, navigate to `http://localhost:8001` to access the JupyterHub interface through the Nginx Reverse Proxy.

## Contributing

Contributions are welcome! For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgments

Improvement contributed by Hung Dinh Xuan @hungdinhxuan
