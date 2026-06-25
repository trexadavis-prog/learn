# -*- coding: utf-8 -*-
import ast
import sys
import inspect
import io
import builtins
import random

def get_user_code():
    try:
        with open(sys.argv[0], "r", encoding="utf-8") as f:
            content = f.read()
        if "# --- AUTOMATED TESTS ---" in content:
            return content.split("# --- AUTOMATED TESTS ---")[0]
        return content
    except Exception:
        return ""

def verify_no_hardcoding(code, target_var, required_vars):
    tree = ast.parse(code)
    found_target = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == target_var:
                    found_target = True
                    rhs_names = {n.id for n in ast.walk(node.value) if isinstance(n, ast.Name)}
                    for req in required_vars:
                        if req not in rhs_names:
                            raise AssertionError(f"Assignment to '{target_var}' must reference variable '{req}'. Don't hardcode the result!")
                    if isinstance(node.value, ast.Constant):
                        raise AssertionError(f"Assignment to '{target_var}' cannot be a hardcoded constant.")
    if not found_target:
        raise AssertionError(f"Variable '{target_var}' is not assigned in the code.")

def verify_fstring_or_format(code, target_var, required_vars):
    tree = ast.parse(code)
    found_target = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == target_var:
                    found_target = True
                    val = node.value
                    
                    is_formatted = False
                    if isinstance(val, ast.JoinedStr):
                        is_formatted = True
                    elif isinstance(val, ast.Call) and isinstance(val.func, ast.Attribute) and val.func.attr == "format":
                        is_formatted = True
                    elif isinstance(val, ast.BinOp) and isinstance(val.op, ast.Mod):
                        is_formatted = True
                    elif isinstance(val, ast.BinOp) and isinstance(val.op, ast.Add):
                        is_formatted = True
                        
                    if not is_formatted:
                        raise AssertionError(f"Assignment to '{target_var}' must use string formatting or concatenation rather than static text.")
                        
                    rhs_names = {n.id for n in ast.walk(val) if isinstance(n, ast.Name)}
                    for req in required_vars:
                        if req not in rhs_names:
                            raise AssertionError(f"String formatting/concatenation for '{target_var}' must reference variable '{req}'.")
    if not found_target:
        raise AssertionError(f"Variable '{target_var}' is not assigned in the code.")

def verify_list_methods(code, target_var, required_methods):
    tree = ast.parse(code)
    found_methods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == target_var:
                found_methods.add(node.func.attr)
    for method in required_methods:
        if method not in found_methods:
            raise AssertionError(f"Expected to call '.{method}()' on list '{target_var}'.")

def verify_dict_lookup(code, target_var, dict_var, key):
    tree = ast.parse(code)
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == target_var:
                    val = node.value
                    if isinstance(val, ast.Subscript):
                        if isinstance(val.value, ast.Name) and val.value.id == dict_var:
                            slice_node = val.slice
                            if hasattr(ast, 'Index') and isinstance(slice_node, ast.Index):
                                slice_node = slice_node.value
                            if isinstance(slice_node, ast.Constant) and slice_node.value == key:
                                found = True
                            elif isinstance(slice_node, ast.Str) and slice_node.s == key:
                                found = True
                    elif isinstance(val, ast.Call) and isinstance(val.func, ast.Attribute):
                        if isinstance(val.func.value, ast.Name) and val.func.value.id == dict_var and val.func.attr == "get":
                            if len(val.args) >= 1:
                                arg0 = val.args[0]
                                if isinstance(arg0, ast.Constant) and arg0.value == key:
                                    found = True
                                elif isinstance(arg0, ast.Str) and arg0.s == key:
                                    found = True
    if not found:
        raise AssertionError(f"Expected variable '{target_var}' to be assigned the lookup of key '{key}' from dictionary '{dict_var}'.")

def verify_set_intersection(code, target_var, set_a, set_b):
    tree = ast.parse(code)
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == target_var:
                    val = node.value
                    if isinstance(val, ast.Call) and isinstance(val.func, ast.Attribute):
                        if isinstance(val.func.value, ast.Name) and val.func.value.id in (set_a, set_b) and val.func.attr == "intersection":
                            if len(val.args) >= 1 and isinstance(val.args[0], ast.Name) and val.args[0].id in (set_a, set_b):
                                found = True
                    elif isinstance(val, ast.BinOp) and isinstance(val.op, ast.BitAnd):
                        if isinstance(val.left, ast.Name) and val.left.id in (set_a, set_b):
                            if isinstance(val.right, ast.Name) and val.right.id in (set_a, set_b):
                                found = True
    if not found:
        raise AssertionError(f"Expected to calculate '{target_var}' using set intersection (.intersection() or &) between '{set_a}' and '{set_b}'.")

