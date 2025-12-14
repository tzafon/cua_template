from typing import Tuple


def get_coords(action):
    """Extract x, y from action - handles both {x: 1, y: 2} and {x: [1, 2]} formats."""
    if "y" in action:
        return action["x"], action["y"]
    elif isinstance(action.get("x"), list):
        return action["x"][0], action["x"][1]
    elif "coordinate" in action:
        return action["coordinate"][0], action["coordinate"][1]
    raise ValueError(f"Cannot extract coordinates from {action}")


def adjust_coordinates(
    viewport_width: int, viewport_height: int, x: int, y: int
) -> Tuple[int, int]:
    """Scale coordinates from 0-999 grid to actual viewport dimensions."""
    x_scale = viewport_width / 999
    y_scale = viewport_height / 999
    return int(x * x_scale), int(y * y_scale)


def execute_action(
    computer, action, viewport_width: int, viewport_height: int, screenshot: str
):
    """Execute an action on the computer and return True if should continue."""
    action_type = action.get("action")

    if action_type == "click":
        x, y = get_coords(action)
        x, y = adjust_coordinates(viewport_width, viewport_height, x, y)
        computer.click(x, y)
    elif action_type == "double_click":
        x, y = get_coords(action)
        x, y = adjust_coordinates(viewport_width, viewport_height, x, y)
        computer.double_click(x, y)
    elif action_type == "right_click":
        x, y = get_coords(action)
        x, y = adjust_coordinates(viewport_width, viewport_height, x, y)
        computer.right_click(x, y)
    elif action_type == "type":
        computer.type(action["text"])
    elif action_type == "hotkey":
        computer.hotkey(*action["keys"])
    elif action_type == "scroll":
        computer.scroll(dx=action.get("dx", 0), dy=action.get("dy", 0))
    elif action_type == "drag":
        from_x, from_y = adjust_coordinates(
            viewport_width, viewport_height, action["from_x"], action["from_y"]
        )
        to_x, to_y = adjust_coordinates(
            viewport_width, viewport_height, action["to_x"], action["to_y"]
        )
        computer.drag(from_x, from_y, to_x, to_y)
    elif action_type == "navigate":
        computer.navigate(action["url"])
    elif action_type == "wait":
        computer.wait(action.get("seconds", 1))
    elif action_type == "done":
        print(f"Task complete: {action.get('result', '')}")
        print(screenshot)
        return False
    else:
        print(f"Unknown action: {action_type}")

    return True
