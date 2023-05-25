import pickle

with open("./database/hash_table.dat", "rb") as f:
  HASH_TABLE = pickle.load(f)

with open("./database/songs_db.dat", "rb") as f:
  SONGS = pickle.load(f)