def verify_has_loops(code):
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            return
    raise AssertionError("Your code should use a loop (for or while) to repeat tasks.")

def verify_has_while_loop(code):
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.While):
            return
    raise AssertionError("Your code should use a while loop to repeat tasks.")

# Module 1
def check_m1_ex1_normal(g):
    assert 'student_name' in g, "Variable 'student_name' is missing."
    assert 'hours_studied' in g, "Variable 'hours_studied' is missing."
    assert g['student_name'] == "Alex", "student_name should be 'Alex'."
    assert g['hours_studied'] == 4, "hours_studied should be 4."

def check_m1_ex1_variant(g):
    assert 'employee_name' in g, "Variable 'employee_name' is missing."
    assert 'years_service' in g, "Variable 'years_service' is missing."
    assert g['employee_name'] == "Sarah", "employee_name should be 'Sarah'."
    assert g['years_service'] == 5, "years_service should be 5."

def check_m1_ex2_normal(g, code):
    assert 'base_salary' in g, "Variable 'base_salary' is missing."
    assert 'bonus' in g, "Variable 'bonus' is missing."
    assert 'total_pay' in g, "Variable 'total_pay' is missing."
    assert g['base_salary'] == 1200, "base_salary should be 1200."
    assert g['bonus'] == 350, "bonus should be 350."
    assert g['total_pay'] == 1550, "total_pay should be 1550."
    verify_no_hardcoding(code, 'total_pay', ['base_salary', 'bonus'])

def check_m1_ex2_variant(g, code):
    assert 'rent' in g, "Variable 'rent' is missing."
    assert 'utilities' in g, "Variable 'utilities' is missing."
    assert 'total_expenses' in g, "Variable 'total_expenses' is missing."
    assert g['rent'] == 800, "rent should be 800."
    assert g['utilities'] == 150, "utilities should be 150."
    assert g['total_expenses'] == 950, "total_expenses should be 950."
    verify_no_hardcoding(code, 'total_expenses', ['rent', 'utilities'])

def check_m1_ex3_normal(g, code):
    assert 'city' in g, "Variable 'city' is missing."
    assert 'country' in g, "Variable 'country' is missing."
    assert 'travel_message' in g, "Variable 'travel_message' is missing."
    assert g['city'] == "Paris", "city should be 'Paris'."
    assert g['country'] == "France", "country should be 'France'."
    assert g['travel_message'] == "I want to visit Paris, France.", "travel_message is incorrect."
    verify_fstring_or_format(code, 'travel_message', ['city', 'country'])

def check_m1_ex3_variant(g, code):
    assert 'movie' in g, "Variable 'movie' is missing."
    assert 'genre' in g, "Variable 'genre' is missing."
    assert 'movie_message' in g, "Variable 'movie_message' is missing."
    assert g['movie'] == "Toy Story", "movie should be 'Toy Story'."
    assert g['genre'] == "Animation", "genre should be 'Animation'."
    assert g['movie_message'] == "The movie Toy Story is in the Animation genre.", "movie_message is incorrect."
    verify_fstring_or_format(code, 'movie_message', ['movie', 'genre'])

def check_m1_ex4_normal(g, code):
    assert 'total_slices' in g, "Variable 'total_slices' is missing."
    assert 'slices_per_person' in g, "Variable 'slices_per_person' is missing."
    assert 'leftover_slices' in g, "Variable 'leftover_slices' is missing."
    assert g['total_slices'] == 15, "total_slices should be 15."
    assert g['slices_per_person'] == 3, "slices_per_person should be 3."
    assert g['leftover_slices'] == 3, "leftover_slices should be 3."
    verify_no_hardcoding(code, 'slices_per_person', ['total_slices'])
    verify_no_hardcoding(code, 'leftover_slices', ['total_slices'])

