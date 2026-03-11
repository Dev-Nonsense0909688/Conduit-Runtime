from llama_cpp import Llama
from conduit.runtime.tuner import RuntimeTuner
import os
import contextlib
import time


class ModelLoader:

    REQUIRED_CFG = [
        "threads",
        "ctx",
        "gpu_layers",
        "n_batch",
        "use_mlock",
    ]

    def __init__(self, path: str, model_name: str, cfg=None):

        self.path = path
        self.model_name = model_name

        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Model file not found: {self.path}")

        if cfg:
            self.config = cfg
        else:
            tuner = RuntimeTuner(model_name)
            self.config = tuner.config()

        self._validate_config()

    def _validate_config(self):

        for key in self.REQUIRED_CFG:
            if key not in self.config:
                raise RuntimeError(f"Missing runtime config key: {key}")

    def run(self):

        cfg = self.config

        print(
            f"[runtime] loading {self.model_name} | "
            f"threads={cfg['threads']} | ctx={cfg['ctx']} | "
            f"batch={cfg['n_batch']} | gpu_layers={cfg['gpu_layers']}"
        )

        start = time.time()

        try:

            with open(os.devnull, "w") as f, contextlib.redirect_stdout(
                f
            ), contextlib.redirect_stderr(f):

                model = Llama(
                    model_path=self.path,
                    n_ctx=cfg["ctx"],
                    n_threads=cfg["threads"],
                    n_gpu_layers=cfg["gpu_layers"],
                    n_batch=cfg["n_batch"],
                    use_mmap=True,
                    use_mlock=cfg["use_mlock"],
                    verbose=False,
                )

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")

        load_time = round(time.time() - start, 2)

        print(f"[runtime] model ready in {load_time}s")

        return model

    def warmup(self, model: Llama):

        try:
            model("Hello", max_tokens=1)
        except Exception:
            pass

    def get_metadata(self, model: Llama):

        try:
            return model.metadata
        except Exception:
            return {}

    def info(self):

        return {
            "model": self.model_name,
            "path": self.path,
            "config": self.config,
        }
