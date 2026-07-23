from __future__ import annotations

import json
import os
import subprocess
from datetime import date, datetime, timedelta
from typing import Any


def _gh_graphql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    command = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        command.extend(["-F", f"{key}={value}"])
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def _project(owner: str, number: int) -> dict[str, Any]:
    body = """
      id
      fields(first: 100) {
        nodes {
          ... on ProjectV2Field { id name dataType }
          ... on ProjectV2SingleSelectField { id name options { id name } }
          ... on ProjectV2IterationField {
            id name
            configuration { iterations { id title startDate duration } }
          }
        }
      }
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue { state }
            ... on PullRequest { state merged }
          }
          fieldValues(first: 50) {
            nodes {
              ... on ProjectV2ItemFieldDateValue { date field { ... on ProjectV2Field { id name } } }
              ... on ProjectV2ItemFieldSingleSelectValue { name field { ... on ProjectV2SingleSelectField { id name } } }
              ... on ProjectV2ItemFieldIterationValue { iterationId field { ... on ProjectV2IterationField { id name } } }
            }
          }
        }
      }
    """
    user_query = "query($owner:String!,$number:Int!){user(login:$owner){projectV2(number:$number){__BODY__}}}".replace(
        "__BODY__", body
    )
    result = _gh_graphql(user_query, {"owner": owner, "number": number})
    project = result.get("data", {}).get("user", {}).get("projectV2")
    if project is not None:
        return project
    org_query = "query($owner:String!,$number:Int!){organization(login:$owner){projectV2(number:$number){__BODY__}}}".replace(
        "__BODY__", body
    )
    result = _gh_graphql(org_query, {"owner": owner, "number": number})
    project = result.get("data", {}).get("organization", {}).get("projectV2")
    if project is None:
        raise RuntimeError(f"Project {owner}/{number} was not found.")
    return project


def _update(
    project_id: str, item_id: str, field_id: str, value: str, kind: str
) -> None:
    value_field = {"date": "date", "iteration": "iterationId"}[kind]
    mutation = f"""
      mutation($project:ID!,$item:ID!,$field:ID!,$value:String!) {{
        updateProjectV2ItemFieldValue(input: {{
          projectId:$project itemId:$item fieldId:$field
          value: {{{value_field}:$value}}
        }}) {{ projectV2Item {{ id }} }}
      }}
    """
    _gh_graphql(
        mutation,
        {"project": project_id, "item": item_id, "field": field_id, "value": value},
    )


def _current_iteration(field: dict[str, Any], today: date) -> str | None:
    for iteration in field.get("configuration", {}).get("iterations", []):
        start = date.fromisoformat(iteration["startDate"])
        end = start + timedelta(days=int(iteration["duration"]))
        if start <= today < end:
            return str(iteration["id"])
    return None


def main() -> None:
    owner = os.environ["PROJECT_OWNER"]
    number = int(os.environ["PROJECT_NUMBER"])
    start_field_name = os.getenv("PROJECT_START_FIELD", "Start date")
    end_field_name = os.getenv("PROJECT_END_FIELD", "End date")
    iteration_field_name = os.getenv("PROJECT_ITERATION_FIELD", "Iteration")
    in_progress_names = {
        item.strip().casefold()
        for item in os.getenv(
            "PROJECT_IN_PROGRESS_VALUES", "In Progress,Started"
        ).split(",")
    }
    done_names = {
        item.strip().casefold()
        for item in os.getenv("PROJECT_DONE_VALUES", "Done,Closed").split(",")
    }
    today = datetime.utcnow().date()
    project = _project(owner, number)
    fields = {field.get("name"): field for field in project["fields"]["nodes"]}
    missing = [
        name
        for name in (start_field_name, end_field_name, iteration_field_name)
        if name not in fields
    ]
    if missing:
        raise RuntimeError(f"Missing Project fields: {missing}")
    iteration_id = _current_iteration(fields[iteration_field_name], today)
    if iteration_id is None:
        raise RuntimeError("No current Project iteration contains today's date.")

    for item in project["items"]["nodes"]:
        values = item["fieldValues"]["nodes"]
        status = next(
            (
                value.get("name")
                for value in values
                if value.get("field", {}).get("name") == "Status"
            ),
            None,
        )
        dates = {
            value.get("field", {}).get("name"): value.get("date")
            for value in values
            if "date" in value
        }
        current_iteration = next(
            (
                value.get("iterationId")
                for value in values
                if value.get("field", {}).get("name") == iteration_field_name
            ),
            None,
        )
        content = item.get("content") or {}
        content_closed = content.get("state") == "CLOSED" or bool(content.get("merged"))
        normalized_status = str(status or "").casefold()

        if normalized_status in in_progress_names:
            if not dates.get(start_field_name):
                _update(
                    project["id"],
                    item["id"],
                    fields[start_field_name]["id"],
                    today.isoformat(),
                    "date",
                )
            if current_iteration != iteration_id:
                _update(
                    project["id"],
                    item["id"],
                    fields[iteration_field_name]["id"],
                    iteration_id,
                    "iteration",
                )

        if content_closed or normalized_status in done_names:
            if not dates.get(end_field_name):
                _update(
                    project["id"],
                    item["id"],
                    fields[end_field_name]["id"],
                    today.isoformat(),
                    "date",
                )


if __name__ == "__main__":
    main()
