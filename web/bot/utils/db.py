# db.py faylini quyidagicha yangilang:

import asyncpg
import ssl
import os
import json
from typing import List, Optional
import logging

logger = logging.getLogger("bot")

class Database:
    def __init__(self, connection_string=None):
        if connection_string:
            self.connection_string = connection_string
        else:
            self.connection_string = os.getenv('DATABASE_URL')
        self.pool = None
    
    async def create_pool(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            ssl=ssl_context
        )
    
    async def create_tables(self):
        await self.create_pool()
        async with self.pool.acquire() as conn:
            
            # Foydalanuvchilar jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT UNIQUE,
                    username VARCHAR(100),
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    phone VARCHAR(20),
                    language VARCHAR(10) DEFAULT 'uz',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # E'lonlar jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS listings (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    category VARCHAR(50),
                    floor VARCHAR(20),
                    rooms VARCHAR(20),
                    title VARCHAR(200),
                    description TEXT,
                    price DECIMAL(15, 2),
                    currency VARCHAR(10) DEFAULT 'UZS',
                    phone VARCHAR(20),
                    optional_phone VARCHAR(20),
                    location TEXT,
                    file_ids JSONB,
                    status VARCHAR(20) DEFAULT 'pending',
                    views INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Rasmlar jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS listing_photos (
                    id SERIAL PRIMARY KEY,
                    listing_id INTEGER,
                    file_id VARCHAR(200),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE
                )
            ''')
            
            logger.info("✅ Database tables created successfully")
    
    async def add_user(self, user_id, username, first_name, last_name, phone=None, language="uz"):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (user_id, username, first_name, last_name, phone, language)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (user_id) DO UPDATE
                SET username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    phone = EXCLUDED.phone,
                    language = EXCLUDED.language
            """, user_id, username, first_name, last_name, phone, language)

    async def get_user(self, user_id: int):
        """Foydalanuvchini ID bo'yicha olish"""
        async with self.pool.acquire() as conn:
            try:
                user = await conn.fetchrow('''
                    SELECT * FROM users WHERE user_id = $1
                ''', user_id)
                return dict(user) if user else None
            except Exception as e:
                logger.error(f"❌ Error getting user: {e}")
                return None
    
    async def get_stats(self):
        """Statistika olish"""
        async with self.pool.acquire() as conn:
            try:
                # Foydalanuvchilar soni
                total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
                daily_users = await conn.fetchval("""
                    SELECT COUNT(*) FROM users 
                    WHERE created_at >= CURRENT_DATE
                """)
                weekly_users = await conn.fetchval("""
                    SELECT COUNT(*) FROM users 
                    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                """)
                monthly_users = await conn.fetchval("""
                    SELECT COUNT(*) FROM users 
                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                """)
                
                # E'lonlar soni
                total_listings = await conn.fetchval("SELECT COUNT(*) FROM listings")
                daily_listings = await conn.fetchval("""
                    SELECT COUNT(*) FROM listings 
                    WHERE created_at >= CURRENT_DATE
                """)
                weekly_listings = await conn.fetchval("""
                    SELECT COUNT(*) FROM listings 
                    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                """)
                monthly_listings = await conn.fetchval("""
                    SELECT COUNT(*) FROM listings 
                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                """)
                
                # Faol e'lonlar
                active_listings = await conn.fetchval("""
                    SELECT COUNT(*) FROM listings WHERE status = 'active'
                """)
                inactive_listings = await conn.fetchval("""
                    SELECT COUNT(*) FROM listings WHERE status = 'inactive'
                """)
                
                # E'lon joylagan foydalanuvchilar
                users_with_listings = await conn.fetchval("""
                    SELECT COUNT(DISTINCT user_id) FROM listings
                """)
                
                return {
                    "users": {
                        "total": total_users,
                        "daily": daily_users,
                        "weekly": weekly_users,
                        "monthly": monthly_users,
                        "with_listings": users_with_listings
                    },
                    "listings": {
                        "total": total_listings,
                        "daily": daily_listings,
                        "weekly": weekly_listings,
                        "monthly": monthly_listings,
                        "active": active_listings,
                        "inactive": inactive_listings
                    }
                }
            except Exception as e:
                logger.error(f"❌ Error getting stats: {e}")
                return {
                    "users": {"total": 0, "daily": 0, "weekly": 0, "monthly": 0, "with_listings": 0},
                    "listings": {"total": 0, "daily": 0, "weekly": 0, "monthly": 0, "active": 0, "inactive": 0}
                }
    
    async def get_all_users(self):
        """Barcha foydalanuvchilarni olish"""
        async with self.pool.acquire() as conn:
            try:
                users = await conn.fetch('''
                    SELECT * FROM users ORDER BY created_at DESC
                ''')
                return [dict(user) for user in users]
            except Exception as e:
                logger.error(f"❌ Error getting all users: {e}")
                return []
    
    async def add_listing(self, user_id: int, category: str, floor: str, rooms: str, 
                         title: str, description: str, price: float, currency: str,
                         phone: str, optional_phone: str = None, location: str = None,
                         file_ids: List[str] = None) -> int:
        async with self.pool.acquire() as conn:
            try:
                # Avval foydalanuvchini qo'shamiz
                await self.add_user(
                    user_id=user_id,
                    username="",
                    first_name="",
                    last_name=""
                )
                
                # E'lonni qo'shamiz
                result = await conn.fetchrow('''
                    INSERT INTO listings 
                    (user_id, category, floor, rooms, title, description, price, currency, 
                     phone, optional_phone, location, file_ids)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    RETURNING id
                ''', user_id, category, floor, rooms, title, description, price, currency,
                   phone, optional_phone, location, json.dumps(file_ids) if file_ids else None)
                
                listing_id = result['id']
                
                # Rasmlarni alohida jadvalga qo'shamiz
                if file_ids:
                    for file_id in file_ids:
                        await conn.execute('''
                            INSERT INTO listing_photos (listing_id, file_id)
                            VALUES ($1, $2)
                        ''', listing_id, file_id)
                
                logger.info(f"✅ Listing added successfully: ID {listing_id}")
                return listing_id
                
            except Exception as e:
                logger.error(f"❌ Error adding listing: {e}")
                raise
    
    async def get_active_listings(self):
        """Faol e'lonlarni olish"""
        query = """
            SELECT id, title, category, price, currency, floor, rooms, location, photos, status
            FROM listings 
            WHERE status = 'active'
            ORDER BY created_at DESC
        """
    
    
    async def increment_listing_views(self, listing_id):
        """E'lonning ko'rishlar sonini oshirish"""
        query = """
            UPDATE listings 
            SET views = views + 1 
            WHERE id = $1
        """
        await self.pool.execute(query, listing_id)
    
    
    async def get_listing(self, listing_id: int):
        async with self.pool.acquire() as conn:
            try:
                listing = await conn.fetchrow('''
                    SELECT l.*, u.first_name, u.username
                    FROM listings l
                    LEFT JOIN users u ON l.user_id = u.user_id
                    WHERE l.id = $1
                ''', listing_id)
                
                if listing:
                    # Rasmlarni olish
                    photos = await conn.fetch('''
                        SELECT file_id FROM listing_photos WHERE listing_id = $1
                    ''', listing_id)
                    
                    listing_dict = dict(listing)
                    listing_dict['photos'] = [photo['file_id'] for photo in photos]
                    return listing_dict
                return None
                
            except Exception as e:
                logger.error(f"❌ Error getting listing: {e}")
                return None
    
    async def get_user_listings(self, user_id: int):
        async with self.pool.acquire() as conn:
            try:
                listings = await conn.fetch('''
                    SELECT * FROM listings 
                    WHERE user_id = $1 
                    ORDER BY created_at DESC
                ''', user_id)
                
                return [dict(listing) for listing in listings]
            except Exception as e:
                logger.error(f"❌ Error getting user listings: {e}")
                return []
    
    async def update_listing_status(self, listing_id: int, status: str):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute('''
                    UPDATE listings SET status = $1 WHERE id = $2
                ''', status, listing_id)
                return True
            except Exception as e:
                logger.error(f"❌ Error updating listing status: {e}")
                return False
    
    async def increment_listing_views(self, listing_id: int):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute('''
                    UPDATE listings SET views = views + 1 WHERE id = $1
                ''', listing_id)
                return True
            except Exception as e:
                logger.error(f"❌ Error incrementing views: {e}")
                return False
    
    async def get_active_listings(self, category: str = None, limit: int = 50, offset: int = 0):
        async with self.pool.acquire() as conn:
            try:
                query = '''
                    SELECT l.*, u.first_name, u.username
                    FROM listings l
                    LEFT JOIN users u ON l.user_id = u.user_id
                    WHERE l.status = 'active'
                '''
                params = []
                
                if category:
                    query += ' AND l.category = $1'
                    params.append(category)
                
                query += ' ORDER BY l.created_at DESC LIMIT $2 OFFSET $3'
                params.extend([limit, offset])
                
                listings = await conn.fetch(query, *params)
                return [dict(listing) for listing in listings]
            except Exception as e:
                logger.error(f"❌ Error getting active listings: {e}")
                return []
    
    async def search_listings(self, query: str, category: str = None, 
                            min_price: float = None, max_price: float = None):
        async with self.pool.acquire() as conn:
            try:
                sql = '''
                    SELECT l.*, u.first_name, u.username
                    FROM listings l
                    LEFT JOIN users u ON l.user_id = u.user_id
                    WHERE l.status = 'active'
                    AND (l.title ILIKE $1 OR l.description ILIKE $1)
                '''
                params = [f'%{query}%']
                
                if category:
                    sql += ' AND l.category = $2'
                    params.append(category)
                
                if min_price is not None:
                    sql += ' AND l.price >= $3'
                    params.append(min_price)
                
                if max_price is not None:
                    sql += ' AND l.price <= $4'
                    params.append(max_price)
                
                sql += ' ORDER BY l.created_at DESC'
                
                listings = await conn.fetch(sql, *params)
                return [dict(listing) for listing in listings]
            except Exception as e:
                logger.error(f"❌ Error searching listings: {e}")
                return []
    
# db.py faylida delete_listing metodini yangilang
    async def delete_listing(self, listing_id: int, user_id: int = None, is_admin: bool = False):
        async with self.pool.acquire() as conn:
            try:
                # Avval e'lon mavjudligini tekshiramiz
                listing = await conn.fetchrow('''
                    SELECT user_id FROM listings WHERE id = $1
                ''', listing_id)
                
                if not listing:
                    return False  # E'lon topilmadi
                    
                # Admin yoki e'lon egasini tekshiramiz
                if not is_admin and listing['user_id'] != user_id:
                    return False  # Ruxsat yo'q
                    
                # Avval rasmlarni o'chiramiz
                await conn.execute('''
                    DELETE FROM listing_photos WHERE listing_id = $1
                ''', listing_id)
                
                # Keyin e'lonni o'chiramiz
                await conn.execute('''
                    DELETE FROM listings 
                    WHERE id = $1
                ''', listing_id)
                
                logger.info(f"✅ Listing {listing_id} deleted by user {user_id}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Error deleting listing: {e}")
                return False
    
    async def close(self):
        if self.pool:
            await self.pool.close()

# Global database instance
db = Database()