import pathlib
import re
from math import sqrt

def ask(message):
    try:
        return input(message).strip()
    except EOFError:
        return ""


def ask_yes_no(message):
    while True:
        answer = ask(message + " (yes/no): ").lower()
        if answer == "yes" or answer == "y":
            return True
        if answer == "no" or answer == "n" or answer == "":
            return False
        print("Please type 'yes' or 'no'.")


def read_number(message):
    while True:
        text = ask(message)
        if text == "":
            return 0.0
        try:
            return float(text.replace(",", "."))
        except ValueError:
            print("'" + text + "' is not a valid number, please try again.")

def parse_line(line):
    if line.count("=") != 1:
        raise ValueError("the equation must contain exactly one '=' sign")

    left, right = line.split("=")
    left = left.strip()
    right = right.strip()

    if left == "":
        raise ValueError("the left side of the '=' sign is missing")

    try:
        b = float(right.replace(" ", "").replace(",", "."))
    except ValueError:
        raise ValueError("'" + right + "' on the right side of the '=' sign is not a number")

    rest = re.sub(r'([+-]?)\s*(\d*\.?\d*)\s*([a-zA-Z])', "", left).strip()
    if rest != "":
        raise ValueError("cannot understand the part '" + rest + "'")

    coefs = {}
    terms = re.findall(r'([+-]?)\s*(\d*\.?\d*)\s*([a-zA-Z])', left)

    for idx in range(len(terms)):
        sign, number, var = terms[idx]

        if idx > 0 and sign == "":
            raise ValueError("missing + or - before the term with '" + var + "'")

        if number == "":
            value = 1.0
        else:
            try:
                value = float(number)
            except ValueError:
                raise ValueError("the coefficient '" + number + "' is not a valid number")

        if sign == "-":
            value = -value

        if var in coefs:
            coefs[var] = coefs[var] + value
        else:
            coefs[var] = value

    return coefs, b


def show_system(equations, all_vars):
    header = "No".ljust(4)
    for var in all_vars:
        header = header + var.rjust(8)
    header = header + " |" + "B".rjust(8)
    print(header)
    print("-" * len(header))

    for i in range(len(equations)):
        coefs, b = equations[i]
        row = str(i + 1).ljust(4)
        for var in all_vars:
            if var in coefs:
                row = row + str(coefs[var]).rjust(8)
            else:
                row = row + ".".rjust(8)
        row = row + " |" + str(b).rjust(8)
        print(row)


def equation_text(coefs, b, all_vars):
    text = ""
    for var in all_vars:
        c = coefs.get(var, 0.0)
        if text == "":
            if c < 0:
                text = "-"
        elif c < 0:
            text = text + " - "
        else:
            text = text + " + "
        text = text + str(abs(c)) + var
    return text + " = " + str(b)


