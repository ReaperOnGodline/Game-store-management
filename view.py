import tkinter as tk
from tkinter import ttk,messagebox
from controller import GameController, GenreController


game_ctrl = GameController()
genre_ctrl = GenreController()


win = tk.Tk()
win.title("game store manager")
win.geometry("1200x700")

#show each section
def show_games_section():
    hide_all_sections()
    games_frame.place(x=10, y=50, width=1180, height=640)

def show_genres_section():
    hide_all_sections()
    genres_frame.place(x=10, y=50, width=1180, height=640)



def hide_all_sections():
    for frame in (games_frame, genres_frame):
        frame.place_forget()

def exit_click():
    if messagebox.askyesno("EXIT", "Do you want to exit ? "):
        exit()

#buttons
btn_games = ttk.Button(win, text="Games", command=show_games_section)
btn_games.place(x=20, y=10, width=120)

btn_genres = ttk.Button(win, text="Genres", command=show_genres_section)
btn_genres.place(x=160, y=10, width=120)


exit_btn = ttk.Button(win, text="EXIT", command=exit_click)
exit_btn.place(x=1100, y=10)


#GAMES
games_frame = tk.Frame(win, relief=tk.RIDGE, bd=2)

tk.Label(games_frame, text="title").place(x=10, y=10)
title_ent = ttk.Entry(games_frame)
title_ent.place(x=80, y=10, width=350)

tk.Label(games_frame, text="company").place(x=450, y=10)
company_ent = ttk.Entry(games_frame)
company_ent.place(x=520, y=10, width=220)

tk.Label(games_frame, text="release date").place(x=890, y=10)
release_ent = ttk.Entry(games_frame)
release_ent.place(x=980, y=10, width=160)

tk.Label(games_frame, text="genre").place(x=10, y=45)
genre_ent = ttk.Entry(games_frame)
genre_ent.place(x=80, y=45, width=200)

tk.Label(games_frame, text="price").place(x=300, y=45)
price_ent = ttk.Entry(games_frame)
price_ent.place(x=350, y=45, width=100)

tk.Label(games_frame, text="rating").place(x=760, y=10)
rating_ent = ttk.Entry(games_frame)
rating_ent.place(x=810, y=10, width=60)

tk.Label(games_frame, text="stock").place(x=470, y=45)
stock_ent = ttk.Entry(games_frame)
stock_ent.place(x=520, y=45, width=80)

#buttons function
def games_add_click():
    title = title_ent.get()
    company = company_ent.get()
    release = release_ent.get()
    genre = genre_ent.get()
    price = price_ent.get()
    rating = rating_ent.get()
    stock = stock_ent.get()

    status, msg = game_ctrl.add_game(title, company, release, genre, price, rating, stock)
    if status:
        messagebox.showinfo("Game Added", msg)
        games_refresh_click()
        games_clear_form()
def games_clear_form():
    for entry in (title_ent, company_ent, release_ent, genre_ent, price_ent, rating_ent, stock_ent):
        entry.delete(0, tk.END)

def games_refresh_click():
    status, msg = game_ctrl.sort_all("game_title", False)
    if not status:
        messagebox.showerror("Sort Failed", msg)
        return

    for game in game_table.get_children():
        game_table.delete(game)
    for x in msg:
        game_table.insert("", "end", values=(x.get("code"), x.get("game_title"), x.get("company"),
                                             x.get("release_date"), x.get("genre_name"), x.get("final_price"),
                                              x.get("rating"), x.get("in_stock")))

def games_search_click():
    gse = games_search_ent.get()
    status, prob = game_ctrl.search(gse)
    if not status:
        messagebox.showerror("Search Failed", prob)
        return
    for game in game_table.get_children():
        game_table.delete(game)
    for x in prob:
        game_table.insert("", "end", values=(x.get("code"), x.get("game_title"), x.get("company"),
                                             x.get("release_date"), x.get("genre_name"), x.get("final_price"),
                                             x.get("rating"), x.get("in_stock")))
def games_delete_click():
    selected_game = game_table.focus()
    if not selected_game:
        messagebox.showerror("error", "select a game to delete")
        return
    game_code = game_table.item(selected_game, "values")[0]
    if messagebox.askyesno("Delete Game", "Are you sure you want to delete this game?"):
        status, msg = game_ctrl.delete_game_code(game_code)
        if status:
            messagebox.showinfo("success", msg)
            games_refresh_click()
        else:
            messagebox.showerror("error", msg)



add_game_btn = ttk.Button(games_frame, text="add/update game", command=games_add_click)
add_game_btn.place(x=750, y=45, width=150)

games_clear_btn = ttk.Button(games_frame, text="clear games", command=games_clear_form)
games_clear_btn.place(x=910, y=45, width=100)

games_search_ent = ttk.Entry(games_frame)
games_search_ent.place(x=10, y=100, width=300)

games_search_btn = ttk.Button(games_frame, text="search", command=games_search_click)
games_search_btn.place(x=320, y=100, width=80)

games_refresh_btn = ttk.Button(games_frame, text="refresh", command=games_refresh_click)
games_refresh_btn.place(x=410, y=100, width=100)

games_delete_btn = ttk.Button(games_frame, text="delete game", command=games_delete_click)
games_delete_btn.place(x=1020, y=45, width=100)


