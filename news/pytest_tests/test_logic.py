import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import News, Comment


@pytest.fixture
def news(db):
    """Создаёт новость для тестов."""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def comment(author, news):
    """Создаёт комментарий, принадлежащий автору."""
    return Comment.objects.create(news=news, 
                                  author=author, 
                                  text='Текст комментария')


@pytest.fixture
def form_data():
    """Данные для формы комментария."""
    return {'text': 'Текст комментария'}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authorized_user_can_create_comment(author_client,
                                            author,
                                            news,
                                            form_data):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    # Проверяем редирект к секции комментариев
    assertRedirects(response, f'{url}#comments')
    # Проверяем, что комментарий создался
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_comment_with_bad_words_not_created(author_client, news):
    """Если комментарий содержит запрещённые слова, он не будет опубликован."""
    url = reverse('news:detail', args=(news.id,))
    bad_text = f'Текст с {BAD_WORDS[0]} внутри'
    response = author_client.post(url, data={'text': bad_text})
    form = response.context['form']
    assertFormError(form, 'text', WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment):
    """Авторизованный пользователь может редактировать свой комментарий."""
    url = reverse('news:edit', args=(comment.id,))
    new_text = 'Обновлённый комментарий'
    response = author_client.post(url, data={'text': new_text})
    assertRedirects(response, reverse('news:detail',
                                      args=(comment.news.id,)) + '#comments')
    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    """Авторизованный пользователь может удалить свой комментарий."""
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)
    assertRedirects(response, reverse('news:detail',
                                      args=(comment.news.id,)) + '#comments')
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_other_user_cant_edit_comment(not_author_client, comment):
    """Авторизованный пользователь не может редактировать чужой комментарий."""
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, data={'text': 'Попытка взлома'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'


@pytest.mark.django_db
def test_other_user_cant_delete_comment(not_author_client, comment):
    """Авторизованный пользователь не может удалить чужой комментарий."""
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
