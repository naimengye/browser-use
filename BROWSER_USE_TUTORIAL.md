# Browser-Use Agent: Complete Architecture & Implementation Tutorial

## Table of Contents
1. [Introduction](#introduction)
2. [Core Architecture](#core-architecture)
3. [Agent Execution Loop](#agent-execution-loop)
4. [State Capture System](#state-capture-system)
5. [LLM Decision Making](#llm-decision-making)
6. [Action Execution System](#action-execution-system)
7. [Memory & State Management](#memory--state-management)
8. [Error Handling & Recovery](#error-handling--recovery)
9. [Configuration & Setup](#configuration--setup)
10. [Practical Examples](#practical-examples)
11. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## Introduction

Browser-Use is an intelligent web automation agent that combines Large Language Models (LLMs) with browser automation to perform complex web tasks. Unlike traditional web scraping or automation tools, it can:

- **See** web pages through screenshots
- **Understand** page content and structure
- **Reason** about what actions to take
- **Execute** browser interactions
- **Learn** from previous actions
- **Recover** from errors intelligently

### Key Capabilities
- Visual understanding of web pages
- Multi-step task execution
- Error recovery and retry logic
- Memory management for long conversations
- Domain-specific actions (Google Sheets, etc.)
- Security controls and domain restrictions

---

## Core Architecture

The browser-use agent follows a **modular architecture** with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Agent       │    │   Controller    │    │     Browser     │
│   (service.py)  │◄──►│  (service.py)   │◄──►│   (context.py)  │
│                 │    │                 │    │                 │
│ • Task planning │    │ • Action exec   │    │ • State capture │
│ • LLM comms     │    │ • Registry mgmt │    │ • DOM parsing   │
│ • Memory mgmt   │    │ • Error handling│    │ • Screenshots   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ MessageManager  │    │    Registry     │    │   DOMService    │
│                 │    │                 │    │                 │
│ • Prompt mgmt   │    │ • Action registry│    │ • Element detect│
│ • Token mgmt    │    │ • Dynamic models│    │ • CSS selectors │
│ • History mgmt  │    │ • Validation    │    │ • Click detection│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

#### 1. **Agent** (`agent/service.py`)
- **Purpose**: Orchestrates the entire automation process
- **Key Methods**:
  - `run()`: Main execution loop
  - `step()`: Single step execution
  - `get_next_action()`: LLM communication
  - `multi_act()`: Action execution

#### 2. **Controller** (`controller/service.py`)
- **Purpose**: Manages available actions and their execution
- **Key Features**:
  - Dynamic action registry
  - Parameter validation
  - Action result handling

#### 3. **BrowserContext** (`browser/context.py`)
- **Purpose**: Manages browser state and interactions
- **Key Methods**:
  - `get_state()`: Capture current page state
  - `take_screenshot()`: Visual state capture
  - Browser navigation and interaction

#### 4. **MessageManager** (`agent/message_manager/`)
- **Purpose**: Handles LLM communication and conversation management
- **Key Features**:
  - Token counting and management
  - Message history pruning
  - Prompt construction

---

## Agent Execution Loop

The agent operates through a **perception-action loop** that mimics human web browsing behavior:

### Main Loop Structure

```python
async def run(self, max_steps: int = 100):
    """Main execution loop - simplified version"""
    
    for step in range(max_steps):
        self.logger.info(f'📍 Step {step}')
        
        try:
            # 1. 📸 PERCEPTION: Capture current browser state
            state = await self.browser_context.get_state(
                cache_clickable_elements_hashes=True
            )
            
            # 2. 💾 MEMORY: Update procedural memory if needed
            if self.enable_memory and step % self.memory.config.memory_interval == 0:
                self.memory.create_procedural_memory(step)
            
            # 3. 🧠 REASONING: Get next action from LLM
            messages = self._message_manager.get_messages()
            model_output = await self.get_next_action(messages)
            
            # 4. 🎯 ACTION: Execute the chosen action(s)
            result = await self.multi_act(model_output.action)
            
            # 5. 📊 EVALUATION: Assess results and update state
            self.state.last_result = result
            self._make_history_item(model_output, state, result)
            
            # 6. ✅ COMPLETION: Check if task is done
            if result and result[-1].is_done:
                self.logger.info(f'📄 Result: {result[-1].extracted_content}')
                break
                
        except Exception as e:
            # Handle errors and continue or abort
            result = await self._handle_step_error(e)
            self.state.last_result = result
```

### Step-by-Step Breakdown

#### Step 1: Perception (State Capture)
```python
# The agent "sees" the current page state
state = await self.browser_context.get_state()

# State includes:
# - Screenshot (base64 encoded image)
# - Interactive elements with indexes
# - Current URL and page title
# - Open tabs information
# - DOM structure
```

#### Step 2: Memory Management
```python
# Every N steps, consolidate conversation history
if step % memory_interval == 0:
    # Convert recent messages to procedural memory
    procedural_memory = self._consolidate_messages()
    # Store in vector database for retrieval
    self.memory.vector_store.insert(procedural_memory)
```

#### Step 3: Reasoning (LLM Decision)
```python
# Build conversation context
messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=state_description),
    # ... previous conversation history
]

# Get structured response from LLM
response = await self.llm.invoke(messages)
# Response format: {"current_state": {...}, "action": [...]}
```

#### Step 4: Action Execution
```python
# Execute one or more actions in sequence
for action in model_output.action:
    result = await self.controller.act(
        action=action,
        browser_context=self.browser_context
    )
    
    # Stop sequence if page state changes significantly
    if result.interrupts_sequence:
        break
```

---

## State Capture System

The state capture system is crucial for providing the LLM with accurate information about the current page.

### BrowserState Structure

```python
@dataclass
class BrowserState:
    url: str                    # Current page URL
    title: str                  # Page title
    screenshot: str | None      # Base64 encoded screenshot
    elements: list[DOMElement]  # Interactive elements
    selector_map: SelectorMap   # Index -> element mapping
    tabs: list[TabInfo]         # Open tabs information
```

### State Capture Process

```python
async def get_state(self, cache_clickable_elements_hashes: bool) -> BrowserState:
    """Capture comprehensive browser state"""
    
    # 1. Get current page reference
    page = await self.get_current_page()
    
    # 2. Take screenshot for visual context
    screenshot = await self.take_screenshot()
    
    # 3. Extract DOM elements and make them clickable
    dom_service = DomService()
    clickable_elements = await dom_service.get_clickable_elements(
        page=page,
        viewport_expansion=self.config.viewport_expansion
    )
    
    # 4. Build selector map (index -> element mapping)
    selector_map = {}
    for i, element in enumerate(clickable_elements):
        selector_map[i] = element
    
    # 5. Get tab information
    tabs = await self.get_tabs_info()
    
    # 6. Highlight elements on page (if enabled)
    if self.config.highlight_elements:
        await self._highlight_elements(clickable_elements)
    
    return BrowserState(
        url=page.url,
        title=await page.title(),
        screenshot=screenshot,
        elements=clickable_elements,
        selector_map=selector_map,
        tabs=tabs
    )
```

### Element Detection & Processing

The DOM service identifies interactive elements:

```python
class ClickableElementProcessor:
    """Processes DOM to find clickable elements"""
    
    CLICKABLE_SELECTORS = [
        'button', 'a[href]', 'input', 'select', 'textarea',
        '[onclick]', '[role="button"]', '[tabindex]',
        # ... more selectors
    ]
    
    async def get_clickable_elements(self, page: Page) -> list[DOMElement]:
        elements = []
        
        # Find all potentially interactive elements
        for selector in self.CLICKABLE_SELECTORS:
            page_elements = await page.query_selector_all(selector)
            
            for element in page_elements:
                # Check if element is actually clickable
                if await self._is_element_clickable(element):
                    dom_node = await self._create_dom_node(element)
                    elements.append(dom_node)
        
        return elements
```

---

## LLM Decision Making

The agent uses structured prompts to guide LLM decision-making.

### System Prompt Structure

The system prompt (`agent/system_prompt.md`) defines:

1. **Role Definition**: "You are an AI agent designed to automate browser tasks"
2. **Input Format**: How page state is presented
3. **Response Format**: Required JSON structure
4. **Action Rules**: How to execute actions
5. **Error Handling**: How to recover from failures
6. **Task Completion**: When and how to finish

### Prompt Construction

```python
class SystemPrompt:
    def get_system_message(self) -> str:
        return f"""
You are an AI agent designed to automate browser tasks.

# Input Format
Task: {self.task}
Current URL: {current_url}
Interactive Elements:
{self._format_elements()}

# Response Rules
1. RESPONSE FORMAT: You must ALWAYS respond with valid JSON:
{{"current_state": {{
    "evaluation_previous_goal": "Success|Failed|Unknown - ...",
    "memory": "Description of what has been done...",
    "next_goal": "What needs to be done next..."
}},
"action": [{{"action_name": {{"param": "value"}}}}]}}

# Available Actions:
{self.action_description}
"""
```

### State Message Format

Interactive elements are presented in a structured format:

```
Interactive Elements:
[1]<button>Submit Form</button>
[2]<input type="text" placeholder="Enter name">Name Input</input>
[3]<a href="/profile">View Profile</a>
    *[4]*<span>New notification</span>  # New element (marked with *)
```

### LLM Response Processing

```python
async def get_next_action(self, input_messages: list[BaseMessage]) -> AgentOutput:
    """Get structured response from LLM"""
    
    try:
        # Send messages to LLM
        response = await self.llm.ainvoke(input_messages)
        
        # Parse JSON response
        json_response = extract_json_from_model_output(response.content)
        
        # Validate against schema
        validated_output = self.AgentOutput(**json_response)
        
        return validated_output
        
    except ValidationError as e:
        # Handle malformed responses
        self.logger.error(f"Invalid LLM response: {e}")
        # Retry with clarification message
        retry_response = await self._retry_with_clarification(input_messages)
        return retry_response
```

---

## Action Execution System

The action system uses a **registry pattern** for dynamic action management.

### Action Registry

```python
class Registry:
    def __init__(self, exclude_actions: list[str] = []):
        self.actions: dict[str, ActionInfo] = {}
        self.exclude_actions = exclude_actions
    
    def action(self, description: str, param_model=None, domains=None):
        """Decorator to register actions"""
        def decorator(func):
            action_info = ActionInfo(
                name=func.__name__,
                description=description,
                function=func,
                param_model=param_model,
                domains=domains
            )
            self.actions[func.__name__] = action_info
            return func
        return decorator
```

### Core Actions

#### Navigation Actions
```python
@registry.action('Navigate to URL in the current tab')
async def go_to_url(params: GoToUrlAction, browser: BrowserContext):
    page = await browser.get_current_page()
    await page.goto(params.url)
    await page.wait_for_load_state()
    return ActionResult(
        extracted_content=f'🔗  Navigated to {params.url}',
        include_in_memory=True
    )

@registry.action('Go back')
async def go_back(_: NoParamsAction, browser: BrowserContext):
    await browser.go_back()
    return ActionResult(
        extracted_content='🔙  Navigated back',
        include_in_memory=True
    )
```

#### Interaction Actions
```python
@registry.action('Click element by index')
async def click_element_by_index(params: ClickElementAction, browser: BrowserContext):
    # Validate element exists
    if params.index not in await browser.get_selector_map():
        raise Exception(f'Element with index {params.index} does not exist')
    
    # Get DOM element
    element_node = await browser.get_dom_element_by_index(params.index)
    
    # Handle special cases (file uploads, downloads)
    if await browser.is_file_uploader(element_node):
        return ActionResult(
            extracted_content='Element opens file upload dialog',
            include_in_memory=True
        )
    
    # Perform click
    download_path = await browser._click_element_node(element_node)
    
    if download_path:
        msg = f'💾  Downloaded file to {download_path}'
    else:
        element_text = element_node.get_all_text_till_next_clickable_element()
        msg = f'🖱️  Clicked element {params.index}: {element_text}'
    
    return ActionResult(extracted_content=msg, include_in_memory=True)

@registry.action('Input text into interactive element')
async def input_text(params: InputTextAction, browser: BrowserContext):
    element_node = await browser.get_dom_element_by_index(params.index)
    await browser._input_text_element_node(element_node, params.text)
    
    return ActionResult(
        extracted_content=f'⌨️  Input {params.text} into index {params.index}',
        include_in_memory=True
    )
```

#### Information Extraction
```python
@registry.action('Extract page content for specific information')
async def extract_content(
    goal: str, 
    should_strip_link_urls: bool, 
    browser: BrowserContext, 
    page_extraction_llm: BaseChatModel
):
    # Get page content
    page_content = await browser.get_page_structure()
    
    # Use LLM to extract specific information
    extraction_prompt = f"""
Extract the following information from this page content:
Goal: {goal}

Page Content:
{page_content}

Return only the requested information in a clear, structured format.
"""
    
    response = await page_extraction_llm.ainvoke([
        HumanMessage(content=extraction_prompt)
    ])
    
    return ActionResult(
        extracted_content=response.content,
        include_in_memory=True
    )
```

### Domain-Specific Actions

The system supports domain-specific actions for specialized websites:

```python
# Google Sheets specific actions
@registry.action('Get sheet contents', domains=['sheets.google.com'])
async def get_sheet_contents(browser: BrowserContext):
    # Implementation specific to Google Sheets
    pass

@registry.action('Select cell range', domains=['sheets.google.com'])
async def select_cell_or_range(browser: BrowserContext, cell_range: str):
    # Implementation for cell selection
    pass
```

---

## Memory & State Management

The agent maintains multiple types of state to ensure consistent operation.

### State Types

#### 1. Agent State
```python
@dataclass
class AgentState:
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    n_steps: int = 0
    consecutive_failures: int = 0
    last_result: list[ActionResult] = field(default_factory=list)
    history: AgentHistoryList = field(default_factory=AgentHistoryList)
    stopped: bool = False
    paused: bool = False
    message_manager_state: MessageManagerState = field(default_factory=MessageManagerState)
```

#### 2. Browser State
```python
@dataclass
class BrowserState:
    url: str
    title: str
    screenshot: str | None
    elements: list[DOMElementNode]
    selector_map: SelectorMap
    tabs: list[TabInfo]
```

#### 3. Message State
```python
class MessageManagerState:
    def __init__(self):
        self.history = ConversationHistory()
        self.current_tokens = 0
        self.max_tokens = 128000
```

### Memory Management

#### Short-term Memory (Conversation History)
```python
class MessageManager:
    def add_state_message(self, state: BrowserState, last_result: list[ActionResult]):
        """Add current state to conversation"""
        
        # Format state for LLM
        state_content = f"""
Current URL: {state.url}
Page Title: {state.title}

Interactive Elements:
{self._format_elements(state.elements)}

Previous Action Results:
{self._format_results(last_result)}
"""
        
        # Add to conversation history
        self._add_message_with_tokens(HumanMessage(content=state_content))
        
        # Include screenshot if vision is enabled
        if self.settings.use_vision and state.screenshot:
            self._add_image_message(state.screenshot)
    
    def cut_messages(self):
        """Remove older messages to stay within token limits"""
        while self.state.current_tokens > self.settings.max_input_tokens:
            if len(self.state.history.messages) > 2:  # Keep system + latest
                removed_message = self.state.history.messages.pop(1)  # Remove oldest
                self.state.current_tokens -= removed_message.token_count
```

#### Long-term Memory (Procedural Memory)
```python
class Memory:
    def create_procedural_memory(self, step: int):
        """Consolidate recent conversation into procedural memory"""
        
        # Get recent messages
        recent_messages = self.message_manager.get_recent_messages(
            since_step=step - self.config.memory_interval
        )
        
        # Summarize using LLM
        summary_prompt = f"""
Summarize the key actions, findings, and current state from these recent steps:

{self._format_messages_for_summary(recent_messages)}

Focus on:
1. What was accomplished
2. What was learned/found
3. Current progress toward the goal
4. Any errors or issues encountered
"""
        
        summary = await self.llm.ainvoke([HumanMessage(content=summary_prompt)])
        
        # Store in vector database
        self.vector_store.insert({
            'step': step,
            'summary': summary.content,
            'timestamp': datetime.now()
        })
        
        # Clear processed messages from short-term memory
        self.message_manager.consolidate_messages(recent_messages)
```

### History Management

```python
@dataclass
class AgentHistory:
    model_output: AgentOutput | None
    result: list[ActionResult]
    state: BrowserStateHistory
    metadata: StepMetadata | None = None
    
    @staticmethod
    def get_interacted_element(
        model_output: AgentOutput,
        selector_map: SelectorMap
    ) -> list[DOMElementNode | None]:
        """Extract which elements were interacted with"""
        
        interacted_elements = []
        for action in model_output.action:
            if hasattr(action, 'index'):
                element = selector_map.get(action.index)
                interacted_elements.append(element)
            else:
                interacted_elements.append(None)
        
        return interacted_elements
```

---

## Error Handling & Recovery

The agent includes comprehensive error handling and recovery mechanisms.

### Error Types & Handling

#### 1. Browser Errors
```python
async def _handle_step_error(self, error: Exception) -> list[ActionResult]:
    """Handle various types of errors during step execution"""
    
    error_msg = AgentError.format_error(error, include_trace=self.logger.isEnabledFor(logging.DEBUG))
    self.state.consecutive_failures += 1
    
    # Browser connection errors
    if 'Browser closed' in error_msg:
        self.logger.error('❌ Browser is closed or disconnected')
        return [ActionResult(
            error='Browser closed or disconnected, unable to proceed',
            include_in_memory=False
        )]
    
    # Validation errors (malformed LLM response)
    if isinstance(error, (ValidationError, ValueError)):
        self.logger.error(f'❌ Validation error: {error_msg}')
        
        if 'Max token limit reached' in error_msg:
            # Reduce token limit and cut conversation history
            self._message_manager.settings.max_input_tokens -= 500
            self._message_manager.cut_messages()
            
        elif 'Could not parse response' in error_msg:
            # Give model hint about expected format
            error_msg += '\n\nReturn a valid JSON object with the required fields.'
    
    # Rate limit errors
    elif isinstance(error, (RateLimitError, ResourceExhausted)):
        self.logger.warning(f'⚠️ Rate limit hit: {error_msg}')
        await asyncio.sleep(self.settings.retry_delay)
    
    return [ActionResult(error=error_msg, include_in_memory=True)]
```

#### 2. Element Interaction Errors
```python
async def click_element_by_index(params: ClickElementAction, browser: BrowserContext):
    try:
        # Validate element exists
        if params.index not in await browser.get_selector_map():
            raise Exception(f'Element with index {params.index} does not exist - retry or use alternative actions')
        
        element_node = await browser.get_dom_element_by_index(params.index)
        
        # Attempt click
        await browser._click_element_node(element_node)
        
        return ActionResult(extracted_content=f'✅ Clicked element {params.index}')
        
    except Exception as e:
        self.logger.warning(f'❌ Element not clickable: {params.index} - page may have changed')
        return ActionResult(error=str(e))
```

#### 3. Recovery Strategies
```python
class Agent:
    async def step(self):
        """Execute one step with error recovery"""
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Attempt normal step execution
                return await self._execute_step()
                
            except TimeoutError:
                if attempt < max_retries - 1:
                    self.logger.warning(f'⚠️ Timeout on attempt {attempt + 1}, retrying...')
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    self.logger.error('❌ Max retries exceeded for timeout')
                    raise
                    
            except ValidationError:
                if attempt < max_retries - 1:
                    # Add clarification message for malformed responses
                    clarification = HumanMessage(
                        content='Invalid response format. Please respond with valid JSON.'
                    )
                    self._message_manager._add_message_with_tokens(clarification)
                    continue
                else:
                    raise
```

### Failure Recovery Patterns

#### Pattern 1: Page Navigation Recovery
```python
# If stuck on a page, try going back
if self.state.consecutive_failures >= 2:
    if 'navigation' not in [r.error for r in self.state.last_result]:
        # Try going back to previous page
        await self.browser_context.go_back()
        return ActionResult(extracted_content='Went back due to repeated failures')
```

#### Pattern 2: Element Re-detection
```python
# If element not found, refresh page state
if 'Element with index' in error_msg and 'does not exist' in error_msg:
    # Page may have changed, get fresh state
    await self.browser_context.get_state(cache_clickable_elements_hashes=False)
    # Retry action with updated element indexes
```

#### Pattern 3: Alternative Action Paths
```python
# If direct action fails, try alternatives
if click_failed:
    # Try using keyboard navigation
    await self.send_keys('Tab')  # Navigate to element
    await self.send_keys('Enter')  # Activate
    
    # Or try JavaScript click
    await self.execute_javascript(f'document.querySelector("{selector}").click()')
```

---

## Configuration & Setup

### Configuration Overview

The browser-use agent now supports comprehensive YAML-based configuration for all major components:

- **Browser Settings**: Window size, headless mode, security settings
- **Context Settings**: Cookies, user agent, permissions, domain restrictions  
- **LLM Settings**: Provider, model, temperature, token limits
- **Agent Settings**: Step limits, failure handling, vision, memory
- **Task Settings**: Task file location

This allows you to configure the entire agent behavior without touching code.

#### Benefits of YAML Configuration:
- **Version Control**: Easy to track configuration changes
- **Environment-Specific**: Different configs for dev/staging/prod
- **Team Sharing**: Standardized settings across team members
- **Quick Adjustments**: Modify behavior without code changes
- **Documentation**: Self-documenting configuration with comments

### Basic Setup

#### 1. Configuration Files
```yaml
# configs/config.yaml
browser:
  headless: false
  use_test_profile: true
  test_profile_name: "test_profile"
  extra_browser_args: []

context:
  disable_security: false
  cookies_file: "auth_data/test_profile/cookies.json"
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  permissions: ["clipboard-read", "clipboard-write"]
  allowed_domains: null

llm:
  provider: "openai"  # or "anthropic"
  model: "gpt-4o"
  temperature: 0.0
  max_tokens: 4000

# Agent configuration
agent:
  max_steps: 100  # Maximum number of steps the agent will take per task

tasks_file: "tasks.txt"
```

#### 2. Environment Variables
```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

#### 3. Task Definition
```
# tasks.txt
Academic website: Go to the website "https://naimengye.github.io/", explore and analyze the content
Google search: Search for "browser automation tools" and extract the top 5 results
Form filling: Fill out the contact form on example.com with test data
```

#### 4. Different Configurations for Different Use Cases

**Quick Testing (config_quick.yaml):**
```yaml
agent:
  max_steps: 20           # Shorter for quick tests
  max_failures: 2         # Fail fast
  use_vision: false       # Faster without screenshots
  enable_memory: false    # Skip memory for speed

llm:
  model: "gpt-4o-mini"    # Faster, cheaper model
  temperature: 0.0        # Deterministic
```

**Deep Research (config_research.yaml):**
```yaml
agent:
  max_steps: 200          # Allow longer exploration  
  max_failures: 5         # More tolerant of failures
  use_vision: true        # Full visual understanding
  enable_memory: true     # Remember across long sessions
  max_actions_per_step: 3 # More deliberate actions

llm:
  model: "gpt-4o"         # Most capable model
  temperature: 0.1        # Slightly creative
```

**Production (config_prod.yaml):**
```yaml
agent:
  max_steps: 50           # Reasonable limit
  max_failures: 3         # Standard tolerance
  use_vision: true        # Full capabilities
  enable_memory: true     # Context awareness

context:
  allowed_domains:        # Security restrictions
    - "trusted-site.com"
    - "api.trusted-site.com"

browser:
  headless: true          # No GUI in production
```

### Advanced Configuration

#### Browser Configuration
```python
browser_config = BrowserConfig(
    headless=False,                    # Show browser window
    use_test_profile=True,            # Use persistent profile
    test_profile_name="my_profile",   # Profile name
    extra_browser_args=[              # Additional Chrome args
        "--disable-web-security",     # Disable CORS (dangerous)
        "--disable-features=VizDisplayCompositor"
    ]
)
```

#### Context Configuration
```python
context_config = BrowserContextConfig(
    window_width=1920,               # Browser window size
    window_height=1080,
    viewport_expansion=100,          # Include elements outside viewport
    highlight_elements=True,         # Highlight clickable elements
    save_recording_path="recordings/", # Save video recordings
    allowed_domains=[               # Security: restrict domains
        "example.com",
        "api.example.com"
    ],
    permissions=[                   # Browser permissions
        "clipboard-read",
        "clipboard-write",
        "geolocation"
    ]
)
```

#### Agent Configuration

**YAML Configuration (Recommended):**
```yaml
# Agent configuration in config.yaml
agent:
  max_steps: 100          # Maximum number of steps the agent will take per task
  max_failures: 3         # Maximum consecutive failures before stopping
  retry_delay: 10         # Delay in seconds between retries after failures
  use_vision: true        # Enable screenshot analysis
  enable_memory: true     # Enable long-term memory
  max_actions_per_step: 10 # Maximum actions the agent can take in a single step
```

**Programmatic Configuration:**
```python
agent = Agent(
    task=task,
    llm=llm,
    use_vision=True,                 # Enable screenshot analysis
    max_failures=5,                  # Max failures before stopping
    retry_delay=3,                   # Delay between retries
    max_actions_per_step=5,          # Max actions per LLM call
    enable_memory=True,              # Enable long-term memory
    memory_config=MemoryConfig(
        memory_interval=10,          # Consolidate every 10 steps
        max_memories=50              # Max stored memories
    ),
    save_conversation_path="logs/",  # Save conversation logs
    generate_gif=True                # Generate GIF of session
)

# Run with max_steps from config or override
await agent.run(max_steps=config['agent']['max_steps'])  # From YAML
# OR
await agent.run(max_steps=50)  # Override in code
```

---

## Practical Examples

### Example 1: Web Research Task

```python
async def research_task_example():
    """Example: Research a topic and extract information"""
    
    # Setup
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    agent = Agent(
        task="Research browser automation tools and create a comparison table",
        llm=llm,
        use_vision=True,
        enable_memory=True
    )
    
    # The agent will automatically:
    # 1. Navigate to search engines
    # 2. Search for relevant terms
    # 3. Visit result pages
    # 4. Extract key information
    # 5. Compile findings into structured format
    
    result = await agent.run(max_steps=50)
    print(f"Research completed: {result.history[-1].result[-1].extracted_content}")
```

### Example 2: Form Automation

```python
async def form_automation_example():
    """Example: Fill out complex multi-step form"""
    
    agent = Agent(
        task="Complete the job application form with provided candidate data",
        llm=ChatOpenAI(model="gpt-4o"),
        sensitive_data={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-0123"
        }
    )
    
    # Agent will:
    # 1. Navigate to form
    # 2. Fill each field appropriately
    # 3. Handle multi-step forms
    # 4. Upload files if needed
    # 5. Submit and confirm
    
    await agent.run()
```

### Example 3: E-commerce Automation

```python
async def ecommerce_example():
    """Example: Product research and price comparison"""
    
    agent = Agent(
        task="Find the best price for 'wireless headphones under $100' across 3 shopping sites",
        llm=ChatOpenAI(model="gpt-4o"),
        max_actions_per_step=3,  # Efficient multi-action sequences
        enable_memory=True       # Remember findings across sites
    )
    
    # Agent process:
    # 1. Visit multiple e-commerce sites
    # 2. Search for the product
    # 3. Extract product details and prices
    # 4. Compare across sites
    # 5. Generate summary report
    
    results = await agent.run(max_steps=100)
```

### Example 4: API Documentation Analysis

```python
async def api_documentation_example():
    """Example: Analyze API documentation and extract endpoints"""
    
    agent = Agent(
        task="Analyze the API documentation and create a list of all available endpoints with their methods and parameters",
        llm=ChatOpenAI(model="gpt-4o"),
        use_vision=True,  # Important for complex documentation layouts
    )
    
    # Custom action for structured extraction
    @agent.controller.registry.action("Extract API endpoints")
    async def extract_api_endpoints(browser: BrowserContext):
        page_content = await browser.get_page_structure()
        
        # Use LLM to structure the extraction
        extraction_prompt = """
        Extract all API endpoints from this documentation page.
        Return in JSON format:
        {
          "endpoints": [
            {
              "method": "GET|POST|PUT|DELETE",
              "path": "/api/endpoint",
              "description": "What this endpoint does",
              "parameters": ["param1", "param2"]
            }
          ]
        }
        """
        
        # Implementation details...
        pass
    
    await agent.run()
```

---

## Troubleshooting Common Issues

### Issue 1: Browser Timeouts

**Symptoms:**
```
ERROR [browser] ❌ Failed to update state: Timeout 2000ms exceeded.
```

**Causes & Solutions:**
```python
# Cause: Page taking too long to load
# Solution 1: Increase timeout
context_config = BrowserContextConfig(
    maximum_wait_page_load_time=15.0,  # Increase from default 10s
    wait_for_network_idle_page_load_time=2.0  # Increase network wait
)

# Solution 2: Add wait actions when needed
@agent.controller.registry.action("Wait for page load")
async def wait_for_load():
    await asyncio.sleep(3)
    return ActionResult(extracted_content="Waited for page to load")
```

### Issue 2: Element Not Found Errors

**Symptoms:**
```
Element with index 5 does not exist - retry or use alternative actions
```

**Causes & Solutions:**
```python
# Cause: Page changed after state capture, elements shifted
# Solution 1: Use more robust element selection
context_config = BrowserContextConfig(
    include_dynamic_attributes=False,  # More stable selectors
    viewport_expansion=200  # Include more elements in state
)

# Solution 2: Add retry logic in custom actions
@agent.controller.registry.action("Robust click")
async def robust_click(index: int, browser: BrowserContext):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Refresh state before clicking
            await browser.get_state(cache_clickable_elements_hashes=False)
            
            # Attempt click
            element = await browser.get_dom_element_by_index(index)
            await browser._click_element_node(element)
            return ActionResult(extracted_content=f"Clicked element {index}")
            
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            raise e
```

### Issue 3: Memory/Token Limit Issues

**Symptoms:**
```
Max token limit reached - cutting messages from history
```

**Causes & Solutions:**
```python
# Solution 1: Configure memory management
agent = Agent(
    task=task,
    llm=llm,
    max_input_tokens=100000,  # Increase limit
    enable_memory=True,       # Enable long-term memory
    memory_config=MemoryConfig(
        memory_interval=5,    # Consolidate more frequently
        max_memories=100      # Keep more memories
    )
)

# Solution 2: Custom message pruning
class CustomMessageManager(MessageManager):
    def cut_messages(self):
        """Custom logic to preserve important messages"""
        
        # Keep system message and recent state
        important_messages = [
            self.state.history.messages[0],  # System
            self.state.history.messages[-1]  # Latest state
        ]
        
        # Keep successful action results
        for msg in self.state.history.messages[1:-1]:
            if "Success" in msg.content or "✅" in msg.content:
                important_messages.insert(-1, msg)
        
        self.state.history.messages = important_messages
        self._recalculate_tokens()
```

### Issue 4: PDF/File Loading Issues

**Symptoms:**
```
⚠ Eval: Failed - The PDF document failed to load
```

**Causes & Solutions:**
```python
# Solution 1: Handle file downloads explicitly
@agent.controller.registry.action("Download and process file")
async def download_file(url: str, browser: BrowserContext):
    try:
        # Navigate to file URL
        page = await browser.get_current_page()
        
        # Set up download handling
        async with page.expect_download() as download_info:
            await page.goto(url)
        
        download = await download_info.value
        file_path = await download.path()
        
        # Process downloaded file
        if file_path.endswith('.pdf'):
            # Use PDF processing library
            content = extract_pdf_content(file_path)
        elif file_path.endswith('.txt'):
            with open(file_path, 'r') as f:
                content = f.read()
        
        return ActionResult(
            extracted_content=f"Downloaded and processed: {content[:500]}..."
        )
        
    except Exception as e:
        return ActionResult(error=f"Failed to download file: {str(e)}")

# Solution 2: Alternative content access
@agent.controller.registry.action("Get PDF content via text extraction")
async def extract_pdf_via_text(browser: BrowserContext):
    # Try to get text content from PDF viewer
    page = await browser.get_current_page()
    
    # Wait for PDF to load
    await page.wait_for_timeout(5000)
    
    # Try to extract text from PDF viewer
    text_content = await page.evaluate("""
        () => {
            // Try different PDF viewer text extraction methods
            const textElements = document.querySelectorAll('.textLayer, .page-text, [data-text]');
            return Array.from(textElements).map(el => el.textContent).join('\\n');
        }
    """)
    
    return ActionResult(extracted_content=text_content or "Could not extract PDF text")
```

### Issue 5: Authentication & Session Management

**Symptoms:**
```
Need to login repeatedly, session not maintained
```

**Solutions:**
```python
# Solution 1: Persistent browser profile
browser_config = BrowserConfig(
    use_test_profile=True,
    test_profile_name="persistent_session"
)

context_config = BrowserContextConfig(
    cookies_file="auth_data/persistent_session/cookies.json"
)

# Solution 2: Custom authentication handler
class AuthenticationManager:
    def __init__(self, browser_context: BrowserContext):
        self.browser_context = browser_context
        self.auth_state = {}
    
    async def ensure_logged_in(self, site: str):
        """Ensure user is logged in to specified site"""
        
        current_url = await self.browser_context.get_current_page().url
        
        # Check if already logged in
        if await self._is_logged_in(site):
            return True
        
        # Attempt login
        return await self._perform_login(site)
    
    async def _is_logged_in(self, site: str) -> bool:
        """Check if currently logged in"""
        page = await self.browser_context.get_current_page()
        
        # Site-specific login detection
        if site == "google":
            # Look for Google account indicators
            account_elements = await page.query_selector_all('[data-gb-role="PROFILE"]')
            return len(account_elements) > 0
        
        # Generic detection
        login_indicators = await page.query_selector_all('a[href*="logout"], .user-menu, .profile-dropdown')
        return len(login_indicators) > 0
    
    async def _perform_login(self, site: str) -> bool:
        """Perform login process"""
        # Site-specific login logic
        pass

# Usage in agent
auth_manager = AuthenticationManager(browser_context)

@agent.controller.registry.action("Ensure authentication")
async def ensure_auth(site: str = "auto"):
    """Ensure user is authenticated before proceeding"""
    success = await auth_manager.ensure_logged_in(site)
    
    if success:
        return ActionResult(extracted_content=f"Authenticated for {site}")
    else:
        return ActionResult(error=f"Failed to authenticate for {site}")
```

### Debugging Tips

#### 1. Enable Detailed Logging
```python
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# Enable specific loggers
logging.getLogger('browser_use.agent').setLevel(logging.DEBUG)
logging.getLogger('browser_use.controller').setLevel(logging.DEBUG)
logging.getLogger('browser_use.browser').setLevel(logging.DEBUG)
```

#### 2. Screenshot Analysis
```python
# Save screenshots at each step for debugging
agent = Agent(
    task=task,
    llm=llm,
    generate_gif=True,  # Create animated GIF of session
    save_conversation_path="debug_logs/"  # Save all conversations
)

# Custom screenshot saving
@agent.controller.registry.action("Debug screenshot")
async def debug_screenshot(description: str, browser: BrowserContext):
    screenshot = await browser.take_screenshot()
    
    # Save with timestamp and description
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"debug_{timestamp}_{description.replace(' ', '_')}.png"
    
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(screenshot))
    
    return ActionResult(extracted_content=f"Debug screenshot saved: {filename}")
```

#### 3. State Inspection
```python
# Custom state inspection action
@agent.controller.registry.action("Inspect current state")
async def inspect_state(browser: BrowserContext):
    state = await browser.get_state(cache_clickable_elements_hashes=False)
    
    inspection_report = f"""
    Current State Inspection:
    - URL: {state.url}
    - Title: {state.title}
    - Interactive Elements: {len(state.elements)}
    - Tabs: {len(state.tabs)}
    
    Elements Summary:
    """
    
    for i, element in enumerate(state.elements[:10]):  # First 10 elements
        inspection_report += f"\n[{i}] {element.tag_name}: {element.text[:50]}..."
    
    return ActionResult(extracted_content=inspection_report)
```

---

## Conclusion

The Browser-Use agent represents a sophisticated approach to web automation that combines:

1. **Visual Understanding**: Screenshot-based page comprehension
2. **Intelligent Decision Making**: LLM-powered action selection
3. **Robust Error Handling**: Multiple recovery strategies
4. **Memory Management**: Both short-term and long-term memory systems
5. **Flexible Action System**: Extensible registry-based actions
6. **Security Controls**: Domain restrictions and sensitive data handling

### Key Advantages

- **Human-like Interaction**: Uses visual cues and reasoning like humans
- **Adaptability**: Handles dynamic web content and unexpected changes
- **Extensibility**: Easy to add domain-specific actions
- **Reliability**: Built-in error recovery and retry mechanisms
- **Scalability**: Memory management for long-running tasks

### Use Cases

- **Web Research**: Automated information gathering and analysis
- **Form Automation**: Complex multi-step form completion
- **Testing**: Intelligent web application testing
- **Data Extraction**: Content scraping with understanding
- **Workflow Automation**: End-to-end business process automation

The system's modular architecture makes it suitable for a wide range of web automation tasks while maintaining reliability and extensibility.