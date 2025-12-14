import json
from core.clients import llm_client, client
from core.prompts import SYSTEM_PROMPT

from core.utils import execute_action


def agent_loop(
    task: str, start_url: str = "https://wikipedia.com", max_steps: int = 10
):
    with client.create(kind="browser") as computer:
        computer.navigate(start_url)
        computer.wait(1)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        for step in range(max_steps):
            screenshot = computer.screenshot()
            screenshot_url = screenshot.result["screenshot_url"]
            viewport_width = screenshot.page_context.viewport_width
            viewport_height = screenshot.page_context.viewport_height

            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Task: {task}\n\nViewport: {viewport_width}x{viewport_height}\n\nCurrent screenshot:",
                        },
                        {"type": "image_url", "image_url": {"url": screenshot_url}},
                    ],
                }
            )

            response = llm_client.chat.completions.create(
                model="tzafon.northstar.cua.sft",
                messages=messages,
            )

            response_text = response.choices[0].message.content
            print(f"Step {step + 1}: {response_text}")

            messages.append({"role": "assistant", "content": response_text})

            try:
                action = json.loads(response_text)
            except json.JSONDecodeError:
                print(f"Failed to parse JSON: {response_text}")
                break

            if not execute_action(
                computer, action, viewport_width, viewport_height, screenshot_url
            ):
                break

            computer.wait(0.5)


def main():
    agent_loop("Change the language to Spanish")


if __name__ == "__main__":
    main()
