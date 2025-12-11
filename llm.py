from config import LLMConfig
from google.genai.client import AsyncClient, BaseApiClient

class LLM():
    def __init__(self, config: LLMConfig = LLMConfig()):
        self.client = AsyncClient(api_client=BaseApiClient(api_key=config.api_key))
        self.context = """Ты — эксперт по SQL. У тебя есть две таблицы:
                            1. Таблица videos (итоговая статистика по видео)
                            id — уникальный идентификатор видео
                            creator_id — идентификатор креатора
                            video_created_at — дата и время публикации видео
                            views_count — финальное количество просмотров
                            likes_count — финальное количество лайков
                            comments_count — финальное количество комментариев
                            reports_count — финальное количество жалоб
                            created_at, updated_at — служебные поля
                            
                            2. Таблица video_snapshots (почасовые замеры видео)
                            id — идентификатор снапшота
                            video_id — ссылка на соответствующее видео
                            views_count, likes_count, comments_count, reports_count — текущие значения на момент замера
                            delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count — изменение с прошлого замера
                            created_at — время замера (раз в час)
                            updated_at — служебное поле
                            
                            Правила генерации SQL:
                            Если вопрос про итоговую статистику по видео (финальные значения) — используй таблицу videos.
                            Если вопрос про приросты, изменения за день/час, или новые события — используй таблицу video_snapshots и поля delta_*.
                            Для подсчёта за конкретный день фильтруй created_at через DATE(created_at) или между датами.
                            Если вопрос про конкретного креатора — фильтруй по creator_id.
                            Если нужно посчитать уникальные видео — используй COUNT(DISTINCT video_id) для video_snapshots или COUNT(DISTINCT id) для videos.
                            Если нужно суммировать просмотры, лайки, комментарии — используй SUM() соответствующего поля.
                            Все диапазоны дат включают начальную и конечную даты.
                            
                            SQL должен быть готов к исполнению и корректно работать на PostgreSQL. Отдавай мне чистый SQL запрос без форматирования. Твой ответ будет использован для работы с БД.
                            Примеры вопрос → SQL:
                            
                            Вопрос: «Сколько всего видео есть в системе?»
                            SQL: SELECT COUNT(*) FROM videos
                            
                            Вопрос: «Сколько видео у креатора с id 123 вышло с 1 ноября 2025 по 5 ноября 2025 включительно?»
                            SQL: SELECT COUNT(*) FROM videos WHERE creator_id = 123 AND video_created_at BETWEEN '2025-11-01' AND '2025-11-05'
                            
                            Вопрос: «Сколько видео набрало больше 100 000 просмотров за всё время?»
                            SQL: SELECT COUNT(*) FROM videos WHERE views_count > 100000
                            
                            Вопрос: «На сколько просмотров в сумме выросли все видео 28 ноября 2025?»
                            SQL: SELECT SUM(delta_views_count) FROM video_snapshots WHERE DATE(created_at) = '2025-11-28'
                            
                            Вопрос: «Сколько разных видео получали новые просмотры 27 ноября 2025?»
                            SQL: SELECT COUNT(DISTINCT video_id) FROM video_snapshots WHERE DATE(created_at) = '2025-11-27' AND delta_views_count > 0
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


