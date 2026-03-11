import re
import psutil
import os
import math


class RuntimeTuner:

    def __init__(self, model):
        self.ram = psutil.virtual_memory().total / (1024**3)
        self.cores = os.cpu_count() or 4
        self.params = self._params(model)
        
        self.safe_ram = self.ram * 0.85

    def _params(self, name):
        m = re.search(r"(\d+(\.\d+)?)\s*B", name, re.I)
        return float(m.group(1)) if m else 7.0

    def model_ram(self):
        return self.params * 0.6

    def ctx(self):
        kv_per_token = self.params * 0.00052
        available = self.safe_ram - self.model_ram()
        if available <= 0:
            return 1024

        max_tokens = available / kv_per_token
        ctx = int(2 ** math.floor(math.log2(max_tokens)))
        return max(512, min(ctx, 16384))

    def n_batch(self):
        batch = int(math.sqrt(self.ctx()) * 6)
        return min(1024, max(128, batch))

    def threads(self):
        return max(1, self.cores)

    def use_mlock(self):
        return self.model_ram() < self.ram * 0.75

    def config(self):

        return {
            "ctx": self.ctx(),
            "threads": self.threads(),
            "n_batch": self.n_batch(),
            "gpu_layers": 0,
            "ram_gb": round(self.ram, 2),
            "model_params": self.params,
            "use_mlock": self.use_mlock(),
        }