def check_m1_ex4_variant(g, code):
    assert 'total_candies' in g, "Variable 'total_candies' is missing."
    assert 'candies_per_child' in g, "Variable 'candies_per_child' is missing."
    assert 'leftover_candies' in g, "Variable 'leftover_candies' is missing."
    assert g['total_candies'] == 22, "total_candies should be 22."
    assert g['candies_per_child'] == 4, "candies_per_child should be 4."
    assert g['leftover_candies'] == 2, "leftover_candies should be 2."
    verify_no_hardcoding(code, 'candies_per_child', ['total_candies'])
    verify_no_hardcoding(code, 'leftover_candies', ['total_candies'])

# Module 2
class VariableRemover(ast.NodeTransformer):
    def __init__(self, var_name):
        self.var_name = var_name
    def visit_Assign(self, node):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == self.var_name:
            return None
        return node

def check_m2_ex1_normal(g, code):
    assert 'number' in g, "Variable 'number' is missing."
    assert 'classification' in g, "Variable 'classification' is missing."
    
    assert g['number'] == -7.5, "Keep number set to -7.5."
    assert g['classification'] == "negative", "classification should be 'negative' for -7.5."
    
    tree = ast.parse(code)
    new_tree = VariableRemover('number').visit(tree)
    ast.fix_missing_locations(new_tree)
    compiled = compile(new_tree, filename="<string>", mode="exec")
    
    # Test positive
    g_pos = {"number": 10.5}
    exec(compiled, g_pos)
    assert g_pos.get('classification') == "positive", "Your logic returned incorrect classification for positive numbers (e.g. 10.5)."
    
    # Test negative
    g_neg = {"number": -2}
    exec(compiled, g_neg)
    assert g_neg.get('classification') == "negative", "Your logic returned incorrect classification for negative numbers (e.g. -2)."
    
    # Test zero
    g_zero = {"number": 0}
    exec(compiled, g_zero)
    assert g_zero.get('classification') == "zero", "Your logic returned incorrect classification for zero (0)."

def check_m2_ex1_variant(g, code):
    assert 'score' in g, "Variable 'score' is missing."
    assert 'result_status' in g, "Variable 'result_status' is missing."
    
    assert g['score'] == 85, "Keep score set to 85."
    assert g['result_status'] == "pass", "result_status should be 'pass' for 85."
    
    tree = ast.parse(code)
    new_tree = VariableRemover('score').visit(tree)
    ast.fix_missing_locations(new_tree)
    compiled = compile(new_tree, filename="<string>", mode="exec")
    
    # Test pass border cases
    for s in [60, 100, 85]:
        g_test = {"score": s}
        exec(compiled, g_test)
        assert g_test.get('result_status') == "pass", f"Your logic returned incorrect status for score {s} (expected 'pass')."
        
    # Test fail border cases
    for s in [0, 59, 30]:
        g_test = {"score": s}
        exec(compiled, g_test)
        assert g_test.get('result_status') == "fail", f"Your logic returned incorrect status for score {s} (expected 'fail')."
        
    # Test error cases
    for s in [-5, 101, 150]:
        g_test = {"score": s}
        exec(compiled, g_test)
        assert g_test.get('result_status') == "error", f"Your logic returned incorrect status for score {s} (expected 'error')."

def check_m2_ex2_normal(g, code):
    assert 'results' in g, "Variable 'results' is missing."
    assert g['results'] == [10, 20, 30, 40, 50, 60, 70, 80, 90, 100], "results list is incorrect."
    verify_has_loops(code)

def check_m2_ex2_variant(g, code):
    assert 'squares' in g, "Variable 'squares' is missing."
    assert g['squares'] == [1, 4, 9, 16, 25], "squares list is incorrect."
    verify_has_loops(code)

def check_m2_ex3_normal(g, code):
    assert 'charge' in g, "Variable 'charge' is missing."
    assert 'ticks' in g, "Variable 'ticks' is missing."
    assert g['charge'] >= 100, "Battery should be fully charged (>= 100)."
    assert g['ticks'] == 7, "ticks should be 7."
    verify_has_while_loop(code)

def check_m2_ex3_variant(g, code):
    assert 'distance' in g, "Variable 'distance' is missing."
    assert 'steps' in g, "Variable 'steps' is missing."
    assert g['distance'] >= 80, "distance should reach at least 80."
    assert g['steps'] == 7, "steps should be 7."
    verify_has_while_loop(code)

