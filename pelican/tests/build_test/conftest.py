def pytest_addoption(parser):
    parser.addoption(
        "--check-wheel",
        action="store",
        default=False,
        help="Check wheel contents.",
    )
