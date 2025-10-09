from http import HTTPStatus
import pytest
from pytest_lazy_fixtures import lf
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    [
        ('news:home', None),
        ('news:detail', lf('news_id_for_args')),
        ('users:login', None),
        ('users:signup', None),
    ],
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """
    Проверяет, что анонимному пользователю доступны:
    - главная страница новостей;
    - страница отдельной новости;
    - страницы входа, регистрации и выхода.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    [
        (lf('author_client'), HTTPStatus.OK),
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
    ],
)
@pytest.mark.parametrize(
    'name',
    ['news:edit', 'news:delete'],
)
def test_comment_pages_availability_for_different_users(
    parametrized_client, name, comment, expected_status
):
    """
    Проверяет доступ к страницам редактирования и удаления комментариев:
    - Автор комментария получает статус 200 (OK);
    - Чужой пользователь — 404 (NOT FOUND).
    """
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ['news:edit', 'news:delete'],
)
def test_redirects_for_anonymous_user(client, name, comment):
    """
    Проверяет, что анонимный пользователь при попытке перейти на
    страницы редактирования или удаления комментария перенаправляется
    на страницу логина.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_redirect = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_redirect)
