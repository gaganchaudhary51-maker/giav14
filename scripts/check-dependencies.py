"""Check every declared backend requirement before starting GIA."""
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import subprocess
import sys

from pip._vendor.packaging.requirements import Requirement


def main():
    requirements = Path(__file__).resolve().parents[1] / "backend" / "requirements.txt"
    problems = []
    for line in requirements.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        requirement = Requirement(line)
        if requirement.marker and not requirement.marker.evaluate():
            continue
        try:
            installed = version(requirement.name)
        except PackageNotFoundError:
            problems.append(f"Missing: {requirement.name}")
            continue
        if installed not in requirement.specifier:
            problems.append(f"Incompatible: {requirement.name} {installed}; needs {requirement.specifier}")
    if problems:
        print("\n".join(problems))
        return 1
    return subprocess.call([sys.executable, "-m", "pip", "check"])


if __name__ == "__main__":
    sys.exit(main())
