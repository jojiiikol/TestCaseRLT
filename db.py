from datetime import datetime

import asyncpg
from asyncpg import connect
import json
from config import DatabaseConfig

class DBManager:
    def __init__(self, config: DatabaseConfig = DatabaseConfig()):
        self.user = config.user
        self.host = config.host
        self.database = config.database
        self.password = config.password

    async def __aenter__(self):
        self.connection = await asyncpg.connect(user=self.user, host=self.host, database=self.database,
                                           password=self.password)
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connection.close()

class Database:

    async def check_tables(self):
        async with DBManager() as connection:
            result = await connection.fetch("SELECT * FROM videos LIMIT 5;")
        return result


    async def import_data(self):
        with open("videos.json", "r") as f:
            data = json.load(f)

        async with DBManager() as connection:
            for video in data['videos']:
                await connection.execute("""
                    INSERT INTO videos (id, video_created_at, views_count, likes_count, reports_count,
                                        comments_count, creator_id, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (id) DO NOTHING
                    """,
                                   video['id'],
                                   datetime.fromisoformat(video['video_created_at']),
                                   video['views_count'],
                                   video['likes_count'],
                                   video['reports_count'],
                                   video['comments_count'],
                                   video['creator_id'],
                                   datetime.fromisoformat(video['created_at']),
                                   datetime.fromisoformat(video['updated_at'])
                                   )

                for snap in video.get('snapshots', []):
                    await connection.execute("""
                        INSERT INTO video_snapshots (id, video_id, views_count, likes_count, reports_count,
                                               comments_count, delta_views_count, delta_likes_count,
                                               delta_reports_count, delta_comments_count, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                        ON CONFLICT (id) DO NOTHING
                        """,
                                       snap['id'],
                                       snap['video_id'],
                                       snap['views_count'],
                                       snap['likes_count'],
                                       snap['reports_count'],
                                       snap['comments_count'],
                                       snap['delta_views_count'],
                                       snap['delta_likes_count'],
                                       snap['delta_reports_count'],
                                       snap['delta_comments_count'],
                                       datetime.fromisoformat(snap['created_at']),
                                       datetime.fromisoformat(snap['updated_at'])
                                       )
    async def init_database(self):
        datas = await self.check_tables()
        if datas:
            return
        await self.import_data()
        print("Database initialized")

    async def get_data(self, query: str):
        async with DBManager() as connection:
            result = await connection.fetch(query)
        return str(result[0][0])