game_table = ttk.Treeview(games_frame, columns=("code", "title", "company", "release_date", "genre", "price", "rating", "stock",)
                          , show="headings")
game_table.heading("code", text="Code")
game_table.heading("title", text="Title")
game_table.heading("company", text="Company")
game_table.heading("release_date", text="Release Date")
game_table.heading("genre", text="Genre")
game_table.heading("price", text="Price")
game_table.heading("rating", text="Rating")
game_table.heading("stock", text="In stock")

game_table.column("code", width=40)
game_table.column("title", width=200)
game_table.column("company", width=150)
game_table.column("release_date", width=100)
game_table.column("genre", width=100)
game_table.column("price", width=60)
game_table.column("rating", width=60)
game_table.column("stock", width=60)

game_table.place(x=10, y=140, width=1150, height=480)

def on_game_select(event):
    pal = game_table.focus()
    if not pal:
        return
    vals = game_table.item(pal, "values")
    genre_name_ent.delete(0, tk.END)
    genre_name_ent.insert("end", vals[1])
    genre_discount_ent.delete(0, tk.END)
    genre_discount_ent.insert("end", vals[2])






game_table.bind("<<TreeviewSelect>>", on_game_select)





#GENRES
genres_frame = tk.Frame(win, relief=tk.RIDGE, bd=2)

tk.Label(genres_frame, text="genre name").place(x=10, y=10)
genre_name_ent = ttk.Entry(genres_frame)
genre_name_ent.place(x=110, y=10, width=220)

tk.Label(genres_frame, text="discount%").place(x=350, y=10)
genre_discount_ent = ttk.Entry(genres_frame)
genre_discount_ent.place(x=450, y=10, width=80)

def genres_clear_form():
    genre_name_ent.delete(0, tk.END)
    genre_discount_ent.delete(0, tk.END)

def genres_add_click():
    name = genre_name_ent.get()
    status, msg = genre_ctrl.add_genre(name)
    if status:
        messagebox.showinfo("added genre", msg)
        genres_refresh_click()
        genres_clear_form()
    else:
        messagebox.showerror("error", msg)

def genres_refresh_click():
    status, rows = genre_ctrl.search_genres("")
    if not status:
        messagebox.showerror("error", rows)
        return
    for genre in genre_table.get_children():
        genre_table.delete(genre)
    for row in rows:
        genre_table.insert("", "end", values=(row[0], row[1], row[2]))

def genres_update_click():
    name = genre_name_ent.get()
    discount = genre_discount_ent.get()
    status, msg = genre_ctrl.update_genre_discount(name, discount)
    if status:
        messagebox.showinfo("updated genre", msg)
        genres_refresh_click()
        games_refresh_click()
    else:
        messagebox.showerror("error", msg)

def genres_search_click():
    resgen = genres_search_ent.get()
    status, rows = genre_ctrl.search_genres(resgen)
    if not status:
        messagebox.showerror("error", rows)
        return
    for genre in genre_table.get_children():
        genre_table.delete(genre)
    for row in rows:
        genre_table.insert("", "end", values=(row[0], row[1], row[2]))

def genres_delete_click():
    selected_item = genre_table.focus()
    if not selected_item:
        messagebox.showerror("error", "select a genre to delete")
        return
    genre_name = genre_table.item(selected_item, "values")[1]
    if messagebox.askyesno("delete", f"delete {genre_name}?"):
        status, msg = genre_ctrl.delete_genre(genre_name)
        if status:
            messagebox.showinfo("deleted genre", msg)
            genres_refresh_click()
            genres_clear_form()
        else:
            messagebox.showerror("error", msg)



genres_search_ent = ttk.Entry(genres_frame)
genres_search_ent.place(x=10, y=50, width=300)

tk.Button(genres_frame, text="add", command=genres_add_click).place(x=560, y=8, width=80)
tk.Button(genres_frame, text="update discount", command=genres_update_click).place(x=650, y=8, width=130)
tk.Button(genres_frame, text="clear", command=genres_clear_form).place(x=790, y=8, width=80)
tk.Button(genres_frame, text="delete", command=genres_delete_click).place(x=880, y=8, width=80)
tk.Button(genres_frame, text="search", command=genres_search_click).place(x=320, y=48, width=80)
tk.Button(genres_frame, text="refresh", command=genres_refresh_click).place(x=410, y=48, width=80)

genre_table = ttk.Treeview(genres_frame, columns=("code", "name", "discount"), show="headings")
genre_table.heading("code", text="Code")
genre_table.heading("name", text="Genre")
genre_table.heading("discount", text="Discount %")
genre_table.column("code", width=60)
genre_table.column("name", width=200)
genre_table.column("discount", width=100)
genre_table.place(x=10, y=90, width=960, height=410)

def on_genre_select(event):
    sele= genre_table.focus()
    if not sele:
        return
    vals = genre_table.item(sele, "values")
    genre_name_ent.delete(0, tk.END)
    genre_name_ent.insert("end", vals[1])

    genre_discount_ent.delete(0, tk.END)
    genre_discount_ent.insert("end", vals[2])

genre_table.bind("<<TreeviewSelect>>", on_genre_select)


note = tk.Label(genres_frame, text="Note: prices gets updated after reopening the 'game store manager'")
note.place(x=10, y=500)

#begining
show_games_section()
games_refresh_click()

win.mainloop()
