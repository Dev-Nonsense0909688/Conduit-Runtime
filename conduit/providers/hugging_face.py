import os
import requests
from conduit.providers.quant_select import QuantSelector
from conduit.commands.path import get_path
from tqdm import tqdm
import re

BASE = "https://huggingface.co"

HEADERS = (
    {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    if os.getenv("HF_TOKEN")
    else {}
)

UNSUPPORTED = [
    "qwen3",
    "qwen3.5",
    "deepseek-v3",
    "deepseek-r1",
    "glm-4",
    "yi-34b-chat-vl",
    "internlm2",
    "minicpm-v",
    "baichuan2",
    "qwen-vl",
    "qwen2-vl",
]


def clean_name(filename):
    name, ext = os.path.splitext(filename)
    name = re.sub(r"[-_.]q\d(_k_[ms]|_k|_0)?", "", name, flags=re.IGNORECASE)

    return name + ext


class HuggingFace:

    def __init__(self):
        self.quant = QuantSelector()

    def normalize(self, x):
        return x.lower().replace("-", "").replace("_", "").replace(".", "")

    def score(self, query, model_id):

        q = self.normalize(query)
        m = self.normalize(model_id)

        if q == m:
            return 100
        if m.startswith(q):
            return 80
        if q in m:
            return 60
        return 0

    def search(self, query, limit=20):

        print(f"Searching HuggingFace for {query}")

        r = requests.get(
            f"{BASE}/api/models",
            params={
                "search": query,
                "limit": 100,
                "sort": "downloads",
                "direction": -1,
            },
            headers=HEADERS,
            timeout=30,
        )

        r.raise_for_status()

        ranked = []

        for m in r.json():

            model_id = m.get("id", "").lower()

            if "gguf" not in model_id:
                continue

            if any(bad in model_id for bad in UNSUPPORTED):
                continue

            s = self.score(query, model_id)

            if s == 0:
                continue

            ranked.append(
                (
                    s,
                    {
                        "id": m.get("id"),
                        "task": m.get("pipeline_tag"),
                        "downloads": m.get("downloads", 0),
                        "likes": m.get("likes", 0),
                        "tags": m.get("tags", []),
                    },
                )
            )

        ranked.sort(key=lambda x: (x[0], x[1]["downloads"]), reverse=True)

        return [m for _, m in ranked[:limit]]

    def links(self, repo):

        r = requests.get(f"{BASE}/api/models/{repo}", headers=HEADERS, timeout=30)

        r.raise_for_status()

        files = [f["rfilename"] for f in r.json().get("siblings", [])]

        valid_quants = (
            "q8_0",
            "q6_k",
            "q5_k_m",
            "q5_k_s",
            "q5_0",
            "q4_k_m",
            "q4_k_s",
            "q4_0",
            "q4",
            "q3_k_m",
            "q3_k_s",
            "q2_k",
        )

        links = [
            f"{BASE}/{repo}/resolve/main/{f}"
            for f in files
            if f.endswith(".gguf")
            and any(q in f.lower() for q in valid_quants)
            and not any(x in f.lower() for x in ("ud-", "iq", "bf16", "mmproj"))
        ]

        if not links:
            print("No compatible GGUF files found.")

        return links

    def best_quant(self, repo):

        links = self.links(repo)

        if not links:
            raise RuntimeError("No GGUF files found.")

        return self.quant.select(links)

    def metadata(self, repo):

        r = requests.get(f"{BASE}/api/models/{repo}", headers=HEADERS, timeout=30)

        r.raise_for_status()

        data = r.json()

        return {
            "id": data.get("id"),
            "downloads": data.get("downloads"),
            "likes": data.get("likes"),
            "tags": data.get("tags"),
        }

    def download(self, url, path=None, repo=None):
        
        if path is None:
            path = get_path()
            os.makedirs(path, exist_ok=True)
        
        raw = os.path.basename(url)
        filename = clean_name(raw)
        file = os.path.join(path, filename)
        temp = file + ".part"

        resume_pos = 0
        if os.path.exists(temp):
            resume_pos = os.path.getsize(temp)
            print(f"Resuming download from {resume_pos} bytes")

        headers = HEADERS.copy()
        if resume_pos:
            headers["Range"] = f"bytes={resume_pos}-"

        r = requests.get(url, headers=headers, stream=True, timeout=60)
        r.raise_for_status()

        total = int(r.headers.get("content-length", 0)) + resume_pos
        mode = "ab" if resume_pos else "wb"

        with open(temp, mode) as f, tqdm(
            total=total,
            initial=resume_pos,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=filename,
        ) as bar:

            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))

        os.rename(temp, file)

        print(f"Downloaded → {file}")
        return file


    def install(self, repo, quant=None):

        print(f"\nInstalling model: {repo}")

        links = self.links(repo)

        if not links:
            print("No GGUF files found.")
            return
        
        if quant:
            for l in links:
                if quant.lower() in l.lower():
                    best = l
                    break
            else:
                print(f"Quant '{quant}' not found for this model.")
                return
        else:
            best = self.quant.select(links)

        print(f"Selected quant: {os.path.basename(best)}")

        return self.download(best, repo=repo)
