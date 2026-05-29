"""
NeXifyAI Model Router — adapted from adversarial-spec models.py.
Routes to DeepSeek v3/v4 (OpenRouter) and Nscale models.
Uses Data Vault credentials (DS_ env vars) — never raw keys.
"""
import os, time, logging
from dataclasses import dataclass, field
from typing import Optional
import concurrent.futures

logger = logging.getLogger("adversarial.model_router")

# ── Provider configs (all from Data Vault) ──
PROVIDER_CONFIGS = {
    "deepseek-v3": {
        "api_key_env": "DS_DEEPSEEK_600C3ECB__API_KEY",
        "base_url_env": None,
        "model_id": "deepseek-chat",
        "cost_per_1m_input": 0.14,
        "cost_per_1m_output": 0.28,
    },
    "deepseek-v4-flash": {
        "api_key_env": "DS_DEEPSEEK_D7D70D9A__API_KEY",
        "base_url_env": "DS_DEEPSEEK_D7D70D9A__BASE_URL",
        "model_id": "deepseek-v4-flash",
        "cost_per_1m_input": 0.50,
        "cost_per_1m_output": 2.00,
    },
    "nscale-qwen3-32b": {
        "api_key_env": "DS_NSCALE_EF975EBE__API_KEY",
        "base_url_env": "DS_NSCALE_EF975EBE__BASE_URL",
        "model_id": "qwen3-32b",
        "cost_per_1m_input": 0.80,
        "cost_per_1m_output": 0.80,
    },
    "nscale-qwen3-14b": {
        "api_key_env": "DS_NSCALE_EF975EBE__API_KEY",
        "base_url_env": "DS_NSCALE_EF975EBE__BASE_URL",
        "model_id": "qwen3-14b",
        "cost_per_1m_input": 0.40,
        "cost_per_1m_output": 0.40,
    },
    "nscale-qwen-coder-32b": {
        "api_key_env": "DS_NSCALE_EF975EBE__API_KEY",
        "base_url_env": "DS_NSCALE_EF975EBE__BASE_URL",
        "model_id": "qwen2.5-coder-32b",
        "cost_per_1m_input": 0.80,
        "cost_per_1m_output": 0.80,
    },
    "nscale-qwq-32b": {
        "api_key_env": "DS_NSCALE_EF975EBE__API_KEY",
        "base_url_env": "DS_NSCALE_EF975EBE__BASE_URL",
        "model_id": "qwq-32b",
        "cost_per_1m_input": 0.80,
        "cost_per_1m_output": 0.80,
    },
    "openrouter-deepseek-v4-flash": {
        "api_key_env": "DS_OPENROUTER_58984AC0__API_KEY",
        "base_url_env": "DS_OPENROUTER_58984AC0__BASE_URL",
        "model_id": "deepseek/deepseek-v4-flash",
        "cost_per_1m_input": 2.50,
        "cost_per_1m_output": 10.00,
    },
}

MODEL_ALIASES = {
    "v3": "deepseek-v3",
    "v4": "deepseek-v4-flash",
    "qwen32": "nscale-qwen3-32b",
    "qwen14": "nscale-qwen3-14b",
    "coder": "nscale-qwen-coder-32b",
    "qwq": "nscale-qwq-32b",
    "openrouter": "openrouter-deepseek-v4-flash",
}

@dataclass
class ModelResponse:
    """Response from a model in the debate."""
    model: str
    response: str
    agreed: bool
    spec: Optional[str] = None
    error: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0

@dataclass
class DebateResult:
    """Complete debate result across all models."""
    task: str
    models_used: list[str]
    rounds: int
    consensus: bool
    responses: list[ModelResponse]
    final_spec: Optional[str] = None
    total_cost: float = 0.0
    duration_seconds: float = 0.0

def resolve_model(model_name: str) -> dict:
    """Resolve model name or alias to provider config."""
    if model_name in MODEL_ALIASES:
        model_name = MODEL_ALIASES[model_name]
    if model_name in PROVIDER_CONFIGS:
        return PROVIDER_CONFIGS[model_name]
    # Try provider:model syntax
    if ":" in model_name:
        provider, model = model_name.split(":", 1)
        if provider in PROVIDER_CONFIGS:
            config = dict(PROVIDER_CONFIGS[provider])
            config["model_id"] = model
            return config
    logger.warning(f"Unknown model: {model_name}, falling back to deepseek-v3")
    return PROVIDER_CONFIGS["deepseek-v3"]

