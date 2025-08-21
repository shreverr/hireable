---
applyTo: '**'
---
========================
CODE SNIPPETS
========================
TITLE: Registering Custom Tools (Python)
DESCRIPTION: Demonstrates how to register custom tools (FileReaderTool and FileWriterTool) using an InMemoryToolRegistry.

SOURCE: https://docs.portialabs.ai/add-custom-tools

LANGUAGE: python
CODE:
```
"""Registry containing my custom tools."""

from portia import InMemoryToolRegistry
from my_custom_tools.file_reader_tool import FileReaderTool
from my_custom_tools.file_writer_tool import FileWriterTool

custom_tool_registry = InMemoryToolRegistry.from_local_tools(
[
        FileReaderTool(),
        FileWriterTool(),
],
)
```

----------------------------------------

TITLE: File Writer Tool using @tool Decorator
DESCRIPTION: A custom Portia tool that writes provided content to a specified local file. If the file exists, its content is overwritten; otherwise, a new file is created. Requires pathlib.

SOURCE: https://docs.portialabs.ai/add-custom-tools

LANGUAGE: python
CODE:
```
from pathlib import Path
from typing import Annotated
from portia import tool

@tool
defile_writer_tool(
    filename: Annotated[str,"The location where the file should be saved"],
    content: Annotated[str,"The content to write to the file"]
)->str:
"""Writes content to a file."""
    filepath = Path(filename)
if filepath.is_file():
withopen(filepath,"w")asfile:
file.write(content)
else:
withopen(filepath,"x")asfile:
file.write(content)
returnf"Content written to {filename}"

```

----------------------------------------

TITLE: Create and Initialize Tool Registry
DESCRIPTION: Demonstrates how to create a custom tool registry by instantiating the ToolRegistry class with a list of tool functions. This registry can then be used to group custom tools for later import into code.

SOURCE: https://docs.portialabs.ai/add-custom-tools

LANGUAGE: python
CODE:
```
"""Registry containing my custom tools."""

from portia import ToolRegistry

my_tool_registry = ToolRegistry([
    file_reader_tool(),
    file_writer_tool(),
])

```

----------------------------------------

TITLE: Add Custom Tools with @tool Decorator
DESCRIPTION: Demonstrates how to create custom tools for Portia AI using the @tool decorator in Python. This allows LLMs to interact with local files by writing and reading content.

SOURCE: https://docs.portialabs.ai/extend-run-tools

LANGUAGE: python
CODE:
```
from portia_sdk import tool

@tool
def write_to_file(filename: str, content: str):
    """Writes content to a specified file."""
    with open(filename, 'w') as f:
        f.write(content)
    return f"Successfully wrote to {filename}"

@tool
def read_from_file(filename: str):
    """Reads content from a specified file."""
    with open(filename, 'r') as f:
        content = f.read()
    return content
```

----------------------------------------

TITLE: File Reader Tool using @tool Decorator
DESCRIPTION: A custom Portia tool that reads content from local files. It supports CSV, JSON, Excel, TXT, and LOG file formats, returning their content as strings or dictionaries. Requires pandas and pathlib.

SOURCE: https://docs.portialabs.ai/add-custom-tools

LANGUAGE: python
CODE:
```
from pathlib import Path
import pandas as pd
import json
from typing import Annotated
from portia import tool

@tool
defile_reader_tool(
    filename: Annotated[str,"The location where the file should be read from"]
)->str|dict:
"""Finds and reads content from a local file on Disk."""
    file_path = Path(filename)
    suffix = file_path.suffix.lower()

if file_path.is_file():
if suffix =='.csv':
return pd.read_csv(file_path).to_string()
elif suffix =='.json':
with file_path.open('r', encoding='utf-8')as json_file:
                data = json.load(json_file)
return data
elif suffix in['.xls','.xlsx']:
return pd.read_excel(file_path).to_string()
elif suffix in['.txt','.log']:
return file_path.read_text(encoding="utf-8")

```

----------------------------------------

TITLE: Customize Cloud Tools with Tool Descriptions
DESCRIPTION: Demonstrates how to customize cloud-based tools or remote MCP server tool descriptions using the `ToolRegistry.with_tool_description` function. This allows for tailored integration of third-party tools.

SOURCE: https://docs.portialabs.ai/cloud-tool-registry

LANGUAGE: Python
CODE:
```
from portia_sdk.registry import ToolRegistry

# Assuming 'registry' is an instance of ToolRegistry
# and 'tool_name' is the name of the tool to customize
# and 'new_description' is the new description string

registry.with_tool_description(tool_name, new_description)
```

----------------------------------------

TITLE: Customize Tool Descriptions with Portia
DESCRIPTION: Demonstrates how to provide custom instructions to Portia agents for using a specific tool by modifying its description. This example customizes the Linear MCP server's 'create_issue' tool to use a default team ID.

SOURCE: https://docs.portialabs.ai/integrating-tools

LANGUAGE: python
CODE:
```
from portia import Config, Portia, PortiaToolRegistry
from portia.cli import CLIExecutionHooks

my_config = Config.from_default()

portia = Portia(
    config=my_config,
    tools=PortiaToolRegistry(my_config).with_tool_description(
"portia:mcp:custom:mcp.linear.app:create_issue",
"If a teamID is not provided, use teamID 123."),
    execution_hooks=CLIExecutionHooks(),
)
```

----------------------------------------

