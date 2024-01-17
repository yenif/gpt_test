import asyncio
import os
import subprocess
import docker

client = docker.from_env()
container_name = 'gpt_bash'

initialized = False
if not initialized:
    # Stop and remove any existing container with the same name
    try:
        container = client.containers.get(container_name)
        container.stop()
        container.remove()
        print(f"Existing container '{container_name}' stopped and removed.")
    except docker.errors.NotFound:
        print(f"No existing container named '{container_name}' found.")

    # Start the Ruby Docker container running with pwd mounted to /usr/src/
    current_working_dir = os.getcwd()
    client.containers.run(
        'ruby:latest',
        name=container_name,
        command="tail -f /dev/null",
        detach=True,
        volumes={current_working_dir: {'bind': '/usr/src/', 'mode': 'rw'}},
        working_dir='/usr/src/'
    )

    initialized = True

async def run_command_with_async_readers(command):
    # Prepare the Docker exec command
    docker_exec_command = ["docker", "exec", container_name, "bash", "-c", command]

    # Start the subprocess without using the shell
    process = await asyncio.create_subprocess_exec(
        *docker_exec_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    output = []

    # Read from stdout
    async for line in process.stdout:
        decoded_line = line.decode().rstrip()
        output.append(decoded_line)
        print(decoded_line)

    # Read from stderr
    async for line in process.stderr:
        decoded_line = line.decode().rstrip()
        output.append(decoded_line)
        print(decoded_line)

    # Wait for the subprocess to finish
    await process.wait()

    result = "\n".join(output)

    # If result is > 50000 characters, return an error message
    if len(result) > 50000:
        return f"ERROR: Output too long, {len(result)} characters"

    return result

async def bash(command):
    return await run_command_with_async_readers(command)

if __name__ == '__main__':
    # Run the bash command
    result = asyncio.run(bash('echo "Hello, World!"'))
    print(result)
