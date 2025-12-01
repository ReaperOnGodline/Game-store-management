"""
a model for an MVC Game Store Management system
"""
from mysql.connector import Error
from db_connection import connect_to_db


# database class
class DBModel:
    def __init__(self):
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor()

    def close(self):
            self.cursor.close()
            self.connection.close()

allowed_search = ["rating", "game_price", "release_date", "game_title", "in_stock", "genre_name"]
# class game
class Game(DBModel):
    # add game if it already exists it will update the stock
    def add_game(self, game_title, company, release_date, genre_code, game_price, rating=0.0, in_stock=0):
        try:
            self.cursor.execute("SELECT in_stock FROM games WHERE game_title = %s", (game_title,))
            existing_game = self.cursor.fetchone()

            if existing_game:
                # Update stuff
                self.cursor.execute("UPDATE games SET company = %s, release_date = %s, genre_code = %s, game_price = %s,"
                        " rating = %s, in_stock = in_stock + %s WHERE game_title = %s"
                                    , (company, release_date, genre_code, game_price, rating, in_stock, game_title))
                self.connection.commit()
                print(f"Game '{game_title}' already exists, stock updated.")
            else:
                # Insert new game
                self.cursor.execute("INSERT INTO games (game_title, company, release_date, genre_code, game_price, rating, in_stock)"
                  " VALUES (%s, %s, %s, %s, %s, %s, %s)"
                , (game_title, company, release_date, genre_code, game_price, rating, in_stock))
                self.connection.commit()
                print(f"New game '{game_title}' added.")

        except Error as e:
            print(f"Encountered error: {e} while adding the game")


    # Show all game
    def show_all_games(self):
        try:
            show_stuff =("SELECT g.code, g.game_title, g.company, g.release_date, ge.genre_name, g.game_price, g.rating, g.in_stock,"
                         " ROUND(g.game_price * (1 - (COALESCE(ge.discount, 0) / 100)), 2) as final_price"
                         " FROM games g LEFT JOIN genres ge ON g.genre_code = ge.code")
            self.cursor.execute(show_stuff)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error: {e} while showing all games")
            return []

    def get_game_code_title(self, title: str):
        self.cursor.execute("SELECT code FROM games WHERE game_title = %s", (title,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    # Search games
    def find_games(self, searched_word, order_by="rating", descending=True):
        if order_by not in allowed_search:
            order_by = "rating"

        order = "DESC" if descending else "ASC"
        like = f"%{searched_word}%"
        try:
            self.cursor.execute(f"SELECT g.*, ge.genre_name, ge.discount, ROUND(g.game_price * (1 - (COALESCE(ge.discount,0) / 100)), 2) "
                                f" as final_price FROM games g JOIN genres ge ON g.genre_code = ge.code"
                                f" WHERE g.game_title LIKE %s"
                                f" OR g.company LIKE %s"
                                f" OR ge.genre_name LIKE %s OR ge.code LIKE %s ORDER BY {order_by} {order}", (like, like, like, like))
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error: {e} while finding games")
            return []

    # Sorting games
    def sort_games(self, by="rating", descending=True):
        if by not in allowed_search:
            by = "rating"
        # sort by a default of rating
        order = "DESC" if descending else "ASC"
        try:
            self.cursor.execute(f"SELECT * FROM games ORDER BY {by} {order}")
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error: {e} while sorting games")
            return []

    def delete_game(self, code: int):
        try:
            self.cursor.execute("DELETE FROM games WHERE code = %s", (code,))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error: {e} while deleting game")
            return False

# genre class
class Genre(DBModel):
    def get_genre_code(self, genre_name):
        try:
            self.cursor.execute("SELECT code FROM genres WHERE genre_name = %s", (genre_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error: {e} while getting genre code")
            return None

    # def add a new genre
    def add_genre(self, genre_name):
        try:
            self.cursor.execute("SELECT * FROM genres WHERE genre_name = %s", (genre_name,))
            existing_genre = self.cursor.fetchone()

            if existing_genre:
                print(f"Genre '{genre_name}' already exists")
            else:
                self.cursor.execute(
                    "INSERT INTO genres (genre_name) VALUES (%s)", (genre_name,)
                )
                print(f"Genre '{genre_name}' added.")
            self.connection.commit()
        except Error as e:
            print(f"Error: {e} while adding the genre")

    # update a genred
    def update_genre(self, genre_name, new_discount):
        try:
            self.cursor.execute(
                "UPDATE genres SET discount = %s WHERE genre_name = %s", (new_discount, genre_name)
            )
            self.connection.commit()
            print(f"Genre '{genre_name}' updated.")
        except Error as e:
            print(f"Error: {e} while updating the genre")

    def show_all_genres(self, searched_word=""):
        try:
            like = f"%{searched_word}%"
            self.cursor.execute(
                "SELECT * FROM genres WHERE genre_name LIKE %s OR CAST(discount AS CHAR) LIKE %s", (like, like)
            )
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error: {e} while showing all genres")
            return[]

    def get_games_by_genre(self, genre_name):
        try:
            genre_code = self.get_genre_code(genre_name)
            if genre_code is None:
                print("genre not found")
                return[]
            self.cursor.execute(
                "SELECT * FROM games WHERE genre_code = %s ORDER BY rating DESC", (genre_code,)
            )
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error: {e} while getting games from genre")
            return []


    def delete_genre(self, genre_code):
        try:
            self.cursor.execute("DELETE FROM genres WHERE code = %s", (genre_code,))
            self.connection.commit()
            return True, "genre deleted"
        except Error as e:
            if e.errno == 1451:
                return False, "genre contains a game and can not be deleted"
            print(f"Error: {e} while deleting genre")
            return False, f"error : {e}"
