import optengine as ope


def main() -> None:
    problem = (
        "Optimize a candidate design using AI analysis, FNO surrogate evaluation, "
        "classical search, quantum search, and a feasibility-policy decision."
    )

    ope.run(
        problem,
        render=True,
        title="OptEngine :: Quickstart",
        run_name="quickstart",
    )


if __name__ == "__main__":
    main()
