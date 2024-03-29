from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK

from baserow.core.jobs.models import Job


@pytest.mark.django_db(transaction=True)
@patch("baserow.core.jobs.handler.run_async_job")
def test_create_job(mock_run_async, data_fixture, api_client):
    data_fixture.register_temp_job_types()

    user, token = data_fixture.create_user_and_token()
    group = data_fixture.create_group(user=user)

    response = api_client.post(
        reverse("api:jobs:list"),
        {},
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_REQUEST_BODY_VALIDATION"
    assert response.json() == {
        "error": "ERROR_REQUEST_BODY_VALIDATION",
        "detail": {
            "type": [{"error": "This field is required.", "code": "required"}],
        },
    }

    response = api_client.post(
        reverse("api:jobs:list"),
        {
            "type": "tmp_job_type_1",
        },
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_REQUEST_BODY_VALIDATION"
    assert response.json() == {
        "error": "ERROR_REQUEST_BODY_VALIDATION",
        "detail": {
            "test_request_field": [
                {"error": "This field is required.", "code": "required"}
            ],
        },
    }

    response = api_client.post(
        reverse("api:jobs:list"),
        {
            "type": "tmp_job_type_1",
            "test_request_field": "test",
        },
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_REQUEST_BODY_VALIDATION"
    assert response.json() == {
        "error": "ERROR_REQUEST_BODY_VALIDATION",
        "detail": {
            "test_request_field": [
                {"error": "A valid integer is required.", "code": "invalid"}
            ],
        },
    }

    response = api_client.post(
        reverse("api:jobs:list"),
        {
            "type": "tmp_job_type_3",
            "test_request_field": 1,
        },
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "TEST_EXCEPTION"

    response = api_client.post(
        reverse("api:jobs:list"),
        {
            "type": "tmp_job_type_1",
            "test_request_field": 1,
        },
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_200_OK
    job = Job.objects.all().first()

    assert response.json() == {
        "id": job.id,
        "type": "tmp_job_type_1",
        "test_field": 42,
        "state": "pending",
        "progress_percentage": 0,
        "human_readable_error": "",
    }
    mock_run_async.delay.assert_called()

    response = api_client.post(
        reverse("api:jobs:list"),
        {
            "type": "tmp_job_type_1",
            "test_request_field": 1,
        },
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_MAX_JOB_COUNT_EXCEEDED"


@pytest.mark.django_db
def test_list_jobs(data_fixture, api_client):
    user, token = data_fixture.create_user_and_token()
    job_1 = data_fixture.create_fake_job(user=user)
    job_2 = data_fixture.create_fake_job(user=user, state="failed")
    job_3 = data_fixture.create_fake_job()

    response = api_client.get(
        reverse(
            "api:jobs:list",
        ),
        HTTP_AUTHORIZATION=f"JWT {token}",
    )

    assert response.status_code == HTTP_200_OK
    json = response.json()

    assert json == [
        {
            "id": job_1.id,
            "type": "tmp_job_type_1",
            "progress_percentage": 0,
            "state": "pending",
            "human_readable_error": "",
            "test_field": 42,
        },
        {
            "id": job_2.id,
            "type": "tmp_job_type_1",
            "progress_percentage": 0,
            "state": "failed",
            "human_readable_error": "",
            "test_field": 42,
        },
    ]


@pytest.mark.django_db
def test_get_job(data_fixture, api_client):
    user, token = data_fixture.create_user_and_token()
    job_1 = data_fixture.create_fake_job(user=user)
    job_2 = data_fixture.create_fake_job()

    response = api_client.get(
        reverse(
            "api:jobs:item",
            kwargs={"job_id": job_2.id},
        ),
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_JOB_DOES_NOT_EXIST"

    response = api_client.get(
        reverse(
            "api:jobs:item",
            kwargs={"job_id": job_1.id},
        ),
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_200_OK
    json = response.json()

    assert json == {
        "id": job_1.id,
        "type": "tmp_job_type_1",
        "progress_percentage": 0,
        "state": "pending",
        "human_readable_error": "",
        "test_field": 42,
    }

    job_1.progress_percentage = 50
    job_1.state = "failed"
    job_1.human_readable_error = "Wrong"
    job_1.save()

    response = api_client.get(
        reverse(
            "api:jobs:item",
            kwargs={"job_id": job_1.id},
        ),
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_200_OK
    json = response.json()

    assert json == {
        "id": job_1.id,
        "type": "tmp_job_type_1",
        "progress_percentage": 50,
        "state": "failed",
        "human_readable_error": "Wrong",
        "test_field": 42,
    }
