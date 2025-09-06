"""Example multi-agent pipeline using the OpenAI agent SDK.

The script shows how to orchestrate agents for marketing copy generation,
simulated A/B testing, and prompt improvement through feedback.
"""
from __future__ import annotations

import random
from typing import Dict, List

from openai import OpenAI


class CopyWriterAgent:
    """Agent responsible for generating marketing copy variants."""

    def __init__(self, client: OpenAI, model: str = "gpt-4.1-mini") -> None:
        self.client = client
        self.model = model

    def generate_copies(self, product: str, prompt_template: str, n: int = 2) -> List[str]:
        """Return *n* candidate copies using the provided template."""
        prompt = prompt_template.format(product=product, n=n)
        response = self.client.responses.create(model=self.model, input=prompt)
        lines = [line.strip("- ") for line in response.output_text.splitlines() if line.strip()]
        return lines[:n]


class ABTesterAgent:
    """Agent that performs a dummy A/B test by simulating conversion rates."""

    def run(self, copies: List[str]) -> Dict[str, float]:
        return {copy: random.random() for copy in copies}


class FeedbackAgent:
    """Agent that proposes a better prompt template using feedback."""

    def __init__(self, client: OpenAI, model: str = "gpt-4.1-mini") -> None:
        self.client = client
        self.model = model

    def improve_prompt(self, template: str, results: Dict[str, float]) -> str:
        best_copy = max(results, key=results.get)
        feedback_prompt = (
            "The following marketing copy performed best in an A/B test:\n"
            f"{best_copy}\n\n"
            "Original prompt template:\n"
            f"{template}\n\n"
            "Suggest an improved prompt template that could yield better copies."
        )
        response = self.client.responses.create(model=self.model, input=feedback_prompt)
        return response.output_text.strip()


class PromptOptimizer:
    """High level loop that iteratively updates the prompt template."""

    def __init__(self, copy_agent: CopyWriterAgent, tester: ABTesterAgent,
                 fb_agent: FeedbackAgent, template: str) -> None:
        self.copy_agent = copy_agent
        self.tester = tester
        self.fb_agent = fb_agent
        self.template = template

    def optimize(self, product: str, rounds: int = 3) -> str:
        for _ in range(rounds):
            copies = self.copy_agent.generate_copies(product, self.template)
            results = self.tester.run(copies)
            self.template = self.fb_agent.improve_prompt(self.template, results)
        return self.template


def main() -> None:
    client = OpenAI()
    copy_agent = CopyWriterAgent(client)
    tester = ABTesterAgent()
    fb_agent = FeedbackAgent(client)
    template = "Generate {n} short, catchy marketing copies for {product}." \
               "Each copy should be under 20 words."
    optimizer = PromptOptimizer(copy_agent, tester, fb_agent, template)
    final_template = optimizer.optimize("wireless earbuds", rounds=2)
    print("Final optimized prompt:\n", final_template)


if __name__ == "__main__":
    main()
