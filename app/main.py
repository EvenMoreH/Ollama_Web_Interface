from fasthtml.common import *
import httpx

app, rt = fast_app(hdrs=(
    Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github-dark.min.css"),
    Script(src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js")
))

# Styling for the page
style = Style('''
    * {
        width: min(1200px, 90%);
        font-size: 18px;
        background-color: rgb(40, 40, 40);
        color: rgb(215, 215, 215);
        font-family: Arial, Helvetica, sans-serif;
    }

    button {
        width: min(250px, 30%);
        margin-bottom: 1%;
        margin-top: 1%;
    }

    #response {
        white-space: pre-wrap;  /* Preserve line breaks */
        padding: 10px;
        border: 1px solid #555;
        border-radius: 8px;
        margin-top: 10px;
    }
''')

# JavaScript to reset button text after response update
reset_button_script = Script('''
    document.body.addEventListener('htmx:afterSwap', function(event) {
        if (event.target.id === 'response') {
            document.getElementById('sb').innerText = 'Send';
        }
    });
''')

@rt("/")
def get():
    return Titled("Ollama LLM Chat",
        style,
        reset_button_script,
        H2("Chat with Local LLM (Ollama)"),
        Form(
            Input(id="userInput", name="prompt", placeholder="Type your message here"),
            Button("Send", id="sb", type="submit", onclick="document.getElementById('sb').innerText = 'Thinking...'") ,
            hx_post="/generate", hx_target="#response"
        ),
        P(Strong("Response:")),
        Div(id="response")
    )

@rt("/generate")
def post(prompt: str):
    try:
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-r1:14b",
                "prompt": prompt,
                "stream": False
            },
            timeout=300  # Timeout set to 5 minutes for reasoning model
        )

        data = response.json()
        response_text = data.get("response", "No response")

        # Auto-detect and format code blocks
        import re
        response_text = re.sub(
            r"```(\w+)?\n([\s\S]*?)```",
            lambda m: f'<pre><code class="language-{m.group(1) or "plaintext"}">{m.group(2)}</code></pre>',
            response_text
        )

        # Add paragraphs for better readability
        response_text = re.sub(r'(\n\s*\n)+', '</p><p>', response_text)
        response_text = f'<p>{response_text}</p>'

        # JavaScript to highlight code blocks
        highlight_script = Script('''
            document.querySelectorAll("pre code").forEach(el => {
                hljs.highlightElement(el);
            });
        ''')

        return Div(NotStr(response_text)), highlight_script

    except Exception as e:
        return Div(f"Error: {str(e)}")

serve()