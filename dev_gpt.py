import logging
import inspect
import asyncio
from autogen import UserProxyAgent, ConversableAgent
from autogen.code_utils import content_str
from autogen.agentchat.contrib.compressible_agent import CompressibleAgent
from prompt_toolkit import PromptSession

from bash_tool import bash

logging.basicConfig(level=logging.INFO)

SEED = 10

assistant = CompressibleAgent(
#assistant = ConversableAgent(
    name="LLM Programmer",
    llm_config={
        # "model": "gpt-3.5-turbo-1106",
        "model": "gpt-4-1106-preview",
        "max_retries": 100,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "bash",
                    "description": "Execute command in a secure bash shell",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Command to execute in the bash shell"},
                        },
                        "required": ["command"]
                    }
                }
            }
        ],
        "cache_seed": SEED,
    },
    compress_config={
        "mode": "COMPRESS",
        "trigger_count": 8000,
        "last_n_messages": 10,
        "verbose": True,
        "llm_config": {
            "model": "gpt-4-1106-preview",
        }
    },
    system_message=inspect.cleandoc("""
        You are an advanced LLM programmer working with an SRE to iteratively improve the system to better align with best practices. Defer to the SRE for high level planning, but make sure to work through your thought process and ask clarifying questions to ensure you understand the SRE's goals. As the conversation gets longer, the history will be summarized, so call out key points that should be maintained in summarization as you go. Also call out when previously summarized information should be updated.

        If you get stuck without forward progress after a few back and forth messages, you can break out by ending with "INTERVENE"

        Don't forget to write your code to disk in the appropriate files. You can use the "bash" tool to write to files.

        ## Tools

        You have access to a "bash" function that can be used to execute commands in a secure bash shell. You can use this tool to read and write files, install packages, and execute other bash commands. The tool is called with a single parameter "command" that is a string containing the command to execute. The output of the command is returned as a string.

        ## Example:

        ### Run a Rails commnand
        {
            "name": "bash",
            "arguments": {
                "command": "rails new myapp"
            }
        }

        ### Read file
        {
            "name": "bash",
            "arguments": {
                "command": "cat /path/to/file"
            }
        }

        ### Write file
        {
            "name": "bash",
            "arguments": {
                "command": "cat > /path/to/file << 'EOF'\nThis is the content of the file\nEOF\n"
            }
        }

        ### Generate RDoc documentation
        {
            "name": "bash",
            "arguments": {
                "command": "rdoc -f markdown -O --op collaged/doc collaged"
            }
        }

        ### List files
        {
            "name": "bash",
            "arguments": {
                "command": "ls -lh /path/to/directory"
            }
        }

        ### List files recursively
        {
            "name": "bash",
            "arguments": {
                "command": "find collaged/doc -type f | sort "
            }
        }
    """)
)

class UserPromptAgent(UserProxyAgent):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.session = PromptSession()

    async def get_human_input(self, prompt):
        return await self.session.prompt_async(prompt, multiline=True, vi_mode=True)

user_proxy = UserPromptAgent(
    name="Staff SRE",
    human_input_mode="TERMINATE",
    is_termination_msg=(lambda x: content_str(x.get("content")) in ["TERMINATE","INTERVENE"]),
    max_consecutive_auto_reply=100,
    llm_config={
        "model": "gpt-4-1106-preview",
        "max_retries": 100,
        "cache_seed": SEED,
    },
    code_execution_config=False,
    system_message=inspect.cleandoc("""
        # Persona
        You are an SRE iteratively improving the system to better align with best practices. You are working with an advanced
        LLM programmer to accomplish goals by iteratively breaking them down into smaller goals and working step by step to make
        continous progress. Make sure to call out when each goal has been accomplished. As the conversation gets longer, the
        history will be summarized, so call out key points that should be maintained in summarization as you go. Also call out
        when previously summarized information should be updated.

        You may need to tell the assistant to use `cat` to read the contents of files or to write to a file with
        `cat > ./path/to/file << 'EOF'`. If your assistant tries to write out code that comments out sections along the lines of
        "code goes here...", make sure to tell it to ensure all code required for the file to work need to be included. If your
        assistant thinks that a file must be read manually, try asking it to read the file and then prompting it to take the
        desired actions based on the file contents.

        If any goals are not completed or are stated as being manual, encourage the assistant to try to accomplish those tasks
        one by one or to break them down futher. Remember, NEVER consider a task complete until any implementing actions have
        been tested and verified, for example by re-reading a file that has just been written and double checking the result.
        Make sure all actions are actually implemented and that none are skipped through implication.

        # Goal
        ./collaged_old is an old rails project. So old that it can not be updated through normal procedures.

        First, investigate the collaged_old project to understand its dependencies, configurations, features, user experience, and testing.

        Then, please create a new rails project at ./collaged
        * Make sure Gemfile has the modern equivalents for all of the dependencies in collaged_old
            * do not pin versions in the Gemfile unless required due to the latest version not being usable.
            * If you do need to pin a version, make sure to document why.
        * Move the code in collaged_old to collaged by reading each file and writing the updated equivalent to collaged
            * list all the files that are critical to configuring and implementing the functionality of collaged_old
            * then iterating the list, read each file, consider what needs to be changed to be compatible with the new version of rails
            * in collaged, write the complete new file with only the changes required to be compatible with the new dependencies
            * the updated code should have the same functionality and be identical in all other respects to what is in collaged_old
            * Consider if there are any updates to collaged that are implied by the code being copied from collaged_old outside of the files being copied.
            * If you come to a decision with mutltiple options, generally prefer the option with the least amount of changes that still accomplishes the intent of the goal. Further refactoring can always be done in the future.
        * After all code, configurations, and specs have been copied, run the specs in collaged to ensure that the code is working as expected
        * If you run into any issues make sure to debug them thoroughly and follow the scientific method to break down the issue and implement a solution

        Remember, the LLM Programmer you are working with is an advanced programmer with access to a bash tool to execute and neccessary commands. If the LLM Programmer responds with niceties, please explicitly redirect them to implementing the task at hand.

        Make sure to take a step back, work through the process step by step to make a plan, and run tests as soon as you are able to in order to guide debugging.

        The Goal is not complete untill the updated version of collaged can successfully run the tests copied from collaged_old and `rails server` can be run to start the server.
    """)
)

user_proxy.register_function({
    "bash": bash,
})

asyncio.run(assistant.a_initiate_chat(
    user_proxy,
    message=inspect.cleandoc("""
        I'm an advanced LLM programmer. I can help you with your task. I have access to a bash tool that can execute commands in a secure bash shell. I can use this tool to read and write files, install packages, and execute other bash commands. How can I help you?
    """)
))