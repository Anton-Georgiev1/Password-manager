import tkinter as tk
from tkinter import ttk, messagebox
from typing import cast

from crypto_manager import CryptoManager
from data_manager import DataManager
from password_generator import PasswordGenerator, PasswordSettings

class PasswordManagerApp:
    """Main Application GUI."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Secure Password Manager")
        self.root.resizable(False, False)
        self.root.geometry("500x400")

        self.crypto: CryptoManager | None = None
        self.data_manager: DataManager | None = None

        self._show_login()

    def _show_login(self) -> None:
        """Displays the master password login screen."""
        self.login_frame = ttk.Frame(self.root, padding="20")
        self.login_frame.pack(expand=True)

        ttk.Label(self.login_frame, text="Enter Master Password:").pack(pady=5)
        self.master_pass_entry = ttk.Entry(self.login_frame, show="*")
        self.master_pass_entry.pack(pady=5)
        self.master_pass_entry.bind("<Return>", lambda e: self._handle_login())

        ttk.Button(self.login_frame, text="Login", command=self._handle_login).pack(pady=10)

    def _handle_login(self) -> None:
        """Handles password verification and transitions to main UI."""
        password = self.master_pass_entry.get()
        if not password:
            messagebox.showerror("Error", "Password cannot be empty.")
            return

        try:
            # Initialize crypto and try to decrypt (if data exists)
            self.crypto = CryptoManager(password)
            self.data_manager = DataManager(self.crypto)
            
            # Verify by checking if decryption works if file exists
            if self.data_manager.DATA_FILE.exists():
                try:
                    self.crypto.decrypt(self.data_manager.DATA_FILE.read_bytes())
                except Exception:
                    messagebox.showerror("Error", "Incorrect Master Password.")
                    return

            self.login_frame.destroy()
            self._setup_main_ui()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def _setup_main_ui(self) -> None:
        """Sets up the tabbed interface."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # Tabs
        self.passwords_tab = ttk.Frame(self.notebook)
        self.add_tab = ttk.Frame(self.notebook)
        self.gen_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.passwords_tab, text="Passwords")
        self.notebook.add(self.add_tab, text="Add New")
        self.notebook.add(self.gen_tab, text="Generator")

        self._setup_passwords_tab()
        self._setup_add_tab()
        self._setup_gen_tab()

    # --- Passwords Tab ---
    def _setup_passwords_tab(self) -> None:
        frame = self.passwords_tab
        
        columns = ("website", "username", "password")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree.heading("website", text="Website")
        self.tree.heading("username", text="Username")
        self.tree.heading("password", text="Password")
        self.tree.column("website", width=150)
        self.tree.column("username", width=150)
        self.tree.column("password", width=150)
        self.tree.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Remove Selected", command=self._remove_selected).pack(side="left")
        ttk.Button(btn_frame, text="Refresh", command=self._refresh_tree).pack(side="right")

        self._refresh_tree()

    def _refresh_tree(self) -> None:
        """Reloads the list of passwords."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.data_manager:
            for cred in self.data_manager.credentials:
                self.tree.insert("", "end", values=(cred["website"], cred["username"], cred["password"]))

    def _remove_selected(self) -> None:
        """Removes the selected item from the list."""
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        index = self.tree.index(selected_item[0])
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this credential?"):
            if self.data_manager:
                self.data_manager.remove_credential(index)
                self._refresh_tree()

    # --- Add New Tab ---
    def _setup_add_tab(self) -> None:
        frame = self.add_tab
        form = ttk.Frame(frame, padding="20")
        form.pack(expand=True)

        ttk.Label(form, text="Website:").grid(row=0, column=0, sticky="w", pady=5)
        self.site_entry = ttk.Entry(form, width=30)
        self.site_entry.grid(row=0, column=1, pady=5)

        ttk.Label(form, text="Username:").grid(row=1, column=0, sticky="w", pady=5)
        self.user_entry = ttk.Entry(form, width=30)
        self.user_entry.grid(row=1, column=1, pady=5)

        ttk.Label(form, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
        self.pass_entry = ttk.Entry(form, width=30)
        self.pass_entry.grid(row=2, column=1, pady=5)

        ttk.Button(form, text="Add Credential", command=self._add_credential).grid(row=3, column=1, pady=20)

    def _add_credential(self) -> None:
        site = self.site_entry.get()
        user = self.user_entry.get()
        pwd = self.pass_entry.get()

        if not all([site, user, pwd]):
            messagebox.showwarning("Warning", "All fields are required.")
            return

        if self.data_manager:
            self.data_manager.add_credential(site, user, pwd)
            messagebox.showinfo("Success", "Credential added.")
            self.site_entry.delete(0, tk.END)
            self.user_entry.delete(0, tk.END)
            self.pass_entry.delete(0, tk.END)
            self._refresh_tree()

    # --- Generator Tab ---
    def _setup_gen_tab(self) -> None:
        frame = self.gen_tab
        form = ttk.Frame(frame, padding="20")
        form.pack(expand=True)

        ttk.Label(form, text="Length:").grid(row=0, column=0, sticky="w", pady=5)
        self.len_var = tk.IntVar(value=16)
        ttk.Spinbox(form, from_=4, to=64, textvariable=self.len_var, width=5).grid(row=0, column=1, sticky="w")

        self.up_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form, text="Include Uppercase", variable=self.up_var).grid(row=1, column=0, columnspan=2, sticky="w")

        self.low_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form, text="Include Lowercase", variable=self.low_var).grid(row=2, column=0, columnspan=2, sticky="w")

        self.num_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form, text="Include Numbers", variable=self.num_var).grid(row=3, column=0, columnspan=2, sticky="w")

        self.spec_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form, text="Include Special Symbols", variable=self.spec_var).grid(row=4, column=0, columnspan=2, sticky="w")

        self.gen_pass_entry = ttk.Entry(form, width=30)
        self.gen_pass_entry.grid(row=5, column=0, columnspan=2, pady=10)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Generate", command=self._generate_password).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Copy to Clipboard", command=self._copy_to_clipboard).pack(side="left", padx=5)

    def _generate_password(self) -> None:
        settings = PasswordSettings(
            length=self.len_var.get(),
            use_upper=self.up_var.get(),
            use_lower=self.low_var.get(),
            use_digits=self.num_var.get(),
            use_special=self.spec_var.get()
        )
        try:
            pwd = PasswordGenerator.generate(settings)
            self.gen_pass_entry.delete(0, tk.END)
            self.gen_pass_entry.insert(0, pwd)
        except ValueError as e:
            messagebox.showwarning("Warning", str(e))

    def _copy_to_clipboard(self) -> None:
        pwd = self.gen_pass_entry.get()
        if pwd:
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            messagebox.showinfo("Success", "Password copied to clipboard.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
