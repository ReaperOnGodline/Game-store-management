import re
from model import Game, Genre
from datetime import date


COLUMN_INDEX = {"code": 0, "game_title": 1, "company": 2, "release_date": 3, "genre_name": 4, "game_price": 5, "rating": 6, "in_stock": 7}

class GameController:
    def __init__(self):
        self.model = Game()
        self.genre_model = Genre()

    def validate_title(self, title: str):
        title = (title or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9\s.:,'!?()&-]{3,52}", title):
            return False, "game_title is invalid"
        return True, title

    def validate_company(self, company: str):
        company = (company or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9\s.&-]{3,42}", company):
            return False, "company is invalid"
        return True, company

    def validate_genre(self, genre: str):
        genre = (genre or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9\s&-]{2,60}", genre):
            return False, "genre is invalid"
        return True, genre

    def validate_price(self, price: str):
        price = (price or "").strip()
        if not re.fullmatch(r"\d+(\.\d{1,2})?", price):
            return False, "price must be a positive number with maximum of two decimals"
        price_float = float(price)
        if price_float < 0:
            return False, "price must be positive"
        return True, price_float

    def validate_rating(self, rating: str):
        rating = (rating or "").strip()
        if rating == "":
            return True, 0.0
        if not re.fullmatch(r"\d+(\.\d{1,2})?", rating):
            return False, "rating must be a number between 0 and 10"
        rating_float = float(rating)
        if rating_float < 0 or rating_float > 10:
            return False, "rating must be between 0 and 10"
        return True, rating_float

    def validate_stock(self, stock: str):
        stock = (stock or "").strip()
        if stock =="":
            return  True, 0
        if not re.fullmatch(r"\d+", stock):
            return False, "stock must be a positive integer"
        int_stock = int(stock)
        if int_stock < 0:
            return False, "stock must be positive"
        return True, int_stock

    def validate_date(self, date_str: str):
        val_date = (date_str or "").strip()
        if val_date == "":
            return True, None
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", val_date):
            return False, "date format should be Year{4}-Month{2}-Day{2}"
        try:
            date_iso = date.fromisoformat(val_date)
            return True, date_iso.isoformat()
        except ValueError:
            return False, "date format should be Year{4}-Month{2}-Day{2}"

    def add_game(self, title, company, release_date, genre_name, price, rating="", stock=""):
        try:
            status, title = self.validate_title(title)
            if not status: return False, title

            status, company = self.validate_company(company)
            if not status: return False, company

            status, genre_name = self.validate_genre(genre_name)
            if not status: return False, genre_name

            status, price = self.validate_price(price)
            if not status: return False, price

            status, rating = self.validate_rating(rating)
            if not status: return False, rating

            status, stock = self.validate_stock(stock)
            if not status: return False, stock

            status, release_date = self.validate_date(release_date)
            if not status: return False, release_date

            genre_code = self.genre_model.get_genre_code(genre_name)
            if genre_code is None:
                self.genre_model.add_genre(genre_name)
                genre_code = self.genre_model.get_genre_code(genre_name)

            self.model.add_game(title, company, release_date, genre_code, price, rating, stock)
            return True, "game added"

        except Exception as e:
            print(f"controller got error: {e}")
            return False, f"controller got error: {e}"

    def search(self, text, order_by="rating", descending=True):
        try:
            text = (text or "").strip()
            rows = self.model.show_all_games()
            games = [self.row_to_dict(row) for row in rows]

            if text == "":
                return True, self.sort_list(games, order_by, descending)

            letters = text.split()
            filters = []

            #filter with regex
            numbers_check = re.compile(r"(?i)^(price|game_price|rating|in_stock)\s*([<>]=?)\s*(\d+(\.\d+)?)$")
            keyvalue_check = re.compile(r"(?i)^(genre|company|title):(.+)$")

            for letter in letters:
                num_match = numbers_check.match(letter)
                word_match = keyvalue_check.match(letter)


                if num_match:
                    field, op, val, _ = num_match.groups()
                    field = field.lower()
                    value = float(val)

                    def num_filter(item):
                        try:
                            match field:
                                case "price" | "game_price":
                                    retval = float(item.get("game_price") or 0)
                                case "rating":
                                    retval = float(item.get("rating") or 0)
                                case "in_stock":
                                    retval = int(item.get("in_stock") or 0)
                                case _:
                                    return False
                        except ValueError:
                            return False

                        match op:
                            case ">":
                                return retval > value
                            case "<":
                                return retval < value
                            case ">=":
                                return retval >= value
                            case "<=":
                                return retval <= value
                            case _:
                                return False

                    filters.append(num_filter)
                    continue

                if word_match:
                    key, val = word_match.groups()
                    key = key.lower()
                    val = val.strip().lower()

                    def field_filter(item):
                            match key:
                                case "title":
                                    return val in (item.get("game_title") or "").lower()
                                case "company":
                                    return val in (item.get("company") or "").lower()
                                case "genre":
                                    return val in (item.get("genre_name") or "").lower()
                                case _:
                                   return False

                    filters.append(field_filter)
                    continue

                # just search with a keyword
                kw = letter.lower()

                def kw_filter(item):
                    item_title = (item.get("game_title") or "").lower()
                    item_company = (item.get("company") or "").lower()
                    item_genre = (item.get("genre_name") or "").lower()
                    return (kw in item_title or kw in item_company or kw in item_genre)

                filters.append(kw_filter)

            def matches_all(item):
                return all(f(item) for f in filters)

            result = [g for g in games if matches_all(g)]
            return True, self.sort_list(result, order_by, descending)

        except Exception as e:
            print(f"search got error: {e}")
            return False, f"search error: {e}"


    def sort_all(self, by="rating", descending=True):
        try:
            rows = self.model.show_all_games()
            games = [self.row_to_dict(row) for row in rows]
            sorted_games = self.sort_list(games, by, descending)
            return True, sorted_games
        except Exception as e:
            print(f"sorting error: {e}")
            return False, f"sorting error: {e}"

    def sort_list(self, rows, order_by, descending):
        if order_by not in ("rating", "game_price", "release_date", "game_title", "in_stock"):
            order_by = "rating"
        return sorted(rows, key=lambda r: (r[order_by] is None, r[order_by]), reverse=descending)

    def row_to_dict(self, row):
        return {
            "code": row[0],
            "game_title": row[1],
            "company": row[2],
            "release_date": row[3],
            "genre_name": row[4],
            "game_price": row[5],
            "rating": row[6],
            "in_stock": row[7],
            "final_price": row[8]
        }

    def delete_game_code(self, game_code):
        try:
            code = int(game_code)
            status = self.model.delete_game(code)
            if status:
                return True, "game deleted"
            else:
                return False, "couldn't delete game"
        except ValueError:
            return False, "invalid game code"
        except Exception as e:
            print(f"got error: {e}")
            return False, f"got error: {e}"



class GenreController:
    def __init__(self):
        self.model = Genre()


    def validate_genre_name(self, name: str):
        name = (name or "").strip()
        if not re.fullmatch("[A-Za-z0-9\s&-]{2,60}", name):
            return False, "genre name is invalid use: A-Za-z0-9 space - &"
        return True, name

    def validate_discount(self, discount: str):
        discount = (discount or "").strip()
        if discount == "":
            return True, 0
        try:
            val = float(discount)
            if val < 0 or val > 100:
                return False, "discount must be between 0 and 100"
            return True, val
        except ValueError:
            return False, "discount must be a number"


    def add_genre(self, name):
        status, genre_name = self.validate_genre_name(name)
        if not status:
            return False, genre_name

        try:
            existing = self.model.get_genre_code(genre_name)
            if existing:
                return False, f"genre {genre_name} already exists"
            self.model.add_genre(genre_name)
            return True, f"genre: {genre_name} added"
        except Exception as e:
            return False, f"error: {e} while adding genre"

    def update_genre_discount(self, name, discount):
        status, genre_name = self.validate_genre_name(name)
        if not status:
            return False, genre_name
        status, discount_val = self.validate_discount(discount)
        if not status:
            return False, discount_val
        try:
            self.model.update_genre(genre_name, discount_val)
            return True, f"discount: {discount_val} updated for genre: {genre_name}"
        except Exception as e:
            return False, f"error: {e} while updating genre"

    def search_genres(self, search_word=""):
        try:
            return True, self.model.show_all_genres(search_word)
        except Exception as e:
            return False, f"error: {e} while getting genres"

    def get_games_for_genre(self, genre_name):
        status, genre_name = self.validate_genre_name(genre_name)
        if not status:
            return False, genre_name
        try:
            games = self.model.get_games_by_genre(genre_name)
            if not games:
                return True, []
            return True, games
        except Exception as e:
            return False, f"error: {e} while showing games for genre: {genre_name}"

    def delete_genre(self, genre_name):
        status, name = self.validate_genre_name(genre_name)
        if not status:
            return False, name

        genre_code = self.model.get_genre_code(name)
        if genre_code is None:
            return False, "genre code doesnt exist"
        return self.model.delete_genre(genre_code)