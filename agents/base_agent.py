from openai import OpenAI
from dotenv import load_dotenv
import os
from logs.logger import WorkflowLogger

from tools.tool_registry import TOOLS
import json


class BaseAgent:

    def __init__(self, name, system_prompt, tools=None):

        load_dotenv()

        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools or {}

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.memory = []

    def use_tools(self, user_message):

        user_message_lower = user_message.lower()

        for tool_name, tool_data in self.tools.items():

            keywords = tool_data["keywords"]

            if any(keyword in user_message_lower for keyword in keywords):

                WorkflowLogger.log(f"Tool Selected: {tool_name}")

                tool_function = tool_data["function"]

                if tool_name == "calculator":

                    expression = (
                        user_message_lower
                        .replace("calculate", "")
                        .replace("what is", "")
                        .strip()
                    )

                    result = tool_function(expression)

                else:

                    result = tool_function()

                WorkflowLogger.log(f"Tool Result: {result}")

                formatted_tool_name = tool_name.replace("_", " ").upper()

                return {
                    "status": "success",
                    "source": "tool",
                    "tool_name": tool_name,
                    "result": result
                }

        return None

    def chat(self, user_message):
        ##WorkflowLogger.log(f"User Input: {user_message}")

        tool_result = self.use_tools(user_message)

        if tool_result:

            self.memory.append({
                "role": "user",
                "content": user_message
            })

            self.memory.append({
                "role": "assistant",
                "content": json.dumps(tool_result)
            })

            return tool_result

            self.memory.append({
                "role": "user",
                "content": user_message
            })

            self.memory.append({
                "role": "assistant",
                "content": assistant_reply
            })

            ##WorkflowLogger.log("Tool Used: DateTime Tool")
            ##WorkflowLogger.log(f"Tool Result: {tool_result}")

            return assistant_reply

        self.memory.append({
            "role": "user",
            "content": user_message
        })

        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ] + self.memory

        try:

            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages
            )

            assistant_reply = response.choices[0].message.content

            ##WorkflowLogger.log(f"LLM Response: {assistant_reply}")

        except Exception as e:

            ##WorkflowLogger.error(f"Error occurred: {str(e)}")

            return {
                "status": "error",
                "message": str(e)
            }

        self.memory.append({
            "role": "assistant",
            "content": assistant_reply
        })
        ##WorkflowLogger.log(f"LLM Response: {assistant_reply}")
        return {
            "status": "success",
            "source": "llm",
            "response": assistant_reply
        }