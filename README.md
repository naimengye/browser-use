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
git clone https://github.com/naimengye/browser-use.git
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

2. Run one time the setup environment script
```bash
python setup_test_env.py
```

This script will:
- Prompt you to input the login credentials that gets programmatically processed once, and then save the cookies for future launches

2. Run the main script:
```bash
python main.py
```

The script will:
- Either programmatically login to (currently set) google when there is no cookie available, or read from past browser cookies and launch a browser that is already logged in.
- Read tasks from `tasks.txt`
- Execute each task using an AI agent
- Generate detailed logs in the `agent_logs` directory
- Capture screenshots in the `agent_screenshots` directory
- Note that currently the script is written such that the white listed domains are limited to a few big websites. Should change this later.


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
