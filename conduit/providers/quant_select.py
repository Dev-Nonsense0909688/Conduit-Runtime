import psutil
import re

class QuantSelector:

    QUANT_FACTORS = {
        "Q2_K": 0.35,
        "Q3_K_M": 0.45,
        "Q4_K_M": 0.60,
        "Q5_K_M": 0.75,
        "Q6_K": 0.90,
        "Q8_0": 1.20,
    }

    PARAM_RE = re.compile(r"(\d+(?:[._]\d+)?)\s*B", re.I)

    def __init__(self):
        self.ram = psutil.virtual_memory().total / (1024**3)

    def estimate(self, params, quant):

        factor = self.QUANT_FACTORS.get(quant)
        if factor is None:
            return None

        model_ram = params * factor
        overhead = 1.5  # runtime + KV cache

        return model_ram + overhead

    def extract_params(self, link):

        m = self.PARAM_RE.search(link)
        if not m:
            return None

        val = m.group(1).replace("_", ".")
        return float(val)

    def extract_quant(self, link):

        link_l = link.lower()

        for q in self.QUANT_FACTORS:
            if q.lower() in link_l:
                return q

        return None

    def select(self, links):

        safe_ram = self.ram * 0.70
        best = None

        for link in links:

            params = self.extract_params(link)
            quant = self.extract_quant(link)

            if params is None or quant is None:
                continue

            est = self.estimate(params, quant)

            if est and est <= safe_ram:

                score = self.QUANT_FACTORS[quant]

                if not best or score > best[1]:
                    best = (link, score)

        if best:
            return best[0]

        return links[0] if links else None
