import optengine as ope


def test_quickstart_run_returns_solution():
    solution = ope.run("Test optimization problem.", run_name="test")

    assert solution.decision["action"] in {"stop", "switch", "scale"}
    assert "confidence" in solution.metrics
    assert solution.results
    assert solution.output_path is not None
