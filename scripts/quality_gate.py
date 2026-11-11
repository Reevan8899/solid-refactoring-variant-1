"""Проверяет сложность и индекс поддерживаемости исходного кода."""

from pathlib import Path
from statistics import mean

from radon.complexity import cc_rank, cc_visit
from radon.metrics import mi_rank, mi_visit
from radon.raw import analyze
from radon.visitors import Function

ROOT = Path(__file__).resolve().parents[1]


def analyze_files(paths):
    modules = []
    functions = []
    for path in paths:
        source = path.read_text(encoding="utf-8")
        lines = analyze(source).sloc
        if lines:
            modules.append((path, lines, mi_visit(source, multi=True)))
            functions.extend(block for block in cc_visit(source) if isinstance(block, Function))
    average = mean(block.complexity for block in functions)
    weighted_mi = sum(lines * score for _, lines, score in modules) / sum(lines for _, lines, _ in modules)
    return modules, functions, average, weighted_mi


def main() -> int:
    modules, functions, average, weighted_mi = analyze_files(sorted((ROOT / "src").rglob("*.py")))
    print(f"Средняя сложность {average:.2f} ({cc_rank(average)}). Методов и функций: {len(functions)}.")
    print(f"Индекс поддерживаемости с весами SLOC: {weighted_mi:.2f}.")
    for path, _, score in modules:
        print(f"{path.relative_to(ROOT).as_posix()}: {mi_rank(score)} ({score:.2f})")
    violations = []
    if average > 10:
        violations.append("Средняя сложность превышает предел B (10).")
    if weighted_mi < 60:
        violations.append("Взвешенный индекс поддерживаемости ниже 60.")
    if any(mi_rank(score) != "A" for _, _, score in modules):
        violations.append("Есть модули с индексом поддерживаемости ниже ранга A.")
    print("\n".join(violations) if violations else "Проверка Radon пройдена.")
    return int(bool(violations))


if __name__ == "__main__":
    raise SystemExit(main())
