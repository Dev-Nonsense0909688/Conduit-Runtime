import os
import time
from conduit.runtime.loader import ModelLoader
from conduit.commands.path import get_path
MAX_HISTORY = 10

class Engine:

    def __init__(self, model, cfg = None):
        model_dir = get_path()
        model_path = os.path.join(model_dir, f"{model}.gguf")

        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        if cfg:
            loader = ModelLoader(model_path, model, cfg)
        else:
            loader = ModelLoader(model_path, model)
        print(f"[runtime] loading {model}")

        self.model = loader.run()

        start = time.time()
        print(f"[runtime] warming up model")

        loader.warmup(self.model)

        elapsed = time.time() - start
        print(f"[runtime] warmup completed in {elapsed:.2f}s")

    def _stream(self, prompt):

        return self.model(
            prompt,
            max_tokens=128,
            temperature=0.24,
            top_p=0.89,
            top_k=1,
            repeat_penalty=1.12,
            stream=True,
        )

    def generate(self, prompt):

        stream = self._stream(prompt)

        for chunk in stream:

            if not chunk:
                continue

            try:
                token = chunk["choices"][0]["text"]
                if token:
                    yield token

            except KeyError:
                print("[runtime] malformed chunk")
                continue
