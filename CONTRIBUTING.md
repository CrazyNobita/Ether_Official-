# Contributing to Ether

Thank you for your interest in contributing to Ether! We welcome all developers who are passionate about building secure, modular, and high-performance Telegram tools.

## Project Philosophy

Ether is designed with three core principles:
1.  **Sovereignty**: Users should have full control over their data and sessions.
2.  **Modularity**: The system should be easily extendable via a simple plugin architecture.
3.  **Performance**: High-concurrency handling using native asynchronous drivers.

## How Can I Help?

### Developing Plugins
Plugins are the heart of Ether. To contribute a new plugin:
- Create a `.py` file in the `plugins/` directory.
- Implement the mandatory `setup(ether, db, owner_id)` entry point.
- Use the `utils.logger` for all logging (avoid `print`).
- Ensure any new database collections follow the naming convention `plugin_name_data`.

### Core Contributions
If you wish to modify the core engine:
1.  Fork the repository and create your feature branch.
2.  Keep changes atomic and focused on a single improvement.
3.  Ensure compatibility with Python 3.10+.
4.  Update the documentation if you change configuration variables or core APIs.

### Bug Reports
- Open a new Issue in the GitHub repository.
- Provide a clear title and a detailed description of the problem.
- Include environment details (OS, Python version, hosting platform).
- Attach relevant logs (with sensitive data like tokens or phone numbers redacted).

## Coding Standards

To maintain a professional codebase, all contributions must adhere to the following:
- **Style**: Follow PEP 8 guidelines.
- **Type Safety**: Use Python type hints for all function signatures.
- **Documentation**: Provide docstrings for classes and complex functions.
- **Async First**: Use `await` for all I/O operations (database, network, file system).

## Attribution & Licensing

Ether is an open-source project that values its origins.
- **Credits**: Original attribution to LearningBotsOfficial must remain intact in all files.
- **License**: All contributions will be licensed under the MIT License.

## Pull Request Process

1.  Synchronize your fork with the `main` branch of the original repository.
2.  Run basic linting on your changes.
3.  Submit your Pull Request with a clear summary of what was added or changed.
4.  Wait for the maintainers to review and provide feedback.

---

**Made with love by [LearningBotsOfficial](https://github.com/LearningBotsOfficial)**
