"""
REST Endpoint Generator.

Converts analyzed Python functions/classes into REST endpoint definitions
and generates complete application code using Jinja2-style templates.
"""
import re
import json
from typing import Any


def _determine_http_method(func: dict) -> str:
    """Infer HTTP method from function name and parameters."""
    name = func["name"].lower()

    # DELETE patterns
    if any(kw in name for kw in ["delete", "remove", "destroy", "drop"]):
        return "DELETE"

    # PUT/PATCH patterns
    if any(kw in name for kw in ["update", "modify", "edit", "patch", "set_"]):
        return "PUT"

    # GET patterns: no body params, or name implies reading
    if any(kw in name for kw in ["get", "fetch", "list", "show", "find", "search", "read", "check", "is_", "has_"]):
        return "GET"

    # POST for everything else (create, process, predict, etc.)
    return "POST"


def _generate_path(func: dict) -> str:
    """Generate a URL path from function name."""
    name = func["name"]
    # Convert snake_case to /kebab-path
    # e.g., get_user_profile → /user-profile
    # Remove common prefixes
    for prefix in ["get_", "create_", "update_", "delete_", "fetch_", "list_", "do_", "run_", "process_"]:
        if name.lower().startswith(prefix):
            name = name[len(prefix):]
            break

    path = "/" + name.replace("_", "-")
    return path


def _build_request_body(func: dict) -> dict | None:
    """Build a request body schema from function parameters."""
    params = func.get("parameters", [])
    if not params:
        return None

    method = _determine_http_method(func)
    if method == "GET":
        return None  # GET uses query params, not body

    properties = {}
    required = []
    for p in params:
        prop = {"type": _python_type_to_json_type(p["type"])}
        if p.get("default") is None:
            required.append(p["name"])
        properties[p["name"]] = prop

    if not properties:
        return None

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def _build_response_schema(func: dict) -> dict:
    """Build a response schema from function return type."""
    return_type = func.get("return_type", "Any")
    json_type = _python_type_to_json_type(return_type)

    return {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {"type": json_type},
            "message": {"type": "string"},
        },
    }


def _python_type_to_json_type(py_type: str) -> str:
    """Map Python type annotations to JSON Schema types."""
    py_type_lower = py_type.lower().strip()
    mapping = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
        "list": "array",
        "dict": "object",
        "none": "null",
        "any": "object",
        "bytes": "string",
    }
    for key, val in mapping.items():
        if key in py_type_lower:
            return val
    return "object"


def generate_endpoints(analysis: dict) -> list[dict]:
    """
    Generate REST endpoint definitions from analysis results.
    """
    endpoints = []

    # From standalone functions
    for func in analysis.get("functions", []):
        method = _determine_http_method(func)
        path = _generate_path(func)
        endpoints.append({
            "method": method,
            "path": path,
            "function_name": func["name"],
            "summary": func.get("docstring", "") or f"Auto-generated endpoint for {func['name']}",
            "request_body": _build_request_body(func),
            "response_schema": _build_response_schema(func),
            "tags": [func.get("file", "default").replace(".py", "")],
            "is_async": func.get("is_async", False),
            "parameters": func.get("parameters", []),
            "return_type": func.get("return_type", "Any"),
        })

    # From class methods (skip private)
    for cls in analysis.get("classes", []):
        for method_info in cls.get("methods", []):
            if method_info["name"].startswith("_"):
                continue
            method = _determine_http_method(method_info)
            class_prefix = "/" + cls["name"].lower().replace("_", "-")
            path = class_prefix + _generate_path(method_info)
            endpoints.append({
                "method": method,
                "path": path,
                "function_name": f"{cls['name']}.{method_info['name']}",
                "summary": method_info.get("docstring", "") or f"{cls['name']}.{method_info['name']}",
                "request_body": _build_request_body(method_info),
                "response_schema": _build_response_schema(method_info),
                "tags": [cls["name"]],
                "is_async": method_info.get("is_async", False),
                "parameters": method_info.get("parameters", []),
                "return_type": method_info.get("return_type", "Any"),
            })

    return endpoints


