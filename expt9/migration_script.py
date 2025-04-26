#!/usr/bin/env python3
"""
MongoDB to PostgreSQL Migration Script for Books Collection
- Fixed table verification issue
"""

import logging
import sys
import time
from typing import Dict, Any, List

import psycopg2
from psycopg2.extras import execute_batch
from pymongo import MongoClient

# Import configuration
from config import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION,
    PG_HOST, PG_DATABASE, PG_USER, PG_PASSWORD, PG_PORT, PG_TABLE,
    BATCH_SIZE
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("migration.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """Establish connection to MongoDB"""
    try:
        client = MongoClient(MONGO_URI)
        # Force a command to test the connection
        client.admin.command('ping')
        db = client[MONGO_DB]
        logger.info(f"Connected to MongoDB database: {MONGO_DB}")
        return client, db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

def connect_to_postgresql():
    """Establish connection to PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD,
            port=PG_PORT
        )
        cursor = conn.cursor()
        logger.info(f"Connected to PostgreSQL database: {PG_DATABASE}")
        return conn, cursor
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        sys.exit(1)

def verify_postgresql_table(cursor, table_name):
    """Verify that the PostgreSQL table exists"""
    try:
        # Check if table exists
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = %s
            )
        """, (table_name,))
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            logger.error(f"Table {table_name} does not exist in PostgreSQL database")
            return False
        
        # Get table columns
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = %s
        """, (table_name,))
        
        columns = [col[0] for col in cursor.fetchall()]
        logger.info(f"Table {table_name} exists with columns: {', '.join(columns)}")
        return True
    except Exception as e:
        logger.error(f"Error verifying PostgreSQL table: {e}")
        return False

def transform_book_data(mongo_record: Dict[str, Any]) -> Dict[str, Any]:
    """Transform book record from MongoDB format to PostgreSQL format"""
    # Handle MongoDB ObjectId
    if '_id' in mongo_record:
        mongo_record['_id'] = str(mongo_record['_id'])
    
    # Transform data - adjust field names based on your actual MongoDB schema
    transformed = {
        "book_id": str(mongo_record.get("_id", "")),  # Use _id as default book_id
        "book_name": mongo_record.get("title", ""),   # Assuming title is used in MongoDB
        "book_authors": ", ".join(mongo_record.get("authors", [])) if isinstance(mongo_record.get("authors"), list) else mongo_record.get("authors", ""),
        "isbn_number": mongo_record.get("isbn", ""),
        "book_category": mongo_record.get("category", ""),
        "edition_number": mongo_record.get("edition", 1),
        "year_of_publication": mongo_record.get("year", 0)
    }
    
    # If we have specific field mapping, use it instead (keep this as example)
    field_mapping = {
        "bookName": "book_name",
        "bookId": "book_id",
        "bookAuthors": "book_authors",
        "isbnNumber": "isbn_number",
        "bookCategory": "book_category",
        "editionNumber": "edition_number",
        "yearOfPublication": "year_of_publication"
    }
    
    # Apply field mapping if MongoDB uses different field names
    for mongo_field, pg_field in field_mapping.items():
        if mongo_field in mongo_record:
            if mongo_field == "bookAuthors" and isinstance(mongo_record[mongo_field], list):
                transformed[pg_field] = ", ".join(mongo_record[mongo_field])
            else:
                transformed[pg_field] = mongo_record[mongo_field]
    
    return transformed

def fetch_data_from_mongodb(db, collection_name, batch_size=BATCH_SIZE):
    """Fetch data from MongoDB in batches"""
    collection = db[collection_name]
    total_count = collection.count_documents({})
    logger.info(f"Found {total_count} documents in {collection_name}")
    
    if total_count == 0:
        logger.warning(f"No documents found in collection {collection_name}")
        return
    
    # Process in batches to handle large collections
    processed = 0
    
    # Use cursor directly for proper pagination
    cursor = collection.find({})
    while True:
        batch = list(cursor.limit(batch_size))
        if not batch:
            break
            
        processed += len(batch)
        logger.info(f"Processing {len(batch)} documents. Progress: {processed}/{total_count}")
        
        yield batch
        
        if len(batch) < batch_size:
            break
            
        # Skip the processed documents
        cursor = collection.find({}).skip(processed)

