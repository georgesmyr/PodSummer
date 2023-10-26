import openai


class LLM:

    def __init__(self, model):

        self._model = model
        self.MODELS = ["gpt-3.5-turbo"]

    
    @property.setter
    def model(self, model):
        self._model = model

        if self._model not in self.MODELS:
            raise ValueError("Model not found. Please choose from the following: {}".format(self.MODELS))
        