def get_api_key(config: dict) -> str:
    """Get API key from environment (Data Vault)."""
    key_name = config.get("api_key_env", "")
    value = os.environ.get(key_name, "")
    if not value:
        logger.warning(f"API key {key_name} not found in environment")
    return value

def get_base_url(config: dict) -> Optional[str]:
    """Get base URL from environment if configured."""
    url_name = config.get("base_url_env")
    if url_name:
        return os.environ.get(url_name)
    return None

def call_model(model_name: str, system_prompt: str, user_prompt: str, 
               temperature: float = 0.7, max_tokens: int = 4000) -> ModelResponse:
    """Call a single model and return its response."""
    import openai
    
    config = resolve_model(model_name)
    api_key = get_api_key(config)
    base_url = get_base_url(config)
    
    if not api_key:
        return ModelResponse(
            model=model_name, response="", agreed=False, 
            error=f"No API key for {model_name}"
        )
    
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    
    try:
        response = client.chat.completions.create(
            model=config["model_id"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        content = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens if response.usage else 0
        output_tokens = response.usage.completion_tokens if response.usage else 0
        
        # Cost calculation
        cost_input = (input_tokens / 1_000_000) * config["cost_per_1m_input"]
        cost_output = (output_tokens / 1_000_000) * config["cost_per_1m_output"]
        total_cost = cost_input + cost_output
        
        # Detect agreement
        agreed = "AGREE" in content.upper()[-200:] or "CONSENSUS" in content.upper()
        
        return ModelResponse(
            model=model_name, response=content, agreed=agreed,
            input_tokens=input_tokens, output_tokens=output_tokens, cost=total_cost
        )
    
    except Exception as e:
        return ModelResponse(
            model=model_name, response="", agreed=False, error=str(e)
        )

def call_models_parallel(model_names: list[str], system_prompt: str, 
                         user_prompt: str, max_workers: int = 4) -> list[ModelResponse]:
    """Call multiple models in parallel and return all responses."""
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(call_model, name, system_prompt, user_prompt): name 
            for name in model_names
        }
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                result = future.result(timeout=120)
                results.append(result)
            except Exception as e:
                results.append(ModelResponse(model=name, response="", agreed=False, error=str(e)))
    
    return results

def run_debate(task: str, spec_draft: str, models: list[str] = None,
               max_rounds: int = 3, doc_type: str = "tech-spec") -> DebateResult:
    """Run a full adversarial debate on a spec draft."""
    import time as time_mod
    start_time = time_mod.time()
    
    if models is None:
        models = ["v4", "qwen32", "qwq"]
    
    from .prompts import get_debate_system_prompt, get_review_prompt
    system = get_debate_system_prompt(doc_type)
    
    all_responses = []
    current_spec = spec_draft
    consensus = False
    round_num = 0
    
    for round_num in range(1, max_rounds + 1):
        logger.info(f"Debate round {round_num}/{max_rounds} with models: {models}")
        
        prompt = get_review_prompt(task, current_spec, round_num, max_rounds)
        responses = call_models_parallel(models, system, prompt)
        all_responses.extend(responses)
        
        agreed_count = sum(1 for r in responses if r.agreed)
        if agreed_count >= len(models) * 0.75:
            consensus = True
            final_responses = [r for r in responses if r.agreed and r.response]
            if final_responses:
                current_spec = final_responses[0].response
            break
        else:
            feedback_parts = []
            for r in responses:
                if r.response:
                    feedback_parts.append(f"## {r.model}\n{r.response[:500]}")
            feedbacks = "\n\n".join(feedback_parts)
            current_spec = (
                current_spec + "\n\n"
                + f"## Review Round {round_num}\n"
                + feedbacks
            )
    
    total_cost = sum(r.cost for r in all_responses)
    duration = time_mod.time() - start_time
    
    return DebateResult(
        task=task, models_used=models, rounds=round_num,
        consensus=consensus, responses=all_responses, final_spec=current_spec,
        total_cost=total_cost, duration_seconds=duration
    )