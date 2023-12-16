import asyncio
import os
import subprocess
import docker

async def read_stream(stream, callback):
    while True:
        line = await stream.readline()
        if line:
            callback(line.decode())
        else:
            break

async def run_command_with_async_readers(command):
    # start ruby docker container if not running with pwd mounted to /usr/src/
    client = docker.from_env()
    try:
        client.containers.get('ruby')
    except docker.errors.NotFound:
        current_working_dir=os.getcwd()
        client.containers.run(
            'ruby',
            name='gpt_bash',
            detach=True,
            volumes={current_working_dir: {'bind': '/usr/src/', 'mode': 'rw'}})

    # Run the command in

    # Start the subprocess using asyncio's subprocess
    process = await asyncio.create_subprocess_shell(
        command,
        stdin=asyncio.subprocess.DEVNULL, # Disable stdin
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

    # If result is > 1024 characters, return "Output too long: {total character count}" instead
    if len(result) > 50000:
        return f"ERROR: Output too long, {len(result)} characters"

    return result

async def bash(command):
    return await run_command_with_async_readers(command)

if __name__ == '__main__':
    print(bash('echo "Hello, World!"'))