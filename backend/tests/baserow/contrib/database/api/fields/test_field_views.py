import pytest

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_204_NO_CONTENT,
    HTTP_409_CONFLICT,
)

from django.shortcuts import reverse
from django.conf import settings

from baserow.contrib.database.fields.models import Field, TextField, NumberField
from baserow.contrib.database.tokens.handler import TokenHandler
from baserow.test_utils.helpers import independent_test_db_connection


@pytest.mark.django_db
def test_list_fields(api_client, data_fixture):
    user, jwt_token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table_1 = data_fixture.create_database_table(user=user)
    table_2 = data_fixture.create_database_table()
    field_1 = data_fixture.create_text_field(table=table_1, order=1, primary=True)
    field_2 = data_fixture.create_text_field(table=table_1, order=3)
    field_3 = data_fixture.create_number_field(table=table_1, order=2)
    data_fixture.create_boolean_field(table=table_2, order=1)

    token = TokenHandler().create_token(user, table_1.database.group, "Good")
    wrong_token = TokenHandler().create_token(user, table_1.database.group, "Wrong")
    TokenHandler().update_token_permissions(
        user, wrong_token, False, False, False, True
    )

    # Test access with JWT token
    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table_1.id}),
        **{"HTTP_AUTHORIZATION": f"JWT {jwt_token}"},
    )
    assert response.status_code == HTTP_200_OK
    response_json = response.json()

    assert len(response_json) == 3

    assert response_json[0]["id"] == field_1.id
    assert response_json[0]["type"] == "text"
    assert response_json[0]["primary"]
    assert response_json[0]["text_default"] == field_1.text_default

    assert response_json[1]["id"] == field_3.id
    assert response_json[1]["type"] == "number"
    assert not response_json[1]["primary"]
    assert response_json[1]["number_decimal_places"] == field_3.number_decimal_places
    assert response_json[1]["number_negative"] == field_3.number_negative

    assert response_json[2]["id"] == field_2.id
    assert response_json[2]["type"] == "text"
    assert not response_json[2]["primary"]
    assert response_json[2]["text_default"] == field_2.text_default

    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table_2.id}),
        **{"HTTP_AUTHORIZATION": f"JWT {jwt_token}"},
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_USER_NOT_IN_GROUP"

    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": 999999}),
        **{"HTTP_AUTHORIZATION": f"JWT {jwt_token}"},
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_TABLE_DOES_NOT_EXIST"

    # Without any token
    url = reverse("api:database:fields:list", kwargs={"table_id": table_1.id})
    response = api_client.get(url)
    assert response.status_code == HTTP_401_UNAUTHORIZED

    data_fixture.create_template(group=table_1.database.group)
    url = reverse("api:database:fields:list", kwargs={"table_id": table_1.id})
    response = api_client.get(url)
    assert response.status_code == HTTP_200_OK

    # Test authentication with token
    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table_1.id}),
        format="json",
        HTTP_AUTHORIZATION="Token abc123",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_TOKEN_DOES_NOT_EXIST"

    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table_1.id}),
        format="json",
        HTTP_AUTHORIZATION=f"Token {wrong_token.key}",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_NO_PERMISSION_TO_TABLE"

    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table_1.id}),
        format="json",
        HTTP_AUTHORIZATION=f"Token {token.key}",
    )
    assert response.status_code == HTTP_200_OK

    response = api_client.delete(
        reverse(
            "api:groups:item",
            kwargs={"group_id": table_1.database.group.id},
        ),
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_204_NO_CONTENT
    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table_1.id}),
        **{"HTTP_AUTHORIZATION": f"JWT {jwt_token}"},
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_TABLE_DOES_NOT_EXIST"


