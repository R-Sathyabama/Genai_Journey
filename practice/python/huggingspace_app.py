import gradio as gr
import subprocess
import json
import os
import ssl
import certifi
from huggingface_hub import InferenceClient

# --- 1. SSL & ENVIRONMENT SETUP ---
os.environ['SSL_CERT_FILE'] = certifi.where()
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# --- 2. AI CLIENT SETUP ---
# On Hugging Face Spaces, it uses the Secret named HF_TOKEN.
HF_TOKEN = os.getenv("HF_TOKEN") or "" 
client = InferenceClient("meta-llama/Meta-Llama-3-8B-Instruct", token=HF_TOKEN)

def analyze_infrastructure(input_content):
    print("--- Analysis Started ---")
    
    if not input_content.strip():
        return "⚠️ Please paste some code (Terraform or YAML) first!"

    # 1. Create directory and save file
    os.makedirs("scan_dir", exist_ok=True)
    
    # Check if it looks like YAML or Terraform
    is_yaml = any(x in input_content for x in ["kind:", "jobs:", "services:", "steps:", "apiVersion:"])
    file_ext = ".yaml" if is_yaml else ".tf"
    file_path = f"scan_dir/input_config{file_ext}"
    
    with open(file_path, "w") as f:
        f.write(input_content)

    print(f"Scanning file: {file_path}")

    # 2. RUN CHECKOV (Removed --no-guide to fix the error)
    cmd = ["checkov", "-f", file_path, "--output", "json", "--quiet", "--soft-fail"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check if Checkov output is empty or contains an error
    if not result.stdout.strip():
        print("CHECK_ERROR:", result.stderr)
        return f"⚠️ Checkov failed to return data. Error details: {result.stderr}"

    try:
        raw_output = json.loads(result.stdout)
        
        # Checkov JSON output is usually a dict, but can be a list in some versions
        if isinstance(raw_output, list):
            failed_checks = raw_output[0].get("results", {}).get("failed_checks", [])
        else:
            failed_checks = raw_output.get("results", {}).get("failed_checks", [])
            
    except Exception as e:
        print("JSON_PARSE_ERROR:", str(e))
        return f"⚠️ JSON Parse Error. Check terminal logs. Raw snippet: {result.stdout[:100]}"

    print(f"Found {len(failed_checks)} security violations.")

    if not failed_checks:
        return "✅ **No vulnerabilities detected!** Your configuration follows security best practices."

    # 3. AI REASONING
    summary = "\n".join([f"- {c['check_id']}: {c['check_name']} (Resource: {c['resource']})" for c in failed_checks[:5]])
    
    messages = [
        {
            "role": "system", 
            "content": "You are a Senior DevSecOps Architect. Analyze security violations and explain the 'Attack Path' and provide 'Remediation Code'."
        },
        {
            "role": "user", 
            "content": f"The following security violations were found in my code:\n{summary}\n\nPlease provide a threat analysis and the fixed code blocks."
        }
    ]

    print("Fetching AI response from Llama-3...")
    response = ""
    try:
        for message in client.chat_completion(messages, max_tokens=1500, stream=True):
            token = message.choices.delta.content
            if token:
                response += token
        print("--- Analysis Completed ---")
        return response
    except Exception as e:
        return f"❌ AI Service Error: {str(e)}"

# --- 3. GRADIO UI ---
with gr.Blocks(title="AI DevSecOps Assistant") as demo:
    gr.Markdown("# 🛡️ AI-Driven DevSecOps Threat Modeler")
    gr.Markdown("Supports: **Terraform, Kubernetes, and CI/CD Pipelines**")
    
    with gr.Row():
        with gr.Column(scale=1):
            code_input = gr.Textbox(label="Paste Code (TF/YAML)", lines=18)
            submit_btn = gr.Button("🚀 Analyze Architecture", variant="primary")
        
        with gr.Column(scale=1):
            output_report = gr.Markdown(label="Analysis Report", value="Results will appear here...")

    submit_btn.click(
        fn=analyze_infrastructure, 
        inputs=code_input, 
        outputs=output_report
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
