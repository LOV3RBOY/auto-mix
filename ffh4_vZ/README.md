# AI Music Production Assistant

Welcome to the AI Music Production Assistant, a full-stack application designed to generate complete music tracks from natural language prompts. This project leverages a microservice architecture to handle distinct stages of the music creation process, from prompt analysis to final mastering.

---

## 1. System Architecture

The application is built around a central **Job Orchestrator** that manages a workflow across several specialized microservices. A request from a client (e.g., the CLI) triggers a series of asynchronous tasks handled by a Celery worker.

### Architectural Flow

