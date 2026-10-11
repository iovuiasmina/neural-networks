import pathlib
import re
from math import sqrt

def load_system(path: pathlib.Path) -> tuple[list[list[float]], list[float]]:
    lines = path.read_text().strip().splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    
    all_vars = []
    for line in lines:
        left, _ = line.split("=")
        found_vars = re.findall(r'[a-zA-Z]', left)
        for v in found_vars:
            if v not in all_vars:
                all_vars.append(v)
                
    A = []
    B = []
    
    for line in lines:
        left, right = line.split("=")
        B.append(float(right.strip()))
        
        row = []
        for var in all_vars:
            pattern = rf'([+-]?\s*\d*\.?\d*)\s*{var}'
            
            match = re.search(pattern, left)
            
            if match:
                val_str = match.group(1).replace(" ", "")
                
                if val_str == '' or val_str == '+':
                    coef = 1.0   
                elif val_str == '-':
                    coef = -1.0  
                else:
                    coef = float(val_str)
                row.append(coef)
            else:
                row.append(0.0)
                
        A.append(row)
        
    return A, B


A, B = load_system(pathlib.Path("system.txt"))
print(f"Matricea A = {A}")
print(f"Vectorul B = {B}\n")


def determinant(matrix: list[list[float]]) -> float:
    n = len(matrix)
    m = len(matrix) if n > 0 else 0

    if m != n:
        return 0.0    
    if n == 1:
        return matrix[0][0]
    
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    
    det = 0.0
    for col in range(n):
        minor = [row[:col] + row[col+1:] for row in matrix[1:]]
        
        cofactor = ((-1) ** col) * matrix[0][col] * determinant(minor)
        det += cofactor
        
    return det

det_A = determinant(A)
print(f"Determinantul matricei A este: {det_A}")

def trace(matrix: list[list[float]]) -> float:
    return sum(matrix[i][i] for i in range(len(matrix)))

print(f"{trace(A)=}")


def norm(vector: list[float]) -> float:
    return sqrt(sum(x ** 2 for x in vector))

print(f"{norm(B)=}")

def transpose(matrix: list[list[float]]) -> list[list[float]]:
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
    if len(matrix[0]) != len(vector):
        raise ValueError("Nu se pot inmulti: numarul de coloane ale matricei trebuie sa fie egal cu dimensiunea vectorului!")
        
    result = []
    
    for row in matrix:
        current_sum = 0.0
        for i in range(len(row)):
            current_sum += row[i] * vector[i]
            
        result.append(current_sum)
        
    return result

print(f"{multiply(A, B)=}")

def solve_cramer(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(matrix)
    m = len(matrix[0]) if n > 0 else 0
    
    if n != m or n != len(vector):
        print("Atentie: Regula lui Cramer necesita o matrice patratica si dimensiuni compatibile cu vectorul!")
        return []
        
    det_matrix = determinant(matrix)
    
    if det_matrix == 0.0:
        print("Determinantul este 0, sistemul nu are solutie unica!")
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
    cof_matrix = []
    
    # Parcurgem fiecare element al matricei pentru a-i calcula cofactorul
    for i in range(n):
        row = []
        for j in range(n):
            # 1. Calculam minorul pentru pozitia (i, j)
            m = minor(matrix, i, j)
            # 2. Calculam determinantul minorului
            det_m = determinant(m)
            # 3. Aplicam semnul alternant (-1)^(i+j)
            sign = (-1) ** (i + j)
            row.append(sign * det_m)
        cof_matrix.append(row)
        
    return cof_matrix


def adjoint(matrix: list[list[float]]) -> list[list[float]]:
    # Matricea adjuncta este transpusa matricei cofactorilor
    cof = cofactor(matrix)
    return transpose(cof)


def solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    # 1. Calculam determinantul matricei principale
    det = determinant(matrix)
    
    if det == 0.0:
        print("Determinantul este 0, matricea nu poate fi inversata (nu exista solutie unica)!")
        return []
        
    # 2. Obtinem matricea adjuncta
    adj = adjoint(matrix)
    
    # 3. inmultim adjuncta cu vectorul B (folosind functia noastra de multiply)
    mult_result = multiply(adj, vector)
    
    # 4. impartim rezultatul la determinant (X = (1 / det) * adj * B)
    solution = [val / det for val in mult_result]
    
    return solution

# Apelul functiei finale de rezolvare prin inversare
print(f"{solve(A, B)=}")