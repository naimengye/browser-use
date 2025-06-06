# Browser Use - Enhanced Logging and Bug Report Generation

This repository is a fork of [browser-use](https://github.com/gregpr07/browser-use) with enhanced logging capabilities and automated bug report generation. It allows AI agents to control web browsers to complete given task while providing detailed logging and analysis of agent behavior.

## Features

- **YAML-based Configuration**: All agent behavior configurable via YAML files
- **Enhanced Logging**: Detailed logging of agent actions and browser interactions
- **Automated Bug Report Generation**: Generate comprehensive bug reports
- **Screenshot Capture**: Visual documentation of agent actions
- **Flexible Task Execution**: Execute tasks from configurable task files
- **Multi-LLM Support**: Support for OpenAI, Anthropic, and other LLM providers
- **Memory Management**: Long-term memory for complex multi-step tasks
- **Authentication Management**: Persistent login and session management
- **Security Controls**: Domain restrictions and sensitive data handling

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
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
GEMINI_API_KEY=
DEEPSEEK_API_KEY=
GROK_API_KEY=
NOVITA_API_KEY=
```

## Quick Start

For a quick test run:

1. Set your OpenAI API key in `.env`
2. Run: `python main.py`
3. The agent will execute the default task with 5 steps
4. Check `agent_logs/` and `agent_screenshots/` for results

For detailed documentation, see [BROWSER_USE_TUTORIAL.md](BROWSER_USE_TUTORIAL.md).

## Usage

### 1. Configure the Agent

Edit `configs/config.yaml` to configure browser, LLM, and agent settings:

```yaml
# Browser configuration
browser:
  headless: false
  use_test_profile: true
  test_profile_name: "test_profile"

# Browser context configuration
context:
  disable_security: true
  cookies_file: "auth_data/test_profile/cookies.json"
  allowed_domains: null  # null = allow all domains

# LLM configuration
llm:
  provider: "openai"  # or "anthropic"
  model: "gpt-4o"
  temperature: 0.7

# Agent configuration
agent:
  max_steps: 5            # Maximum steps per task
  max_failures: 3         # Max consecutive failures
  use_vision: true        # Enable screenshot analysis
  enable_memory: true     # Enable long-term memory
  max_actions_per_step: 10

# Authentication management
auth_manager:
  ensure_logged_in: false  # Auto-login to services
  save_auth_state: false   # Save auth between runs

tasks_file: "tasks_test.txt"
```

### 2. Create Tasks

Create a task file (e.g., `tasks_test.txt`) with your tasks:
```
Academic website: Go to the website "https://naimengye.github.io/", explore and analyze the content
Google search: Search for "browser automation tools" and extract the top 5 results
Form filling: Fill out the contact form on example.com with test data
```

### 3. Setup Environment (One-time)

Run the setup script to configure authentication:
```bash
python setup_test_env.py
```

This script will:
- Prompt you to input login credentials for automated processing
- Save browser cookies for future launches

### 4. Run the Agent

Execute the main script:
```bash
python main.py
```

The script will:
- Load configuration from `configs/config.yaml`
- Either use saved cookies or perform programmatic login
- Read tasks from the configured task file
- Execute each task using the AI agent with your configured settings
- Generate logs in the `agent_logs/` directory
- Capture screenshots in the `agent_screenshots/` directory

### 5. Advanced Usage

**Custom Configuration:**
```bash
# Use a different config file
python main.py with configs/config_research.yaml
```

**Different Use Cases:**

**Quick Testing (`config_quick.yaml`):**
```yaml
agent:
  max_steps: 10
  use_vision: false
  enable_memory: false
llm:
  model: "gpt-4o-mini"
```

**Production (`config_prod.yaml`):**
```yaml
agent:
  max_steps: 50
browser:
  headless: true
context:
  allowed_domains: ["trusted-site.com"]
```


### 6. Generate Bug Reports

Run the bug report generation pipeline:
```bash
python generate_bug_report.py
```
This generates bug reports in the `bug_reports/` directory - change the specific task to generate a report on.

## Configuration Options

Key configuration parameters in `configs/config.yaml`:

| Section | Parameter | Description | Default |
|---------|-----------|-------------|---------|
| `agent` | `max_steps` | Maximum steps per task | `5` |
| `agent` | `max_failures` | Max consecutive failures | `3` |
| `agent` | `use_vision` | Enable screenshot analysis | `true` |
| `agent` | `enable_memory` | Enable long-term memory | `true` |
| `llm` | `provider` | LLM provider (openai/anthropic) | `"openai"` |
| `llm` | `model` | Model name | `"gpt-4o"` |
| `browser` | `headless` | Run without GUI | `false` |
| `context` | `allowed_domains` | Restrict to specific domains | `null` |

For complete configuration documentation, see [BROWSER_USE_TUTORIAL.md](BROWSER_USE_TUTORIAL.md).

## Project Structure

- `main.py` - Main entry point for running tasks
- `configs/config.yaml` - Main configuration file for all agent settings
- `setup_test_env.py` - Script for setting up login credentials
- `generate_bug_report.py` - Script for generating bug reports
- `analyze_agent_run.py` - Script for analyzing agent runs
- `agent_logs/` - Directory containing detailed agent logs
- `agent_screenshots/` - Directory containing screenshots of agent actions
- `bug_reports/` - Directory containing generated bug reports
- `tasks_test.txt` - Default file containing tasks to be executed
- `auth_data/` - Directory containing saved browser profiles and cookies
- `BROWSER_USE_TUTORIAL.md` - Comprehensive tutorial on agent architecture and usage

## License

This project is licensed under the same license as the original browser-use repository.

## Acknowledgments

This project is based on the original [browser-use](https://github.com/gregpr07/browser-use) repository by Gregor Žunič and Magnus Müller.