def generate_fastapi_code(
    project_name: str,
    endpoints: list[dict],
    original_files: dict[str, str],
) -> dict[str, str]:
    """
    Generate a complete FastAPI project from endpoint definitions.
    Returns: {filename: source_code}
    """
    # ── app.py ──
    imports = [
        "from fastapi import FastAPI, HTTPException, UploadFile, File, Query",
        "from fastapi.middleware.cors import CORSMiddleware",
        "from pydantic import BaseModel",
        "from typing import Any, Optional, List",
        "import json",
        "",
    ]

    app_setup = [
        f'app = FastAPI(',
        f'    title="{project_name} API",',
        f'    description="Auto-generated REST API for {project_name}",',
        f'    version="1.0.0",',
        f')',
        '',
        'app.add_middleware(',
        '    CORSMiddleware,',
        '    allow_origins=["*"],',
        '    allow_credentials=True,',
        '    allow_methods=["*"],',
        '    allow_headers=["*"],',
        ')',
        '',
    ]

    # Generate Pydantic models for request bodies
    models_code = []
    for ep in endpoints:
        if ep.get("request_body") and ep["request_body"].get("properties"):
            model_name = _to_pascal_case(ep["function_name"]) + "Request"
            fields = []
            for pname, pinfo in ep["request_body"]["properties"].items():
                py_type = _json_type_to_python_type(pinfo.get("type", "object"))
                if pname in ep["request_body"].get("required", []):
                    fields.append(f"    {pname}: {py_type}")
                else:
                    fields.append(f"    {pname}: Optional[{py_type}] = None")
            models_code.append(f"class {model_name}(BaseModel):")
            models_code.extend(fields)
            models_code.append("")

    # Generate route functions
    routes_code = []
    for ep in endpoints:
        method = ep["method"].lower()
        path = ep["path"]
        func_name = ep["function_name"].replace(".", "_").lower()
        summary = ep.get("summary", "")

        # Decorator
        routes_code.append(f'@app.{method}("{path}", summary="{summary}")')

        # Function signature
        if ep.get("request_body") and ep["request_body"].get("properties"):
            model_name = _to_pascal_case(ep["function_name"]) + "Request"
            if ep.get("is_async"):
                routes_code.append(f"async def {func_name}_endpoint(request: {model_name}):")
            else:
                routes_code.append(f"def {func_name}_endpoint(request: {model_name}):")
            routes_code.append('    """' + summary + '"""')
            routes_code.append("    try:")
            # Call original function with unpacked params
            param_names = list(ep["request_body"]["properties"].keys())
            call_args = ", ".join(f"{p}=request.{p}" for p in param_names)
            routes_code.append(f"        result = {ep['function_name']}({call_args})")
            routes_code.append('        return {"success": True, "data": result, "message": "OK"}')
            routes_code.append("    except Exception as e:")
            routes_code.append('        raise HTTPException(status_code=500, detail=str(e))')
        elif ep["method"] == "GET" and ep.get("parameters"):
            # Use query parameters
            query_params = []
            for p in ep["parameters"]:
                py_type = _json_type_to_python_type(p.get("type", "Any"))
                if p.get("default") is not None:
                    query_params.append(f'{p["name"]}: {py_type} = Query(default={p["default"]})')
                else:
                    query_params.append(f'{p["name"]}: {py_type} = Query(...)')
            sig = ", ".join(query_params)
            if ep.get("is_async"):
                routes_code.append(f"async def {func_name}_endpoint({sig}):")
            else:
                routes_code.append(f"def {func_name}_endpoint({sig}):")
            routes_code.append('    """' + summary + '"""')
            routes_code.append("    try:")
            call_args = ", ".join(f"{p['name']}={p['name']}" for p in ep["parameters"])
            routes_code.append(f"        result = {ep['function_name']}({call_args})")
            routes_code.append('        return {"success": True, "data": result, "message": "OK"}')
            routes_code.append("    except Exception as e:")
            routes_code.append('        raise HTTPException(status_code=500, detail=str(e))')
        else:
            if ep.get("is_async"):
                routes_code.append(f"async def {func_name}_endpoint():")
            else:
                routes_code.append(f"def {func_name}_endpoint():")
            routes_code.append('    """' + summary + '"""')
            routes_code.append("    try:")
            routes_code.append(f"        result = {ep['function_name']}()")
            routes_code.append('        return {"success": True, "data": result, "message": "OK"}')
            routes_code.append("    except Exception as e:")
            routes_code.append('        raise HTTPException(status_code=500, detail=str(e))')

        routes_code.append("")

    # ── main entry ──
    main_block = [
        '',
        'if __name__ == "__main__":',
        '    import uvicorn',
        f'    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)',
    ]

    # Combine everything
    app_code = "\n".join(imports + app_setup + models_code + routes_code + main_block)

    # Build requirements
    requirements = "fastapi==0.104.1\nuvicorn==0.24.0\npydantic==2.5.2\npython-multipart==0.0.6\n"

    files = {
        "app.py": app_code,
        "requirements.txt": requirements,
    }

    # Include original source files
    for fname, code in original_files.items():
        files[fname] = code

    return files


