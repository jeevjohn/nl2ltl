# -*- coding: utf-8 -*-

"""
Implementation of the GPT engine.

Website:

    https://openai.com

"""
import json
import os
from enum import Enum
from pathlib import Path
from typing import Dict, Set

import openai
from pylogics.syntax.base import Formula

from nl2ltl.engines.base import Engine
from nl2ltl.engines.gpt import ENGINE_ROOT
from nl2ltl.engines.gpt.output import GPTOutput, parse_gpt_output, parse_gpt_result
from nl2ltl.filters.base import Filter

openai.api_key = os.getenv("OPENAI_API_KEY")
engine_root = ENGINE_ROOT
DATA_DIR = engine_root / "data"
PROMPT_PATH = engine_root / DATA_DIR / "prompt.json"


class Models(Enum):
    """The set of available GPT language models."""

    DAVINCI = "text-davinci-003"
    GPT3 = "gpt-3"
    GPT35 = "gpt-3.5"
    GPT4 = "gpt-4"


SUPPORTED_MODELS: Set[str] = {v.value for v in Models}


class GPTEngine(Engine):
    """The GPT engine."""

    def __init__(
        self,
        model: str = Models.GPT4.value,
        prompt: Path = PROMPT_PATH,
        temperature: float = 0.5,
    ):
        """GPT LLM Engine initialization."""
        self.model = model
        self.prompt = self._load_prompt(prompt)
        self.temperature = temperature

        self._check_consistency()

    def _load_prompt(self, prompt):
        return json.load(open(prompt, "r"))["prompt"]

    def _check_consistency(self) -> None:
        """Run consistency checks."""
        self.__check_openai_version()
        self.__check_model_support()

    def __check_openai_version(self):
        """Check that the GPT tool is at the right version."""
        is_right_version = openai.__version__ == "0.27.8"
        if not is_right_version:
            raise Exception(
                "OpenAI needs to be at version 0.27.8. "
                "Please install it manually using:"
                "\n"
                "pip install openai==0.27.8"
            )

    def __check_model_support(self):
        """Check if the model is a supported model."""
        is_supported = self.model in SUPPORTED_MODELS
        if not is_supported:
            raise Exception(
                f"The LLM model {self.model} is not currently supported by nl2ltl."
            )

    def translate(
        self, utterance: str, filtering: Filter = None
    ) -> Dict[Formula, float]:
        """From NL to best matching LTL formulas with confidence."""
        return _process_utterance(
            utterance, self.model, self.prompt, self.temperature, filtering
        )


def _process_utterance(
    utterance: str, model: str, prompt: str, temperature: float, filtering: Filter
) -> Dict[Formula, float]:
    """
    Process NL utterance.

    :param utterance: the natural language utterance
    :param model: the specific GPT model
    :param prompt: the prompt
    :param temperature: the temperature
    :param filtering: the filter used to remove formulas
    :return: a dict matching formulas to their confidence
    """
    query = "NL: " + utterance + "\n"
    prediction = openai.Completion.create(
        model=model,
        prompt=prompt + query,
        temperature=temperature,
        max_tokens=200,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\n\n"],
    )
    gpt_result: GPTOutput = parse_gpt_output(prediction)
    matching_formulas: Dict[Formula, float] = parse_gpt_result(gpt_result, filtering)
    return matching_formulas
