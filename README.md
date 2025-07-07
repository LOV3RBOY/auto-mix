# AI Music Production Assistant

Welcome to the AI Music Production Assistant, a full-stack application designed to generate complete music tracks from natural language prompts. This project leverages a microservice architecture to handle distinct stages of the music creation process, from prompt analysis to final mastering.

---

## 1. Project Overview

The system empowers users to create music by simply describing what they want. It can take prompts like *"A high-energy drum and bass track at 174 bpm in the style of Pendulum"* and produce a ready-to-listen audio file. This is achieved through a pipeline of specialized AI and audio processing services working in concert.

This repository contains the complete, production-ready source code, comprehensive documentation, a full test suite, and a continuous integration pipeline, making it a robust foundation for further development.

## 2. Architecture

The application is built using a **microservice architecture**. A central **Job Orchestrator** manages the workflow, delegating tasks to specialized services. This design ensures scalability, fault isolation, and maintainability.

### Architectural Flow

