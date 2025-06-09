import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

FILE_PATH = "contacts.json"

def load_contacts():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    return []

def save_contacts():
    with open(FILE_PATH, "w") as f:
        json.dump(contacts, f, indent=4)

contacts = load_contacts()

class ContactApp:
    def __init__(self, root):
        self.root = root
        root.title("Contact Manager")
        root.geometry("650x450")
        root.configure(bg="#f5f7fa")

        style = ttk.Style()
        style.theme_use("clam")

        # Customizing ttk styles
        style.configure("TButton",
                        font=("Segoe UI", 10),
                        padding=6,
                        foreground="#ffffff",
                        background="#008080")
        style.map("TButton",
                  background=[('active', '#006666')])

        style.configure("TLabel",
                        font=("Segoe UI", 11),
                        background="#f5f7fa")

        style.configure("TEntry",
                        font=("Segoe UI", 11),
                        padding=5)

        # Search Frame
        search_frame = ttk.Frame(root)
        search_frame.pack(fill='x', padx=15, pady=10)

        ttk.Label(search_frame, text="Search (Name or Phone):").pack(side='left', padx=(0,10))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side='left', fill='x', expand=True)
        self.search_entry.insert(0, "Type to search...")
        self.search_entry.bind("<FocusIn>", self.clear_search_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_search_placeholder)
        self.search_entry.bind("<KeyRelease>", self.search_contacts)

        # Main frame for list + details
        main_frame = ttk.Frame(root)
        main_frame.pack(fill='both', expand=True, padx=15, pady=(0,10))

        # Contact list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(side='left', fill='both', expand=True)

        self.listbox = tk.Listbox(list_frame, font=("Segoe UI", 11), bd=1, relief='solid',
                                  selectbackground="#008080", selectforeground="white")
        self.listbox.pack(side='left', fill='both', expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.show_contact_details)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Details panel
        details_frame = ttk.LabelFrame(main_frame, text="Contact Details", padding=10)
        details_frame.pack(side='right', fill='both', expand=True, padx=(10,0))

        self.details_text = tk.Text(details_frame, height=10, font=("Segoe UI", 11),
                                    state='disabled', bg="#f0f0f0", relief='flat')
        self.details_text.pack(fill='both', expand=True)

        # Buttons Frame
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill='x', padx=15, pady=(0,15))

        self.btn_add = ttk.Button(btn_frame, text="Add Contact", command=self.add_contact)
        self.btn_add.pack(side='left', padx=5)

        self.btn_update = ttk.Button(btn_frame, text="Update Contact", command=self.update_contact)
        self.btn_update.pack(side='left', padx=5)

        self.btn_delete = ttk.Button(btn_frame, text="Delete Contact", command=self.delete_contact)
        self.btn_delete.pack(side='left', padx=5)

        self.refresh_listbox()

    def clear_search_placeholder(self, event):
        if self.search_entry.get() == "Type to search...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(foreground='black')

    def add_search_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Type to search...")
            self.search_entry.config(foreground='grey')

    def refresh_listbox(self, filtered=None):
        self.listbox.delete(0, tk.END)
        display_list = filtered if filtered is not None else contacts
        for c in display_list:
            self.listbox.insert(tk.END, f"{c['name']} - {c['phone']}")
        self.clear_details()

    def search_contacts(self, event=None):
        query = self.search_var.get().strip().lower()
        if query == "" or query == "type to search...":
            self.refresh_listbox()
            return
        filtered = [c for c in contacts if query in c['name'].lower() or query in c['phone']]
        self.refresh_listbox(filtered)

    def show_contact_details(self, event):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            displayed_text = self.listbox.get(index)
            name_part = displayed_text.split(" - ")[0]
            contact = next((c for c in contacts if c['name'] == name_part), None)
            if contact:
                details = (f"Name: {contact['name']}\n"
                           f"Phone: {contact['phone']}\n"
                           f"Email: {contact['email']}\n"
                           f"Address: {contact['address']}")
                self.details_text.config(state='normal')
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(tk.END, details)
                self.details_text.config(state='disabled')

    def clear_details(self):
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)
        self.details_text.config(state='disabled')

    def add_contact(self):
        new_contact = self.get_contact_info()
        if new_contact:
            contacts.append(new_contact)
            save_contacts()
            self.refresh_listbox()

    def update_contact(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a contact to update.")
            return

        index = selection[0]
        contact_name = self.listbox.get(index).split(" - ")[0]
        contact = next((c for c in contacts if c['name'] == contact_name), None)
        if not contact:
            messagebox.showerror("Error", "Contact not found.")
            return

        updated_contact = self.get_contact_info(contact)
        if updated_contact:
            contact.update(updated_contact)
            save_contacts()
            self.refresh_listbox()

    def delete_contact(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a contact to delete.")
            return

        index = selection[0]
        contact_name = self.listbox.get(index).split(" - ")[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Delete contact '{contact_name}'?")
        if confirm:
            global contacts
            contacts = [c for c in contacts if c['name'] != contact_name]
            save_contacts()
            self.refresh_listbox()
            self.clear_details()

    def get_contact_info(self, existing=None):
        # Custom popups for better input UX
        popup = tk.Toplevel(self.root)
        popup.title("Contact Info")
        popup.geometry("350x280")
        popup.resizable(False, False)
        popup.grab_set()  # Modal

        fields = ['Name', 'Phone', 'Email', 'Address']
        entries = {}

        for idx, field in enumerate(fields):
            ttk.Label(popup, text=field + ":").place(x=20, y=20 + idx*50)
            ent = ttk.Entry(popup, width=40)
            ent.place(x=100, y=20 + idx*50)
            if existing:
                ent.insert(0, existing[field.lower()])
            entries[field.lower()] = ent

        result = {}

        def on_submit():
            name_val = entries['name'].get().strip()
            if not name_val:
                messagebox.showerror("Error", "Name is required.")
                return
            result['name'] = name_val
            result['phone'] = entries['phone'].get().strip()
            result['email'] = entries['email'].get().strip()
            result['address'] = entries['address'].get().strip()
            popup.destroy()

        submit_btn = ttk.Button(popup, text="Submit", command=on_submit)
        submit_btn.place(x=140, y=220)

        popup.wait_window()  # Wait for popup to close
        return result if result else None

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactApp(root)
    root.mainloop()
