"""Execute a command."""

import os
import sys

import anyio
import dagger


async def test() -> None:
    """Run unit tests in dagger."""
    versions = ["3.10", "3.11"]
    async with dagger.Connection(dagger.Config(log_output=sys.stdout)) as client:
        # get reference to the local project
        src = client.host().directory(".", exclude=["./venv"])
        sonar = (
            client.container()
            .from_("sonarsource/sonar-scanner-cli:latest")
            .with_env_variable("SONAR_HOST_URL", "https://sonarcloud.io")
            .with_env_variable("SONAR_SCANNER_OPTS", os.environ["SONAR_SCANNER_OPTS"])
            .with_env_variable("SONAR_LOGIN", os.environ["SONAR_LOGIN"])
            .with_mounted_directory("/usr/src", src)
            .with_exec(["sonar-scanner"])
        )
        await sonar.exit_code()
        for version in versions:
            venv_cache = client.cache_volume(f"venv-{version}")

            base = (
                client.container().from_(f"python:{version}-slim-buster")
                # mount cloned repository into image
                .with_mounted_directory("/src", src)
                # mount cached venv
                .with_mounted_cache("/src/venv", venv_cache)
                # set current working directory for next commands
                # .with_workdir("/src")
                # create virtual environment
                .with_exec(["python", "-m", "venv", "/src/venv"])
                # activate virtual environment
                .with_env_variable("PATH", "/src/venv/bin")
                # .with_exec(["source", "/src/venv/bin/activate"])
                # upgrade pip
                .with_exec(["pip", "install", "--upgrade", "pip"])
                # install test dependencies
                .with_exec(["pip", "install", "-r", "/src/requirements.txt"])
            )

            runner = base.with_workdir("/src")
            if version == "3.10":
                print("Starting linting stage...")
                linter = runner.with_exec(["ruff", "."]).with_exec(["mypy", "app/"])
                await linter.exit_code()
                print("Linting has finished")

            print(f"Starting tests for Python {version}")
            tests = (
                # run tests
                runner.with_exec(["pytest", "."])
            )

            # execute
            await tests.exit_code()
            print(f"Tests for Python {version} succeeded!")

    print("All tasks have finished")


if __name__ == "__main__":
    anyio.run(test)
