# Browser Use - Enhanced Logging and Bug Report Generation

This repository is a fork of [browser-use](https://github.com/gregpr07/browser-use) with enhanced logging capabilities and automated bug report generation. It allows AI agents to control web browsers to complete given task while providing detailed logging and analysis of agent behavior.

## Features

- Enhanced logging of agent actions and browser interactions
- Automated bug report generation
- Screenshot capture of agent actions
- Task execution from a task list file
- Support for multiple LLM providers (Anthropic, OpenAI, etc.)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/browser-use.git
cd browser-use
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Patchright (required for browser automation):
```bash
patchright install chromium --with-deps --no-shell
```

4. Create a `.env` file with your API keys:
```bash
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
GEMINI_API_KEY=
DEEPSEEK_API_KEY=
GROK_API_KEY=
NOVITA_API_KEY=
```

## Usage

1. Create a `tasks.txt` file with your tasks in the format:
```
task_name: task description
```

2. Run the main script:
```bash
python main.py
```

The script will:
- Read tasks from `tasks.txt`
- Execute each task using an AI agent
- Generate detailed logs in the `agent_logs` directory
- Capture screenshots in the `agent_screenshots` directory


3. Run the bug report generation pipeline:
```bash
python generate_bug_report.py
```
This generates bug reports in the `bug_reports` directory

## Project Structure

- `main.py` - Main entry point for running tasks
- `generate_bug_report.py` - Script for generating bug reports
- `analyze_agent_run.py` - Script for analyzing agent runs
- `agent_logs/` - Directory containing detailed agent logs
- `agent_screenshots/` - Directory containing screenshots of agent actions
- `bug_reports/` - Directory containing generated bug reports
- `tasks.txt` - File containing tasks to be executed

## License

This project is licensed under the same license as the original browser-use repository.

## Acknowledgments

This project is based on the original [browser-use](https://github.com/gregpr07/browser-use) repository by Gregor Žunič and Magnus Müller.
