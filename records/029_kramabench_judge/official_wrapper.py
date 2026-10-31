"""Load unmodified official files; change only client configuration and model ID."""
from pathlib import Path
import importlib
import sys
import types

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OFFICIAL = ROOT / 'records/027_kramabench_source/official'
BASE_URL = 'https://openrouter.ai/api/v1'
MODEL = 'openai/gpt-5-mini'

def official_metric(client_factory):
    # Avoid benchmark/__init__.py importing the unrelated agent/execution workflow.
    # The metric, llm_tools package and its modules are imported from original files.
    package = types.ModuleType('benchmark')
    package.__path__ = [str(OFFICIAL / 'benchmark')]
    package.__package__ = 'benchmark'
    sys.modules['benchmark'] = package
    metrics = importlib.import_module('benchmark.metrics')
    gpt = importlib.import_module('benchmark.llm_tools.gpt_interface')
    original_interface = gpt.GPTInterface

    # Change 1: client_factory supplies OpenRouter base_url and the file-loaded key.
    gpt.OpenAI = client_factory

    # Change 2: map only the official model ID to its OpenRouter identifier.
    def routed_interface(*args, **kwargs):
        assert not args and kwargs == {'model': 'gpt-5-mini'}
        return original_interface(model=MODEL)

    metrics.GPTInterface = routed_interface
    return metrics.metric_factory('llm_paraphrase')
