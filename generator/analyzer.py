"""
AST-based Python Code Analyzer.

Scans Python source files, extracts functions and classes,
detects parameters with type hints, return types, and project characteristics.
"""
import ast
import re
from typing import Any


def _get_type_annotation(node: ast.expr | None) -> str:
    """Convert an AST annotation node to a readable type string."""
    if node is None:
        return "Any"
    return ast.unparse(node)


def _get_default_value(node: ast.expr | None) -> str | None:
    """Convert a default value node to a string."""
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return "..."


def _get_decorators(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Extract decorator names."""
    decorators = []
    for dec in node.decorator_list:
        try:
            decorators.append(ast.unparse(dec))
        except Exception:
            decorators.append("unknown")
    return decorators


def analyze_function(node: ast.FunctionDef | ast.AsyncFunctionDef, filename: str) -> dict:
    """Extract metadata from a function definition."""
    params = []
    args = node.args

    # Positional args
    defaults_offset = len(args.args) - len(args.defaults)
    for i, arg in enumerate(args.args):
        if arg.arg == "self" or arg.arg == "cls":
            continue
        default_idx = i - defaults_offset
        default = _get_default_value(args.defaults[default_idx]) if default_idx >= 0 else None
        params.append({
            "name": arg.arg,
            "type": _get_type_annotation(arg.annotation),
            "default": default,
        })

    # Keyword-only args
    for i, arg in enumerate(args.kwonlyargs):
        default = _get_default_value(args.kw_defaults[i]) if i < len(args.kw_defaults) and args.kw_defaults[i] else None
        params.append({
            "name": arg.arg,
            "type": _get_type_annotation(arg.annotation),
            "default": default,
        })

    return_type = _get_type_annotation(node.returns)
    docstring = ast.get_docstring(node) or ""
    is_async = isinstance(node, ast.AsyncFunctionDef)

    return {
        "name": node.name,
        "docstring": docstring,
        "parameters": params,
        "return_type": return_type,
        "is_async": is_async,
        "decorators": _get_decorators(node),
        "file": filename,
        "line": node.lineno,
    }


def analyze_class(node: ast.ClassDef, filename: str) -> dict:
    """Extract metadata from a class definition."""
    methods = []
    for item in ast.walk(node):
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.append(analyze_function(item, filename))

    return {
        "name": node.name,
        "docstring": ast.get_docstring(node) or "",
        "methods": methods,
        "file": filename,
        "line": node.lineno,
    }


def analyze_file(source_code: str, filename: str = "module.py") -> dict:
    """
    Analyze a single Python file.
    Returns functions, classes, and detected characteristics.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return {
            "error": f"Syntax error in {filename}: {e}",
            "functions": [],
            "classes": [],
        }

    functions = []
    classes = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip private / dunder functions
            if not node.name.startswith("_"):
                functions.append(analyze_function(node, filename))
        elif isinstance(node, ast.ClassDef):
            classes.append(analyze_class(node, filename))

    return {
        "functions": functions,
        "classes": classes,
    }


def analyze_js_file(source_code: str, filename: str) -> dict:
    """Regex-based parser for JavaScript files."""
    functions = []
    
    # Catch: (async)? function name (args)
    func_pattern = re.compile(r'(async\s+)?function\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)')
    for match in func_pattern.finditer(source_code):
        is_async = bool(match.group(1))
        name = match.group(2)
        args_str = match.group(3)
        
        params = []
        if args_str.strip():
            for arg_str in args_str.split(','):
                arg_name = arg_str.strip().split('=')[0].strip()
                if arg_name:
                    params.append({"name": arg_name, "type": "Any", "default": None})
                    
        functions.append({
            "name": name,
            "docstring": "",
            "parameters": params,
            "return_type": "Any",
            "is_async": is_async,
            "decorators": [],
            "file": filename,
            "line": 1
        })
        
    # Catch arrow functions: const name = async (args) =>
    arrow_pattern = re.compile(r'(const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(async\s+)?\(([^)]*)\)\s*=>')
    for match in arrow_pattern.finditer(source_code):
        name = match.group(2)
        is_async = bool(match.group(3))
        args_str = match.group(4)
        
        params = []
        if args_str.strip():
            for arg_str in args_str.split(','):
                arg_name = arg_str.strip().split('=')[0].strip()
                if arg_name:
                    params.append({"name": arg_name, "type": "Any", "default": None})
                    
        functions.append({
            "name": name,
            "docstring": "",
            "parameters": params,
            "return_type": "Any",
            "is_async": is_async,
            "decorators": [],
            "file": filename,
            "line": 1
        })

    return {"functions": [f for f in functions if not f["name"].startswith("_")], "classes": []}


def analyze_java_file(source_code: str, filename: str) -> dict:
    """Regex-based parser for Java files."""
    classes = []
    
    # Find class name
    class_match = re.search(r'class\s+([a-zA-Z0-9_]+)', source_code)
    class_name = class_match.group(1) if class_match else "AppController"
    
    methods = []
    # Find public methods: public [static] ReturnType methodName(Type arg1, Type arg2)
    method_pattern = re.compile(r'public\s+(?:static\s+)?([a-zA-Z0-9_<>\[\]]+)\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)')
    for match in method_pattern.finditer(source_code):
        return_type = match.group(1)
        name = match.group(2)
        args_str = match.group(3)
        
        if name == class_name:
            continue
            
        params = []
        if args_str.strip():
            for arg_str in args_str.split(','):
                parts = arg_str.strip().split()
                if len(parts) >= 2:
                    p_type = parts[0]
                    p_name = parts[-1]
                    params.append({"name": p_name, "type": p_type, "default": None})
                    
        methods.append({
            "name": name,
            "docstring": "",
            "parameters": params,
            "return_type": return_type,
            "is_async": False,
            "decorators": [],
            "file": filename,
            "line": 1
        })
        
    classes.append({
        "name": class_name,
        "docstring": "",
        "methods": methods,
        "file": filename,
        "line": 1
    })
    
    return {"functions": [], "classes": classes}


def analyze_ts_file(source_code: str, filename: str) -> dict:
    """Regex-based parser for TypeScript files."""
    functions = []
    
    # Catch: (export)? (async)? function name (args)
    func_pattern = re.compile(r'(?:export\s+)?(async\s+)?function\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)')
    for match in func_pattern.finditer(source_code):
        is_async = bool(match.group(1))
        name = match.group(2)
        args_str = match.group(3)
        
        params = []
        if args_str.strip():
            for arg_str in args_str.split(','):
                arg_name = arg_str.strip().split(':')[0].split('=')[0].strip()
                if arg_name:
                    params.append({"name": arg_name, "type": "Any", "default": None})
                    
        functions.append({
            "name": name,
            "docstring": "",
            "parameters": params,
            "return_type": "Any",
            "is_async": is_async,
            "decorators": [],
            "file": filename,
            "line": 1
        })
        
    return {"functions": [f for f in functions if not f["name"].startswith("_")], "classes": []}


def analyze_go_file(source_code: str, filename: str) -> dict:
    """Regex-based parser for Go files."""
    functions = []
    
    # Find exported functions: func Name(args)
    func_pattern = re.compile(r'func\s+([A-Z][a-zA-Z0-9_]*)\s*\(([^)]*)\)')
    for match in func_pattern.finditer(source_code):
        name = match.group(1)
        args_str = match.group(2)
        
        params = []
        if args_str.strip():
            for arg_str in args_str.split(','):
                parts = arg_str.strip().split()
                if len(parts) >= 2:
                    p_name = parts[0]
                    p_type = parts[-1]
                    params.append({"name": p_name, "type": p_type, "default": None})
                    
        functions.append({
            "name": name,
            "docstring": "",
            "parameters": params,
            "return_type": "Any",
            "is_async": False,
            "decorators": [],
            "file": filename,
            "line": 1
        })
        
    return {"functions": functions, "classes": []}


def analyze_cs_file(source_code: str, filename: str) -> dict:
    """Regex-based parser for C# files."""
    classes = []
    
    class_match = re.search(r'class\s+([a-zA-Z0-9_]+)', source_code)
    class_name = class_match.group(1) if class_match else "AppController"
    
    methods = []
    method_pattern = re.compile(r'public\s+(?:async\s+(?:Task<)?|Task<)?(?:static\s+)?([a-zA-Z0-9_<>\[\]]+)>?\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)')
    for match in method_pattern.finditer(source_code):
        return_type = match.group(1)
        name = match.group(2)
        args_str = match.group(3)
        
        if name == class_name:
            continue
            
        params = []
        if args_str.strip():
            for arg_str in args_str.split(','):
                parts = arg_str.strip().split()
                if len(parts) >= 2:
                    p_type = parts[0]
                    p_name = parts[-1]
                    params.append({"name": p_name, "type": p_type, "default": None})
                    
        methods.append({
            "name": name,
            "docstring": "",
            "parameters": params,
            "return_type": return_type,
            "is_async": "Task" in match.group(0),
            "decorators": [],
            "file": filename,
            "line": 1
        })
        
    classes.append({
        "name": class_name,
        "docstring": "",
        "methods": methods,
        "file": filename,
        "line": 1
    })
    
    return {"functions": [], "classes": classes}


def detect_project_characteristics(files: dict[str, str]) -> dict:
    """
    Analyze all files in a project to detect:
    - async usage
    - database models (SQLAlchemy, Django)
    - ML models (sklearn, torch, tensorflow, keras)
    - file I/O operations
    """
    all_code = "\n".join(files.values())
    code_lower = all_code.lower()

    has_async = "async def" in all_code or "await " in all_code
    has_db_models = any(kw in code_lower for kw in [
        "sqlalchemy", "django.db", "from models import", "base.metadata",
        "db.column", "db.session", "peewee", "tortoise",
    ])
    has_ml_models = any(kw in code_lower for kw in [
        "sklearn", "torch", "tensorflow", "keras", "xgboost",
        "model.predict", "model.fit", "pipeline", "joblib",
        "transformers", "huggingface",
    ])
    has_file_io = any(kw in code_lower for kw in [
        "open(", "pathlib", "shutil", "os.path", "cv2.imread",
        "pillow", "pil", "image.open", "uploadfile",
    ])

    return {
        "has_async": has_async,
        "has_db_models": has_db_models,
        "has_ml_models": has_ml_models,
        "has_file_io": has_file_io,
    }


def analyze_project(project_name: str, files: dict[str, str]) -> dict:
    """
    Full project analysis:
    1. Analyze each file for functions and classes
    2. Detect project characteristics
    3. Generate framework recommendation
    """
    from generator.framework_selector import select_framework

    all_functions = []
    all_classes = []

    for filename, source_code in files.items():
        if filename.endswith(".py"):
            result = analyze_file(source_code, filename)
        elif filename.endswith(".js"):
            result = analyze_js_file(source_code, filename)
        elif filename.endswith(".java"):
            result = analyze_java_file(source_code, filename)
        elif filename.endswith(".ts"):
            result = analyze_ts_file(source_code, filename)
        elif filename.endswith(".go"):
            result = analyze_go_file(source_code, filename)
        elif filename.endswith(".cs"):
            result = analyze_cs_file(source_code, filename)
        else:
            continue
            
        all_functions.extend(result.get("functions", []))
        all_classes.extend(result.get("classes", []))

    characteristics = detect_project_characteristics(files)
    framework, reason = select_framework(characteristics, all_functions, all_classes, files)

    return {
        "project_name": project_name,
        "files_scanned": len(files),
        "functions": all_functions,
        "classes": all_classes,
        "has_async": characteristics["has_async"],
        "has_db_models": characteristics["has_db_models"],
        "has_ml_models": characteristics["has_ml_models"],
        "has_file_io": characteristics["has_file_io"],
        "framework_recommendation": framework,
        "framework_reason": reason,
    }
