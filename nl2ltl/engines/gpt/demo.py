from nl2ltl import translate
from nl2ltl.engines.rasa.core import RasaEngine
from nl2ltl.engines.gpt.core import GPTEngine
from nl2ltl.filters.simple_filters import BasicFilter
from nl2ltl.engines.utils import pretty

# Instantiate the GPTEngine with GPT-3.5 model
gpt3_engine = GPTEngine()


filter = BasicFilter()
utterance = "Eventually send me a Slack after receiving a Gmail"
#utterance="FORMAT_VERSION: This value is incremented when changes are made to the eeprom format"

ltlf_formulas = translate(utterance, engine= gpt3_engine)
pretty(ltlf_formulas)
