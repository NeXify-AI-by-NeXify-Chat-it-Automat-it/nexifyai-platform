"""
NeXifyAI Adversarial Debate Prompts — adapted from adversarial-spec prompts.py.
Templates for spec review, critique, and consensus building.
"""

DOC_TYPES = {
    "prd": "Product Requirements Document",
    "tech-spec": "Technical Specification",
    "architecture": "Architecture Decision Record",
    "api-spec": "API Specification",
    "data-model": "Data Model / Schema Design",
    "security-review": "Security Review Document",
    "code-review": "Code Review",
    "general": "Specification Document",
}

FOCUS_AREAS = ["architecture", "security", "performance", "scalability", "maintainability",
               "error-handling", "data-integrity", "api-design", "testing", "documentation"]

def get_doc_type_name(doc_type: str) -> str:
    return DOC_TYPES.get(doc_type, DOC_TYPES["general"])

def get_debate_system_prompt(doc_type: str = "tech-spec") -> str:
    """System prompt that sets up the adversarial reviewer role."""
    doc_name = get_doc_type_name(doc_type)
    return f"""You are an expert technical reviewer specializing in {doc_name}.

Your task is to:
1. Carefully review the provided {doc_name} draft
2. Identify gaps, ambiguities, edge cases, security concerns, and architectural issues
3. Propose concrete improvements — not just criticism
4. End your review with "AGREE" if the spec is production-ready, or "REVISE" if changes are needed
5. If REVISE, provide the revised specification text

Be rigorous but constructive. Every concern must have a specific recommendation.
Focus on what would actually break in production — not hypothetical edge cases."""

def get_review_prompt(task: str, spec: str, round_num: int, max_rounds: int) -> str:
    """Build the review prompt for a debate round."""
    return f"""TASK: {task}

SPECIFICATION DRAFT (Round {round_num}/{max_rounds}):

{spec}

---

Review the specification above. Check for:
- **Completeness:** Are all requirements covered? Edge cases?
- **Consistency:** Do any sections contradict each other?
- **Security:** Are there security vulnerabilities or missing security controls?
- **Architecture:** Are the component boundaries clear? Data flow defined?
- **Performance:** Are there obvious bottlenecks or scaling issues?
- **Error Handling:** How are failures handled? Retry logic? Graceful degradation?

Reply with your review. End with "AGREE" if ready, or "REVISE" followed by the revised spec."""

PRESERVE_INTENT_PROMPT = """
**PRESERVE ORIGINAL INTENT**
This document represents deliberate design choices. Before suggesting removal of any requirement:
1. Explain why the original intent may be valid
2. Propose modifications that preserve the core value
3. Only suggest removal if you can articulate why the requirement is actively harmful
"""

FINAL_CONSENSUS_PROMPT = """
**FINAL CONSENSUS CHECK**
You are the last reviewer in this debate. Multiple models have already reviewed this spec.
Your role:
1. Summarize the key points of agreement
2. Highlight any remaining disagreements between previous reviewers
3. Provide a final, unified specification that synthesizes all feedback
4. If all major concerns are resolved, clearly state CONSENSUS REACHED
"""
