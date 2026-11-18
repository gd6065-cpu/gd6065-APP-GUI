import math
import random
import tkinter as tk

W, H = 900, 450

# (lon, lat) rough continent outlines
LAND = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 72), (-80, 70), (-62, 60), (-55, 50), (-67, 45), (-76, 35),
     (-81, 25), (-97, 26), (-97, 18), (-87, 21), (-83, 10), (-78, 8), (-90, 15), (-105, 22), (-117, 32),
     (-125, 42), (-124, 48), (-135, 58), (-150, 60), (-165, 60)],
    [(-78, 8), (-60, 10), (-50, 0), (-35, -6), (-40, -22), (-48, -27), (-58, -38), (-65, -45), (-68, -55),
     (-75, -50), (-73, -37), (-71, -18), (-81, -5)],
    [(-10, 36), (-9, 43), (-2, 48), (5, 52), (10, 56), (5, 62), (15, 69), (30, 71), (60, 70), (100, 77),
     (140, 72), (170, 70), (180, 66), (160, 58), (140, 52), (135, 43), (122, 40), (122, 30), (110, 20),
     (105, 10), (100, 2), (98, 15), (92, 22), (80, 8), (73, 20), (67, 25), (57, 25), (52, 16), (43, 13),
     (35, 28), (35, 36), (28, 36), (22, 37), (12, 38), (8, 43), (-2, 37)],
    [(-17, 21), (-10, 35), (10, 37), (32, 31), (43, 12), (51, 12), (40, -5), (40, -15), (33, -27), (20, -35),
     (15, -27), (12, -5), (9, 4), (-8, 4), (-17, 14)],
    [(114, -22), (130, -12), (142, -11), (153, -26), (147, -38), (135, -35), (115, -34)],
    [(-55, 60), (-20, 70), (-20, 82), (-60, 82), (-72, 76)],
]

# name, lat, lon, clues (vague -> specific)
PLACES = [
    ("Paris, France", 48.86, 2.35, ["Capital known for its lattice iron tower", "Its river is the Seine", "Home of the Louvre"]),
    ("Cairo, Egypt", 30.04, 31.24, ["Near some of the oldest stone monuments on Earth", "Sits on the Nile", "The Giza pyramids are on its edge"]),
    ("Tokyo, Japan", 35.68, 139.69, ["Island nation, one of the world's largest metro areas", "Bullet trains and cherry blossoms", "Shibuya Crossing"]),
    ("Sydney, Australia", -33.87, 151.21, ["Southern hemisphere harbour city", "Famous shell-shaped performance venue", "Harbour Bridge"]),
    ("Rio de Janeiro, Brazil", -22.91, -43.17, ["Carnival capital of the world", "A huge statue overlooks the city", "Christ the Redeemer"]),
    ("New York, USA", 40.71, -74.01, ["Called the city that never sleeps", "A green statue greets harbour arrivals", "Times Square"]),
    ("Cape Town, South Africa", -33.92, 18.42, ["Southern tip of a continent", "Flat-topped mountain dominates the skyline", "Table Mountain"]),
    ("Moscow, Russia", 55.76, 37.62, ["World's largest country by area", "Colourful onion domes", "Red Square"]),
    ("Mumbai, India", 19.08, 72.88, ["Financial capital of its country", "Gateway monument by the Arabian Sea", "Bollywood"]),
    ("Chennai, India", 13.08, 80.27, ["Coastal city on the Bay of Bengal", "Marina Beach is one of the longest urban beaches", "Capital of Tamil Nadu"]),
    ("Rome, Italy", 41.90, 12.50, ["All roads supposedly lead here", "Has a famous ancient amphitheatre", "The Colosseum"]),
    ("Mexico City, Mexico", 19.43, -99.13, ["Built on a drained lake bed at high altitude", "Aztec capital Tenochtitlan once stood here", "Zocalo"]),
    ("Beijing, China", 39.90, 116.41, ["Capital of the most populous East Asian country", "Forbidden City", "Great Wall nearby"]),
    ("Reykjavik, Iceland", 64.15, -21.94, ["Northernmost national capital", "Geothermal energy, glaciers and volcanoes", "Land of fire and ice"]),
    ("Dubai, UAE", 25.20, 55.27, ["Desert city of record-breaking skyscrapers", "Home of the Burj Khalifa", "On the Persian Gulf"]),
    ("Toronto, Canada", 43.65, -79.38, ["Largest city of its country", "On the shore of Lake Ontario", "CN Tower"]),
    ("Singapore", 1.35, 103.82, ["City-state near the equator", "Marina Bay Sands and Gardens by the Bay", "Merlion statue"]),
    ("Buenos Aires, Argentina", -34.60, -58.38, ["Tango was born here", "Paris of South America", "Obelisk on Avenida 9 de Julio"]),
]


