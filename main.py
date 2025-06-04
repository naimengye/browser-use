# main.py
from browser_use.agent.service import Agent
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from langchain_anthropic import ChatAnthropic
import asyncio
from dotenv import load_dotenv
from auth_manager import SecureAuthManager
from login_handlers import LoginHandlers

load_dotenv()

async def setup_authenticated_browser():
    """Set up browser with test account authentication"""
    
    # Create auth manager
    auth_manager = SecureAuthManager("test_profile")
    
    # Store test credentials (do this once)
    #auth_manager.store_test_credentials("google", "ai.web.testing@gmail.com", "columbia!123")
    #auth_manager.store_test_credentials("huggingface", "ai.web.testing@gmail.com", "Columbia!123")
    #auth_manager.store_test_credentials("outlook", "ai.web.testing@gmail.com", "columbia!123")
    #auth_manager.store_test_credentials("github", "ai.web.testing@gmail.com", "columbia!123")

    # test if the credentials are stored
    print(auth_manager.get_credentials("google"))
    print(auth_manager.get_credentials("huggingface"))
    print(auth_manager.get_credentials("outlook"))
    print(auth_manager.get_credentials("github"))
    
    # Configure browser
    browser_config = BrowserConfig(
        headless=False,
        use_test_profile=True,
        test_profile_name="test_profile",
        extra_browser_args=["--disable-blink-features=AutomationControlled"],
    )
    
    # Configure context with security settings
    context_config = BrowserContextConfig(
        disable_security=True,
        cookies_file="auth_data/test_profile/cookies.json",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        permissions=["clipboard-read", "clipboard-write"],
        # Important: set allowed domains for sensitive operations
        #allowed_domains=["amazon.com", "google.com", "github.com", "huggingface.co", "outlook.com"],
    )

    browser = Browser(config=browser_config)
    context = await browser.new_context(config=context_config)
    
    # Check if we need to login
    await ensure_logged_in(context, auth_manager)
    return browser, context

async def ensure_logged_in(context, auth_manager):
    """Ensure we're logged into required services"""
    
    # Try to load existing auth
    google_auth_loaded = await auth_manager.load_auth_state(context, "google")
    if google_auth_loaded:
        print("Google already logged in")
    if not google_auth_loaded:
        # Need to login
        username, password = auth_manager.get_credentials("google")
        success = await LoginHandlers.login_google(context, username, password)
        print("Logged in to Google")
        
        if success:
            await auth_manager.save_auth_state(context, "google")
        else:
            raise Exception("Failed to login to Google")

async def main():
    # Set up authenticated browser
    browser, browser_context = await setup_authenticated_browser()
    print("Browser and context initialized, ready to run tasks")
    # Read tasks
    with open("tasks_test.txt", "r") as f:
        for line in f:
            if line.strip() == "":
                continue

            name, task = line.strip().split(":", 1)
            
            # Create agent with authenticated browser
            agent = Agent(
                task=task,
                llm=ChatAnthropic(model="claude-3-7-sonnet-20250219"),
                task_name=name,
                browser=browser,
                browser_context=browser_context
            )
            
            try:
                await agent.run()
            finally:
                # Save auth state after each task
                auth_manager = SecureAuthManager("test_profile")
                await auth_manager.save_auth_state(browser_context, "google")

if __name__ == "__main__":
    asyncio.run(main())