def _to_pascal_case(name: str) -> str:
    """Convert snake_case or dot.notation to PascalCase."""
    parts = re.split(r'[_.]', name)
    return "".join(p.capitalize() for p in parts)


def _json_type_to_python_type(json_type: str) -> str:
    """Map JSON Schema types back to Python types."""
    mapping = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "List",
        "object": "dict",
        "null": "None",
    }
    return mapping.get(json_type, "Any")


def generate_express_code(
    project_name: str,
    endpoints: list[dict],
    original_files: dict[str, str],
) -> dict[str, str]:
    """Generate a Node.js Express project."""
    # ── server.js ──
    imports = [
        "const express = require('express');",
        "const cors = require('cors');",
        "const app = express();",
        "",
        "app.use(cors());",
        "app.use(express.json());",
        ""
    ]
    
    routes_code = []
    for ep in endpoints:
        method = ep["method"].lower()
        path = ep["path"]
        func_name = ep["function_name"]
        
        routes_code.append(f"// {ep.get('summary', '')}")
        routes_code.append(f"app.{method}('{path}', async (req, res) => {{")
        routes_code.append(f"    try {{")
        if method in ("post", "put"):
            routes_code.append(f"        const data = req.body;")
        else:
            routes_code.append(f"        const data = req.query;")
        routes_code.append(f"        // TODO: Import and call original logic for {func_name}(data)")
        routes_code.append(f"        res.json({{ success: true, data: {{}}, message: 'OK' }});")
        routes_code.append(f"    }} catch (error) {{")
        routes_code.append(f"        res.status(500).json({{ success: false, error: error.message }});")
        routes_code.append(f"    }}")
        routes_code.append(f"}});")
        routes_code.append("")
        
    main_block = [
        "const PORT = process.env.PORT || 3000;",
        "app.listen(PORT, () => {",
        f"    console.log(`{project_name} API running on port ${{PORT}}`);",
        "});"
    ]
    
    server_code = "\n".join(imports + routes_code + main_block)
    
    package_json = json.dumps({
        "name": project_name.replace("_", "-"),
        "version": "1.0.0",
        "main": "server.js",
        "scripts": {
            "start": "node server.js",
            "dev": "nodemon server.js"
        },
        "dependencies": {
            "express": "^4.18.2",
            "cors": "^2.8.5"
        }
    }, indent=2)

    files = {
        "server.js": server_code,
        "package.json": package_json,
    }
    for fname, code in original_files.items():
        files[fname] = code
        
    return files


