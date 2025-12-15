import json
import os
from pathlib import Path
from urllib.request import urlretrieve
from core.clients import llm_client, client
from core.prompts import SYSTEM_PROMPT
from core.workflow import get_thinkpad_workflow_instructions, extract_result_info

from core.utils import execute_action


def agent_loop(
    task: str, start_url: str = "https://www.lenovo.com/us/en/configurator/cto/index.html?bundleId=21NXCTO1WWUS1", max_steps: int = 100
):
    if not start_url.startswith(("http://", "https://")):
        start_url = f"https://{start_url}"
    
    try:
        session = client.create(kind="browser")
        session_id = session.id
    except Exception as e:
        print(f"Failed to create browser session: {e}")
        return
    
    screenshots_dir = Path("screenshots") / session_id
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    print(f"Saving screenshots to: {screenshots_dir}")
    
    try:
        with session as computer:
            nav_result = computer.navigate(start_url)
            if nav_result.status != "SUCCESS":
                print(f"Failed to navigate to {start_url}: {nav_result.status}")
                if nav_result.error_message:
                    print(f"Error message: {nav_result.error_message}")
                return
            
            computer.wait(3)

            # Add workflow instructions if this is a ThinkPad configuration task
            system_prompt = SYSTEM_PROMPT
            if "thinkpad" in task.lower() or "x1" in task.lower():
                workflow_instructions = get_thinkpad_workflow_instructions(task)
                system_prompt = SYSTEM_PROMPT + workflow_instructions

            messages = [{"role": "system", "content": system_prompt}]

            for step in range(max_steps):
                screenshot = computer.screenshot()
                
                if screenshot.result is None:
                    print(f"Error: Screenshot result is None")
                    if screenshot.error_message:
                        print(f"Error message: {screenshot.error_message}")
                    print(f"Screenshot status: {screenshot.status}")
                    break
                
                if screenshot.status != "SUCCESS":
                    print(f"Error: Screenshot status is {screenshot.status}")
                    if screenshot.error_message:
                        print(f"Error message: {screenshot.error_message}")
                    break
                
                screenshot_url = screenshot.result["screenshot_url"]
                viewport_width = screenshot.page_context.viewport_width
                viewport_height = screenshot.page_context.viewport_height
                
                screenshot_path = screenshots_dir / f"step_{step + 1:03d}.jpeg"
                try:
                    urlretrieve(screenshot_url, screenshot_path)
                    print(f"Saved screenshot: {screenshot_path}")
                except Exception as e:
                    print(f"Failed to save screenshot: {e}")

                # Note: HTML/clickable element extraction is not currently available via Tzafon API
                # The agent uses visual analysis from screenshots only
                # Bbox utilities are available for future use if HTML extraction becomes available
                clickable_elements_text = ""

                task_text = f"Task: {task}\n\nViewport: {viewport_width}x{viewport_height}\n"
                if clickable_elements_text:
                    task_text += clickable_elements_text
                task_text += "\nCurrent screenshot:"

                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": task_text,
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

                action_result = execute_action(
                    computer, action, viewport_width, viewport_height, screenshot_url
                )
                
                if not action_result:
                    # Task completed - extract and display results
                    if action.get("action") == "done":
                        result_text = action.get("result", "")
                        print(f"\n{'='*60}")
                        print("TASK COMPLETED")
                        print(f"{'='*60}")
                        print(f"Result: {result_text}\n")
                        
                        # Extract structured information
                        result_info = extract_result_info(result_text)
                        print("EXTRACTED INFORMATION:")
                        print(f"  Status: {result_info['status']}")
                        if result_info.get('price'):
                            print(f"  Price: ${result_info['price']:,.2f}")
                        if result_info.get('quantity'):
                            print(f"  Quantity: {result_info['quantity']}")
                        if result_info.get('unit_price'):
                            print(f"  Unit Price: ${result_info['unit_price']:,.2f}")
                        if result_info.get('total_price'):
                            print(f"  Total Price: ${result_info['total_price']:,.2f}")
                        print(f"{'='*60}\n")
                    break

                computer.wait(0.5)
    except Exception as e:
        print(f"Unexpected error during agent loop: {e}")
        import traceback
        traceback.print_exc()


def main():
    agent_loop("500 ThinkPad X1 Carbons, 32GB RAM, 1TB SSD, 3-year warranty for healthcare customer in Texas")


if __name__ == "__main__":
    main()
