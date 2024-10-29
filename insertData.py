from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Wordlewords

# Used to insert Data quickly into the database
URL = os.environ.get('DATABASE_URL')

# Check if the URL is properly set
if URL is None:
    raise ValueError("DATABASE_URL environment variable not set.")

engine = create_engine(URL)
Session = sessionmaker(bind=engine)

# Remove existing data in table
with Session() as session:
    session.query(Wordlewords).delete()
    session.commit()

# Read the text file
with open('data/wordleValidWords.txt', 'r') as file:
    words = [line.strip() for line in file]

# Insert each word into the table
with Session() as session:
    for word in words:
        new_word = Wordlewords(word=word)
        session.add(new_word)
    session.commit()

print(f'Inserted {len(words)} words into the database.')