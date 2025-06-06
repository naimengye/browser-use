# LLM Provider Configuration

This document explains how to configure and use different LLM providers (OpenAI and Anthropic) dynamically.

## Configuration

The LLM provider is configured in `configs/config.yaml` under the `llm` section:

```yaml
llm:
  provider: "openai"          # Choose "openai" or "anthropic"
  model: "gpt-4o"             # Model name specific to the provider
  temperature: 0.0            # Controls randomness (0.0 = deterministic, 1.0 = creative)
  max_tokens: null            # Maximum tokens in response (null = use model default)
```

## Supported Providers

### OpenAI
- **Provider**: `openai`
- **Required Environment Variable**: `OPENAI_API_KEY`
- **Popular Models**:
  - `gpt-4o` - Latest GPT-4 Omni (recommended)
  - `gpt-4o-mini` - Smaller, faster GPT-4 Omni
  - `gpt-4-turbo` - GPT-4 Turbo
  - `gpt-3.5-turbo` - GPT-3.5 (most cost-effective)

### Anthropic
- **Provider**: `anthropic`
- **Required Environment Variable**: `ANTHROPIC_API_KEY`
- **Popular Models**:
  - `claude-3-5-sonnet-20241022` - Latest Claude 3.5 Sonnet (recommended)
  - `claude-3-5-haiku-20241022` - Claude 3.5 Haiku (faster, more cost-effective)
  - `claude-3-opus-20240229` - Claude 3 Opus (most capable, slower)

## Environment Variables

Create a `.env` file in your project root with the appropriate API keys:

```bash
# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# For Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# You can have both keys present - only the one specified in config.yaml will be used
```

## Example Configurations

### OpenAI Configuration
```yaml
llm:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.0
  max_tokens: null
```

### Anthropic Configuration
```yaml
llm:
  provider: "anthropic"
  model: "claude-3-5-sonnet-20241022"
  temperature: 0.0
  max_tokens: null
```

## Switching Providers

To switch providers:

1. Update the `provider` field in `configs/config.yaml`
2. Update the `model` field to a model supported by that provider
3. Ensure the corresponding API key is set in your `.env` file
4. Restart your application

## Testing

You can test your configuration using the provided test script:

```bash
python test_llm_providers.py
```

This will verify:
- Configuration file loading
- API key availability
- LLM instance creation
- Basic functionality test

## Error Handling

The system will provide clear error messages if:
- The provider is not supported
- Required API keys are missing
- Invalid model names are specified
- API calls fail

## Cost Considerations

Different models have different costs and capabilities:

**OpenAI** (approximate costs per 1M tokens):
- GPT-4o: $2.50 input / $10.00 output
- GPT-4o-mini: $0.15 input / $0.60 output
- GPT-4-turbo: $10.00 input / $30.00 output

**Anthropic** (approximate costs per 1M tokens):
- Claude-3.5-Sonnet: $3.00 input / $15.00 output
- Claude-3.5-Haiku: $0.25 input / $1.25 output
- Claude-3-Opus: $15.00 input / $75.00 output

Choose the model that best fits your performance and budget requirements. 