# Module 3
def check_m3_ex1_normal(g, code):
    assert 'shopping_list' in g, "Variable 'shopping_list' is missing."
    assert 'list_length' in g, "Variable 'list_length' is missing."
    assert "milk" not in g['shopping_list'], "milk should be removed from shopping_list."
    assert "eggs" in g['shopping_list'], "eggs should be added to shopping_list."
    assert g['shopping_list'] == ["apples", "bread", "eggs"], "shopping_list items or order is incorrect."
    assert g['list_length'] == 3, "list_length should be 3."
    verify_list_methods(code, 'shopping_list', ['append', 'remove'])

def check_m3_ex1_variant(g, code):
    assert 'todo_list' in g, "Variable 'todo_list' is missing."
    assert 'todo_length' in g, "Variable 'todo_length' is missing."
    assert "study" not in g['todo_list'], "study should be removed from todo_list."
    assert "read" in g['todo_list'], "read should be added to todo_list."
    assert g['todo_list'] == ["clean", "exercise", "read"], "todo_list items or order is incorrect."
    assert g['todo_length'] == 3, "todo_length should be 3."
    verify_list_methods(code, 'todo_list', ['append', 'remove'])

def check_m3_ex2_normal(g, code):
    assert 'inventory' in g, "Variable 'inventory' is missing."
    assert 'bananas_qty' in g, "Variable 'bananas_qty' is missing."
    assert g['inventory'].get('apples') == 12, "apples should be 12 in inventory."
    assert g['inventory'].get('oranges') == 5, "oranges should be 5 in inventory."
    assert g['inventory'].get('bananas') == 15, "bananas should be 15 in inventory."
    assert g['bananas_qty'] == 15, "bananas_qty should be 15."
    verify_dict_lookup(code, 'bananas_qty', 'inventory', 'bananas')

def check_m3_ex2_variant(g, code):
    assert 'prices' in g, "Variable 'prices' is missing."
    assert 'cheese_cost' in g, "Variable 'cheese_cost' is missing."
    assert g['prices'].get('milk') == 3.50, "milk price should be 3.50."
    assert g['prices'].get('bread') == 2.20, "bread price should be 2.20."
    assert g['prices'].get('cheese') == 4.80, "cheese price should be 4.80."
    assert g['cheese_cost'] == 4.80, "cheese_cost should be 4.80."
    verify_dict_lookup(code, 'cheese_cost', 'prices', 'cheese')

def check_m3_ex3_normal(g, code):
    assert 'alice_set' in g, "alice_set is missing."
    assert 'bob_set' in g, "bob_set is missing."
    assert 'shared_colors' in g, "shared_colors is missing."
    assert g['alice_set'] == {"blue", "green", "red"}, "alice_set is incorrect."
    assert g['bob_set'] == {"green", "yellow", "blue"}, "bob_set is incorrect."
    assert g['shared_colors'] == {"blue", "green"}, "shared_colors should contain blue and green."
    verify_set_intersection(code, 'shared_colors', 'alice_set', 'bob_set')

def check_m3_ex3_variant(g, code):
    assert 'set_a' in g, "set_a is missing."
    assert 'set_b' in g, "set_b is missing."
    assert 'shared_members' in g, "shared_members is missing."
    assert g['set_a'] == {"cat", "dog", "bird"}, "set_a is incorrect."
    assert g['set_b'] == {"dog", "fish", "cat"}, "set_b is incorrect."
    assert g['shared_members'] == {"cat", "dog"}, "shared_members should contain cat and dog."
    verify_set_intersection(code, 'shared_members', 'set_a', 'set_b')

# Module 4
def check_m4_ex1_normal(g):
    assert 'to_celsius' in g, "to_celsius function is missing."
    func = g['to_celsius']
    assert callable(func), "to_celsius should be a function."
    assert func(32) == 0.0, "to_celsius(32) should return 0.0."
    assert func(212) == 100.0, "to_celsius(212) should return 100.0."
    assert func(50) == 10.0, "to_celsius(50) should return 10.0."
    assert func(-40) == -40.0, "to_celsius(-40) should return -40.0."

def check_m4_ex1_variant(g):
    assert 'inches_to_cm' in g, "inches_to_cm function is missing."
    func = g['inches_to_cm']
    assert callable(func), "inches_to_cm should be a function."
    assert func(0) == 0.0, "inches_to_cm(0) should return 0.0."
    assert func(1) == 2.54, "inches_to_cm(1) should return 2.54."
    assert func(10) == 25.4, "inches_to_cm(10) should return 25.4."
    assert func(5) == 12.7, "inches_to_cm(5) should return 12.7."

