"""Execute a command."""

import sys

import anyio
import dagger


async def test() -> None:
    """Run unit tests in dagger."""
    versions = ["3.10", "3.11"]
    async with dagger.Connection(dagger.Config(log_output=sys.stdout)) as client:
        # get reference to the local project
        src = client.host().directory(".")

        for version in versions:
            base = (
                client.container().from_(f"python:{version}-slim-buster")
                # mount cloned repository into image
                .with_mounted_directory("/src", src)
                # set current working directory for next commands
                .with_workdir("/src")
                # install test dependencies
                .with_exec(["pip", "install", "-r", "requirements.txt"])
            )
            print(f"Starting tests for Python {version}")
            tests = (
                # run tests
                base.with_exec(["pytest", "."])
            )

            # execute
            await tests.exit_code()
            print(f"Tests for Python {version} succeeded!")

            if version == "3.10":
                print("Starting linting stage...")
                linter = base.with_exec(["ruff", "."]).with_exec(["mypy", "app/"])
                await linter.exit_code()
                print("Linting has finished")

    print("All tasks have finished")


if __name__ == "__main__":
    anyio.run(test)
