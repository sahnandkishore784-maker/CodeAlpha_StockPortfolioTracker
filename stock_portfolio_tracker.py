import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime


def get_stock_prices():
    return {
        "AAPL": 189.45,
        "TSLA": 258.72,
        "MSFT": 420.15,
        "GOOGL": 175.30,
        "AMZN": 185.60,
        "META": 590.20,
        "NVDA": 120.88,
        "NFLX": 740.50,
    }


class StockPortfolioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Portfolio Tracker")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        self.prices = get_stock_prices()
        self.portfolio = {}
        self.breakdown = []
        self.total = 0.0

        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root, padx=20, pady=15)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="Stock Portfolio Tracker", font=("Segoe UI", 20, "bold")).pack()

        input_frame = tk.Frame(self.root, padx=20, pady=10)
        input_frame.pack(fill=tk.X)

        tk.Label(input_frame, text="Ticker:", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.ticker_var = tk.StringVar()
        self.ticker_combo = ttk.Combobox(input_frame, textvariable=self.ticker_var, values=sorted(self.prices.keys()), state="readonly", width=12, font=("Segoe UI", 11))
        self.ticker_combo.grid(row=0, column=1, padx=(0, 20))

        tk.Label(input_frame, text="Quantity:", font=("Segoe UI", 11)).grid(row=0, column=2, sticky="w", padx=(0, 8))
        self.qty_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.qty_var, width=12, font=("Segoe UI", 11)).grid(row=0, column=3, padx=(0, 20))

        tk.Button(input_frame, text="Add Stock", command=self.add_stock, font=("Segoe UI", 11), bg="#4CAF50", fg="white", padx=15).grid(row=0, column=4, padx=(0, 10))
        tk.Button(input_frame, text="Clear", command=self.clear_inputs, font=("Segoe UI", 11), padx=15).grid(row=0, column=5)

        table_frame = tk.Frame(self.root, padx=20, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("#", "ticker", "qty", "price", "investment", "pct")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.heading("#", text="#")
        self.tree.heading("ticker", text="Ticker")
        self.tree.heading("qty", text="Qty")
        self.tree.heading("price", text="Price")
        self.tree.heading("investment", text="Investment")
        self.tree.heading("pct", text="%")

        self.tree.column("#", width=40, anchor="center")
        self.tree.column("ticker", width=100, anchor="center")
        self.tree.column("qty", width=80, anchor="center")
        self.tree.column("price", width=100, anchor="center")
        self.tree.column("investment", width=120, anchor="center")
        self.tree.column("pct", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        bottom_frame = tk.Frame(self.root, padx=20, pady=15)
        bottom_frame.pack(fill=tk.X)

        self.total_label = tk.Label(bottom_frame, text="Total Investment: $0.00", font=("Segoe UI", 13, "bold"))
        self.total_label.pack(side=tk.LEFT, padx=(0, 40))

        self.top_label = tk.Label(bottom_frame, text="", font=("Segoe UI", 11))
        self.top_label.pack(side=tk.LEFT)

        btn_frame = tk.Frame(self.root, padx=20, pady=10)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Sort", command=self.open_sort_window, font=("Segoe UI", 11), padx=15).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_frame, text="Export TXT", command=lambda: self.export_txt(), font=("Segoe UI", 11), padx=15).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_frame, text="Export CSV", command=lambda: self.export_csv(), font=("Segoe UI", 11), padx=15).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_frame, text="Exit", command=self.root.quit, font=("Segoe UI", 11), padx=15).pack(side=tk.RIGHT)

        self.status_label = tk.Label(self.root, text="Ready", anchor="w", padx=20, pady=5, fg="#555")
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

    def add_stock(self):
        ticker = self.ticker_var.get().strip().upper()
        qty_text = self.qty_var.get().strip()

        if not ticker:
            messagebox.showwarning("Input Error", "Please select a stock ticker.")
            return
        if ticker not in self.prices:
            messagebox.showerror("Invalid Ticker", f"'{ticker}' is not supported.\nSupported: {', '.join(sorted(self.prices.keys()))}")
            return
        if not qty_text:
            messagebox.showwarning("Input Error", "Please enter a quantity.")
            return

        try:
            qty = int(qty_text)
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be a positive whole number.")
            return

        self.portfolio[ticker] = self.portfolio.get(ticker, 0) + qty
        self.calculate_breakdown()
        self.refresh_table()
        self.clear_inputs()
        self.status_label.config(text=f"Added/Updated: {self.portfolio[ticker]} shares of {ticker}")

    def clear_inputs(self):
        self.ticker_var.set("")
        self.qty_var.set("")

    def refresh_table(self, data=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if data is None:
            data = self.breakdown

        self.total = 0.0
        for item in data:
            self.total += item["investment"]

        for idx, item in enumerate(data, start=1):
            pct = (item["investment"] / self.total) * 100 if self.total > 0 else 0.0
            self.tree.insert("", tk.END, values=(
                idx,
                item["ticker"],
                item["quantity"],
                f"${item['price']:.2f}",
                f"${item['investment']:,.2f}",
                f"{pct:.1f}%"
            ))

        self.total_label.config(text=f"Total Investment: ${self.total:,.2f}")

        if data:
            top = max(data, key=lambda x: x["investment"])
            self.top_label.config(text=f"Top holding: {top['ticker']} ({top['investment'] / self.total * 100:.1f}%)")
        else:
            self.top_label.config(text="")

    def calculate_breakdown(self):
        self.breakdown = []
        for ticker, qty in self.portfolio.items():
            price = self.prices[ticker]
            investment = price * qty
            self.breakdown.append({
                "ticker": ticker,
                "quantity": qty,
                "price": price,
                "investment": investment,
            })

    def open_sort_window(self):
        if not self.breakdown:
            messagebox.showinfo("Info", "No stocks to sort.")
            return

        sort_win = tk.Toplevel(self.root)
        sort_win.title("Sort Portfolio")
        sort_win.geometry("300x180")
        sort_win.resizable(False, False)

        tk.Label(sort_win, text="Sort by:", font=("Segoe UI", 12, "bold")).pack(pady=15)

        btn_frame = tk.Frame(sort_win)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Ticker", command=lambda: self.apply_sort("ticker", sort_win), width=12, font=("Segoe UI", 11)).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Quantity", command=lambda: self.apply_sort("quantity", sort_win), width=12, font=("Segoe UI", 11)).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(btn_frame, text="Investment", command=lambda: self.apply_sort("investment", sort_win), width=12, font=("Segoe UI", 11)).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Price", command=lambda: self.apply_sort("price", sort_win), width=12, font=("Segoe UI", 11)).grid(row=1, column=1, padx=5, pady=5)

    def apply_sort(self, key, window):
        reverse = key != "ticker"
        self.breakdown.sort(key=lambda x: x[key], reverse=reverse)
        self.refresh_table()
        window.destroy()
        self.status_label.config(text=f"Sorted by {key}")

    def export_txt(self):
        if not self.breakdown:
            messagebox.showinfo("Info", "No data to export.")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], initialfile="portfolio_report.txt")
        if not filepath:
            return

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("STOCK PORTFOLIO REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 65 + "\n")
                f.write(f"{'#':<4} {'Ticker':<10} {'Qty':>6} {'Price':>10} {'Investment':>14} {'%':>6}\n")
                f.write("-" * 65 + "\n")
                for idx, item in enumerate(self.breakdown, start=1):
                    pct = (item["investment"] / self.total) * 100 if self.total > 0 else 0.0
                    f.write(f"{idx:<4} {item['ticker']:<10} {item['quantity']:>6} ${item['price']:>9.2f} ${item['investment']:>13,.2f} {pct:>5.1f}%\n")
                f.write("-" * 65 + "\n")
                f.write(f"{'TOTAL INVESTMENT':<32} ${self.total:>13,.2f} {'100.0%':>6}\n")
                f.write("=" * 65 + "\n")
            messagebox.showinfo("Export", f"Report exported to:\n{filepath}")
            self.status_label.config(text=f"Exported TXT: {filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def export_csv(self):
        if not self.breakdown:
            messagebox.showinfo("Info", "No data to export.")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialfile="portfolio_report.csv")
        if not filepath:
            return

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["#", "Ticker", "Quantity", "Price", "Investment", "Percentage"])
                for idx, item in enumerate(self.breakdown, start=1):
                    pct = (item["investment"] / self.total) * 100 if self.total > 0 else 0.0
                    writer.writerow([idx, item["ticker"], item["quantity"], f"{item['price']:.2f}", f"{item['investment']:.2f}", f"{pct:.2f}"])
                writer.writerow(["TOTAL", "", "", "", f"{self.total:.2f}", "100.00"])
            messagebox.showinfo("Export", f"Report exported to:\n{filepath}")
            self.status_label.config(text=f"Exported CSV: {filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))


def main():
    root = tk.Tk()
    app = StockPortfolioApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