def load_system(path: pathlib.Path) -> tuple[list[list[float]], list[float]]:
    if not path.exists():
        print("The file '" + str(path) + "' does not exist.")
        return [], []
    if not path.is_file():
        print("'" + str(path) + "' is not a file.")
        return [], []

    lines = path.read_text(encoding="utf-8-sig").strip().splitlines()
    lines = [line.strip() for line in lines if line.strip()]

    if len(lines) == 0:
        print("The file is empty.")
        return [], []

    equations = []
    modified = False

    for nr in range(len(lines)):
        line = lines[nr]
        while True:
            try:
                coefs, b = parse_line(line)
                equations.append([coefs, b])
                break
            except ValueError as err:
                print()
                print("Error on line " + str(nr + 1) + ": " + line)
                print("  -> " + str(err))
                answer = ask("Type the correct equation (or press Enter to skip it): ")
                modified = True
                if answer == "":
                    print("The line was skipped.")
                    break
                line = answer

    if len(equations) == 0:
        print("No valid equation is left.")
        return [], []

    all_vars = []
    for coefs, b in equations:
        for var in coefs:
            if var not in all_vars:
                all_vars.append(var)

    print("System read:")
    show_system(equations, all_vars)

    missing = []
    for i in range(len(equations)):
        for var in all_vars:
            if var not in equations[i][0]:
                missing.append((i, var))

    if len(missing) > 0:
        print()
        print("Some equations do not contain all the variables (marked with '.' in the table):")
        for i, var in missing:
            print("  - equation " + str(i + 1) + " does not contain '" + var + "'")

        if ask_yes_no("Do you want to fill in the missing coefficients now? (otherwise they will be 0)"):
            for i, var in missing:
                equations[i][0][var] = read_number(
                    "  coefficient of " + var + " in equation " + str(i + 1) + " (Enter = 0): ")
            modified = True
        else:
            for i, var in missing:
                equations[i][0][var] = 0.0

    while len(equations) < len(all_vars):
        print()
        print("The system has " + str(len(equations)) + " equations, but " + str(len(all_vars))
              + " unknowns. " + str(len(all_vars) - len(equations)) + " equation(s) missing.")
        show_system(equations, all_vars)

        if not ask_yes_no("Do you want to add an equation now?"):
            break

        new_coefs = {}
        for var in all_vars:
            new_coefs[var] = read_number("  coefficient of " + var + " (Enter = 0): ")
        new_b = read_number("  free term (Enter = 0): ")

        last = len(equations) + 1
        position = last
        while True:
            text = ask("At which position should it go? (1-" + str(last) + ", Enter = at the end): ")
            if text == "":
                break
            if text.isdigit() and 1 <= int(text) <= last:
                position = int(text)
                break
            print("Type a number between 1 and " + str(last) + ".")

        equations.insert(position - 1, [new_coefs, new_b])
        print("Added: " + equation_text(new_coefs, new_b, all_vars))
        modified = True

    while len(equations) > len(all_vars):
        print()
        print("The system has " + str(len(equations)) + " equations, but only " + str(len(all_vars))
              + " unknowns.")
        show_system(equations, all_vars)

        text = ask("Which equation do you want to delete? (1-" + str(len(equations)) + ", Enter = keep them): ")
        if text == "":
            break
        if text.isdigit() and 1 <= int(text) <= len(equations):
            removed = equations.pop(int(text) - 1)
            print("Deleted: " + equation_text(removed[0], removed[1], all_vars))
            modified = True
        else:
            print("Invalid number.")

    if modified:
        print()
        print("Final system:")
        show_system(equations, all_vars)
        if ask_yes_no("Save the changes to the file?"):
            text = ""
            for coefs, b in equations:
                text = text + equation_text(coefs, b, all_vars) + "\n"
            path.write_text(text, encoding="utf-8")
            print("Saved.")

    A = []
    B = []
    for coefs, b in equations:
        row = []
        for var in all_vars:
            row.append(coefs[var])
        A.append(row)
        B.append(b)

    return A, B


A, B = load_system(pathlib.Path("system.txt"))
print()
print(f"Matrix A = {A}")
print(f"Vector B = {B}\n")

if len(A) == 0:
    print("There is no valid system, the program stops.")
    raise SystemExit

square = len(A) == len(A[0])
if not square:
    print("Warning: the matrix is not square, some calculations will be skipped.\n")

def check_matrix(matrix):
    if len(matrix) == 0 or len(matrix[0]) == 0:
        raise ValueError("The matrix is empty!")
    for row in matrix:
        if len(row) != len(matrix[0]):
            raise ValueError("The rows of the matrix do not have the same length!")

def determinant(matrix: list[list[float]]) -> float:
    check_matrix(matrix)
    n = len(matrix)
    m = len(matrix[0])

    if m != n:
        raise ValueError("The determinant exists only for square matrices!")

    if n == 1:
        return matrix[0][0]

    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

    det = 0.0
    for col in range(n):
        minor_matrix = [row[:col] + row[col + 1:] for row in matrix[1:]]

        cofactor_value = ((-1) ** col) * matrix[0][col] * determinant(minor_matrix)
        det += cofactor_value

    return det


