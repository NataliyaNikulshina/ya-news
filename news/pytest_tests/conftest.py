import pytest
from django.contrib.auth import get_user_model
from news.models import News, Comment

User = get_user_model()


@pytest.fixture
def author(db):
    return User.objects.create_user(username='Автор', password='pass')


@pytest.fixture
def not_author(db):
    return User.objects.create_user(username='Другой', password='pass')


@pytest.fixture
def news(db):
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def comment(db, author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Комментарий'
    )


@pytest.fixture
def client(client):
    return client


@pytest.fixture
def author_client(client, author):
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(client, not_author):
    client.force_login(not_author)
    return client


@pytest.fixture
def news_id_for_args(news):
    """Помощная фикстура, чтобы передавать id новости в parametrize."""
    return (news.id,)


User = get_user_model()


@pytest.fixture
def author(db):
    return User.objects.create_user(username='Автор', password='123')


@pytest.fixture
def author_client(client, author):
    client.force_login(author)
    return client


@pytest.fixture
def author(db):
    return User.objects.create_user(username='Автор', password='123')


@pytest.fixture
def not_author(db):
    return User.objects.create_user(username='Не автор', password='321')


@pytest.fixture
def author_client(client, author):
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(client, not_author):
    client.force_login(not_author)
    return client
