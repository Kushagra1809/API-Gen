"""
CLI Tool — api-gen command line interface.

Commands:
    api-gen scan ./myproject    — Analyze a Python project
    api-gen recommend "idea"    — Get API recommendations
    api-gen deploy              — Generate deployment configs
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import print as rprint

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """🚀 API Gen — AI-Powered API Discovery & REST API Generator"""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--framework", "-f", default=None, help="Force a specific framework")
@click.option("--output", "-o", default="./generated", help="Output directory")
def scan(path, framework, output):
    """🔬 Analyze a Python project and generate REST API."""
    from generator.analyzer import analyze_project
    from generator.rest_generator import generate_endpoints, generate_fastapi_code
    from generator.doc_generator import generate_openapi_spec
    from deployment.generators import generate_all_deployment_configs

    console.print(Panel.fit("🔬 [bold cyan]Scanning Python Project[/bold cyan]", border_style="cyan"))

    # Read all .py files
    files = {}
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            files[os.path.basename(path)] = f.read()
    else:
        for root, dirs, filenames in os.walk(path):
            for fname in filenames:
                if fname.endswith(".py") and not fname.startswith("__"):
                    fpath = os.path.join(root, fname)
                    rel_path = os.path.relpath(fpath, path)
                    with open(fpath, "r", encoding="utf-8") as f:
                        files[rel_path] = f.read()

    if not files:
        console.print("[red]❌ No Python files found![/red]")
        return

    console.print(f"📂 Found [bold]{len(files)}[/bold] Python files")

    # Analyze
    project_name = os.path.basename(os.path.abspath(path))
    analysis = analyze_project(project_name, files)

    # Display analysis
    table = Table(title="📊 Analysis Results", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Files Scanned", str(analysis["files_scanned"]))
    table.add_row("Functions Found", str(len(analysis["functions"])))
    table.add_row("Classes Found", str(len(analysis["classes"])))
    table.add_row("Has Async", "✅" if analysis["has_async"] else "❌")
    table.add_row("Has DB Models", "✅" if analysis["has_db_models"] else "❌")
    table.add_row("Has ML Models", "✅" if analysis["has_ml_models"] else "❌")
    table.add_row("Framework", analysis["framework_recommendation"])
    console.print(table)

    # Generate endpoints
    endpoints = generate_endpoints(analysis)
    console.print(f"\n🔗 Generated [bold]{len(endpoints)}[/bold] REST endpoints:")

    ep_table = Table(show_header=True, header_style="bold blue")
    ep_table.add_column("Method", style="magenta", width=8)
    ep_table.add_column("Path", style="cyan")
    ep_table.add_column("Function", style="green")
    for ep in endpoints:
        ep_table.add_row(ep["method"], ep["path"], ep["function_name"])
    console.print(ep_table)

    # Generate code
    fw = framework or analysis["framework_recommendation"]
    generated = generate_fastapi_code(project_name, endpoints, files)
    deploy_configs = generate_all_deployment_configs(project_name, fw)

    # Save output
    os.makedirs(output, exist_ok=True)
    for fname, code in generated.items():
        fpath = os.path.join(output, fname)
        os.makedirs(os.path.dirname(fpath) if os.path.dirname(fpath) else output, exist_ok=True)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(code)

    deploy_dir = os.path.join(output, "deploy")
    os.makedirs(deploy_dir, exist_ok=True)
    for fname, code in deploy_configs.items():
        with open(os.path.join(deploy_dir, fname), "w", encoding="utf-8") as f:
            f.write(code)

    console.print(f"\n✅ [bold green]Generated project saved to {output}/[/bold green]")
    console.print(f"   📁 {len(generated)} app files + {len(deploy_configs)} deployment configs")
    console.print(f"\n   Run: [bold]cd {output} && pip install -r requirements.txt && python app.py[/bold]")


@cli.command()
@click.argument("idea")
@click.option("--free-only", is_flag=True, help="Show only free APIs")
@click.option("--limit", "-n", default=5, help="Max APIs per category")
def recommend(idea, free_only, limit):
    """🔍 Get API recommendations for your application idea."""
    from database import SessionLocal, init_db
    from discovery.knowledge_base import seed_database
    from discovery.engine import discover_apis

    console.print(Panel.fit(f"🔍 [bold cyan]Discovering APIs for:[/bold cyan] {idea}", border_style="cyan"))

    init_db()
    db = SessionLocal()
    seed_database(db)

    result = discover_apis(idea, db)

    for feature in result["features"]:
        tree = Tree(f"{feature['icon']} [bold]{feature['feature']}[/bold] ({feature['category']})")

        apis = feature["apis"]
        if free_only:
            apis = [a for a in apis if a.get("free_tier")]
        apis = apis[:limit]

        for api in apis:
            score = api.get("composite_score", 0)
            free_badge = " [green]FREE[/green]" if api.get("free_tier") else " [yellow]PAID[/yellow]"
            tree.add(
                f"[bold]{api['name']}[/bold] — {api['provider']}{free_badge} "
                f"(Score: {score}) | Auth: {api['auth_type']} | "
                f"Docs: {api.get('documentation_url', 'N/A')}"
            )

        console.print(tree)
        console.print()

    console.print(f"📊 Total: [bold]{result['total_apis']}[/bold] APIs across "
                  f"[bold]{len(result['features'])}[/bold] categories")
    db.close()


@cli.command()
@click.option("--project-name", "-n", default="my-api", help="Project name")
@click.option("--output", "-o", default="./deploy", help="Output directory")
def deploy(project_name, output):
    """📦 Generate deployment configurations."""
    from deployment.generators import generate_all_deployment_configs

    console.print(Panel.fit("📦 [bold cyan]Generating Deployment Configs[/bold cyan]", border_style="cyan"))

    configs = generate_all_deployment_configs(project_name)

    os.makedirs(output, exist_ok=True)
    for fname, content in configs.items():
        filepath = os.path.join(output, fname)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(f"  ✅ {fname}")

    console.print(f"\n📁 [bold green]{len(configs)} configs saved to {output}/[/bold green]")


if __name__ == "__main__":
    cli()
