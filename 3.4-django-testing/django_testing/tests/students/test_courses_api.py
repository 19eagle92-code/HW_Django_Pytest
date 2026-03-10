import pytest
from django.urls import reverse
from rest_framework import status

from students.models import Course


@pytest.mark.django_db
def test_create_course(api_client):
    """Тест создания курса"""
    url = reverse("courses-list")
    data = {
        "name": "Django",
    }

    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == data["name"]
    assert Course.objects.count() == 1
    assert Course.objects.get().name == data["name"]


@pytest.mark.django_db
def test_retrieve_course(api_client, course_factory):
    """тест на получение курса"""
    course = course_factory(name="Python")

    url = reverse("courses-detail", args=[course.id])
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == course.id
    assert response.data["name"] == course.name


@pytest.mark.django_db
def test_update_course(api_client, course_factory):
    """Тест на обновление курса"""
    course = course_factory(name="Old name")

    url = reverse("courses-detail", args=[course.id])
    data = {
        "name": "New name",
    }

    response = api_client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == course.id
    assert response.data["name"] == data["name"]

    course.refresh_from_db()
    assert course.name == data["name"]


@pytest.mark.django_db
def test_delete_course(api_client, course_factory):
    """Тест по обновлению курса"""
    course = course_factory()

    url = reverse("courses-detail", args=[course.id])
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Course.objects.filter(id=course.id).count() == 0


@pytest.mark.django_db
def test_list_courses(api_client, course_factory):
    """Тест на получение списка курсов"""
    courses = course_factory(_quantity=3)

    url = reverse("courses-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == len(courses)

    returned_ids = [item["id"] for item in response.data]
    expected_ids = [course.id for course in courses]

    assert returned_ids == expected_ids


@pytest.mark.django_db
def test_filter_courses_by_id(api_client, course_factory):
    """Тест фильтрация по id"""
    courses = course_factory(_quantity=3)
    target_course = courses[0]

    url = reverse("courses-list")
    response = api_client.get(url, data={"id": target_course.id})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == target_course.id
    assert response.data[0]["name"] == target_course.name


@pytest.mark.django_db
def test_filter_courses_by_name(api_client, course_factory):
    """Тест фильтрация по имени"""
    target_course = course_factory(name="Python")
    course_factory(name="Java")
    course_factory(name="C++")

    url = reverse("courses-list")
    response = api_client.get(url, data={"name": "Python"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == target_course.id
    assert response.data[0]["name"] == target_course.name
