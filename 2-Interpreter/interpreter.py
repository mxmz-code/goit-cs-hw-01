class TokenType:
    # Визначення типів токенів для арифметичних операцій та чисел
    INTEGER = "INTEGER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EOF = "EOF"


class Token:
    # Клас для представлення токенів (лексичних одиниць)
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f"Token({self.type}, {repr(self.value)})"


class Lexer:
    # Лексер (аналізатор), який розбиває введений текст на токени
    def __init__(self, text):
        self.text = text.replace(" ", "")  # Видаляємо пробіли
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        # Переміщуємо вказівник на наступний символ
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def integer(self):
        # Зчитуємо ціле число з тексту
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        # Генеруємо наступний токен у потоці
        while self.current_char is not None:
            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.integer())
            if self.current_char in "+-*/()":
                token_map = {
                    '+': TokenType.PLUS, '-': TokenType.MINUS,
                    '*': TokenType.MUL, '/': TokenType.DIV,
                    '(': TokenType.LPAREN, ')': TokenType.RPAREN
                }
                token = Token(token_map[self.current_char], self.current_char)
                self.advance()
                return token
            raise Exception(f"Помилка лексичного аналізу: невідомий символ '{self.current_char}'")
        return Token(TokenType.EOF, None)


class AST:
    # Базовий клас для абстрактного синтаксичного дерева (AST)
    pass


class BinOp(AST):
    # Вузол AST для бінарних операцій (арифметичних)
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class Num(AST):
    # Вузол AST для представлення чисел
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Parser:
    # Парсер (аналізатор), який будує AST з токенів
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        # Порівнює поточний токен з очікуваним і просуває далі
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f"Очікував {token_type}, але отримав {self.current_token.type}")

    def factor(self):
        # Обробляє числа та вирази у дужках
        token = self.current_token
        if token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return Num(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        raise Exception("Неправильний фактор")

    def term(self):
        # Обробляє множення та ділення
        node = self.factor()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def expr(self):
        # Обробляє додавання та віднімання
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.term())
        return node


class Interpreter:
    # Інтерпретатор, який виконує обчислення на основі AST
    def __init__(self, parser):
        self.parser = parser

    def visit(self, node):
        # Відвідує вузли AST
        if isinstance(node, Num):
            return node.value
        elif isinstance(node, BinOp):
            return self.visit_BinOp(node)
        raise Exception("Непідтримуваний тип оператора")

    def visit_BinOp(self, node):
        # Виконує обчислення для арифметичних операцій
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        if node.op.type == TokenType.PLUS:
            return left_value + right_value
        elif node.op.type == TokenType.MINUS:
            return left_value - right_value
        elif node.op.type == TokenType.MUL:
            return left_value * right_value
        elif node.op.type == TokenType.DIV:
            if right_value == 0:
                raise Exception("Ділення на нуль")
            return left_value // right_value  # Цілочисельне ділення

    def interpret(self):
        # Інтерпретує вираз
        tree = self.parser.expr()
        return self.visit(tree)


if __name__ == "__main__":
    # Основна програма: зчитує вираз, обробляє його і виводить результат
    while True:
        try:
            text = input("Введіть вираз (або 'exit' для виходу): ").strip()
            if text.lower() == "exit":
                break
            lexer = Lexer(text)
            parser = Parser(lexer)
            interpreter = Interpreter(parser)
            result = interpreter.interpret()
            print("Результат:", result)
        except Exception as e:
            print("Помилка виконання:", e)
