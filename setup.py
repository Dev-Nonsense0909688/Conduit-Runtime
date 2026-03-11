from setuptools import setup, find_packages

setup(
    name="conduit",
    version="0.1.0",
    description="Local LLM runtime CLI",
    author="Dev-Nonsense0909688",
    packages=find_packages(),
    install_requires=["psutil", "requests", "rich", "tqdm"],
    entry_points={"console_scripts": ["conduit=conduit.cli:main"]},
    python_requires=">=3.9",
)
