Proof of concept experiment using Autogen and ChatGPT4 with tool calls to upgrade an old Rails application

example output https://gist.github.com/yenif/2b2aa7322e73d18925a1eb2b50d43e43

```
export OPENAI_API_KEY=...
poetry install
./dev_gpt.sh
```

- `dev_gpt.sh` - entrypoint
- `dev_gpt.py` - agent definitions and related code
- `bash_tool.py` - bash tool implementation, reusable
