from config import LLMConfig
from google.genai.client import AsyncClient, BaseApiClient


class LLM():
    def __init__(self, config: LLMConfig = LLMConfig()):
        self.client = AsyncClient(api_client=BaseApiClient(api_key=config.api_key))
        self.context = """Ты — эксперт по SQL. Твоя задача — по любому запросу на естественном языке генерировать корректный SQL-запрос строго по правилам ниже. SQL должен работать на PostgreSQL и MySQL.
                            У тебя есть две таблицы.
                            Первая таблица — videos (итоговая статистика по ролику) со следующими полями: id (UUID, первичный ключ), creator_id (UUID), video_created_at (TIMESTAMPTZ — дата и время публикации видео), views_count, likes_count, comments_count, reports_count, created_at, updated_at.
                            Вторая таблица — video_snapshots (почасовые замеры по ролику) со следующими полями: id (UUID, первичный ключ), video_id (UUID, внешний ключ на videos.id), views_count, likes_count, comments_count, reports_count, delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count, created_at (TIMESTAMPTZ — время почасового замера), updated_at.
                            Правила генерации SQL:
                            Если нужно получить итоговые значения по ролику (например, финальные просмотры, лайки, количество видео), используй таблицу videos.
                            Если нужно получить изменения, приросты или показатели по часам/дням, используй таблицу video_snapshots и поля delta_*.
                            Фильтры по датам должны строго учитывать время. Никогда не используй BETWEEN для полей с датой-временем. Для диапазона дат (оба конца включительно) нужно писать: поле >= 'YYYY-MM-DD' AND поле < 'YYYY-MM-DD следующего дня/месяца'. Для выборки за конкретный день можно использовать DATE(поле) = 'YYYY-MM-DD'. Если в запросе описан диапазон по датам, всегда преобразуй его в диапазон >= начало и < конец+1 день. Пример: «за июнь 2025» означает video_created_at >= '2025-06-01' AND video_created_at < '2025-07-01'.
                            Фильтры по креатору записываются как creator_id = <id>.
                            Для подсчёта количества уникальных видео используй COUNT(DISTINCT id) для таблицы videos и COUNT(DISTINCT video_id) для таблицы video_snapshots.
                            Для суммирования используй SUM().
                            Ты должен генерировать только готовый SQL-запрос без пояснений, комментариев, описаний, кавычек вокруг самого SQL и без дополнительного текста.
                            
                            Примеры поведения:
                            «Сколько всего видео есть в системе?» → SELECT COUNT() FROM videos;
                            «Сколько видео у автора 123 опубликовано с 1 по 5 ноября 2025 включительно?» → SELECT COUNT() FROM videos WHERE video_created_at >= '2025-11-01' AND video_created_at < '2025-11-06';
                            «Сколько видео набрало больше 100000 просмотров?» → SELECT COUNT(*) FROM videos WHERE views_count > 100000;
                            «На сколько просмотров выросли все видео 28 ноября 2025?» → SELECT SUM(delta_views_count) FROM video_snapshots WHERE DATE(created_at) = '2025-11-28';
                            «Сколько разных видео получали новые просмотры 27 ноября 2025?» → SELECT COUNT(DISTINCT video_id) FROM video_snapshots WHERE DATE(created_at) = '2025-11-27' AND delta_views_count > 0;
                            
                            Задача: по любому запросу на естественном языке генерируй готовый SQL-запрос строго по этим правилам. Возвращай только SQL-запрос и ничего больше.
                            \n\n"""

    def create_promt(self, text: str):
        promt = self.context + text
        return promt

    async def get_answer(self, text: str):
        promt = self.create_promt(text)
        response = await self.client.models.generate_content(
            model="gemini-2.5-flash-lite", contents=promt
        )
        return response.text
