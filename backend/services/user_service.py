from sqlalchemy import select
import traceback
from backend.database import async_session, User

async def ensure_user_in_db(user_session):
    if not user_session:
        return None
    
    google_id = user_session.get("id")
    if not google_id:
        return None
        
    try:
        async with async_session() as session:
            async with session.begin():
                stmt = select(User).where(User.google_id == google_id)
                result = await session.execute(stmt)
                db_user = result.scalar_one_or_none()
                
                if not db_user:
                    print(f"Resurrecting user {google_id} from session data...")
                    db_user = User(
                        google_id=google_id,
                        username=user_session.get("username"),
                        email=user_session.get("email", ""),
                        name=user_session.get("name", "Unknown"),
                        picture=user_session.get("picture"),
                        supporter_badge=user_session.get("supporter_badge"),
                        default_time=user_session.get("default_time", 10.0),
                        default_increment=user_session.get("default_increment", 0.0),
                        default_time_control_enabled=user_session.get("default_time_control_enabled", True)
                    )
                    session.add(db_user)
                return db_user
    except Exception as e:
        print(f"Error resurrecting user {google_id}: {e}")
        traceback.print_exc()
        return None