def generate_spring_code(
    project_name: str,
    endpoints: list[dict],
    original_files: dict[str, str],
) -> dict[str, str]:
    """Generate a Java Spring Boot project."""
    
    package_name = "com.example.api"
    
    # ── ApiController.java ──
    controller = [
        f"package {package_name};",
        "",
        "import org.springframework.web.bind.annotation.*;",
        "import org.springframework.http.ResponseEntity;",
        "import java.util.Map;",
        "import java.util.HashMap;",
        "",
        "@RestController",
        "@CrossOrigin(origins = \"*\")",
        "@RequestMapping(\"/api\")",
        "public class ApiController {"
    ]
    
    for ep in endpoints:
        method = ep["method"]
        path = ep["path"]
        func_name = ep["function_name"].replace(".", "")
        
        mapping = f"@{method.capitalize()}Mapping(\"{path}\")"
        controller.append(f"    {mapping}")
        
        if method in ("POST", "PUT"):
            req_param = "@RequestBody Map<String, Object> payload"
        else:
            req_param = "@RequestParam Map<String, String> params"
            
        controller.append(f"    public ResponseEntity<Map<String, Object>> {func_name}({req_param}) {{")
        controller.append(f"        Map<String, Object> response = new HashMap<>();")
        controller.append(f"        try {{")
        controller.append(f"            // TODO: Call original logic for {func_name}")
        controller.append(f"            response.put(\"success\", true);")
        controller.append(f"            response.put(\"message\", \"OK\");")
        controller.append(f"            response.put(\"data\", new HashMap<>());")
        controller.append(f"            return ResponseEntity.ok(response);")
        controller.append(f"        }} catch (Exception e) {{")
        controller.append(f"            response.put(\"success\", false);")
        controller.append(f"            response.put(\"error\", e.getMessage());")
        controller.append(f"            return ResponseEntity.internalServerError().body(response);")
        controller.append(f"        }}")
        controller.append(f"    }}")
        controller.append("")
        
    controller.append("}")
    
    pom_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.5</version>
        <relativePath/>
    </parent>
    <groupId>com.example</groupId>
    <artifactId>{project_name.replace("_", "-")}</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>{project_name}</name>
    <properties>
        <java.version>17</java.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