def migrate_books(mongo_db, pg_conn, pg_cursor):
    """Migrate books from MongoDB to PostgreSQL"""
    total_migrated = 0
    
    # Get PostgreSQL table columns to ensure we only insert valid columns
    try:
        pg_cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = %s
        """, (PG_TABLE,))
        valid_columns = set(col[0] for col in pg_cursor.fetchall())
        logger.info(f"Valid PostgreSQL columns: {', '.join(valid_columns)}")
    except Exception as e:
        logger.error(f"Error getting table columns: {e}")
        return 0
    
    for batch in fetch_data_from_mongodb(mongo_db, MONGO_COLLECTION):
        # Transform MongoDB documents to PostgreSQL format
        transformed_data = []
        for doc in batch:
            try:
                transformed = transform_book_data(doc)
                # Filter out keys that don't exist in the PostgreSQL table
                filtered = {k: v for k, v in transformed.items() if k in valid_columns}
                transformed_data.append(filtered)
            except Exception as e:
                logger.error(f"Error transforming document: {e}")
        
        if not transformed_data:
            logger.warning("No documents were successfully transformed in this batch")
            continue
            
        # Get column names from the first record
        columns = list(transformed_data[0].keys())
        placeholders = ", ".join(["%s"] * len(columns))
        column_names = ", ".join(columns)
        
        # Create the query with appropriate conflict handling
        # If you have a unique constraint on book_id, use ON CONFLICT
        query = f"INSERT INTO {PG_TABLE} ({column_names}) VALUES ({placeholders})"
        
        if "book_id" in columns:
            query += " ON CONFLICT (book_id) DO NOTHING"
        
        # Convert dictionary values to tuples in the same order as columns
        values = [[record.get(column) for column in columns] for record in transformed_data]
        
        try:
            execute_batch(pg_cursor, query, values, page_size=min(100, len(values)))
            pg_conn.commit()
            total_migrated += len(transformed_data)
            logger.info(f"Inserted {len(transformed_data)} records into table {PG_TABLE}")
        except Exception as e:
            pg_conn.rollback()
            logger.error(f"Error inserting data into {PG_TABLE}: {e}")
            # Try to print sample data for debugging
            if values:
                sample = values[0]
                logger.error(f"Sample data that failed: {list(zip(columns, sample))}")
            if "duplicate key" in str(e):
                logger.warning("You might need to modify ON CONFLICT clause to handle duplicates properly")
    
    return total_migrated

def validate_migration(mongo_db, pg_cursor):
    """Validate the migration by comparing record counts"""
    # Count records in MongoDB
    mongo_count = mongo_db[MONGO_COLLECTION].count_documents({})
    
    # Count records in PostgreSQL
    pg_cursor.execute(f"SELECT COUNT(*) FROM {PG_TABLE}")
    pg_count = pg_cursor.fetchone()[0]
    
    logger.info(f"Validation: MongoDB has {mongo_count} records, PostgreSQL has {pg_count} records")
    
    if mongo_count == pg_count:
        logger.info("✅ Validation successful: Record counts match")
        return True
    else:
        logger.warning(f"⚠️ Validation shows partial migration: {pg_count}/{mongo_count} records migrated ({pg_count/mongo_count*100:.1f}% complete)")
        return False

def main():
    """Main function to run the migration process"""
    start_time = time.time()
    
    try:
        # Connect to databases
        mongo_client, mongo_db = connect_to_mongodb()
        pg_conn, pg_cursor = connect_to_postgresql()
        
        # Verify PostgreSQL table structure
        if not verify_postgresql_table(pg_cursor, PG_TABLE):
            logger.error(f"PostgreSQL table {PG_TABLE} verification failed. Migration aborted.")
            return
        
        # Perform migration
        logger.info(f"Starting migration from MongoDB ({MONGO_COLLECTION}) to PostgreSQL ({PG_TABLE})")
        total_migrated = migrate_books(mongo_db, pg_conn, pg_cursor)
        
        # Calculate duration
        duration = time.time() - start_time
        logger.info(f"Migration completed in {duration:.2f} seconds")
        logger.info(f"Total records migrated: {total_migrated}")
        
        # Validate migration
        validate_migration(mongo_db, pg_cursor)
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
    finally:
        # Close connections
        if 'pg_cursor' in locals() and pg_cursor:
            pg_cursor.close()
        if 'pg_conn' in locals() and pg_conn:
            pg_conn.close()
        if 'mongo_client' in locals() and mongo_client:
            mongo_client.close()
        logger.info("Database connections closed")

if __name__ == "__main__":
    main()