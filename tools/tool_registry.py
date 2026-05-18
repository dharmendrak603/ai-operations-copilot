from tools.date_tool import get_current_datetime
from tools.calculator_tool import calculate_expression

TOOLS = {
    "date_time": {
        "keywords": ["date", "time"],
        "function": get_current_datetime
    },
    "calculator": {
        "keywords": ["calculate", "+", "-", "*", "/"],
        "function": calculate_expression
    }
}