def check_m4_ex2_normal(g):
    assert 'power' in g, "power function is missing."
    func = g['power']
    assert callable(func), "power should be a function."
    assert func(3) == 9, "power(3) should default to 3^2 = 9."
    assert func(2, 3) == 8, "power(2, 3) should return 8."
    assert func(5, 0) == 1, "power(5, 0) should return 1."
    
    sig = inspect.signature(func)
    assert 'exponent' in sig.parameters, "power function should have parameter 'exponent'."
    assert sig.parameters['exponent'].default == 2, "exponent parameter must have a default value of 2."

def check_m4_ex2_variant(g):
    assert 'multiply' in g, "multiply function is missing."
    func = g['multiply']
    assert callable(func), "multiply should be a function."
    assert func(3) == 15, "multiply(3) should default to 3 * 5 = 15."
    assert func(4, 2) == 8, "multiply(4, 2) should return 8."
    assert func(0, 10) == 0, "multiply(0, 10) should return 0."
    
    sig = inspect.signature(func)
    assert 'b' in sig.parameters, "multiply function should have parameter 'b'."
    assert sig.parameters['b'].default == 5, "parameter 'b' must have a default value of 5."

def check_m4_ex3_normal(g):
    assert 'can_ride' in g, "can_ride function is missing."
    func = g['can_ride']
    assert callable(func), "can_ride should be a function."
    assert func(50, 10) is True, "Height 50, Age 10 should return True."
    assert func(48, 8) is True, "Height 48, Age 8 should return True."
    assert func(47, 9) is False, "Height 47, Age 9 should return False (too short)."
    assert func(49, 7) is False, "Height 49, Age 7 should return False (too young)."
    assert func(40, 5) is False, "Height 40, Age 5 should return False."

def check_m4_ex3_variant(g):
    assert 'can_vote' in g, "can_vote function is missing."
    func = g['can_vote']
    assert callable(func), "can_vote should be a function."
    assert func(True, 20) is True, "Registered and 20 years old should return True."
    assert func(True, 18) is True, "Registered and 18 years old should return True."
    assert func(False, 25) is False, "Not registered should return False."
    assert func(True, 17) is False, "Registered but 17 years old should return False (too young)."
    assert func(False, 16) is False, "Not registered and 16 years old should return False."

# Module 5
def check_m5_ex1_normal(code):
    original_randint = random.randint
    random.randint = lambda a, b: 25
    
    inputs = ["10", "40", "25"]
    input_index = 0
    
    def mock_input(prompt=""):
        nonlocal input_index
        if input_index < len(inputs):
            val = inputs[input_index]
            input_index += 1
            return val
        return "25"
        
    original_input = builtins.input
    builtins.input = mock_input
    
    stdout_capture = io.StringIO()
    sys.stdout = stdout_capture
    
    try:
        exec(code, {"__name__": "__main__", "random": random})
    finally:
        sys.stdout = sys.__stdout__
        builtins.input = original_input
        random.randint = original_randint
        
    output = stdout_capture.getvalue().lower()
    assert "too low" in output, "When guess is lower than secret, should output 'Too low!'"
    assert "too high" in output, "When guess is higher than secret, should output 'Too high!'"
    assert "won" in output or "correct" in output or "success" in output or "congratulations" in output, "When guess matches, should output a winning message."

def check_m5_ex1_variant(code):
    original_randint = random.randint
    random.randint = lambda a, b: 12
    
    inputs = ["5", "18", "12"]
    input_index = 0
    
    def mock_input(prompt=""):
        nonlocal input_index
        if input_index < len(inputs):
            val = inputs[input_index]
            input_index += 1
            return val
        return "12"
        
    original_input = builtins.input
    builtins.input = mock_input
    
    stdout_capture = io.StringIO()
    sys.stdout = stdout_capture
    
    try:
        exec(code, {"__name__": "__main__", "random": random})
    finally:
        sys.stdout = sys.__stdout__
        builtins.input = original_input
        random.randint = original_randint
        
    output = stdout_capture.getvalue().lower()
    assert "too low" in output, "When guess is lower than secret, should output 'Too low!'"
    assert "too high" in output, "When guess is higher than secret, should output 'Too high!'"
    assert "won" in output or "correct" in output or "success" in output or "congratulations" in output, "When guess matches, should output a winning message."
