# https://github.com/tsdata/pymcp 판다스스튜디오에서 만든 패키지지
# pip install pymcp

from pymcp import PyMCP

def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    if b == 0:
        return "Cannot divide by zero"
    return a / b

# Combine multiple functions into one server
# PyMCP 서버 객체를 만들어서 함수를 추가하는 형태로 관리
calculator = PyMCP(name="Calculator Server", instructions="A server providing calculator functions")
calculator.add_function(add)
calculator.add_function(multiply)
calculator.add_function(divide)

# Run the server
calculator.run() 