-- Made-up bronze rows for the local dev database only, shaped like real payloads. Never run this on prod.
-- Includes the awkward cases staging must handle: re-fetched stock days, a corrected price,
-- the same Trends window fetched twice, and an early YouTube row that only covered two videos.
truncate bronze.raw_payload;

insert into bronze.raw_payload (source, endpoint, run_id, fetched_at, payload) values
('youtube', 'videos.list', 'sample-1', '2026-11-06 06:41:49+00',
 '{"kind": "youtube#videoListResponse", "items": [
    {"id": "QdBZY2fkU-0", "kind": "youtube#video", "statistics": {"viewCount": "1000", "likeCount": "100", "commentCount": "10", "favoriteCount": "0"}},
    {"id": "VQRLujxTm3c", "kind": "youtube#video", "statistics": {"viewCount": "500", "likeCount": "50", "commentCount": "5", "favoriteCount": "0"}}]}'),
('youtube', 'videos.list', 'sample-2', '2026-11-07 18:17:19+00',
 '{"items": [
    {"id": "QdBZY2fkU-0", "statistics": {"viewCount": "1100", "likeCount": "101", "commentCount": "11", "favoriteCount": "0"}},
    {"id": "VQRLujxTm3c", "statistics": {"viewCount": "520", "likeCount": "51", "commentCount": "5", "favoriteCount": "0"}},
    {"id": "rz1B4B2yBZY", "statistics": {"viewCount": "300", "likeCount": "30", "commentCount": "3", "favoriteCount": "0"}}]}'),

('yfinance', 'history', 'sample-3', '2026-11-06 22:30:00+00',
 '{"ticker": "TTWO", "start": "2026-10-27", "bars": [
    {"date": "2026-11-05", "open": 210, "high": 215, "low": 209, "close": 214, "adj_close": 214, "volume": 1000000},
    {"date": "2026-11-06", "open": 214, "high": 216, "low": 212, "close": 213, "adj_close": 213, "volume": 1200000}]}'),
('yfinance', 'history', 'sample-4', '2026-11-07 11:11:38+00',
 '{"ticker": "TTWO", "start": "2026-10-28", "bars": [
    {"date": "2026-11-05", "open": 210, "high": 215, "low": 209, "close": 214, "adj_close": 214, "volume": 1000000},
    {"date": "2026-11-06", "open": 214, "high": 216, "low": 212, "close": 214.87, "adj_close": 214.87, "volume": 1250000}]}'),
('yfinance', 'history', 'sample-4', '2026-11-07 11:11:40+00',
 '{"ticker": "^GSPC", "start": "2026-10-28", "bars": [
    {"date": "2026-11-05", "open": 7300, "high": 7350, "low": 7290, "close": 7340, "adj_close": 7340, "volume": 3000000000},
    {"date": "2026-11-06", "open": 7340, "high": 7390, "low": 7330, "close": 7376.86, "adj_close": 7376.86, "volume": 3100000000}]}'),

('google_trends', 'interest_over_time', 'sample-5', '2026-11-09 03:53:00+00',
 '{"term": "GTA 6", "geo": "worldwide", "start": "2026-05-13", "end": "2026-11-08", "points": [
    {"date": "2026-11-07", "value": 47, "is_partial": false},
    {"date": "2026-11-08", "value": 50, "is_partial": true}]}'),
('google_trends', 'interest_over_time', 'sample-6', '2026-11-09 15:53:00+00',
 '{"term": "GTA 6", "geo": "worldwide", "start": "2026-05-13", "end": "2026-11-08", "points": [
    {"date": "2026-11-07", "value": 47, "is_partial": false},
    {"date": "2026-11-08", "value": 52, "is_partial": false}]}'),

('twitch', 'streams', 'sample-7', '2026-11-12 00:30:00+00',
 '{"game_id": "000000", "game_name": "Grand Theft Auto VI", "viewer_count": 250000, "stream_count": 4000, "truncated": false}');
