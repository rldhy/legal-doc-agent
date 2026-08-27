# Ollama Docker Setup with NVIDIA GPU Support

This project uses [Ollama](https://ollama.com/) running in Docker for local LLM inference and embeddings.

The following setup is intended for **Linux systems with an NVIDIA GPU**.

## Prerequisites

Before continuing, make sure you have:

* Docker installed and running
* A supported NVIDIA GPU
* NVIDIA drivers installed
* `nvidia-smi` working on the host

You can verify GPU access with:

```bash
nvidia-smi
```

## 1. Install the NVIDIA Container Toolkit

Docker requires the NVIDIA Container Toolkit to expose the host GPU to containers.

Follow the official NVIDIA installation instructions for your Linux distribution:

https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

For Debian/Ubuntu-based systems, the installation includes configuring the NVIDIA package repository and installing:

```bash
sudo apt-get install -y nvidia-container-toolkit
```

## 2. Configure Docker

Configure the NVIDIA Container Toolkit for Docker:

```bash
sudo nvidia-ctk runtime configure --runtime=docker
```

Restart Docker:

```bash
sudo systemctl restart docker
```

## 3. Verify Docker GPU Access

Before starting Ollama, verify that Docker can access the NVIDIA GPU.

For example:

```bash
docker run --rm --gpus all ubuntu nvidia-smi
```

You should see your GPU listed in the output.

## 4. Start Ollama

Create and start the Ollama container:

```bash
docker run -d \
    --gpus=all \
    -v ollama:/root/.ollama \
    -p 11434:11434 \
    --name ollama \
    ollama/ollama
```

This:

* exposes Ollama at `http://localhost:11434`
* gives Ollama access to all available NVIDIA GPUs
* stores downloaded models in the persistent `ollama` Docker volume

Verify that the container is running:

```bash
docker ps
```

## 5. Pull the Models

Pull the local LLM used for answer generation:

```bash
docker exec -it ollama ollama pull gemma3:12b
```

Pull the embedding model used for document retrieval:

```bash
docker exec -it ollama ollama pull nomic-embed-text
```

## 6. Verify the Models

List the installed models:

```bash
docker exec -it ollama ollama list
```

You should see both models:

```text
gemma3:12b
nomic-embed-text
```

You can also verify that the Ollama API is accessible from the host:

```bash
curl http://localhost:11434/api/tags
```

The response should contain the installed models.

## 7. Verify GPU Usage

Run a model:

```bash
docker exec -it ollama ollama run gemma3:12b
```

While the model is running, check GPU usage from another terminal:

```bash
nvidia-smi
```

The Ollama model server should appear as a GPU process and consume GPU memory.

Exit the Ollama prompt with:

```text
/bye
```

## Configuration

The application connects to Ollama using the settings defined in `.env`.

The default configuration is:

```dotenv
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=gemma3:12b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

See `.env.example` for the complete application configuration.
