import numpy as np
from scipy import stats
from typing import Tuple

def generate_math_problem() -> Tuple[str, str]:
    # Define the types and subtypes of math problems
    problem_types = ["Algebra", "Geometry", "Calculus", "Statistics"]
    subtypes = {
        "Algebra": ["Linear Equations", "Quadratic Equations", "Polynomials"],
        "Geometry": ["Area", "Volume", "Angles"],
        "Calculus": ["Derivatives", "Integrals"],
        "Statistics": ["Mean", "Median", "Mode", "Standard Deviation"]
    }

    # Randomly select a problem type and subtype
    problem_type = np.random.choice(problem_types)
    subtype = np.random.choice(subtypes[problem_type])

    # Generate a problem and its solution based on the type and subtype
    if problem_type == "Algebra":
        if subtype == "Linear Equations":
            a, b = np.random.randint(1, 10, size=2)
            question = f"Solve for x: {a}x + {b} = 0"
            answer = f"x = {-b/a}"
        elif subtype == "Quadratic Equations":
            a, b, c = np.random.randint(1, 10, size=3)
            question = f"Solve for x: {a}x^2 + {b}x + {c} = 0"
            discriminant = b**2 - 4 * a * c
            if discriminant >= 0:
                root1 = (-b + np.sqrt(discriminant)) / (2 * a)
                root2 = (-b - np.sqrt(discriminant)) / (2 * a)
                answer = f"x = {root1}, {root2}"
            else:
                answer = "No real roots"
        elif subtype == "Polynomials":
            coeffs = np.random.randint(1, 10, size=3)
            question = f"Find the roots of the polynomial: {coeffs[0]}x^2 + {coeffs[1]}x + {coeffs[2]}"
            roots = np.roots(coeffs)
            answer = f"Roots: {roots}"

    elif problem_type == "Geometry":
        if subtype == "Area":
            length, width = np.random.randint(1, 20, size=2)
            question = f"Find the area of a rectangle with length {length} and width {width}"
            answer = f"Area = {length * width}"
        elif subtype == "Volume":
            radius = np.random.randint(1, 10)
            question = f"Find the volume of a sphere with radius {radius}"
            answer = f"Volume = {(4/3) * np.pi * radius**3}"
        elif subtype == "Angles":
            angle1 = np.random.randint(1, 180)
            question = f"Find the complement of an angle {angle1} degrees"
            answer = f"Complement = {90 - angle1} degrees"

    elif problem_type == "Calculus":
        if subtype == "Derivatives":
            coeff = np.random.randint(1, 10)
            question = f"Find the derivative of {coeff}x^2"
            answer = f"Derivative = {2 * coeff}x"
        elif subtype == "Integrals":
            coeff = np.random.randint(1, 10)
            question = f"Find the integral of {coeff}x"
            answer = f"Integral = {coeff/2}x^2 + C"

    elif problem_type == "Statistics":
        data = np.random.randint(1, 10000, size=10)
        if subtype == "Mean":
            question = f"Find the mean of the data set: {data}"
            answer = f"Mean = {np.mean(data)}"
        elif subtype == "Median":
            question = f"Find the median of the data set: {data}"
            answer = f"Median = {np.median(data)}"
        elif subtype == "Mode":
            mode = stats.mode(data, keepdims=True)
            question = f"Find the mode of the data set: {data}"
            answer = f"Mode = {mode.mode[0]} (appears {mode.count[0]} times)"
        elif subtype == "Standard Deviation":
            question = f"Find the standard deviation of the data set: {data}"
            answer = f"Standard Deviation = {np.std(data)}"

    print(question)
    print(answer)
    return question, answer

# Generate a random math problem
# question, answer = generate_math_problem()
# print("Question:", question)
# print("Answer:", answer)