@pytest.mark.django_db
def test_create_field(api_client, data_fixture):
    user, jwt_token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    table_2 = data_fixture.create_database_table()

    token = TokenHandler().create_token(user, table.database.group, "Good")
    wrong_token = TokenHandler().create_token(user, table.database.group, "Wrong")
    TokenHandler().update_token_permissions(user, wrong_token, True, True, True, True)

    # Test operation with JWT token
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Test 1", "type": "NOT_EXISTING"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_REQUEST_BODY_VALIDATION"
    assert response_json["detail"]["type"][0]["code"] == "invalid_choice"

    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": 99999}),
        {"name": "Test 1", "type": "text"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_TABLE_DOES_NOT_EXIST"

    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table_2.id}),
        {"name": "Test 1", "type": "text"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_USER_NOT_IN_GROUP"

    field_limit = settings.MAX_FIELD_LIMIT
    settings.MAX_FIELD_LIMIT = 0
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Test 1", "type": "text"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_MAX_FIELD_COUNT_EXCEEDED"
    settings.MAX_FIELD_LIMIT = field_limit

    url = reverse("api:database:fields:list", kwargs={"table_id": table_2.id})
    response = api_client.get(url)
    assert response.status_code == HTTP_401_UNAUTHORIZED

    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Test 1", "type": "text", "text_default": "default!"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["type"] == "text"

    text = TextField.objects.filter()[0]
    assert response_json["id"] == text.id
    assert response_json["name"] == text.name
    assert response_json["order"] == text.order
    assert response_json["text_default"] == "default!"

    # Test authentication with token
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Test 1", "type": "text"},
        format="json",
        HTTP_AUTHORIZATION="Token abc123",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_TOKEN_DOES_NOT_EXIST"

    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Test 1", "type": "text"},
        format="json",
        HTTP_AUTHORIZATION=f"Token {wrong_token.key}",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_NO_PERMISSION_TO_TABLE"

    # Even with a token that have all permissions, the call should be rejected
    # for now.
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Test 1", "type": "text"},
        format="json",
        HTTP_AUTHORIZATION=f"Token {token.key}",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_NO_PERMISSION_TO_TABLE"

    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": text.name, "type": "text"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_FIELD_WITH_SAME_NAME_ALREADY_EXISTS"

    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "id", "type": "text"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_RESERVED_BASEROW_FIELD_NAME"

    # Test creating field with too long name
    too_long_field_name = "x" * 256
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": too_long_field_name, "type": "text"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_REQUEST_BODY_VALIDATION"


@pytest.mark.django_db
def test_get_field(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token()
    user_2, token_2 = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    table_2 = data_fixture.create_database_table(user=user_2)
    text = data_fixture.create_text_field(table=table)
    number = data_fixture.create_number_field(table=table_2)

    url = reverse("api:database:fields:item", kwargs={"field_id": number.id})
    response = api_client.get(url, format="json", HTTP_AUTHORIZATION=f"JWT {token}")
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_USER_NOT_IN_GROUP"

    url = reverse("api:database:fields:item", kwargs={"field_id": 99999})
    response = api_client.get(url, format="json", HTTP_AUTHORIZATION=f"JWT {token}")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_FIELD_DOES_NOT_EXIST"

    url = reverse("api:database:fields:item", kwargs={"field_id": text.id})
    response = api_client.get(url, format="json", HTTP_AUTHORIZATION=f"JWT {token}")
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["id"] == text.id
    assert response_json["name"] == text.name
    assert response_json["table_id"] == text.table_id
    assert not response_json["text_default"]

    response = api_client.delete(
        reverse(
            "api:groups:item",
            kwargs={"group_id": table.database.group.id},
        ),
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_204_NO_CONTENT
    url = reverse("api:database:fields:item", kwargs={"field_id": text.id})
    response = api_client.get(url, format="json", HTTP_AUTHORIZATION=f"JWT {token}")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_FIELD_DOES_NOT_EXIST"


@pytest.mark.django_db
def test_update_field(api_client, data_fixture):
    """
    @TODO somehow trigger the CannotChangeFieldType and test if the correct
        ERROR_CANNOT_CHANGE_FIELD_TYPE error is returned.
    """

    user, token = data_fixture.create_user_and_token()
    user_2, token_2 = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    table_2 = data_fixture.create_database_table(user=user_2)
    text = data_fixture.create_text_field(table=table, primary=True)
    text_2 = data_fixture.create_text_field(table=table_2)
    existing_field = data_fixture.create_text_field(table=table, name="existing_field")

    url = reverse("api:database:fields:item", kwargs={"field_id": text_2.id})
    response = api_client.patch(
        url, {"name": "Test 1"}, format="json", HTTP_AUTHORIZATION=f"JWT {token}"
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_USER_NOT_IN_GROUP"

    url = reverse("api:database:fields:item", kwargs={"field_id": 999999})
    response = api_client.patch(
        url, {"name": "Test 1"}, format="json", HTTP_AUTHORIZATION=f"JWT {token}"
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_FIELD_DOES_NOT_EXIST"

    # The primary field is not compatible with a link row field so that should result
    # in an error.
    url = reverse("api:database:fields:item", kwargs={"field_id": text.id})
    response = api_client.patch(
        url, {"type": "link_row"}, format="json", HTTP_AUTHORIZATION=f"JWT {token}"
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_INCOMPATIBLE_PRIMARY_FIELD_TYPE"
    assert (
        response.json()["detail"]
        == "The field type link_row is not compatible with the primary field."
    )

    url = reverse("api:database:fields:item", kwargs={"field_id": text.id})
    response = api_client.patch(
        url,
        {"UNKNOWN_FIELD": "Test 1"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_200_OK

    url = reverse("api:database:fields:item", kwargs={"field_id": text.id})
    response = api_client.patch(
        url,
        {"name": "Test 1", "text_default": "Something"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["id"] == text.id
    assert response_json["name"] == "Test 1"
    assert response_json["text_default"] == "Something"

    text.refresh_from_db()
    assert text.name == "Test 1"
    assert text.text_default == "Something"

    url = reverse("api:database:fields:item", kwargs={"field_id": text.id})
    response = api_client.patch(
        url,
        {"name": "Test 1", "type": "text", "text_default": "Something"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["name"] == "Test 1"
    assert response_json["type"] == "text"

    url = reverse("api:database:fields:item", kwargs={"field_id": text.id})
    response = api_client.patch(
        url,
        {"type": "number", "number_negative": True},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["name"] == "Test 1"
    assert response_json["type"] == "number"
    assert response_json["number_decimal_places"] == 0
    assert response_json["number_negative"]

    url = reverse("api:database:fields:item", kwargs={"field_id": text.id})
    response = api_client.patch(
        url,
        {
            "number_decimal_places": 2,
            "number_negative": False,
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["name"] == "Test 1"
    assert response_json["type"] == "number"
    assert response_json["number_decimal_places"] == 2
    assert not response_json["number_negative"]

    url = reverse("api:database:fields:item", kwargs={"field_id": text.id})
    response = api_client.patch(
        url,
        {"type": "boolean", "name": "Test 2"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["name"] == "Test 2"
    assert response_json["type"] == "boolean"
    assert "number_decimal_places" not in response_json
    assert "number_negative" not in response_json

    url = reverse("api:database:fields:item", kwargs={"field_id": text.id})
    response = api_client.patch(
        url, {"name": "id"}, format="json", HTTP_AUTHORIZATION=f"JWT {token}"
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_RESERVED_BASEROW_FIELD_NAME"

    url = reverse("api:database:fields:item", kwargs={"field_id": text.id})
    response = api_client.patch(
        url,
        {"name": existing_field.name},
        format="json",
        HTTP_AUTHORIZATION=f"JWT" f" {token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_FIELD_WITH_SAME_NAME_ALREADY_EXISTS"

    too_long_field_name = "x" * 256
    url = reverse("api:database:fields:item", kwargs={"field_id": text.id})
    response = api_client.patch(
        url,
        {"name": too_long_field_name},
        format="json",
        HTTP_AUTHORIZATION=f"JWT" f" {token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_REQUEST_BODY_VALIDATION"


@pytest.mark.django_db
def test_update_field_number_type_deprecation_error(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    number_field = data_fixture.create_number_field(
        table=table, number_decimal_places=1
    )

    url = reverse("api:database:fields:item", kwargs={"field_id": number_field.id})
    response = api_client.patch(
        url,
        {"number_type": "INTEGER"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_REQUEST_BODY_VALIDATION"
    assert response.json()["detail"]["number_type"][0]["error"] == (
        "The number_type option has been removed and can no longer be provided. "
        "Instead set number_decimal_places to 0 for an integer or 1-5 for a "
        "decimal."
    )


@pytest.mark.django_db
def test_delete_field(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token()
    user_2, token_2 = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    table_2 = data_fixture.create_database_table(user=user_2)
    text = data_fixture.create_text_field(table=table)
    number = data_fixture.create_number_field(table=table_2)

    url = reverse("api:database:fields:item", kwargs={"field_id": number.id})
    response = api_client.delete(url, HTTP_AUTHORIZATION=f"JWT {token}")
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_USER_NOT_IN_GROUP"

    url = reverse("api:database:fields:item", kwargs={"field_id": 99999})
    response = api_client.delete(url, HTTP_AUTHORIZATION=f"JWT {token}")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_FIELD_DOES_NOT_EXIST"

    url = reverse("api:database:fields:item", kwargs={"field_id": text.id})
    response = api_client.delete(url, HTTP_AUTHORIZATION=f"JWT {token}")
    assert response.status_code == 200

    assert Field.objects.all().count() == 1
    assert TextField.objects.all().count() == 0
    assert NumberField.objects.all().count() == 1

    table_3 = data_fixture.create_database_table(user=user)
    primary = data_fixture.create_text_field(table=table_3, primary=True)

    url = reverse("api:database:fields:item", kwargs={"field_id": primary.id})
    response = api_client.delete(url, HTTP_AUTHORIZATION=f"JWT {token}")
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_CANNOT_DELETE_PRIMARY_FIELD"


@pytest.mark.django_db
def test_unique_row_values(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token(
        email="11@11.com", password="password", first_name="abcd"
    )
    table = data_fixture.create_database_table(user=user)
    text_field = data_fixture.create_text_field(table=table, order=0, name="Letter")
    grid = data_fixture.create_grid_view(table=table)
    model = grid.table.get_model()

    url = reverse(
        "api:database:fields:unique_row_values", kwargs={"field_id": text_field.id}
    )

    # Check for empty values
    response = api_client.get(url, HTTP_AUTHORIZATION=f"JWT {token}")
    response_json = response.json()

    assert response.status_code == HTTP_200_OK
    assert response_json["values"] == []

    # Check that values are sorted by frequency
    values = ["A", "B", "B", "B", "C", "C"]
    for value in values:
        model.objects.create(**{f"field_{text_field.id}": value})

    response = api_client.get(url, HTTP_AUTHORIZATION=f"JWT {token}")
    response_json = response.json()

    assert response.status_code == HTTP_200_OK
    assert response_json["values"] == ["B", "C", "A"]

    # Check that limit is working
    response = api_client.get(url, {"limit": 1}, HTTP_AUTHORIZATION=f"JWT {token}")
    response_json = response.json()

    assert response.status_code == HTTP_200_OK
    assert len(response_json["values"]) == 1

    # Check for non-existent field
    url = reverse("api:database:fields:unique_row_values", kwargs={"field_id": 9999})
    response = api_client.get(url, HTTP_AUTHORIZATION=f"JWT {token}")
    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_unique_row_values_splitted_by_comma(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token(
        email="11@11.com", password="password", first_name="abcd"
    )
    table = data_fixture.create_database_table(user=user)
    text_field = data_fixture.create_text_field(table=table, order=0, name="Letter")
    grid = data_fixture.create_grid_view(table=table)
    model = grid.table.get_model()

    # Check that values are sorted by frequency
    values = ["A,B", "C,D,E", "F,E", "G,E", "E", "F", "E,E"]
    for value in values:
        model.objects.create(**{f"field_{text_field.id}": value})

    url = reverse(
        "api:database:fields:unique_row_values", kwargs={"field_id": text_field.id}
    )
    response = api_client.get(
        url, {"split_comma_separated": "true"}, HTTP_AUTHORIZATION=f"JWT {token}"
    )
    response_json = response.json()

    assert response.status_code == HTTP_200_OK
    assert response_json["values"] == ["E", "F", "C", "D", "B", "G", "A"]


@pytest.mark.django_db
def test_unique_row_values_incompatible_field_type(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token(
        email="11@11.com", password="password", first_name="abcd"
    )
    table = data_fixture.create_database_table(user=user)
    # The file field is not compatible.
    file_field = data_fixture.create_file_field(table=table, order=0)

    url = reverse(
        "api:database:fields:unique_row_values", kwargs={"field_id": file_field.id}
    )
    response = api_client.get(url, HTTP_AUTHORIZATION=f"JWT {token}")
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_INCOMPATIBLE_FIELD_TYPE_FOR_UNIQUE_VALUES"


@pytest.mark.django_db(transaction=True)
def test_update_field_returns_with_error_if_cant_lock_field_if_locked_for_update(
    api_client, data_fixture
):
    user, token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    text_field = data_fixture.create_text_field(user, table=table)

    url = reverse("api:database:fields:item", kwargs={"field_id": text_field.id})
    with independent_test_db_connection() as conn:
        with conn.cursor() as cursor:
            # nosec
            cursor.execute(
                f"SELECT * FROM database_field where id = {text_field.id} "
                f"FOR UPDATE"
            )
            response = api_client.patch(
                url,
                {"name": "Test 1"},
                format="json",
                HTTP_AUTHORIZATION=f"JWT {token}",
            )
    response_json = response.json()
    assert response.status_code == HTTP_409_CONFLICT
    assert response_json["error"] == "ERROR_FAILED_TO_LOCK_FIELD_DUE_TO_CONFLICT"


@pytest.mark.django_db(transaction=True)
def test_update_field_returns_with_error_if_cant_lock_field_if_locked_for_key_share(
    api_client, data_fixture
):
    user, token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    text_field = data_fixture.create_text_field(user, table=table)

    url = reverse("api:database:fields:item", kwargs={"field_id": text_field.id})
    with independent_test_db_connection() as conn:
        with conn.cursor() as cursor:
            # nosec
            cursor.execute(
                f"SELECT * FROM database_field where id = {text_field.id} FOR KEY SHARE"
            )
            response = api_client.patch(
                url,
                {"name": "Test 1"},
                format="json",
                HTTP_AUTHORIZATION=f"JWT {token}",
            )
    response_json = response.json()
    assert response.status_code == HTTP_409_CONFLICT
    assert response_json["error"] == "ERROR_FAILED_TO_LOCK_FIELD_DUE_TO_CONFLICT"


@pytest.mark.django_db(transaction=True)
def test_update_field_returns_with_error_if_cant_lock_table_if_locked_for_update(
    api_client, data_fixture, django_assert_num_queries
):
    user, token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    text_field = data_fixture.create_text_field(user, table=table)

    url = reverse("api:database:fields:item", kwargs={"field_id": text_field.id})
    with independent_test_db_connection() as conn:
        with conn.cursor() as cursor:
            # nosec
            cursor.execute(
                f"SELECT * FROM database_table where id = {table.id} FOR UPDATE"
            )
            response = api_client.patch(
                url,
                {"name": "Test 1"},
                format="json",
                HTTP_AUTHORIZATION=f"JWT {token}",
            )
    response_json = response.json()
    assert response.status_code == HTTP_409_CONFLICT
    assert response_json["error"] == "ERROR_FAILED_TO_LOCK_FIELD_DUE_TO_CONFLICT"


@pytest.mark.django_db(transaction=True)
def test_update_field_returns_with_error_if_cant_lock_table_if_locked_for_key_share(
    api_client, data_fixture
):
    user, token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    text_field = data_fixture.create_text_field(user, table=table)

    url = reverse("api:database:fields:item", kwargs={"field_id": text_field.id})
    with independent_test_db_connection() as conn:
        with conn.cursor() as cursor:
            # nosec
            cursor.execute(
                f"SELECT * FROM database_table where id = {table.id} FOR KEY SHARE"
            )
            response = api_client.patch(
                url,
                {"name": "Test 1"},
                format="json",
                HTTP_AUTHORIZATION=f"JWT {token}",
            )
    response_json = response.json()
    assert response.status_code == HTTP_409_CONFLICT
    assert response_json["error"] == "ERROR_FAILED_TO_LOCK_FIELD_DUE_TO_CONFLICT"


@pytest.mark.django_db(transaction=True)
def test_create_field_returns_with_error_if_cant_lock_table_if_locked_for_update(
    api_client, data_fixture
):
    user, token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)

    with independent_test_db_connection() as conn:
        with conn.cursor() as cursor:
            # nosec
            cursor.execute(
                f"SELECT * FROM database_table where id = {table.id} FOR UPDATE"
            )
            response = api_client.post(
                reverse("api:database:fields:list", kwargs={"table_id": table.id}),
                {"name": "Test 1", "type": "text"},
                format="json",
                HTTP_AUTHORIZATION=f"JWT {token}",
            )
    response_json = response.json()
    assert response.status_code == HTTP_409_CONFLICT
    assert response_json["error"] == "ERROR_FAILED_TO_LOCK_TABLE_DUE_TO_CONFLICT"


@pytest.mark.django_db(transaction=True)
def test_create_field_returns_with_error_if_cant_lock_table_if_locked_for_key_share(
    api_client, data_fixture
):
    user, token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)

    with independent_test_db_connection() as conn:
        with conn.cursor() as cursor:
            # nosec
            cursor.execute(
                f"SELECT * FROM database_table where id = {table.id} FOR KEY SHARE"
            )
            response = api_client.post(
                reverse("api:database:fields:list", kwargs={"table_id": table.id}),
                {"name": "Test 1", "type": "text"},
                format="json",
                HTTP_AUTHORIZATION=f"JWT {token}",
            )
    response_json = response.json()
    assert response.status_code == HTTP_409_CONFLICT
    assert response_json["error"] == "ERROR_FAILED_TO_LOCK_TABLE_DUE_TO_CONFLICT"
