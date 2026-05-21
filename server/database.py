"""MongoDB connection using motor async driver."""
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    """Connect to MongoDB Atlas (free M0 cluster)."""
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DB_NAME]
    await db.users.create_index("email", unique=True)
    await db.claims.create_index("patient_id")
    await db.claims.create_index("doctor_id")
    await db.claims.create_index("status")
    await db.clinical_notes.create_index("doctor_id")
    await db.clinical_notes.create_index("patient_id")
    await db.health_checks.create_index("patient_id")
    print(f"Connected to MongoDB: {settings.DB_NAME}")


async def close_db():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        print("MongoDB connection closed")


def get_db():
    """Get database instance."""
    return db
