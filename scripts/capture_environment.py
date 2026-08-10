from pathlib import Path
from src.utils.reproducibility import capture_environment
if __name__ == "__main__": print(capture_environment(Path("results/reproducibility/environment.json")))
