from workflows.workflow_manager import WorkflowManager

from rich import print
import json


workflow_manager = WorkflowManager()

print("[bold green]Multi-Agent AI System Started[/bold green]\n")

while True:

    user_input = input("\nYou: ").strip()

    if not user_input:
        print("[bold red]Please enter a message.[/bold red]")
        continue

    if user_input.lower() == "exit":
        break

    workflow_result = workflow_manager.execute_workflow(user_input)

    print("\n[bold yellow]Planner Agent Response:[/bold yellow]")

    print(json.dumps(
        workflow_result["planner_response"],
        indent=4
    ))

    print("\n[bold cyan]Analyst Agent Response:[/bold cyan]")

    print(json.dumps(
        workflow_result["analyst_response"],
        indent=4
    ))

    print("\n[bold magenta]Reviewer Agent Response:[/bold magenta]")

    print(json.dumps(
        workflow_result["reviewer_response"],
        indent=4
    ))

    print("\n[bold green]Executor Agent Response:[/bold green]")

    print(json.dumps(
        workflow_result["executor_response"],
        indent=4
    ))