"""

    application_java = f"""package {package_name};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {{
    public static void main(String[] args) {{
        SpringApplication.run(Application.class, args);
    }}
}}
"""

    files = {
        "src/main/java/com/example/api/ApiController.java": "\\n".join(controller),
        "src/main/java/com/example/api/Application.java": application_java,
        "pom.xml": pom_xml,
    }
    for fname, code in original_files.items():
        files[fname] = code
        
    return files


def generate_express_ts_code(
    project_name: str,
    endpoints: list[dict],
    original_files: dict[str, str],
) -> dict[str, str]:
    """Generate a Node.js Express project with TypeScript."""
    
    # ── src/server.ts ──
    imports = [
        "import express, { Request, Response } from 'express';",
        "import cors from 'cors';",
        "",
        "const app = express();",
        "app.use(cors());",
        "app.use(express.json());",
        ""
    ]
    
    routes_code = []
    for ep in endpoints:
        method = ep["method"].lower()
        path = ep["path"]
        func_name = ep["function_name"]
        
        routes_code.append(f"// {ep.get('summary', '')}")
        routes_code.append(f"app.{method}('{path}', async (req: Request, res: Response) => {{")
        routes_code.append(f"    try {{")
        if method in ("post", "put"):
            routes_code.append(f"        const data = req.body;")
        else:
            routes_code.append(f"        const data = req.query;")
        routes_code.append(f"        // TODO: Import and call original logic for {func_name}(data)")
        routes_code.append(f"        res.json({{ success: true, data: {{}}, message: 'OK' }});")
        routes_code.append(f"    }} catch (error: any) {{")
        routes_code.append(f"        res.status(500).json({{ success: false, error: error.message }});")
        routes_code.append(f"    }}")
        routes_code.append(f"}});")
        routes_code.append("")
        
    main_block = [
        "const PORT = process.env.PORT || 3000;",
        "app.listen(PORT, () => {",
        f"    console.log(`{project_name} API running on port ${{PORT}}`);",
        "});"
    ]
    
    server_code = "\n".join(imports + routes_code + main_block)
    
    package_json = json.dumps({
        "name": project_name.replace("_", "-"),
        "version": "1.0.0",
        "main": "dist/server.js",
        "scripts": {
            "start": "node dist/server.js",
            "dev": "ts-node-dev src/server.ts",
            "build": "tsc"
        },
        "dependencies": {
            "express": "^4.18.2",
            "cors": "^2.8.5"
        },
        "devDependencies": {
            "@types/express": "^4.17.17",
            "@types/cors": "^2.8.13",
            "typescript": "^5.0.4",
            "ts-node-dev": "^2.0.0"
        }
    }, indent=2)

    tsconfig_json = json.dumps({
        "compilerOptions": {
            "target": "es2022",
            "module": "commonjs",
            "rootDir": "./src",
            "outDir": "./dist",
            "esModuleInterop": True,
            "forceConsistentCasingInFileNames": True,
            "strict": True,
            "skipLibCheck": True
        }
    }, indent=2)

    files = {
        "src/server.ts": server_code,
        "package.json": package_json,
        "tsconfig.json": tsconfig_json,
    }
    for fname, code in original_files.items():
        files[fname] = code
        
    return files


def generate_gin_code(
    project_name: str,
    endpoints: list[dict],
    original_files: dict[str, str],
) -> dict[str, str]:
    """Generate a Go project using the Gin framework."""
    
    main_go = [
        "package main",
        "",
        "import (",
        "\t\"net/http\"",
        "\t\"github.com/gin-gonic/gin\"",
        ")",
        "",
        "func main() {",
        "\tr := gin.Default()",
        ""
    ]
    
    for ep in endpoints:
        method = ep["method"].upper()
        path = ep["path"]
        func_name = ep["function_name"]
        
        main_go.append(f"\t// {ep.get('summary', '')}")
        main_go.append(f"\tr.{method}(\"{path}\", func(c *gin.Context) {{")
        main_go.append(f"\t\t// TODO: Parse request and call original logic for {func_name}")
        main_go.append(f"\t\tc.JSON(http.StatusOK, gin.H{{")
        main_go.append(f"\t\t\t\"success\": true,")
        main_go.append(f"\t\t\t\"message\": \"OK\",")
        main_go.append(f"\t\t\t\"data\": gin.H{{}},")
        main_go.append(f"\t\t}})")
        main_go.append(f"\t}})")
        main_go.append("")
        
    main_go.append("\tr.Run(\":8080\") // Listen and serve on 0.0.0.0:8080")
    main_go.append("}")
    
    go_mod = f"module {project_name.lower()}\n\ngo 1.20\n\nrequire github.com/gin-gonic/gin v1.9.1\n"
    
    files = {
        "main.go": "\n".join(main_go),
        "go.mod": go_mod,
    }
    for fname, code in original_files.items():
        files[fname] = code
        
    return files


def generate_aspnet_code(
    project_name: str,
    endpoints: list[dict],
    original_files: dict[str, str],
) -> dict[str, str]:
    """Generate a C# ASP.NET Core project."""
    
    proj_name_pascal = "".join(word.capitalize() for word in project_name.split("_"))
    
    # Program.cs (Minimal API style + Controllers)
    program_cs = f"""var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();

app.UseAuthorization();
app.MapControllers();

app.Run();
"""
    
    # ApiController.cs
    controller = [
        "using Microsoft.AspNetCore.Mvc;",
        "using System.Collections.Generic;",
        "using System.Threading.Tasks;",
        "",
        f"namespace {proj_name_pascal}.Controllers",
        "{",
        "    [ApiController]",
        "    [Route(\"api\")]",
        "    public class ApiController : ControllerBase",
        "    {"
    ]
    
    for ep in endpoints:
        method = ep["method"].capitalize()
        path = ep["path"].replace("/api/", "") if ep["path"].startswith("/api/") else ep["path"].lstrip("/")
        func_name = ep["function_name"].replace(".", "")
        
        controller.append(f"        [Http{method}(\"{path}\")]")
        
        if method in ("Post", "Put"):
            req_param = "[FromBody] Dictionary<string, object> payload"
        else:
            req_param = "[FromQuery] Dictionary<string, string> query"
            
        controller.append(f"        public async Task<IActionResult> {func_name}({req_param})")
        controller.append(f"        {{")
        controller.append(f"            try")
        controller.append(f"            {{")
        controller.append(f"                // TODO: Call original logic for {func_name}")
        controller.append(f"                return Ok(new {{ success = true, data = new {{}}, message = \"OK\" }});")
        controller.append(f"            }}")
        controller.append(f"            catch (System.Exception ex)")
        controller.append(f"            {{")
        controller.append(f"                return StatusCode(500, new {{ success = false, error = ex.Message }});")
        controller.append(f"            }}")
        controller.append(f"        }}")
        controller.append("")
        
    controller.append("    }")
    controller.append("}")
    
    # csproj
    csproj = f"""<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Swashbuckle.AspNetCore" Version="6.4.0" />
  </ItemGroup>
</Project>
"""

    files = {
        "Program.cs": program_cs,
        f"{proj_name_pascal}.csproj": csproj,
        "Controllers/ApiController.cs": "\n".join(controller),
    }
    for fname, code in original_files.items():
        files[fname] = code
        
    return files

