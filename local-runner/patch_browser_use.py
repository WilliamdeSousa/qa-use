"""Patch browser-use to work with standard LangChain LLMs that lack .provider and .model_name."""
import os
import re

base = ".venv/lib/python3.12/site-packages/browser_use"

for root, _, files in os.walk(base):
    for f in files:
        if not f.endswith(".py"):
            continue
        path = os.path.join(root, f)
        text = open(path).read()
        new = text
        new = re.sub(r"(?<![_\w])self\.llm\.provider(?![_\w])", 'getattr(self.llm, "provider", None)', new)
        new = re.sub(r"(?<![_\w])agent\.llm\.provider(?![_\w])", 'getattr(agent.llm, "provider", None)', new)
        new = re.sub(r"(?<![_\w])llm\.provider(?![_\w])", 'getattr(llm, "provider", None)', new)
        new = re.sub(r"(?<![_\w])self\.llm\.model_name(?![_\w])", 'getattr(self.llm, "model_name", getattr(self.llm, "model", None))', new)
        new = re.sub(r"(?<![_\w])agent\.llm\.model_name(?![_\w])", 'getattr(agent.llm, "model_name", getattr(agent.llm, "model", None))', new)
        new = re.sub(r"(?<![_\w])llm\.model_name(?![_\w])", 'getattr(llm, "model_name", getattr(llm, "model", None))', new)
        if new != text:
            open(path, "w").write(new)
            print(f"Patched: {path}")
