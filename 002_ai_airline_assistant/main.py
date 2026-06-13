import json
from openai import OpenAI
import gradio as gr

class Tools:

    PRICE_FUNCTION = {
        "name": "get_ticket_price",
        "description": "Get the price of a return ticket to the destination city.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination_city": {
                    "type": "string",
                    "description": "The city that the customer wants to travel to",
                },
            },
            "required": ["destination_city"],
            "additionalProperties": False
        }
    }

    @staticmethod
    def get_ticket_price(destination_city):
        print(f"Tool called for city {destination_city}")
        ticket_prices = {"london": "$799", "paris": "$899", "tokyo": "$1400", "berlin": "$499"}
        price = ticket_prices.get(destination_city.lower(), "Unknown ticket price")
        return f"The price of a ticket to {destination_city} is {price}"

    @classmethod
    def get_tools(cls):
        return [
            {
                "type": "function",
                "function": cls.PRICE_FUNCTION
            }
        ]



class AirlineAssistant:
    
    def __init__(self):
        self.model = "qwen2.5:3b"
        self.openai = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")


    def get_system_message(self):
        return """
                You are a helpful assistant for an Airline called FlightAI.
                Give short, courteous answers, no more than 1 sentence.
                Always be accurate. If you don't know the answer, say so.
                """
    
    def handle_tool_call(self,message):
        tool_call = message.tool_calls[0]
        if tool_call.function.name == "get_ticket_price":
            arguments = json.loads(tool_call.function.arguments)
            city = arguments.get('destination_city')
            price_details =  Tools.get_ticket_price(city)
            response = {
                "role": "tool",
                "content": price_details,
                "tool_call_id": tool_call.id
            }
        return response

    def chat(self,message, history):
        history = [{"role":h["role"], "content":h["content"]} for h in history]
        messages = [{"role": "system", "content": self.get_system_message()}] + history + [{"role": "user", "content": message}]
        response = self.openai.chat.completions.create(model=self.model, messages=messages, tools=Tools.get_tools())

        if response.choices[0].finish_reason=="tool_calls":
            message = response.choices[0].message
            response = self.handle_tool_call(message)
            messages.append(message)
            messages.append(response)
            response = self.openai.chat.completions.create(model=self.model, messages=messages)


        return response.choices[0].message.content
    
    def launch_assistant(self):
        gr.ChatInterface(fn=self.chat).launch()


if __name__ == "__main__":
    assistant = AirlineAssistant()
    assistant.launch_assistant()

