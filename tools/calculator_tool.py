def calculate_expression(expression):

    try:

        result = eval(expression)

        return str(result)

    except Exception:

        return "Invalid mathematical expression."