import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from news.forms import CommentForm


@pytest.fixture
def news_list(db):
    """Создает 11 новостей с разными датами."""
    from news.models import News
    today = timezone.now().date()
    return News.objects.bulk_create([
        News(
            title=f'Новость {i}',
            text='Просто текст.',
            date=today - timedelta(days=i)
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ])


@pytest.fixture
def news(news_list):
    """Возвращает самую свежую новость (первая в списке)."""
    return news_list[0]


@pytest.fixture
def comments(db, news, author):
    """Создает 10 комментариев к новости с возрастающими временными метками."""
    from news.models import Comment
    now = timezone.now()
    comments = []
    for i in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}'
        )
        comment.created = now + timedelta(minutes=i)
        comment.save()
        comments.append(comment)
    return comments


@pytest.mark.django_db
def test_news_count_on_home_page(client, news_list):
    """Проверяет, что на главной странице отображается не более 10 новостей."""
    url = reverse('news:home')
    response = client.get(url)
    news_feed = response.context['news_feed']
    assert news_feed.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order_on_home_page(client, news_list):
    """
    Проверяет, что новости отсортированы по дате:
    от самой свежей (первой) к самой старой (последней).
    """
    url = reverse('news:home')
    response = client.get(url)
    news_feed = response.context['news_feed']
    all_dates = [news.date for news in news_feed]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order_on_detail_page(client, news, comments):
    """
    Проверяет, что комментарии на странице новости отсортированы
    по возрастанию времени создания (старые в начале, новые в конце).
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    news_in_context = response.context['news']
    comment_list = news_in_context.comment_set.all()
    all_timestamps = [c.created for c in comment_list]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_user_has_no_comment_form(client, news):
    """
    Проверяет, что анонимному пользователю недоступна форма
    добавления комментария на странице новости.
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_user_has_comment_form(author_client, news):
    """
    Проверяет, что авторизованный пользователь видит форму
    для добавления комментария на странице новости.
    """
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
