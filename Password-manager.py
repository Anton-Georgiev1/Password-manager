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
        """Displays the master password login screen."""
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.login_frame.grid_columnconfigure(0, weight=1)
        self.login_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        ctk.CTkLabel(self.login_frame, text="Secure Vault", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=20)
        
        self.master_pass_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Master Password", show="*", width=300)
        self.master_pass_entry.grid(row=1, column=0, pady=(10, 0))
        self.master_pass_entry.bind("<Return>", lambda e: self._handle_login())
        self.master_pass_entry.bind("<KeyRelease>", lambda e: self._check_indicators())
        self.master_pass_entry.bind("<FocusIn>", lambda e: self._check_indicators())

        self.caps_warning = ctk.CTkLabel(self.login_frame, text="⚠️ Caps Lock is ON", text_color="orange")
        self.lang_warning = ctk.CTkLabel(self.login_frame, text="Please switch keyboard to English layout", text_color="red")

        self.show_pass_var = tk.BooleanVar(value=False)
        self.show_pass_check = ctk.CTkCheckBox(self.login_frame, text="Show Password", variable=self.show_pass_var, command=self._toggle_login_password)
        self.show_pass_check.grid(row=4, column=0, pady=5)

        self.login_btn = ctk.CTkButton(self.login_frame, text="Login", command=self._handle_login, width=200)
        self.login_btn.grid(row=5, column=0, pady=10)

        self.forgot_btn = ctk.CTkButton(self.login_frame, text="Forgot Password?", command=self._handle_forgot_password, fg_color="transparent", hover_color=None, text_color="gray")
        self.forgot_btn.grid(row=6, column=0, pady=5)

    def _check_indicators(self) -> None:
        """Checks Caps Lock and Keyboard Layout states."""
        # Caps Lock check
        if ctypes.windll.user32.GetKeyState(0x14) & 1:
            self.caps_warning.grid(row=2, column=0, pady=0)
        else:
            self.caps_warning.grid_forget()

        # Keyboard layout check
        u = ctypes.windll.user32
        handle = u.GetForegroundWindow()
        thread = u.GetWindowThreadProcessId(handle, 0)
        layout = u.GetKeyboardLayout(thread)
        lang_id = layout & 0x3FF # Primary language ID (lower 10 bits)
        
        if lang_id != 0x09: # 0x09 is English
            self.lang_warning.grid(row=3, column=0, pady=0)
        else:
            self.lang_warning.grid_forget()

    def _toggle_login_password(self) -> None:
        """Toggles visibility of the master password."""
        if self.show_pass_var.get():
            self.master_pass_entry.configure(show="")
        else:
            self.master_pass_entry.configure(show="*")

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
                self._setup_recovery_flow()
            else:
                self.login_frame.destroy()
                self._setup_main_ui()
        except ValueError:
            messagebox.showerror("Error", "Incorrect Master Password.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def _setup_recovery_flow(self) -> None:
        """Flow for initial recovery key generation."""
        chars = string.ascii_uppercase + string.digits
        recovery_key = "-".join("".join(secrets.choice(chars) for _ in range(4)) for _ in range(6))
        
        # Show recovery key to user
        setup_window = ctk.CTkToplevel(self)
        setup_window.title("Recovery Key Setup")
        setup_window.geometry("500x400")
        setup_window.resizable(False, False)
        setup_window.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(setup_window, text="⚠️ IMPORTANT: Save Your Recovery Key", font=ctk.CTkFont(size=18, weight="bold"), text_color="orange").grid(row=0, column=0, pady=20)
        ctk.CTkLabel(setup_window, text="If you forget your master password, this key is the ONLY way\nto recover your data. Save it to a safe place (e.g., a text file or print it).", justify="center").grid(row=1, column=0, pady=10)
        
        key_entry = ctk.CTkEntry(setup_window, width=350, justify="center", font=ctk.CTkFont(size=16, weight="bold"))
        key_entry.insert(0, recovery_key)
        key_entry.configure(state="readonly")
        key_entry.grid(row=2, column=0, pady=20)

        def confirm_setup():
            if messagebox.askyesno("Confirm", "Have you saved your recovery key to an external location?"):
                if self.data_manager:
                    self.data_manager.setup_recovery(recovery_key)
                    setup_window.destroy()
                    self.login_frame.destroy()
                    self._setup_main_ui()

        ctk.CTkButton(setup_window, text="I Have Saved This Key", command=confirm_setup).grid(row=3, column=0, pady=20)
        
        setup_window.after(100, setup_window.lift)
        setup_window.focus()
        setup_window.grab_set()

    def _handle_forgot_password(self) -> None:
        """Handles the recovery process using the 24-character key."""
        if not DataManager.RECOVERY_HASH_FILE.exists():
            messagebox.showerror("Error", "Recovery system not set up. No recovery key found on this system.")
            return

        dialog = ctk.CTkInputDialog(text="Enter your 24-character Recovery Key:", title="Forgot Password")
        recovery_key = dialog.get_input()
        
        if not recovery_key:
            return

        if DataManager.verify_recovery_key(recovery_key):
            try:
                # Recover master password to decrypt data
                old_password = DataManager.recover_master_password(recovery_key)
                
                # Prompt for new master password
                new_pass_dialog = ctk.CTkInputDialog(text="Recovery successful! Enter your NEW Master Password:", title="Reset Password")
                new_password = new_pass_dialog.get_input()
                
                if new_password:
                    # Initialize data manager with old password
                    self.data_manager = DataManager(old_password)
                    # Change to new password
                    self.data_manager.change_password(new_password)
                    # Also update recovery info with the NEW password
                    self.data_manager.setup_recovery(recovery_key)
                    
                    messagebox.showinfo("Success", "Master Password has been reset. You can now login.")
                    # Refresh login screen (it's already there)
                    self.master_pass_entry.delete(0, tk.END)
                
            except Exception as e:
                messagebox.showerror("Error", f"Recovery failed during decryption: {e}")
        else:
            messagebox.showerror("Error", "Invalid Recovery Key.")

    def _setup_main_ui(self) -> None:
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tabview.add("Passwords")
        self.tabview.add("Add New")
        self.tabview.add("Generator")
        self.tabview.add("Settings")

        self._setup_passwords_tab()
        self._setup_add_tab()
        self._setup_gen_tab()
        self._setup_settings_tab()

    def _setup_settings_tab(self) -> None:
        tab = self.tabview.tab("Settings")
        tab.grid_columnconfigure(0, weight=1)
        
        form = ctk.CTkFrame(tab)
        form.pack(expand=True, padx=20, pady=20)

        ctk.CTkLabel(form, text="Change Master Password", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=10)

        self.current_pass_entry = ctk.CTkEntry(form, placeholder_text="Current Master Password", show="*", width=300)
        self.current_pass_entry.grid(row=1, column=0, padx=20, pady=10)

        self.new_pass_entry = ctk.CTkEntry(form, placeholder_text="New Master Password", show="*", width=300)
        self.new_pass_entry.grid(row=2, column=0, padx=20, pady=10)

        self.confirm_pass_entry = ctk.CTkEntry(form, placeholder_text="Confirm New Password", show="*", width=300)
        self.confirm_pass_entry.grid(row=3, column=0, padx=20, pady=10)

        self.change_btn = ctk.CTkButton(form, text="Update Master Password", command=self._handle_change_password, width=200)
        self.change_btn.grid(row=4, column=0, padx=20, pady=20)

    def _handle_change_password(self) -> None:
        current_pwd = self.current_pass_entry.get()
        new_pwd = self.new_pass_entry.get()
        confirm_pwd = self.confirm_pass_entry.get()

        if not all([current_pwd, new_pwd, confirm_pwd]):
            messagebox.showwarning("Warning", "All fields are required.")
            return

        if new_pwd != confirm_pwd:
            messagebox.showerror("Error", "New passwords do not match.")
            return

        if self.data_manager and current_pwd == self.data_manager.master_password:
            try:
                self.data_manager.change_password(new_pwd)
                # Need to update recovery info too, but we need the key.
                # Since we don't store the key, we should probably ask for it or inform user.
                # For simplicity and to follow "Inside the App" rule, we'll just update the password.
                # If they want to keep recovery working, they'll need a way to update it.
                # I'll add a prompt asking for recovery key to update the backup.
                
                if DataManager.RECOVERY_HASH_FILE.exists():
                   if messagebox.askyesno("Update Recovery", "Master password changed. Would you like to update your recovery file? (Requires your Recovery Key)"):
                       dialog = ctk.CTkInputDialog(text="Enter your Recovery Key:", title="Update Recovery")
                       key = dialog.get_input()
                       if key and DataManager.verify_recovery_key(key):
                           self.data_manager.setup_recovery(key)
                           messagebox.showinfo("Success", "Master password and recovery info updated.")
                       else:
                           messagebox.showwarning("Warning", "Master password updated, but recovery info was NOT updated (Invalid key).")
                else:
                    messagebox.showinfo("Success", "Master Password updated successfully.")
                
                self.current_pass_entry.delete(0, tk.END)
                self.new_pass_entry.delete(0, tk.END)
                self.confirm_pass_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to change password: {e}")
        else:
            messagebox.showerror("Error", "Incorrect current master password.")

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