TITLE: Combine Tool Registries and Run Portia
DESCRIPTION: Shows how to combine multiple tool registries (local and Portia's example registries) using the '+' operator. It then instantiates the Portia class with the combined registry and executes a plan to fetch weather data and write it to a file, demonstrating the integration of custom and example tools.

SOURCE: https://docs.portialabs.ai/add-custom-tools

LANGUAGE: python
CODE:
```
from dotenv import load_dotenv
from portia import(
    Portia,
    example_tool_registry,
    Config,
    LogLevel,
)

load_dotenv()

# Load example and custom tool registries into a single one
complete_tool_registry = example_tool_registry + my_tool_registry
# Instantiate Portia with the tools above
portia = Portia(
    Config.from_default(default_log_level=LogLevel.DEBUG),
    tools=complete_tool_registry,
)

# Execute the plan from the user query
plan_run = portia.run('Get the weather in the town with the longest name in Welsh'
+' and write it to demo_runs/weather.txt.')

# Serialise into JSON and print the output
print(plan_run.model_dump_json(indent=2))

```

----------------------------------------

TITLE: FileWriterTool Implementation (Python)
DESCRIPTION: Implements a tool to write content to a local file. It defines input parameters for filename and content using Pydantic.

SOURCE: https://docs.portialabs.ai/add-custom-tools

LANGUAGE: python
CODE:
```
from pathlib import Path
from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext

class FileWriterToolSchema(BaseModel):
"""Schema defining the inputs for the FileWriterTool."""

    filename:str= Field(...,
        description="The location where the file should be saved",
)
    content:str= Field(...,
        description="The content to write to the file",
)


class FileWriterTool(Tool):
"""Writes content to a file."""

    id:str="file_writer_tool"
    name:str="File writer tool"
    description:str="Writes content to a file locally"
    args_schema:type[BaseModel]= FileWriterToolSchema
    output_schema:tuple[str,str]=("str","A string indicating where the content was written to")

def run(self,_: ToolRunContext, filename:str, content:str)->str:
"""Run the FileWriterTool."""

        filepath = Path(filename)
        if filepath.is_file():
            with open(filepath,"w")as file:
                file.write(content)
        else:
            with open(filepath,"x")as file:
                file.write(content)
        return f"Content written to {filename}"
```

----------------------------------------

TITLE: Use Clarifications in Custom Tools
DESCRIPTION: Explains how to use the Clarification mechanism within custom Portia tools. This allows a plan run to pause and request user input when necessary.

SOURCE: https://docs.portialabs.ai/extend-run-tools

LANGUAGE: python
CODE:
```
from portia_sdk import tool, Clarification

@tool
def process_data(data: str):
    """Processes data, prompting for clarification if needed."""
    if not data:
        raise Clarification("Please provide the data to process.")
    # Process the data here
    return "Data processed successfully."
```

----------------------------------------

TITLE: Custom Emoji Evaluator and Tool Stubbing with Portia
DESCRIPTION: This Python code defines a custom evaluator to count emojis in the output of a plan run and stubs the 'file_reader_tool' to return static content. It then configures a Portia client with the stubbed tool and runs evals using the custom evaluator.

SOURCE: https://docs.portialabs.ai/steel-thread-quickstart

LANGUAGE: python
CODE:
```
from portia import Portia, Config, DefaultToolRegistry
from steelthread.steelthread import SteelThread, EvalConfig
from steelthread.evals import Evaluator, EvalMetric
from steelthread.portia.tools import ToolStubRegistry, ToolStubContext


# Define custom evaluator
class EmojiEvaluator(Evaluator):
    def eval_test_case(self, test_case, plan, plan_run, metadata):
        out = plan_run.outputs.final_output.get_value() or ""
        count = out.count("⚠️")
        return EvalMetric.from_test_case(
            test_case=test_case,
            name="emoji_score",
            score=min(count / 2, 1.0),
            description="Emoji usage",
            explanation=f"Found {count} ⚠️ emojis in the output.",
            actual_value=str(count),
            expectation="2"
        )

# Define stub behavior
def file_reader_stub_response(ctx: ToolStubContext) -> str:
    """Stub response for file reader tool to return static file content."""
    filename = ctx.kwargs.get("filename", "").lower()

    return f"Feedback from file:{filename} suggests \
        ⚠️ 'One does not simply Calorify' \
        and ⚠️ 'Calorify is not a diet' \
        and ⚠️ 'Calorify is not a weight loss program' \
        and ⚠️ 'Calorify is not a fitness program' \
        and ⚠️ 'Calorify is not a health program' \
        and ⚠️ 'Calorify is not a nutrition program' \
        and ⚠️ 'Calorify is not a meal delivery service' \
        and ⚠️ 'Calorify is not a meal kit service' "


config = Config.from_default()

# Add the tool stub definition to your Portia client using a ToolStubRegistry
portia = Portia(
    config,
    tools=ToolStubRegistry(
        DefaultToolRegistry(config),
        stubs={
            "file_reader_tool": file_reader_stub_response,
        },
    ),
)

# Run evals with stubs 
SteelThread().run_evals(
    portia,
    EvalConfig(
        eval_dataset_name="your-dataset-name-here",  # TODO: replace with your dataset name
        config=config,
        iterations=5,
        evaluators=[EmojiEvaluator(config)]
    ),
)

```

----------------------------------------

TITLE: Filter Gmail Tools from Portia Registry
DESCRIPTION: Demonstrates how to create a custom tool registry in Portia AI and filter out specific tools, in this case, excluding all Gmail-related tools. This is achieved by defining a filter function that checks the tool ID.

SOURCE: https://docs.portialabs.ai/integrating-tools

LANGUAGE: python
CODE:
```
from dotenv import load_dotenv
from portia import (
    Portia,
    PortiaToolRegistry,
    Tool,
    default_config,
)

load_dotenv()

def exclude_gmail_filter(tool: Tool) -> bool:
    return not tool.id.startswith("portia:google:gmail:")

registry = PortiaToolRegistry(config=default_config()).filter_tools(exclude_gmail_filter)
portia = Portia(tools=registry)
```

----------------------------------------

TITLE: FileReaderTool Implementation (Python)
DESCRIPTION: Implements a tool to read content from local files (CSV, JSON, Excel, TXT, LOG). It uses Pydantic for schema definition and Pandas for handling CSV and Excel files.

SOURCE: https://docs.portialabs.ai/add-custom-tools

LANGUAGE: python
CODE:
```
from pathlib import Path
import pandas as pd
import json
from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext


class FileReaderToolSchema(BaseModel):
"""Schema defining the inputs for the FileReaderTool."""

    filename:str= Field(...,
        description="The location where the file should be read from",
)


class FileReaderTool(Tool[str]):
"""Finds and reads content from a local file on Disk."""

    id:str="file_reader_tool"
    name:str="File reader tool"
    description:str="Finds and reads content from a local file on Disk"
    args_schema:type[BaseModel]= FileReaderToolSchema
    output_schema:tuple[str,str]=("str","A string dump or JSON of the file content")

def run(self,_: ToolRunContext, filename:str)->str|dict[str,any]:
"""Run the FileReaderTool."""

        file_path = Path(filename)
        suffix = file_path.suffix.lower()

        if file_path.is_file():
            if suffix =='.csv':
                return pd.read_csv(file_path).to_string()
            elif suffix =='.json':
                with file_path.open('r', encoding='utf-8')as json_file:
                    data = json.load(json_file)
                return data
            elif suffix in['.xls','.xlsx']:
                return pd.read_excel(file_path).to_string()
            elif suffix in['.txt','.log']:
                return file_path.read_text(encoding="utf-8")
        return "File not found or unsupported format."
```

----------------------------------------

TITLE: Portia Tool Execution with Clarifications
DESCRIPTION: This Python script demonstrates how to instantiate Portia, load tool registries, execute a plan that requires clarification, and handle user input to resolve the clarification. It then resumes the plan and prints the final output.

SOURCE: https://docs.portialabs.ai/clarifications-in-tools

LANGUAGE: python
CODE:
```
from portia import Portia
from portia.config import default_config
from portia.open_source_tools.registry import example_tool_registry
from my_custom_tools.registry import custom_tool_registry
from portia.clarification import MultipleChoiceClarification
from portia.plan_run import PlanRunState

# Load example and custom tool registries into a single one
complete_tool_registry = example_tool_registry + custom_tool_registry
# Instantiate a Portia instance. Load it with the default config and with the tools above
portia = Portia(tools=complete_tool_registry)

# Execute the plan from the user query
plan_run = portia.run('Read the contents of the file "weather.txt".')

# Check if the plan run was paused due to raised clarifications
while plan_run.state == PlanRunState.NEED_CLARIFICATION:
# If clarifications are needed, resolve them before resuming the plan run
for clarification in plan_run.get_outstanding_clarifications():
# For each clarification, prompt the user for input
print(f"{clarification.user_guidance}")
        user_input =input("Please enter a value:\n"  
+("\n".join(clarification.options)+"\n")if"options"in clarification else"")
# Resolve the clarification with the user input
        plan_run = portia.resolve_clarification(clarification, user_input, plan_run)

# Once clarifications are resolved, resume the plan run
    plan_run = portia.resume(plan_run)

# Serialise into JSON and print the output
print(plan_run.model_dump_json(indent=2))
```

----------------------------------------

TITLE: PortiaMcpTool call_remote_mcp_tool
DESCRIPTION: Calls a tool using the MCP session with a custom timeout implementation using asyncio.wait. This addresses issues with the default client's read timeout, ensuring a correct exception is raised when a deadline is reached. It takes the tool name and optional arguments, returning the result as a string.

SOURCE: https://docs.portialabs.ai/SDK/portia/tool

LANGUAGE: python
CODE:
```
class PortiaMcpTool(Tool[str]):
    async def call_remote_mcp_tool(self, name: str, arguments: dict | None = None) -> str:
        """Call a tool using the MCP session."""
        pass
```

----------------------------------------

TITLE: Example Weather Output
DESCRIPTION: This is an example of the output file generated by the Portia run, containing weather information for a specific location. It demonstrates the result of executing the plan that involves fetching data and writing it to a file.

SOURCE: https://docs.portialabs.ai/add-custom-tools

LANGUAGE: text
CODE:
```
The current weather in Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch is broken clouds with a temperature of 6.76°C.

```

----------------------------------------

TITLE: Python Human-in-the-loop Clarification for Tool Calls
DESCRIPTION: This Python code demonstrates how to create a custom execution hook for Portia AI to implement human-in-the-loop checks. It specifically targets the 'refund_tool' and uses `UserVerificationClarification` to ask the user for confirmation before proceeding with the tool call. If the user does not verify, a `ToolHardError` is raised.

SOURCE: https://docs.portialabs.ai/execution-hooks

LANGUAGE: python
CODE:
```
from typing import Any
from portia import Clarification, ClarificationCategory, ExecutionHooks, PlanRun, Portia, Step, Tool, ToolHardError
from portia.clarification import UserVerificationClarification

def clarify_before_refunds(
    tool: Tool,
    args:dict[str, Any],
    plan_run: PlanRun,
    step: Step,
)-> Clarification |None:
# Only raise a clarification for the refund tool
    if tool.id!="refund_tool":
        return None

# Find if the clarification if we already raised it
    previous_clarification = plan_run.get_clarification_for_step(ClarificationCategory.USER_VERIFICATION)

# If we haven't raised it, or it has been resolved, raise a clarification
    if not previous_clarification or not previous_clarification.resolved:
        return UserVerificationClarification(
            plan_run_id=plan_run.id,
            user_guidance=f"Are you happy to proceed with the call to {tool.name} with args {args}? "
            "Enter 'y' or 'yes' to proceed",
        )

# If the user didn't verify the tool call, error out
    if str(previous_clarification.response).lower() not in ["y","yes"]:
        raise ToolHardError(f"User rejected tool call to {tool.name} with args {args}")

# If the user did verify the tool call, continue to the call
    return None

portia = Portia(execution_hooks=ExecutionHooks(before_tool_call=clarify_before_refunds))
```

----------------------------------------

TITLE: SDK Reference for Clarification
DESCRIPTION: This snippet provides a reference to the Portia SDK for handling clarifications within custom tools. It details how to raise a Clarification to prompt a plan run to interrupt and solicit user input.

SOURCE: https://docs.portialabs.ai/clarifications-in-tools

LANGUAGE: python
CODE:
```
from portia.clarification import Clarification

# Inside a custom tool definition:
def my_custom_tool(input_data):
    # ... tool logic ...
    if needs_clarification(input_data):
        raise Clarification("Please provide additional information: ", context={'some_key': 'some_value'})
    # ... rest of tool logic ...
    return result
```

----------------------------------------

TITLE: End User Update Tool Implementation
DESCRIPTION: Defines and implements a custom Portia tool (`EndUserUpdateTool`) that allows updating an end user's name and setting custom attributes. It uses Pydantic for schema definition and demonstrates how to modify `ToolRunContext`.

SOURCE: https://docs.portialabs.ai/manage-end-users

LANGUAGE: python
CODE:
```
from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext

classEndUserUpdateToolSchema(BaseModel):
"""Input for EndUserUpdateTool."""

    name:str|None= Field(default=None, description="The new name for the end user.")


classEndUserUpdateTool(Tool):
"""Updates the name of the plan runs end user."""

id:str="end_user_update"
    name:str="End User Update Tool"
    description:str="Updates the name of the end user"
    args_schema:type[BaseModel]= EndUserUpdateToolSchema
    output_schema:tuple[str,str]=("str","str: The new name")

defrun(self, ctx: ToolRunContext, name:str)->str:
"""Change the name."""
        ctx.end_user.name = name
        ctx.end_user.set_attribute("has_name_update","true")
return name
```

----------------------------------------

TITLE: Portia Tool Module Overview
DESCRIPTION: This section provides an overview of the portia.tool module, highlighting its role in defining an abstract base class for tools and implementing the PortiaRemoteTool for Portia Cloud interactions. It emphasizes the extendability of these tools for custom integrations.

SOURCE: https://docs.portialabs.ai/SDK/portia/tool

LANGUAGE: python
CODE:
```
This module defines an abstract base class for tools, providing a structure for creating custom tools that can integrate with external systems. It includes an implementation of a base `Tool` class that defines common attributes and behaviors, such as a unique ID and name. Child classes should implement the `run` method to define the specific logic for interacting with the external systems or performing actions.
The module also contains `PortiaRemoteTool`, a subclass of `Tool`, which implements the logic to interact with Portia Cloud, including handling API responses and tool errors.
The tools in this module are designed to be extendable, allowing users to create their own tools while relying on common functionality provided by the base class.
```

----------------------------------------

TITLE: Accessing Clarifications via ToolRunContext in Python
DESCRIPTION: Demonstrates how to access clarifications from the ToolRunContext object within a custom tool's run method. This is useful for clarifications not directly tied to the tool's arguments. It imports necessary classes from the 'portia' library.

SOURCE: https://docs.portialabs.ai/clarifications-in-tools

LANGUAGE: python
CODE:
```
from portia import ToolRunContext, MultipleChoiceClarification

def run(self, ctx: ToolRunContext, filename:str)->str|dict[str,any]| MultipleChoiceClarification:
    """Run the FileReaderTool."""
    clarifications = ctx.clarifications
```

----------------------------------------

TITLE: Equip Portia with Monday.com Tools
DESCRIPTION: Demonstrates how to equip a Portia instance with tools from the Monday.com MCP server alongside default tools. It involves creating a combined tool registry and passing it to the Portia constructor.

SOURCE: https://docs.portialabs.ai/portia-tools/local-mcp/monday

LANGUAGE: python
CODE:
```
from portia import DefaultToolRegistry, McpToolRegistry, Portia, Config

config = Config.from_default()
tool_registry = DefaultToolRegistry(config)+ McpToolRegistry.from_stdio_connection(
    server_name="monday.com",
    command="npx",
    args=[
"@mondaydotcomorg/monday-api-mcp",
"-t",
"<api_key>",
],
)

portia = Portia(config=config, tools=tool_registry)
```

----------------------------------------

TITLE: Importing and Using Open Source Tools in Python
DESCRIPTION: Demonstrates how to import and load Portia's open-source tools into an InMemoryToolRegistry using Python. It also mentions the possibility of combining these with cloud or custom tools.

SOURCE: https://docs.portialabs.ai/portia-tools/open-source/search

LANGUAGE: python
CODE:
```
from portia.open_source_tools.registry import open_source_tool_registry
from portia.registry import InMemoryToolRegistry

# Load tools into an InMemoryToolRegistry
registry = InMemoryToolRegistry()
registry.register_tools(open_source_tool_registry)

# Example of using a tool (assuming 'search_tool' is registered)
# result = registry.get_tool('search_tool').run(search_query='what is the capital of France?')

```

----------------------------------------

TITLE: Import and Load Open Source Tools
DESCRIPTION: Demonstrates how to import the open-source tool registry and load tools into an InMemoryToolRegistry object using Python. This allows for the use of Portia's pre-built open-source tools.

SOURCE: https://docs.portialabs.ai/portia-tools/open-source/crawl

LANGUAGE: python
CODE:
```
from portia.open_source_tools.registry import open_source_tool_registry
from portia.tool_registry import InMemoryToolRegistry

# Initialize the tool registry
tool_registry = InMemoryToolRegistry()

# Load open source tools into the registry
tool_registry.load_tools(open_source_tool_registry)
```

----------------------------------------

TITLE: Instantiate Portia with Default Tool Registry
DESCRIPTION: Shows how to instantiate a Portia instance using the default tool registry, which includes Portia's pre-defined tools and can be configured with environment variables.

SOURCE: https://docs.portialabs.ai/integrating-tools

LANGUAGE: python
CODE:
```
from dotenv import load_dotenv
from portia import(
    DefaultToolRegistry,
    Portia,
    default_config,
)
from portia.open_source_tools.calculator_tool import CalculatorTool
from portia.open_source_tools.search_tool import SearchTool
from portia.open_source_tools.weather import WeatherTool

load_dotenv()

# Instantiate a Portia instance. Load it with the example tools and Portia's tools.
portia = Portia(tools=DefaultToolRegistry(default_config()))
```

----------------------------------------

TITLE: Steel Thread Custom Metrics
DESCRIPTION: Steel Thread supports custom metrics for evaluating agents, which can be deterministic or LLM-as-judge based. Supported metrics include accuracy, completeness, clarity, efficiency, latency, and tool usage.

SOURCE: https://docs.portialabs.ai/steel-thread-intro

LANGUAGE: APIDOC
CODE:
```
Custom Metrics for Steel Thread:
  - Evaluator Types:
    - Deterministic evaluators
    - LLMs-as-judge
  - Supported Metrics:
    - Accuracy
    - Completeness
    - Clarity
    - Efficiency
    - Latency
    - Tool usage
    - Domain-specific checks
```

----------------------------------------

TITLE: FileReaderTool Implementation with Clarification
DESCRIPTION: This Python code defines a `FileReaderTool` that reads various file formats (CSV, JSON, Excel, TXT) and includes a `find_file` method to search for alternative file locations. It uses `MultipleChoiceClarification` to prompt the user when multiple file paths are found.

SOURCE: https://docs.portialabs.ai/clarifications-in-tools

LANGUAGE: python
CODE:
```
from pathlib import Path
import pandas as pd
import json
from pydantic import BaseModel, Field
from portia import (
    MultipleChoiceClarification,
    Tool,
    ToolHardError,
    ToolRunContext,
)


class FileReaderToolSchema(BaseModel):
    """Schema defining the inputs for the FileReaderTool."""

    filename:str= Field(...,
        description="The location where the file should be read from",
)


class FileReaderTool(Tool[str]):
    """Finds and reads content from a local file on Disk."""

    id:str="file_reader_tool"
    name:str="File reader tool"
    description:str="Finds and reads content from a local file on Disk"
    args_schema:type[BaseModel]= FileReaderToolSchema
    output_schema:tuple[str,str]=("str","A string dump or JSON of the file content")

    def run(self, ctx: ToolRunContext, filename:str)->str|dict[str,any]| MultipleChoiceClarification:
        """Run the FileReaderTool."""

        file_path = Path(filename)
        suffix = file_path.suffix.lower()

        if file_path.is_file():
            if suffix =='.csv':
                return pd.read_csv(file_path).to_string()
            elif suffix =='.json':
                with file_path.open('r', encoding='utf-8')as json_file:
                    data = json.load(json_file)
                return data
            elif suffix in['.xls','.xlsx']:
                return pd.read_excel(file_path).to_string
            elif suffix in['.txt','.log']:
                return file_path.read_text(encoding="utf-8")
            else:
                raise ToolHardError(f"Unsupported file format: {suffix}. Supported formats are .txt, .log, .csv, .json, .xls, .xlsx.")

        alt_file_paths = self.find_file(filename)
        if alt_file_paths:
            return MultipleChoiceClarification(
                plan_run_id=ctx.plan_run.id,
                argument_name="filename",
                user_guidance=f"Found {filename} in these location(s). Pick one to continue:\n{alt_file_paths}",
                options=alt_file_paths,
            )

        raise ToolHardError(f"No file found on disk with the path {filename}.")

    def find_file(self, filename:str)->list[Path]:
        """Returns a full file path or None."""

        search_path = Path("../")
        filepaths =[]

        for filepath in search_path.rglob(filename):
            if filepath.is_file():
                filepaths.append(str(filepath))
        if filepaths:
            return filepaths
        return None

```

----------------------------------------

TITLE: Import and Load Open Source Tools
DESCRIPTION: Demonstrates how to import open-source tools from the Portia SDK and load them into an InMemoryToolRegistry. This allows for the use of pre-built tools in your projects.

SOURCE: https://docs.portialabs.ai/portia-tools/open-source/map-website

LANGUAGE: python
CODE:
```
from portia.open_source_tools.registry import open_source_tool_registry
from portia.registry import InMemoryToolRegistry

# Load tools into the registry
registry = InMemoryToolRegistry()
registry.register_tools(open_source_tool_registry)
```

----------------------------------------

TITLE: Import and Use Open Source Tools
DESCRIPTION: Demonstrates how to import open-source tools from the Portia SDK and load them into an InMemoryToolRegistry. This allows for the use of pre-built tools within your project.

SOURCE: https://docs.portialabs.ai/portia-tools/open-source/browser

LANGUAGE: python
CODE:
```
from portia.open_source_tools.registry import open_source_tool_registry
from portia.tool_registry import InMemoryToolRegistry

# Load tools into an InMemoryToolRegistry
tool_registry = InMemoryToolRegistry()
tool_registry.register_tools(open_source_tool_registry)
```

----------------------------------------

TITLE: PortiaMcpTool run method
DESCRIPTION: Invokes a tool by dispatching the call to the MCP server. This method accepts a tool run context and arbitrary keyword arguments for the tool invocation, returning the result as a string.

SOURCE: https://docs.portialabs.ai/SDK/portia/tool

LANGUAGE: python
CODE:
```
class PortiaMcpTool(Tool[str]):
    def run(self, _: ToolRunContext, **kwargs: Any) -> str:
        """Invoke the tool by dispatching to the MCP server."""
        pass
```

----------------------------------------

TITLE: Portia Tool Registry Aggregation
DESCRIPTION: Allows for the aggregation of multiple tool registries or a registry with a list of tools, ensuring unique tool IDs.

SOURCE: https://docs.portialabs.ai/SDK/portia/tool_registry

LANGUAGE: APIDOC
CODE:
```
ToolRegistry:
  __add__(other: ToolRegistry | list[Tool]) -> ToolRegistry
    Returns an aggregated tool registry combining two registries or a registry and tool list.
    Tool IDs must be unique across the two registries otherwise an error will be thrown.
    Arguments:
      other (ToolRegistry | list[Tool]): Another tool registry or a list of tools to be combined.
    Returns:
      AggregatedToolRegistry: A new tool registry containing tools from both registries.
```

----------------------------------------

TITLE: Instantiate Portia with Specific Tools
DESCRIPTION: Demonstrates how to create a Portia instance and provide it with a list of specific tools, such as CalculatorTool, SearchTool, and WeatherTool, for use in answering queries.

SOURCE: https://docs.portialabs.ai/integrating-tools

LANGUAGE: python
CODE:
```
from portia import(
  default_config,
  Portia,
)
from portia.open_source_tools.calculator_tool import CalculatorTool
from portia.open_source_tools.search_tool import SearchTool
from portia.open_source_tools.weather import WeatherTool

# Instantiate a Portia instance. Load it with the default config and with the example tools.
portia = Portia(tools=[CalculatorTool(), SearchTool(), WeatherTool()])
```

----------------------------------------

TITLE: PortiaRemoteTool Class
DESCRIPTION: Represents a tool that forwards run execution to Portia Cloud. It inherits from the base `Tool` class and is generic over a serializable type.

SOURCE: https://docs.portialabs.ai/SDK/portia/tool

LANGUAGE: python
CODE:
```
class PortiaRemoteTool(Tool, Generic[SERIALIZABLE_TYPE_VAR]):
    """Tool that passes run execution to Portia Cloud."""
    pass
```

----------------------------------------

TITLE: DefaultToolRegistry Class
DESCRIPTION: Represents a registry that provides a default set of tools, including open-source tools, search, map, crawl, weather, and Portia cloud tools, depending on API key availability.

SOURCE: https://docs.portialabs.ai/SDK/portia/tool_registry

LANGUAGE: python
CODE:
```
class DefaultToolRegistry(ToolRegistry):
    """A registry providing a default set of tools."""
    pass
```

----------------------------------------

TITLE: Portia Tool Registry Filtering for Microsoft Tools
DESCRIPTION: Demonstrates how to filter the Portia tool registry to exclude Google tools, enabling the use of Microsoft tools like Outlook. This is necessary due to potential tool ID clashes.

SOURCE: https://docs.portialabs.ai/portia-tools/portia-cloud/microsoft-outlook/outlook-send-draft-email

LANGUAGE: python
CODE:
```
from portia import PortiaToolRegistry, default_config

registry = PortiaToolRegistry(default_config()).filter_tools(lambda tool:not tool.id.startswith("portia:google:"))
```

----------------------------------------

TITLE: Portia SDK batch_ready_check
DESCRIPTION: Performs a batch check on the readiness of Portia cloud tools. It takes a configuration, a set of tool IDs, and the tool run context as input, returning a readiness response.

SOURCE: https://docs.portialabs.ai/SDK/portia/tool

LANGUAGE: python
CODE:
```
class PortiaMcpTool(Tool[str]):
    @classmethod
    def batch_ready_check(cls, config: Config, tool_ids: set[str], tool_run_context: ToolRunContext) -> ReadyResponse:
        """Batch check readiness for Portia cloud tools."""
        pass
```

----------------------------------------

TITLE: Portia Tool Class Definition
DESCRIPTION: Defines the abstract base class 'Tool' for creating tools in Portia. It inherits from Pydantic's BaseModel and supports generic types. Child classes must implement the 'run' method.

SOURCE: https://docs.portialabs.ai/SDK/portia/tool

LANGUAGE: python
CODE:
```
class Tool(BaseModel, Generic[SERIALIZABLE_TYPE_VAR]):
    """Abstract base class for a tool."""
    id: str
    name: str
    description: str
    args_schema: type[BaseModel]
    output_schema: tuple[str, str]
    should_summarize: bool
```

----------------------------------------

TITLE: Integrate Open Source Tools with Portia
DESCRIPTION: Shows how to initialize Portia with the open-source tool registry, which includes general-purpose utility tools like web search (Tavily) and weather information (OpenWeatherMap). Some tools may require API keys.

SOURCE: https://docs.portialabs.ai/integrating-tools

LANGUAGE: python
CODE:
```
from portia import open_source_tool_registry, Portia

portia = Portia(tools=open_source_tool_registry)
```

----------------------------------------

TITLE: Python Single Tool Agent Step Example
DESCRIPTION: Illustrates the use of `.single_tool_agent_step()` to call a tool with dynamically resolved arguments. This example shows how to specify the tool, the task, and the inputs required for the tool.

SOURCE: https://docs.portialabs.ai/build-plan

LANGUAGE: python
CODE:
```
builder.single_tool_agent_step(
    tool="web_scraper",
    task="Extract key information from the webpage provided",
    inputs=[StepOutput("text_blob_with_url")],
    name="scrape_webpage"
)
```

----------------------------------------

TITLE: Portia Tool Registry Filtering and Description Updates
DESCRIPTION: Provides methods for filtering tools based on a predicate and updating tool descriptions, either by extending or overwriting.

SOURCE: https://docs.portialabs.ai/SDK/portia/tool_registry

LANGUAGE: APIDOC
CODE:
```
ToolRegistry:
  filter_tools(predicate: Callable[[Tool], bool]) -> ToolRegistry
    Filters the tools in the registry based on a predicate.
    Arguments:
      predicate (Callable[[Tool], bool]): A predicate to filter the tools.
    Returns:
      Self: A new ToolRegistry with the filtered tools.

  with_tool_description(tool_id: str, updated_description: str, *, overwrite: bool = False) -> ToolRegistry
    Updates a tool with an extension or override of the tool description.
    Arguments:
      tool_id (str): The id of the tool to update.
      updated_description (str): The tool description to update. If `overwrite` is False, this will extend the existing tool description, otherwise, the entire tool description will be updated.
      overwrite (bool): Whether to update or extend the existing tool description.
    Returns:
      Self: The tool registry is updated in place and returned.
    Particularly useful for customising tools in MCP servers for usecases. A deep copy is made of the underlying tool such that the tool description is only updated within this registry. Logs a warning if the tool is not found.
```

----------------------------------------

TITLE: Integrate Custom MCP Servers with Portia
DESCRIPTION: Illustrates how to integrate local or remote MCP servers directly into a Portia agent using `McpToolRegistry.from_sse_connection`. This method requires manual authentication handling for the MCP server.

SOURCE: https://docs.portialabs.ai/integrating-tools

LANGUAGE: python
CODE:
```
from portia import Portia, McpToolRegistry

tool_registry =(
# Assumes server is running on port 8000
    McpToolRegistry.from_sse_connection(
        server_name="mcp_sse_example_server",
        url="http://localhost:8000",
)
)
portia = Portia(tools=tool_registry)
```

----------------------------------------

TITLE: Portia Tool Methods and Validators
DESCRIPTION: Provides documentation for key methods and validators within the Portia Tool class, including checking readiness, executing tools synchronously and asynchronously, and validating description length and method signatures.

SOURCE: https://docs.portialabs.ai/SDK/portia/tool

LANGUAGE: python
CODE:
```
def ready(ctx: ToolRunContext) -> ReadyResponse:
    """Check whether the tool can be plan_run."""
    # Implementation details...
    pass

@abstractmethod
def run(ctx: ToolRunContext, *args: Any, **kwargs: Any) -> SERIALIZABLE_TYPE_VAR | Clarification:
    """Run the tool."""
    # Implementation details...
    pass

async def arun(ctx: ToolRunContext, *args: Any, **kwargs: Any) -> SERIALIZABLE_TYPE_VAR | Clarification:
    """Async run the tool."""
    # Implementation details...
    pass

@model_validator(mode="after")
def check_description_length(self) -> Self:
    """Check that the description is less than 16384 characters."""
    # Implementation details...
    pass

@model_validator(mode="after")
def check_run_method_signature(self) -> Self:
    """Ensure the run method signature matches the args_schema."""
    # Implementation details...
    pass

def to_langchain(ctx: ToolRunContext, sync: bool = True) -> StructuredTool:
    """Return a LangChain representation of this tool."""
    # Implementation details...
    pass
```

----------------------------------------

TITLE: Python SDK Usage for Extract Tool
DESCRIPTION: Demonstrates how to import and use the open-source extract tool from the Portia SDK. It shows loading tools into an InMemoryToolRegistry and combining them with other tools.

SOURCE: https://docs.portialabs.ai/portia-tools/open-source/extract

LANGUAGE: python
CODE:
```
from portia.open_source_tools.registry import open_source_tool_registry
from portia.tool_registry import InMemoryToolRegistry

# Load tools into a registry
registry = InMemoryToolRegistry()
registry.register_tools(open_source_tool_registry)

# Example of using the extract tool (assuming it's registered)
# extract_tool = registry.get_tool('extract_tool')
# result = extract_tool(urls=['https://example.com'], include_images=True)
```

----------------------------------------

TITLE: Importing and Using Open Source Tools
DESCRIPTION: Demonstrates how to import open-source tools from Portia's SDK repository and load them into an InMemoryToolRegistry.

SOURCE: https://docs.portialabs.ai/portia-tools/open-source/file-writer

LANGUAGE: python
CODE:
```
from portia.open_source_tools.registry import open_source_tool_registry
from portia.tool_registry import InMemoryToolRegistry

# Load tools into a registry
registry = InMemoryToolRegistry()
registry.register_tools(open_source_tool_registry)
```

----------------------------------------

TITLE: PortiaToolRegistry Filter Method (with_default_tool_filter)
DESCRIPTION: Creates a new PortiaToolRegistry instance configured with a default tool filtering mechanism.

SOURCE: https://docs.portialabs.ai/SDK/portia/tool_registry

LANGUAGE: python
CODE:
```
def with_default_tool_filter() -> PortiaToolRegistry:
    """
    Create a PortiaToolRegistry with a default tool filter.
    """
    pass
```

----------------------------------------

TITLE: Tool Registry Contains Check (__contains__)
DESCRIPTION: Checks if a specific tool, identified by its ID, exists within the tool registry.

SOURCE: https://docs.portialabs.ai/SDK/portia/tool_registry

LANGUAGE: python
CODE:
```
def __contains__(tool_id: str) -> bool:
    """
    Check if a tool is in the registry.
    """
    pass
```

----------------------------------------

TITLE: Equip Portia with Qdrant and Default Tools
DESCRIPTION: Provides a complete example of equipping a Portia instance with both the default tools and the Qdrant MCP server tools. It shows how to configure Portia and combine tool registries.

SOURCE: https://docs.portialabs.ai/portia-tools/local-mcp/qdrant

LANGUAGE: python
CODE:
```
from portia import DefaultToolRegistry, McpToolRegistry, Portia, Config

config = Config.from_default()
tool_registry = DefaultToolRegistry(config)+ McpToolRegistry.from_stdio_connection(
    server_name="qdrant",
    command="uvx",
    args=[
"mcp-server-qdrant",
],
    env={
"QDRANT_LOCAL_PATH":"<path_to_qdrant>",
"COLLECTION_NAME":"<collection_name>",
"EMBEDDING_MODEL":"<model_name>",
},
)


portia = Portia(config=config, tools=tool_registry)
```

----------------------------------------

TITLE: FileWriterTool Functionality
DESCRIPTION: Implements the FileWriterTool, which is responsible for writing provided content to a specified file. It inherits from the generic Tool class.

SOURCE: https://docs.portialabs.ai/SDK/portia/open_source_tools/local_file_writer_tool

LANGUAGE: python
CODE:
```
class FileWriterTool(Tool[str])
```

----------------------------------------

TITLE: Tool Registry Combination (__radd__)
DESCRIPTION: Combines two ToolRegistry instances or a ToolRegistry with a list of Tools. Ensures tool IDs are unique across both to prevent errors.

SOURCE: https://docs.portialabs.ai/SDK/portia/tool_registry

LANGUAGE: python
CODE:
```
def __radd__(other: ToolRegistry | list[Tool]) -> ToolRegistry:
    """
    Return an aggregated tool registry combining two registries or a registry and tool list.
    Tool IDs must be unique across the two registries otherwise an error will be thrown.
    **Arguments** :
      * `other` _ToolRegistry_ - Another tool registry to be combined.
    **Returns** :
      * `ToolRegistry` - A new tool registry containing tools from both registries.
    """
    pass
```

----------------------------------------

TITLE: Python Weather Tool Usage
DESCRIPTION: Demonstrates how to import and use the open-source Weather Tool from the Portia SDK. It explains how to load tools into an InMemoryToolRegistry and combine them with other tools.

SOURCE: https://docs.portialabs.ai/portia-tools/open-source/weather

LANGUAGE: python
CODE:
```
from portia.open_source_tools.registry import open_source_tool_registry
from portia.tool_registry import InMemoryToolRegistry

# Load tools into a registry
registry = InMemoryToolRegistry()
registry.register_tools(open_source_tool_registry)

# Example of using the weather tool (assuming API key is set)
# weather_tool = registry.get_tool("weather_tool")
# result = weather_tool(city="London")
# print(result)
```

----------------------------------------

TITLE: Run Extract Tool
DESCRIPTION: Executes the extract tool to process a list of URLs. It allows configuration for image and favicon inclusion, extraction depth, and output format. The function returns the extracted data as a string.

SOURCE: https://docs.portialabs.ai/SDK/portia/open_source_tools/extract_tool

LANGUAGE: python
CODE:
```
def run(_: ToolRunContext, urls: list[str], include_images: bool = True, include_favicon: bool = True, extract_depth: str = "basic", format: str = "markdown") -> str:
```

----------------------------------------

TITLE: Custom Evaluator Function Signature
DESCRIPTION: Defines the signature for a custom evaluator function in SteelThread. This function receives test case details, plan information, and metadata to calculate evaluation metrics.

SOURCE: https://docs.portialabs.ai/evals-custom-evaluators

LANGUAGE: python
CODE:
```
from portia import Plan, PlanRun
from steelthread.evals import EvalTestCase, EvalMetric, PlanRunMetadata

def eval_test_case(
    self,
    test_case: EvalTestCase,
    final_plan: Plan,
    final_plan_run: PlanRun,
    additional_data: PlanRunMetadata,
)->list[EvalMetric]| EvalMetric |None:

```

========================
QUESTIONS AND ANSWERS
========================
TOPIC: Portia Tools Documentation
Q: What kind of tools are available within the Portia Tool Catalogue?
A: The Portia Tool Catalogue provides access to Open Source tools, Portia Cloud services, and Remote MCP solutions, enabling a wide range of automation and integration capabilities.


SOURCE: https://docs.portialabs.ai/portia-tools/local-mcp/playwright

----------------------------------------

TOPIC: Add Custom Tools - Portia Labs Docs
Q: How can custom tools be created in Portia?
A: Custom tools in Portia can be created by defining Python functions and decorating them with the `@tool` decorator. These functions can then be placed in a dedicated folder, such as `custom_tools`, within the project directory.


SOURCE: https://docs.portialabs.ai/add-custom-tools

----------------------------------------

TOPIC: Portia Tools Documentation
Q: What are some examples of tools available in the Local MCP category?
A: The Local MCP category provides tools for AWS Cost Analysis, AWS Documentation, Basic Memory, BioMCP, Bright Data, Browserbase, Chargebee, Chroma, DBHub, ElevenLabs, GCP Cloud Run, GitHub, Grafana, HubSpot, Hyperbrowser, and JetBrains IDE.


SOURCE: https://docs.portialabs.ai/portia-tools/portia-cloud/microsoft-outlook/outlook-send-draft-email

----------------------------------------

TOPIC: Extend and run tools - Portia AI Docs
Q: How can custom tools be created in Portia AI?
A: Custom tools in Portia AI can be created using the @tool decorator, which provides a straightforward method to build custom tools from Python functions. This allows LLMs to interact with local files for reading and writing content.


SOURCE: https://docs.portialabs.ai/extend-run-tools

----------------------------------------

TOPIC: Portia SDK - Tool Module
Q: How does the portia.tool module support extensibility for custom tools?
A: The tools in the portia.tool module are designed to be extendable. Users can create their own custom tools by inheriting from the base `Tool` class, leveraging the common functionality provided.


SOURCE: https://docs.portialabs.ai/SDK/portia/tool

----------------------------------------

TOPIC: Portia Tools Documentation
Q: What are some examples of tools available under the Local MCP category?
A: The Local MCP category includes tools for AWS Cost Analysis, AWS Documentation, Basic Memory, BioMCP, Bright Data, Browserbase, Chargebee, Chroma, DBHub, ElevenLabs, GCP Cloud Run, GitHub, Grafana, HubSpot, Hyperbrowser, and JetBrains IDE.


SOURCE: https://docs.portialabs.ai/portia-tools/portia-cloud/google-gmail/gmail-send-draft-email

----------------------------------------

TOPIC: Add Custom Tools - Portia Labs Docs
Q: What is the purpose of the `@tool` decorator in Portia?
A: The `@tool` decorator in Portia is used to convert Python functions into Portia tools. This provides a simple and straightforward way to create custom tools for use with the Portia framework.


SOURCE: https://docs.portialabs.ai/add-custom-tools

----------------------------------------

TOPIC: Portia Labs Documentation
Q: What types of tools does Portia offer within its catalogue?
A: Portia's tool catalogue is divided into Open Source tools and Remote MCP (Managed Compute Platform) tools, and Local MCP tools, covering a wide range of integrations and functionalities.


SOURCE: https://docs.portialabs.ai/portia-tools/portia-cloud/google-gmail/gmail-search-email

----------------------------------------

TOPIC: Use clarifications in custom tools - Portia Labs Docs
Q: What is the purpose of raising a `Clarification` in Portia custom tools?
A: Raising a `Clarification` in a custom tool definition prompts a plan run to interrupt itself. This interruption allows for soliciting input from the user or another process.


SOURCE: https://docs.portialabs.ai/clarifications-in-tools

----------------------------------------

TOPIC: Portia Tools Documentation
Q: What types of tools are available in Portia's Local MCP?
A: Portia's Local MCP provides tools for AWS Cost Analysis, AWS Documentation, Basic Memory, BioMCP, Bright Data, Browserbase, Chargebee, Chroma, DBHub, ElevenLabs, GCP Cloud Run, GitHub, Grafana, HubSpot, Hyperbrowser, JetBrains IDE, MiniMax, Monday.com, MongoDB, Netlify, Notion, and Perplexity.


SOURCE: https://docs.portialabs.ai/portia-tools/remote-mcp/cloudflare