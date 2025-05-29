
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from analyzer import DockerfileAnalyzer
from models.finding import Finding
import csv
from fpdf import FPDF

class GUIApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Container Hardening Analyzer")
        self.root.geometry("1000x600")
        self.file_path = None

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Button(frame, text="Select Dockerfile", command=self.select_file).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="Analyze", command=self.analyze_file).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Export Fixed Dockerfile", command=self.export_fixed).grid(row=0, column=2, padx=5)
        tk.Button(frame, text="Export Findings As...", command=self.export_findings).grid(row=0, column=3, padx=5)

        self.use_gpt_var = tk.BooleanVar()
        tk.Checkbutton(frame, text="Use GPT AI", variable=self.use_gpt_var).grid(row=0, column=4)

        self.tree = ttk.Treeview(self.root, columns=("Level", "Message", "Suggestion"), show="headings", height=15)
        for col in ("Level", "Message", "Suggestion"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=300)
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.score_label = tk.Label(self.root, text="Risk Score: 0/10", font=("Arial", 14, "bold"))
        self.score_label.pack(pady=10)

        self.fixed_content = ""
        self.findings = []
        self.root.mainloop()

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Dockerfile or YAML", "*.Dockerfile *.yaml *.yml"), ("All Files", "*.*")])
        if self.file_path:
            with open(self.file_path, "r") as file:
                self.file_content = file.read()

    def analyze_file(self):
        if not self.file_path:
            messagebox.showerror("Error", "No file selected")
            return
        analyzer = DockerfileAnalyzer(self.file_content, use_gpt=self.use_gpt_var.get())
        self.findings = analyzer.analyze()
        score = analyzer.get_score()
        self.fixed_content = analyzer.generate_fixed()

        for row in self.tree.get_children():
            self.tree.delete(row)
        for f in self.findings:
            self.tree.insert("", "end", values=(f.level, f.message, f.suggestion))

        color = "green" if score < 3 else "orange" if score <= 6 else "red"
        emoji = "🟢" if score < 3 else "🟡" if score <= 6 else "🔴"
        self.score_label.config(text=f"Risk Score: {score}/10  {emoji}", fg=color)

    def export_fixed(self):
        if not self.fixed_content:
            messagebox.showerror("Error", "Nothing to export")
            return
        export_path = filedialog.asksaveasfilename(defaultextension=".Dockerfile", filetypes=[("Dockerfile", "*.Dockerfile")])
        if export_path:
            with open(export_path, "w") as f:
                f.write(self.fixed_content)
            messagebox.showinfo("Exported", f"Saved to: {export_path}")

    def export_findings(self):
        if not self.findings:
            messagebox.showerror("Error", "No findings to export")
            return
        fmt = simpledialog.askstring("Export Format", "Enter format (csv, txt, pdf):")
        if fmt == "csv":
            path = filedialog.asksaveasfilename(defaultextension=".csv")
            with open(path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Level", "Message", "Suggestion"])
                for f in self.findings:
                    writer.writerow([f.level, f.message, f.suggestion])
        elif fmt == "txt":
            path = filedialog.asksaveasfilename(defaultextension=".txt")
            with open(path, "w") as file:
                for f in self.findings:
                    file.write(f"{f.level} | {f.message} | {f.suggestion}\n")
        elif fmt == "pdf":
            path = filedialog.asksaveasfilename(defaultextension=".pdf")
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Security Findings", ln=True, align="C")
            for f in self.findings:
                pdf.multi_cell(0, 10, f"{f.level} | {f.message} | {f.suggestion}")
            pdf.output(path)
        else:
            messagebox.showerror("Error", "Invalid format.")

if __name__ == "__main__":
    GUIApp()
