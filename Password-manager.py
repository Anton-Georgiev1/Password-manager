import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import cast
import ctypes
import secrets
import string

from crypto_manager import CryptoManager
from data_manager import DataManager
from password_generator import PasswordGenerator, PasswordSettings

# Set appearance and theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class EditDialog(ctk.CTkToplevel):
    """Dialog for editing an existing credential."""
    def __init__(self, parent, website, username, password, on_save):
        super().__init__(parent)
        self.title("Edit Credential")
        self.geometry("400x350")
        self.resizable(False, False)
        self.on_save = on_save

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        self.site_entry = ctk.CTkEntry(self, placeholder_text="Website", width=300)
        self.site_entry.insert(0, website)
        self.site_entry.grid(row=0, column=0, padx=20, pady=10)

        self.user_entry = ctk.CTkEntry(self, placeholder_text="Username", width=300)
        self.user_entry.insert(0, username)
        self.user_entry.grid(row=1, column=0, padx=20, pady=10)

        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=300)
        self.pass_entry.insert(0, password)
        self.pass_entry.grid(row=2, column=0, padx=20, pady=10)

        self.show_pass_var = tk.BooleanVar(value=False)
        self.show_pass_check = ctk.CTkCheckBox(self, text="Show Password", variable=self.show_pass_var, command=self._toggle_password)
        self.show_pass_check.grid(row=3, column=0, pady=5)

        self.save_btn = ctk.CTkButton(self, text="Save Changes", command=self._save)
        self.save_btn.grid(row=4, column=0, padx=20, pady=20)

        # Force focus
        self.after(100, self.lift)
        self.focus()
        self.grab_set()

    def _toggle_password(self):
        """Toggles visibility of the password."""
        if self.show_pass_var.get():
            self.pass_entry.configure(show="")
        else:
            self.pass_entry.configure(show="*")

    def _save(self):
        site = self.site_entry.get()
        user = self.user_entry.get()
        pwd = self.pass_entry.get()
        
        if not all([site, user, pwd]):
            messagebox.showwarning("Warning", "All fields are required.")
            return
        
        self.on_save(site, user, pwd)
        self.destroy()

