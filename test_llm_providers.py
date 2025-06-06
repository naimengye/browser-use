#!/usr/bin/env python3
"""
Test script to verify dynamic LLM provider switching
"""

import os
import yaml
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

def create_llm(llm_config):
    """Create LLM instance based on provider configuration"""
    provider = llm_config.get('provider', 'openai').lower()
    model = llm_config['model']
    
    # Common LLM parameters
    common_params = {
        'temperature': llm_config.get('temperature', 0.0),
        'max_tokens': llm_config.get('max_tokens', None),
    }
    
    if provider == 'anthropic':
        # Check for Anthropic API key
        if not os.getenv('ANTHROPIC_API_KEY'):
            raise ValueError("ANTHROPIC_API_KEY environment variable is required for Anthropic provider")
        
        anthropic_params = {
            'model': model,
            **common_params
        }
        return ChatAnthropic(**anthropic_params)
    
    elif provider == 'openai':
        # Check for OpenAI API key
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI provider")
        
        openai_params = {
            'model': model,
            **common_params
        }
        return ChatOpenAI(**openai_params)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}. Supported providers: 'anthropic', 'openai'")

def test_provider_switching():
    """Test switching between different LLM providers"""
    load_dotenv()
    
    # Test configurations
    test_configs = [
        {
            'provider': 'openai',
            'model': 'gpt-4o-mini',
            'temperature': 0.0
        },
        {
            'provider': 'anthropic', 
            'model': 'claude-3-5-haiku-20241022',
            'temperature': 0.0
        }
    ]
    
    for config in test_configs:
        try:
            print(f"\n--- Testing {config['provider'].upper()} provider ---")
            print(f"Model: {config['model']}")
            
            llm = create_llm(config)
            print(f"✅ Successfully created {type(llm).__name__} instance")
            
            # Test with a simple message
            test_message = "What is 2+2? Answer with just the number."
            response = llm.invoke([{"role": "user", "content": test_message}])
            print(f"✅ Test response: {response.content.strip()}")
            
        except Exception as e:
            print(f"❌ Error with {config['provider']} provider: {str(e)}")

def test_config_file():
    """Test loading configuration from YAML file"""
    try:
        print("\n--- Testing configuration file loading ---")
        with open('configs/config.yaml', 'r') as f:
            config_data = yaml.safe_load(f)
        
        llm_config = config_data['llm']
        print(f"Provider: {llm_config['provider']}")
        print(f"Model: {llm_config['model']}")
        print(f"Temperature: {llm_config.get('temperature', 'not set')}")
        print(f"Max tokens: {llm_config.get('max_tokens', 'not set')}")
        
        llm = create_llm(llm_config)
        print(f"✅ Successfully created {type(llm).__name__} instance from config file")
        
    except Exception as e:
        print(f"❌ Error loading from config file: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing LLM Provider Switching")
    print("=" * 50)
    
    test_config_file()
    test_provider_switching()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!") 