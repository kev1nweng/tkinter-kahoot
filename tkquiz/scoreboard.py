from tkinter import ttk

from tkquiz.base_window import AppWindow


class ScoreboardWindow(AppWindow):
    def __init__(self, master, storage):
        super().__init__(master, storage, "Scoreboard", "500x350", (600, 250))

        self.table = ttk.Treeview(self.body, columns=("rank", "name", "score"), show="headings")
        self.table.heading("rank", text="Rank")
        self.table.heading("name", text="Player")
        self.table.heading("score", text="Score")
        self.table.column("rank", width=60)
        self.table.column("name", width=200)
        self.table.column("score", width=80)
        self.table.pack(fill="both", expand=True)

        self.refresh()

    def refresh(self):
        for row in self.table.get_children():
            self.table.delete(row)

        rounds = self.storage.list_rounds()
        if len(rounds) == 0:
            return
        players = rounds[0].players

        players.sort(key=get_score, reverse=True)

        rank = 1
        for p in players:
            self.table.insert("", "end", values=(rank, p.name, p.score))
            rank = rank + 1


def get_score(player):
    return player.score  