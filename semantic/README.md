# Semantic Knowledge Layer

This directory contains the semantic assets for the Dashboard v4 project. These assets define the project's domain, concepts, and their relationships in a machine-readable format, which can be used to enhance AI agent understanding and automation.

## Structure

- **`/ontologies`**: Contains formal definitions of concepts and relationships within the project's domain (e.g., jobs, users, approvals). These are typically represented in languages like RDF/OWL, using formats such as Turtle (`.ttl`).

- **`/knowledge-graphs`**: Contains representations of entities and their connections. This can include system architecture, data models, or other structured knowledge, often in formats like GraphML (`.graphml`) or structured YAML (`.yml`).

## Purpose

The goal of this layer is to provide a formal, queryable knowledge base that:
- Improves the accuracy of AI coding agents by providing them with explicit domain knowledge.
- Enables automated reasoning and validation of the system's architecture and logic.
- Serves as a single source of truth for the project's core concepts and terminology. 