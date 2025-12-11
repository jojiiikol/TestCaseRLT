CREATE TABLE IF NOT EXISTS videos (
                id UUID PRIMARY KEY,
                video_created_at TIMESTAMPTZ,
                views_count INT,
                likes_count INT,
                reports_count INT,
                comments_count INT,
                creator_id UUID,
                created_at TIMESTAMPTZ,
                updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS video_snapshots (
                id UUID PRIMARY KEY,
                video_id UUID REFERENCES videos(id),
                views_count INT,
                likes_count INT,
                reports_count INT,
                comments_count INT,
                delta_views_count INT,
                delta_likes_count INT,
                delta_reports_count INT,
                delta_comments_count INT,
                created_at TIMESTAMPTZ,
                updated_at TIMESTAMPTZ
);