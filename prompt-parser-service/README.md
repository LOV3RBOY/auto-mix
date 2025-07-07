# Prompt Parser Service

This service is a core component of the AI Music Production Assistant. Its sole responsibility is to receive a natural-language music prompt and parse it into a structured JSON format that downstream modules can understand.

> This service is part of the AI Music Production Assistant. For global project information, see the [root README.md](../../README.md).

This initial implementation uses regular expressions and keyword matching. It is designed to be replaced or augmented by a more sophisticated NLP model (e.g., using spaCy or a transformer-based NER model) in the future.

---

## API Specification

### Endpoint: `/api/v1/parse`

*   **Method:** `POST`
*   **Description:** Parses a natural language prompt to extract musical entities.
*   **Request Body:** A JSON object with a single `prompt` key.
    ```json
    {
      "prompt": "A high-energy drum and bass track at 174 bpm in the style of Pendulum, with a heavy reese bass"
    }
