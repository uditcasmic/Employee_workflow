from fastapi.testclient import TestClient


def create_workflow(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/workflows",
        headers=auth_headers,
        json={
            "name": "Employee Onboarding",
            "description": "Onboard a new employee",
            "steps": [
                {"name": "Validate Input", "action": "validate", "config": {}},
                {"name": "Create User", "action": "create_user", "config": {}},
                {"name": "Send Welcome Email", "action": "send_email", "config": {}},
            ],
        },
    )
    assert response.status_code == 201
    return response.json()


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auth_me_and_admin_create_user(
    client: TestClient,
    auth_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    me_response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.com"

    create_response = client.post(
        "/api/v1/auth/users",
        headers=admin_headers,
        json={
            "email": "new.user@example.com",
            "password": "strong-password",
            "full_name": "Created By Admin",
            "role": "user",
        },
    )
    assert create_response.status_code == 201
    assert create_response.json()["email"] == "new.user@example.com"


def test_workflow_crud_and_execution_flow(client: TestClient, auth_headers: dict[str, str]) -> None:
    workflow = create_workflow(client, auth_headers)
    workflow_id = workflow["id"]

    list_response = client.get("/api/v1/workflows", headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(f"/api/v1/workflows/{workflow_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Employee Onboarding"

    update_response = client.put(
        f"/api/v1/workflows/{workflow_id}",
        headers=auth_headers,
        json={"description": "Updated workflow description"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Updated workflow description"

    execute_response = client.post(
        f"/api/v1/executions/workflow/{workflow_id}?sync=true",
        headers=auth_headers,
        json={"input_payload": {"employee_email": "hire@example.com"}},
    )
    assert execute_response.status_code == 200
    execution = execute_response.json()
    assert execution["status"] == "success"
    assert execution["result_payload"]["validated"] is True
    assert execution["result_payload"]["user_created"] is True
    assert execution["result_payload"]["email_sent"] is True
    execution_id = execution["id"]

    execution_response = client.get(f"/api/v1/executions/{execution_id}", headers=auth_headers)
    assert execution_response.status_code == 200
    assert execution_response.json()["id"] == execution_id

    logs_response = client.get(f"/api/v1/executions/{execution_id}/logs", headers=auth_headers)
    assert logs_response.status_code == 200
    assert len(logs_response.json()) == 6

    history_response = client.get(
        f"/api/v1/executions/workflow/{workflow_id}/history",
        headers=auth_headers,
    )
    assert history_response.status_code == 200
    assert len(history_response.json()) == 1

    dashboard_response = client.get("/api/v1/executions/dashboard/stats", headers=auth_headers)
    assert dashboard_response.status_code == 200
    payload = dashboard_response.json()
    assert payload["total_workflows"] == 1
    assert payload["failed_workflows"] == 0
    assert payload["success_rate"] == 100.0

    delete_response = client.delete(f"/api/v1/workflows/{workflow_id}", headers=auth_headers)
    assert delete_response.status_code == 204