if square:
    det_A = determinant(A)
    print(f"The determinant of matrix A is: {det_A}")

def trace(matrix: list[list[float]]) -> float:
    check_matrix(matrix)
    if len(matrix) != len(matrix[0]):
        raise ValueError("The trace exists only for square matrices!")
    return sum(matrix[i][i] for i in range(len(matrix)))

if square:
    print(f"{trace(A)=}")

def norm(vector: list[float]) -> float:
    if len(vector) == 0:
        raise ValueError("The vector has no elements!")
    return sqrt(sum(x ** 2 for x in vector))

print(f"{norm(B)=}")

def transpose(matrix: list[list[float]]) -> list[list[float]]:
    check_matrix(matrix)
    n = len(matrix)
    m = len(matrix[0])

    transposed = []

    for c in range(m):
        new_row = []
        for r in range(n):
            new_row.append(matrix[r][c])
        transposed.append(new_row)

    return transposed

print(f"{transpose(A)=}")

def multiply(matrix: list[list[float]], vector: list[float]) -> list[float]:
    check_matrix(matrix)
    if len(matrix[0]) != len(vector):
        raise ValueError("Cannot multiply: the number of columns of the matrix must be equal to the size of the vector!")

    result = []

    for row in matrix:
        current_sum = 0.0
        for i in range(len(row)):
            current_sum += row[i] * vector[i]

        result.append(current_sum)

    return result

if len(A[0]) == len(B):
    print(f"{multiply(A, B)=}")
else:
    print("A * B cannot be computed (different sizes).")

def solve_cramer(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(matrix)
    m = len(matrix[0]) if n > 0 else 0

    if n != m or n != len(vector):
        print("Warning: Cramer's rule requires a square matrix and sizes compatible with the vector!")
        return []

    det_matrix = determinant(matrix)

    if det_matrix == 0.0:
        print("The determinant is 0, the system does not have a unique solution!")
        return []

    solution = []

    for c in range(m):
        temp_matrix = [row.copy() for row in matrix]

        for r in range(n):
            temp_matrix[r][c] = vector[r]

        det_temp = determinant(temp_matrix)

        val = det_temp / det_matrix
        solution.append(val)

    return solution


print(f"{solve_cramer(A, B)=}")

def minor(matrix: list[list[float]], i: int, j: int) -> list[list[float]]:
    if i < 0 or i >= len(matrix) or j < 0 or j >= len(matrix[0]):
        raise ValueError("The indices i and j are outside the matrix!")

    result = []
    for r_idx, row in enumerate(matrix):
        if r_idx == i:
            continue
        new_row = []
        for c_idx, val in enumerate(row):
            if c_idx == j:
                continue
            new_row.append(val)
        result.append(new_row)
    return result


def cofactor(matrix: list[list[float]]) -> list[list[float]]:
    n = len(matrix)

    if n == 1:
        return [[1.0]]

    cof_matrix = []

    for i in range(n):
        row = []
        for j in range(n):
            m = minor(matrix, i, j)
            det_m = determinant(m)
            sign = (-1) ** (i + j)
            row.append(sign * det_m)
        cof_matrix.append(row)

    return cof_matrix


def adjoint(matrix: list[list[float]]) -> list[list[float]]:
    cof = cofactor(matrix)
    return transpose(cof)


def solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(matrix)
    if n == 0 or n != len(matrix[0]) or n != len(vector):
        print("Warning: the inverse requires a square matrix and sizes compatible with the vector!")
        return []

    det = determinant(matrix)

    if det == 0.0:
        print("The determinant is 0, the matrix cannot be inverted (there is no unique solution)!")
        return []

    adj = adjoint(matrix)
    mult_result = multiply(adj, vector)
    solution = [val / det for val in mult_result]

    return solution

print(f"{solve(A, B)=}")