def project(lat, lon):
    return (lon + 180) / 360 * W, (90 - lat) / 180 * H


def unproject(x, y):
    return 90 - y / H * 180, x / W * 360 - 180


def haversine(a, b, c, d):
    r = 6371
    p1, p2 = math.radians(a), math.radians(c)
    dp, dl = p2 - p1, math.radians(d - b)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


class Geo:
    ROUNDS = 5

    def __init__(self, root):
        self.root = root
        root.title("GeoGuesser - Map Edition")
        root.configure(bg="#14213d")
        self.header = tk.Label(root, text="", font=("Helvetica", 14, "bold"), fg="#fca311", bg="#14213d")
        self.header.pack(pady=(8, 0))
        self.clue_box = tk.Label(root, text="", font=("Helvetica", 12), fg="white", bg="#14213d",
                                 justify="left", wraplength=860, height=4, anchor="nw")
        self.clue_box.pack(padx=20, anchor="w")
        self.canvas = tk.Canvas(root, width=W, height=H, bg="#1d4e89", highlightthickness=0)
        self.canvas.pack(padx=10)
        self.canvas.bind("<Button-1>", self.click)
        bar = tk.Frame(root, bg="#14213d")
        bar.pack(pady=8)
        self.btn_clue = tk.Button(bar, text="Reveal next clue (-1000 max)", command=self.reveal)
        self.btn_clue.pack(side="left", padx=5)
        self.btn_next = tk.Button(bar, text="Next round", command=self.next_round, state="disabled")
        self.btn_next.pack(side="left", padx=5)
        self.result = tk.Label(root, text="", font=("Helvetica", 12), fg="#e5e5e5", bg="#14213d")
        self.result.pack(pady=(0, 8))
        self.start_game()

    def draw_map(self):
        c = self.canvas
        c.delete("all")
        for lon in range(-180, 181, 30):
            x, _ = project(0, lon)
            c.create_line(x, 0, x, H, fill="#2a65a8")
        for lat in range(-90, 91, 30):
            _, y = project(lat, 0)
            c.create_line(0, y, W, y, fill="#2a65a8")
        for poly in LAND:
            pts = [coord for lon, lat in poly for coord in project(lat, lon)]
            c.create_polygon(pts, fill="#6a994e", outline="#386641", width=2)

    def start_game(self):
        self.round, self.total = 0, 0
        self.order = random.sample(PLACES, self.ROUNDS)
        self.next_round()

    def next_round(self):
        if self.round >= self.ROUNDS:
            self.start_game()
            return
        self.place = self.order[self.round]
        self.round += 1
        self.clues_shown, self.guessed = 1, False
        self.draw_map()
        self.btn_next.config(state="disabled", text="Next round")
        self.btn_clue.config(state="normal")
        self.result.config(text="Click on the map to place your guess.")
        self.update_clues()

    def update_clues(self):
        self.header.config(text=f"Round {self.round}/{self.ROUNDS}   |   Total score: {self.total}")
        lines = [f"Clue {i + 1}: {t}" for i, t in enumerate(self.place[3][:self.clues_shown])]
        self.clue_box.config(text="\n".join(lines))
        if self.clues_shown >= 3:
            self.btn_clue.config(state="disabled")

    def reveal(self):
        if not self.guessed and self.clues_shown < 3:
            self.clues_shown += 1
            self.update_clues()

    def click(self, e):
        if self.guessed:
            return
        self.guessed = True
        glat, glon = unproject(e.x, e.y)
        name, lat, lon, _ = self.place
        dist = haversine(glat, glon, lat, lon)
        base = 5000 * math.exp(-dist / 2000)
        pts = max(0, round(base - (self.clues_shown - 1) * 500 * base / 5000))
        self.total += pts
        gx, gy = e.x, e.y
        ax, ay = project(lat, lon)
        c = self.canvas
        c.create_line(gx, gy, ax, ay, fill="white", dash=(4, 3), width=2)
        c.create_oval(gx - 6, gy - 6, gx + 6, gy + 6, fill="#e63946", outline="white", width=2)
        c.create_oval(ax - 7, ay - 7, ax + 7, ay + 7, fill="#ffd60a", outline="black", width=2)
        c.create_text(ax, ay - 16, text=name, fill="white", font=("Helvetica", 11, "bold"))
        self.result.config(text=f"{dist:,.0f} km away  ->  +{pts} points")
        self.update_clues()
        self.btn_clue.config(state="disabled")
        last = self.round >= self.ROUNDS
        self.btn_next.config(state="normal", text="Play again" if last else "Next round")
        if last:
            self.result.config(text=self.result.cget("text") + f"   |   Final score: {self.total} / {self.ROUNDS * 5000}")


if __name__ == "__main__":
    root = tk.Tk()
    Geo(root)
    root.mainloop()
