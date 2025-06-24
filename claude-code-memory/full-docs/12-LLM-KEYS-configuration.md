deepseek:
  base_url: "https://api.deepseek.com/v1"
  # 敏感信息通过环境变量占位符加载
  api_key: "sk-325be9f2c5594c3cae07495b28817043"
  models:
    - model_id: "deepseek-chat"
      generation_type: "standard"
    - model_id: "deepseek-reasoner"
      generation_type: "reasoning"
openrouter:
  base_url: "https://openrouter.ai/api/v1"
  # 敏感信息通过环境变量占位符加载
  api_key: "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"
  models:
    - model_id: "openai/gpt-4.1"
      generation_type: "standard"
    - model_id: "google/gemini-2.5-pro"
      generation_type: "standard"
    - model_id: "anthropic/claude-sonnet-4"
      generation_type: "standard"
    - model_id: "minimax/minimax-m1"
      generation_type: "standard"
    - model_id: "google/gemini-2.5-flash-lite-preview-06-17"
      generation_type: "standard"

siliconflow:
  base_url: "https://api.siliconflow.cn/v1"
  api_key: 'sk-lpuljmmwvjwpkluhkglyuqvqhnpzyeumgftjmjlnkxmgjqct'
embedding_model_name: "Pro/BAAI/bge-m3" # 注意：最大批次64
rerank_model_name: "Pro/BAAI/bge-reranker-v2-m3"
