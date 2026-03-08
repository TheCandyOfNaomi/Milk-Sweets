import os
import openai
from flask import current_app
from app.extensions import cache

class AIService:
    def __init__(self, provider=None):
        self.provider = provider or os.getenv('AI_PROVIDER', 'tongyi')
        self.api_key = os.getenv(f'{self.provider.upper()}_API_KEY')
        self.timeout = int(os.getenv('AI_TIMEOUT', 8))

        openai.api_key = self.api_key
        if self.provider == 'tongyi':
            openai.base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1/'
        elif self.provider == 'zhipu':
            openai.base_url = 'https://open.bigmodel.cn/api/paas/v4/'
        elif self.provider == 'deepseek':
            openai.base_url = 'https://api.deepseek.com/v1/'

    def chat_completion(self, messages, temperature=0.3, max_tokens=500):
        model_map = {
            'tongyi': 'qwen-max',
            'zhipu': 'glm-4-plus',
            'deepseek': 'deepseek-chat',
        }
        model = model_map.get(self.provider, 'qwen-max')
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            current_app.logger.error(f"AI API error: {e}")
            return None

    def generate_summary(self, content):
        cache_key = f"summary:{hash(content)}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        messages = [
            {"role": "system", "content": "请为以下内容生成一句话摘要（50字以内）："},
            {"role": "user", "content": content[:2000]}
        ]
        summary = self.chat_completion(messages, max_tokens=100)
        if summary:
            cache.set(cache_key, summary, timeout=3600)
        return summary

    def recommend_tags(self, content):
        messages = [
            {"role": "system", "content": "根据内容推荐1-5个标签，用逗号分隔："},
            {"role": "user", "content": content[:1000]}
        ]
        result = self.chat_completion(messages, temperature=0.2)
        if result:
            return [t.strip() for t in result.split(',') if t.strip()]
        return []