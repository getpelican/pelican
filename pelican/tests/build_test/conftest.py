def pytest_addoption(parser):
    parser.addoption(
        "--check-build",
        action="store",
        default=False,
        help="Check wheel contents.",
    )