class PasswordManagerApp(ctk.CTk):
    """Main Application GUI using CustomTkinter."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Secure Password Manager")
        self.geometry("600x500")
        self.resizable(False, False)

        self.crypto: CryptoManager | None = None
        self.data_manager: DataManager | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._show_login()

    def _show_login(self) -> None:
        """Displays the login screen with tabs for Login, Change, and Recovery."""
        self.login_container = ctk.CTkFrame(self)
        self.login_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.login_container.grid_columnconfigure(0, weight=1)
        self.login_container.grid_rowconfigure(0, weight=1)

        self.login_tabs = ctk.CTkTabview(self.login_container)
        self.login_tabs.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.login_tabs.add("Login")
        self.login_tabs.add("Change Password")
        self.login_tabs.add("Recover Account")

        self._setup_login_tab_ui()
        self._setup_change_tab_ui()
        self._setup_recover_tab_ui()

    def _setup_login_tab_ui(self) -> None:
        tab = self.login_tabs.tab("Login")
        tab.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(tab, text="Secure Vault", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=20)
        
        self.master_pass_entry = ctk.CTkEntry(tab, placeholder_text="Master Password", show="*", width=300)
        self.master_pass_entry.grid(row=1, column=0, pady=(10, 0))
        self.master_pass_entry.bind("<Return>", lambda e: self._handle_login())
        
        self.login_caps_warn = ctk.CTkLabel(tab, text="⚠️ Caps Lock is ON", text_color="orange")
        self.login_lang_warn = ctk.CTkLabel(tab, text="Please switch keyboard to English layout", text_color="red")
        
        self.master_pass_entry.bind("<KeyRelease>", lambda e: self._check_indicators(self.master_pass_entry, self.login_caps_warn, self.login_lang_warn))
        self.master_pass_entry.bind("<FocusIn>", lambda e: self._check_indicators(self.master_pass_entry, self.login_caps_warn, self.login_lang_warn))

        self.login_show_pass_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(tab, text="Show Password", variable=self.login_show_pass_var, 
                        command=lambda: self._toggle_visibility(self.master_pass_entry, self.login_show_pass_var)).grid(row=4, column=0, pady=5)

        ctk.CTkButton(tab, text="Login", command=self._handle_login, width=200).grid(row=5, column=0, pady=20)

    def _setup_change_tab_ui(self) -> None:
        tab = self.login_tabs.tab("Change Password")
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tab, text="Update Master Password", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10)

        self.login_curr_pass = ctk.CTkEntry(tab, placeholder_text="Current Password", show="*", width=300)
        self.login_curr_pass.grid(row=1, column=0, pady=5)

        self.login_new_pass = ctk.CTkEntry(tab, placeholder_text="New Password", show="*", width=300)
        self.login_new_pass.grid(row=2, column=0, pady=5)

        self.login_confirm_pass = ctk.CTkEntry(tab, placeholder_text="Confirm New Password", show="*", width=300)
        self.login_confirm_pass.grid(row=3, column=0, pady=5)

        self.change_caps_warn = ctk.CTkLabel(tab, text="⚠️ Caps Lock is ON", text_color="orange")
        self.change_lang_warn = ctk.CTkLabel(tab, text="Please switch keyboard to English layout", text_color="red")

        for entry in [self.login_curr_pass, self.login_new_pass, self.login_confirm_pass]:
            entry.bind("<KeyRelease>", lambda e, en=entry: self._check_indicators(en, self.change_caps_warn, self.change_lang_warn))
            entry.bind("<FocusIn>", lambda e, en=entry: self._check_indicators(en, self.change_caps_warn, self.change_lang_warn))

        self.change_show_pass_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(tab, text="Show Passwords", variable=self.change_show_pass_var, 
                        command=lambda: self._toggle_multi_visibility([self.login_curr_pass, self.login_new_pass, self.login_confirm_pass], self.change_show_pass_var)).grid(row=6, column=0, pady=5)

        ctk.CTkButton(tab, text="Change & Update Key", command=self._handle_login_screen_change, width=200).grid(row=7, column=0, pady=10)

    def _setup_recover_tab_ui(self) -> None:
        tab = self.login_tabs.tab("Recover Account")
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tab, text="Emergency Recovery", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10)

        self.login_recovery_key = ctk.CTkEntry(tab, placeholder_text="Recovery Key (24-chars)", width=300)
        self.login_recovery_key.grid(row=1, column=0, pady=5)

        self.login_recover_pass = ctk.CTkEntry(tab, placeholder_text="New Master Password", show="*", width=300)
        self.login_recover_pass.grid(row=2, column=0, pady=5)

        self.recover_caps_warn = ctk.CTkLabel(tab, text="⚠️ Caps Lock is ON", text_color="orange")
        self.recover_lang_warn = ctk.CTkLabel(tab, text="Please switch keyboard to English layout", text_color="red")

        self.login_recover_pass.bind("<KeyRelease>", lambda e: self._check_indicators(self.login_recover_pass, self.recover_caps_warn, self.recover_lang_warn))
        self.login_recover_pass.bind("<FocusIn>", lambda e: self._check_indicators(self.login_recover_pass, self.recover_caps_warn, self.recover_lang_warn))

        self.recover_show_pass_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(tab, text="Show Password", variable=self.recover_show_pass_var, 
                        command=lambda: self._toggle_visibility(self.login_recover_pass, self.recover_show_pass_var)).grid(row=5, column=0, pady=5)

        ctk.CTkButton(tab, text="Reset & Generate New Key", command=self._handle_login_screen_recovery, width=200).grid(row=6, column=0, pady=10)

    def _check_indicators(self, entry: ctk.CTkEntry, caps_label: ctk.CTkLabel, lang_label: ctk.CTkLabel) -> None:
        """Checks Caps Lock and Keyboard Layout states for a specific entry."""
        # Caps Lock check
        if ctypes.windll.user32.GetKeyState(0x14) & 1:
            caps_label.grid(row=2, column=0, pady=0)
        else:
            caps_label.grid_forget()

        # Keyboard layout check
        u = ctypes.windll.user32
        handle = u.GetForegroundWindow()
        thread = u.GetWindowThreadProcessId(handle, 0)
        layout = u.GetKeyboardLayout(thread)
        lang_id = layout & 0x3FF
        
        if lang_id != 0x09:
            lang_label.grid(row=3, column=0, pady=0)
        else:
            lang_label.grid_forget()

    def _toggle_visibility(self, entry: ctk.CTkEntry, var: tk.BooleanVar) -> None:
        entry.configure(show="" if var.get() else "*")

    def _toggle_multi_visibility(self, entries: list[ctk.CTkEntry], var: tk.BooleanVar) -> None:
        for entry in entries:
            entry.configure(show="" if var.get() else "*")

    def _handle_login_screen_change(self) -> None:
        current_pwd = self.login_curr_pass.get()
        new_pwd = self.login_new_pass.get()
        confirm_pwd = self.login_confirm_pass.get()

        if not all([current_pwd, new_pwd, confirm_pwd]):
            messagebox.showwarning("Warning", "All fields are required.")
            return

        if new_pwd != confirm_pwd:
            messagebox.showerror("Error", "New passwords do not match.")
            return

        try:
            # Try to initialize with current password
            self.data_manager = DataManager(current_pwd)
            # If successful, change password
            self.data_manager.change_password(new_pwd)
            # Show new recovery key
            self._setup_recovery_flow(reset_login=True)
            messagebox.showinfo("Success", "Master Password updated.")
        except ValueError:
            messagebox.showerror("Error", "Incorrect current master password.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def _handle_login_screen_recovery(self) -> None:
        key = self.login_recovery_key.get()
        new_pwd = self.login_recover_pass.get()

        if not all([key, new_pwd]):
            messagebox.showwarning("Warning", "All fields are required.")
            return

        if DataManager.verify_recovery_key(key):
            try:
                old_password = DataManager.recover_master_password(key)
                self.data_manager = DataManager(old_password)
                self.data_manager.change_password(new_pwd)
                # Force new key generation and show it
                self._setup_recovery_flow(reset_login=True)
                messagebox.showinfo("Success", "Account recovered and password updated.")
            except Exception as e:
                messagebox.showerror("Error", f"Recovery failed: {e}")
        else:
            messagebox.showerror("Error", "Invalid Recovery Key.")

    def _setup_recovery_flow(self, reset_login: bool = False) -> None:
        """Flow for recovery key generation. Shows new key and moves to main UI."""
        chars = string.ascii_uppercase + string.digits
        recovery_key = "-".join("".join(secrets.choice(chars) for _ in range(4)) for _ in range(6))
        
        setup_window = ctk.CTkToplevel(self)
        setup_window.title("New Recovery Key")
        setup_window.geometry("500x400")
        setup_window.resizable(False, False)
        setup_window.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(setup_window, text="⚠️ NEW Recovery Key Generated", font=ctk.CTkFont(size=18, weight="bold"), text_color="orange").grid(row=0, column=0, pady=20)
        ctk.CTkLabel(setup_window, text="Please save this NEW key. The old one will no longer work.", justify="center").grid(row=1, column=0, pady=10)
        
        key_entry = ctk.CTkEntry(setup_window, width=350, justify="center", font=ctk.CTkFont(size=16, weight="bold"))
        key_entry.insert(0, recovery_key)
        key_entry.configure(state="readonly")
        key_entry.grid(row=2, column=0, pady=20)

        def confirm_setup():
            if messagebox.askyesno("Confirm", "Have you saved your NEW recovery key?"):
                if self.data_manager:
                    self.data_manager.setup_recovery(recovery_key)
                    setup_window.destroy()
                    if reset_login:
                        self.login_container.destroy()
                        self._setup_main_ui()

        ctk.CTkButton(setup_window, text="I Have Saved This Key", command=confirm_setup).grid(row=3, column=0, pady=20)
        
        setup_window.after(100, setup_window.lift)
        setup_window.focus()
        setup_window.grab_set()

    def _handle_login(self) -> None:
        # Keyboard layout check enforcement
        u = ctypes.windll.user32
        handle = u.GetForegroundWindow()
        thread = u.GetWindowThreadProcessId(handle, 0)
        layout = u.GetKeyboardLayout(thread)
        if (layout & 0x3FF) != 0x09:
            messagebox.showerror("Error", "Please switch keyboard to English layout.")
            return

        password = self.master_pass_entry.get()
        if not password:
            messagebox.showerror("Error", "Password cannot be empty.")
            return

        try:
            # DataManager now handles crypto and salt loading internally
            self.data_manager = DataManager(password)
            
            # Check if recovery key needs to be generated (Account Creation)
            if not DataManager.RECOVERY_HASH_FILE.exists():
                self._setup_recovery_flow(reset_login=True)
            else:
                self.login_container.destroy()
                self._setup_main_ui()
        except ValueError:
            messagebox.showerror("Error", "Incorrect Master Password.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def _setup_main_ui(self) -> None:
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tabview.add("Passwords")
        self.tabview.add("Add New")
        self.tabview.add("Generator")

        self._setup_passwords_tab()
        self._setup_add_tab()
        self._setup_gen_tab()

    # --- Passwords Tab ---
    def _setup_passwords_tab(self) -> None:
        tab = self.tabview.tab("Passwords")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Using standard Treeview for the list as CTK doesn't have a native table yet
        # But we wrap it in a frame to control layout
        tree_frame = ctk.CTkFrame(tab)
        tree_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        columns = ("website", "username", "password")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("website", text="Website")
        self.tree.heading("username", text="Username")
        self.tree.heading("password", text="Password")
        self.tree.column("website", width=150)
        self.tree.column("username", width=150)
        self.tree.column("password", width=150)
        self.tree.pack(side="top", fill="both", expand=True)

        btn_frame = ctk.CTkFrame(tab)
        btn_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.edit_btn = ctk.CTkButton(btn_frame, text="Edit Selected", command=self._edit_selected, width=120)
        self.edit_btn.pack(side="left", padx=5, pady=5)
        
        self.remove_btn = ctk.CTkButton(btn_frame, text="Remove Selected", command=self._remove_selected, width=120, fg_color="#D35B58", hover_color="#C77C78")
        self.remove_btn.pack(side="left", padx=5, pady=5)
        
        self.refresh_btn = ctk.CTkButton(btn_frame, text="Refresh", command=self._refresh_tree, width=100)
        self.refresh_btn.pack(side="right", padx=5, pady=5)

        self._refresh_tree()

    def _refresh_tree(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        if self.data_manager:
            for cred in self.data_manager.credentials:
                self.tree.insert("", "end", values=(cred["website"], cred["username"], cred["password"]))

    def _remove_selected(self) -> None:
        selected_item = self.tree.selection()
        if not selected_item:
            return
        index = self.tree.index(selected_item[0])
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this credential?"):
            if self.data_manager:
                self.data_manager.remove_credential(index)
                self._refresh_tree()

    def _edit_selected(self) -> None:
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a credential to edit.")
            return
        
        index = self.tree.index(selected_item[0])
        cred = self.data_manager.credentials[index] if self.data_manager else None
        if not cred: return

        def save_edit(site, user, pwd):
            if self.data_manager:
                self.data_manager.update_credential(index, site, user, pwd)
                self._refresh_tree()
                messagebox.showinfo("Success", "Credential updated.")

        EditDialog(self, cred["website"], cred["username"], cred["password"], save_edit)

    # --- Add New Tab ---
    def _setup_add_tab(self) -> None:
        tab = self.tabview.tab("Add New")
        tab.grid_columnconfigure(0, weight=1)
        
        form = ctk.CTkFrame(tab)
        form.pack(expand=True, padx=20, pady=20)

        self.site_entry = ctk.CTkEntry(form, placeholder_text="Website", width=300)
        self.site_entry.grid(row=0, column=0, padx=20, pady=10)

        self.user_entry = ctk.CTkEntry(form, placeholder_text="Username", width=300)
        self.user_entry.grid(row=1, column=0, padx=20, pady=10)

        self.pass_entry = ctk.CTkEntry(form, placeholder_text="Password", show="*", width=300)
        self.pass_entry.grid(row=2, column=0, padx=20, pady=10)

        self.show_add_pass_var = tk.BooleanVar(value=False)
        self.show_add_pass_check = ctk.CTkCheckBox(form, text="Show Password", variable=self.show_add_pass_var, command=self._toggle_add_password)
        self.show_add_pass_check.grid(row=3, column=0, pady=5)

        self.add_btn = ctk.CTkButton(form, text="Add Credential", command=self._add_credential, width=200)
        self.add_btn.grid(row=4, column=0, padx=20, pady=10)

    def _toggle_add_password(self) -> None:
        """Toggles visibility of the add credential password."""
        if self.show_add_pass_var.get():
            self.pass_entry.configure(show="")
        else:
            self.pass_entry.configure(show="*")

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
        tab = self.tabview.tab("Generator")
        
        form = ctk.CTkFrame(tab)
        form.pack(expand=True, padx=20, pady=20)

        ctk.CTkLabel(form, text="Password Length:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.len_slider = ctk.CTkSlider(form, from_=4, to=64, number_of_steps=60)
        self.len_slider.set(16)
        self.len_slider.grid(row=0, column=1, padx=10, pady=10)
        
        self.len_label = ctk.CTkLabel(form, text="16")
        self.len_label.grid(row=0, column=2, padx=10, pady=10)
        self.len_slider.configure(command=lambda v: self.len_label.configure(text=str(int(v))))

        self.up_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(form, text="Uppercase", variable=self.up_var).grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.low_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(form, text="Lowercase", variable=self.low_var).grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.num_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(form, text="Numbers", variable=self.num_var).grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.spec_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(form, text="Special Symbols", variable=self.spec_var).grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.gen_pass_entry = ctk.CTkEntry(form, width=300, placeholder_text="Generated Password")
        self.gen_pass_entry.grid(row=3, column=0, columnspan=3, padx=10, pady=20)

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        ctk.CTkButton(btn_frame, text="Generate", command=self._generate_password, width=120).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Copy", command=self._copy_to_clipboard, width=120).pack(side="left", padx=5)

    def _generate_password(self) -> None:
        settings = PasswordSettings(
            length=int(self.len_slider.get()),
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
            self.clipboard_clear()
            self.clipboard_append(pwd)
            messagebox.showinfo("Success", "Password copied to clipboard.")

if __name__ == "__main__":
    app = PasswordManagerApp()
    app.mainloop()
