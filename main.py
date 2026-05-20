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

    if user_input.lower() == "show workflow history":

        history = workflow_manager.db_manager.get_workflow_history()

        print("\nWorkflow History:\n")

        print(
            "Workflow ID | Approval | Human Approval | "
            "Execution | Risk | Created At"
        )

        print("-" * 100)

        for row in history:

            print(
                f"{row[0]} | "
                f"{row[1]} | "
                f"{row[2]} | "
                f"{row[3]} | "
                f"{row[4]} | "
                f"{row[5]}"
            )

        continue

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