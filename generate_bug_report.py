import os
from dotenv import load_dotenv
from anthropic import Anthropic
from analyze_agent_run import analyze_agent_run

def generate_bug_report(log_file: str) -> str:
    # Load environment variables
    load_dotenv()
    
    # Initialize the Anthropic client
    client = Anthropic()
    
    # Generate the analysis messages
    messages = analyze_agent_run(log_file)
    
    # Get the analysis from Claude
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1024,
        messages=messages
    )
    
    return response.content[0].text

if __name__ == "__main__":
    # Example usage
    log_file = "agent_logs/agent_run_amazon.log"
    bug_report = generate_bug_report(log_file)
    
    # Save the bug report to a file
    output_dir = "bug_reports"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "bug_report_amazon.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(bug_report)
    
    print(f"Bug report has been generated and saved to {output_file}") 