import os
import json
import shutil
import uuid
import webbrowser
import tkinter as tk

from tkinter import ttk, messagebox, filedialog
from urllib.parse import quote

# ----------------------------------
# MY CONTACT BOOK
# ----------------------------------

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "contacts.json")
PHOTO_DIR = os.path.join(APP_DIR, "photos")

os.makedirs(PHOTO_DIR, exist_ok=True)


class ContactBook:

    def __init__(self, root):
        self.root = root
        self.root.title("My Contact Book")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)

        self.contacts = []
        self.selected_photo = ""
        self.selected_id = None
        self.photo_image = None

        self.load_contacts()
        self.create_ui()
        self.refresh_contacts()

    # ----------------------------------
    # LOAD AND SAVE
    # ----------------------------------

    def load_contacts(self):
        if not os.path.exists(DATA_FILE):
            self.contacts = []
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                self.contacts = [
                    c for c in data if isinstance(c, dict)
                ]
            else:
                self.contacts = []

        except (OSError, ValueError):
            messagebox.showerror(
                "Error",
                "Contact फाइल नहीं पढ़ी जा सकी।"
            )
            self.contacts = []

    def save_contacts(self):
        temp_file = DATA_FILE + ".tmp"

        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(
                    self.contacts,
                    f,
                    ensure_ascii=False,
                    indent=4
                )

            os.replace(temp_file, DATA_FILE)
            return True

        except OSError as e:
            messagebox.showerror("Save Error", str(e))

            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except OSError:
                pass

            return False

    # ----------------------------------
    # USER INTERFACE
    # ----------------------------------

    def create_ui(self):

        self.root.configure(bg="#edf2f7")

        title = tk.Label(
            self.root,
            text="MY CONTACT BOOK",
            font=("Arial", 23, "bold"),
            bg="#234a91",
            fg="white",
            pady=15
        )
        title.pack(fill="x")

        # Search section
        search_frame = tk.Frame(
            self.root,
            bg="#edf2f7",
            padx=12,
            pady=10
        )
        search_frame.pack(fill="x")

        tk.Label(
            search_frame,
            text="Search:",
            font=("Arial", 11, "bold"),
            bg="#edf2f7"
        ).pack(side="left")

        self.search_var = tk.StringVar()

        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 11)
        )
        search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=10
        )

        self.search_var.trace_add(
            "write",
            lambda *args: self.refresh_contacts()
        )

        ttk.Button(
            search_frame,
            text="Backup",
            command=self.backup
        ).pack(side="left", padx=4)

        ttk.Button(
            search_frame,
            text="Restore",
            command=self.restore
        ).pack(side="left", padx=4)

        # Main area
        main = tk.Frame(
            self.root,
            bg="#edf2f7",
            padx=12,
            pady=5
        )
        main.pack(fill="both", expand=True)

        # Contact form
        form = ttk.LabelFrame(
            main,
            text="Contact Details",
            padding=12
        )
        form.pack(side="left", fill="y", padx=(0, 12))

        tk.Label(form, text="Name").pack(anchor="w")

        self.name_var = tk.StringVar()

        ttk.Entry(
            form,
            textvariable=self.name_var,
            width=29
        ).pack(fill="x", pady=(3, 10))

        tk.Label(form, text="Mobile Number").pack(anchor="w")

        self.phone_var = tk.StringVar()

        ttk.Entry(
            form,
            textvariable=self.phone_var,
            width=29
        ).pack(fill="x", pady=(3, 10))

        tk.Label(form, text="Address").pack(anchor="w")

        self.address_text = tk.Text(
            form,
            width=28,
            height=4,
            font=("Arial", 10)
        )
        self.address_text.pack(fill="x", pady=(3, 10))

        # Photo preview
        self.photo_label = tk.Label(
            form,
            text="No Photo Selected",
            width=20,
            height=7,
            bg="#dce5f2",
            fg="#234a91",
            relief="groove"
        )
        self.photo_label.pack(pady=8)

        ttk.Button(
            form,
            text="Choose Photo",
            command=self.choose_photo
        ).pack(fill="x", pady=3)

        ttk.Button(
            form,
            text="Remove Photo",
            command=self.remove_photo
        ).pack(fill="x", pady=3)

        ttk.Button(
            form,
            text="Add Contact",
            command=self.add_contact
        ).pack(fill="x", pady=(12, 3))

        ttk.Button(
            form,
            text="Update Contact",
            command=self.update_contact
        ).pack(fill="x", pady=3)

        ttk.Button(
            form,
            text="Delete Contact",
            command=self.delete_contact
        ).pack(fill="x", pady=3)

        ttk.Button(
            form,
            text="Clear Form",
            command=self.clear_form
        ).pack(fill="x", pady=3)

        ttk.Button(
            form,
            text="Call Selected",
            command=self.call_contact
        ).pack(fill="x", pady=3)

        # Contact list
        right = ttk.LabelFrame(
            main,
            text="Saved Contacts",
            padding=8
        )
        right.pack(side="left", fill="both", expand=True)

        columns = ("name", "phone", "address")

        self.tree = ttk.Treeview(
            right,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.tree.heading("name", text="Name")
        self.tree.heading("phone", text="Mobile Number")
        self.tree.heading("address", text="Address")

        self.tree.column("name", width=170)
        self.tree.column("phone", width=135)
        self.tree.column("address", width=240)

        scrollbar = ttk.Scrollbar(
            right,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(side="right", fill="y")

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.select_contact
        )

        self.status = tk.Label(
            self.root,
            text="Ready",
            anchor="w",
            bg="#dce5f2",
            padx=12,
            pady=6
        )
        self.status.pack(fill="x", side="bottom")

    # ----------------------------------
    # PHOTO FUNCTIONS
    # ----------------------------------

    def choose_photo(self):
        path = filedialog.askopenfilename(
            title="Choose Contact Photo",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All Files", "*.*")
            ]
        )

        if not path:
            return

        self.selected_photo = path
        self.show_photo(path)

    def show_photo(self, path):
        if not path or not os.path.isfile(path):
            self.photo_image = None
            self.photo_label.configure(
                image="",
                text="No Photo Selected"
            )
            return

        try:
            from PIL import Image, ImageTk

            with Image.open(path) as image:
                image.thumbnail((140, 120))
                self.photo_image = ImageTk.PhotoImage(
                    image.copy()
                )

            self.photo_label.configure(
                image=self.photo_image,
                text=""
            )

        except Exception:
            self.photo_image = None
            self.photo_label.configure(
                image="",
                text="Preview unavailable"
            )

    def remove_photo(self):
        self.selected_photo = ""
        self.photo_image = None
        self.photo_label.configure(
            image="",
            text="No Photo Selected"
        )

    def copy_photo(self, source):
        if not source or not os.path.isfile(source):
            return ""

        ext = os.path.splitext(source)[1].lower()

        if ext not in (
            ".png", ".jpg", ".jpeg", ".gif", ".bmp"
        ):
            messagebox.showwarning(
                "Photo",
                "PNG, JPG, JPEG, GIF या BMP फोटो चुनें।"
            )
            return None

        destination = os.path.join(
            PHOTO_DIR,
            str(uuid.uuid4()) + ext
        )

        try:
            shutil.copy2(source, destination)
            return destination
        except OSError as e:
            messagebox.showerror("Photo Error", str(e))
            return None

    # ----------------------------------
    # ADD CONTACT
    # ----------------------------------

    def add_contact(self):
        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        address = self.address_text.get(
            "1.0", "end"
        ).strip()

        if not name or not phone:
            messagebox.showwarning(
                "Required",
                "नाम और मोबाइल नंबर भरें।"
            )
            return

        if not phone.isdigit() or len(phone) != 10:
            messagebox.showwarning(
                "Invalid Number",
                "10 अंकों का मोबाइल नंबर लिखें।"
            )
            return

        photo_path = ""

        if self.selected_photo:
            photo_path = self.copy_photo(
                self.selected_photo
            )

            if photo_path is None:
                return

        contact = {
            "id": str(uuid.uuid4()),
            "name": name,
            "phone": phone,
            "address": address,
            "photo": photo_path
        }

        self.contacts.append(contact)

        if self.save_contacts():
            self.refresh_contacts()
            self.clear_form()
            self.status.config(text="Contact Added")

    # ----------------------------------
    # SEARCH AND DISPLAY
    # ----------------------------------

    def refresh_contacts(self):
        if not hasattr(self, "tree"):
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self.search_var.get().strip().casefold()

        for contact in self.contacts:
            searchable = " ".join([
                contact.get("name", ""),
                contact.get("phone", ""),
                contact.get("address", "")
            ]).casefold()

            if query and query not in searchable:
                continue

            contact_id = contact.get("id")

            if not contact_id:
                contact_id = str(uuid.uuid4())
                contact["id"] = contact_id

            self.tree.insert(
                "",
                "end",
                iid=contact_id,
                values=(
                    contact.get("name", ""),
                    contact.get("phone", ""),
                    contact.get("address", "")
                )
            )

        self.status.config(
            text=f"Total Contacts: {len(self.contacts)}"
        )

    # ----------------------------------
    # SELECT AND EDIT
    # ----------------------------------

    def select_contact(self, event=None):
        selection = self.tree.selection()

        if not selection:
            return

        contact_id = selection[0]

        contact = next(
            (
                c for c in self.contacts
                if c.get("id") == contact_id
            ),
            None
        )

        if not contact:
            return

        self.selected_id = contact_id
        self.name_var.set(contact.get("name", ""))
        self.phone_var.set(contact.get("phone", ""))

        self.address_text.delete("1.0", "end")
        self.address_text.insert(
            "1.0", contact.get("address", "")
        )

        self.selected_photo = contact.get("photo", "")
        self.show_photo(self.selected_photo)

    def update_contact(self):
        if not self.selected_id:
            messagebox.showwarning(
                "Select Contact",
                "पहले सूची से Contact चुनें।"
            )
            return

        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        address = self.address_text.get(
            "1.0", "end"
        ).strip()

        if not name or not phone:
            messagebox.showwarning(
                "Required",
                "नाम और मोबाइल नंबर जरूरी हैं।"
            )
            return

        if not phone.isdigit() or len(phone) != 10:
            messagebox.showwarning(
                "Invalid Number",
                "10 अंकों का मोबाइल नंबर लिखें।"
            )
            return

        index = next(
            (
                i for i, c in enumerate(self.contacts)
                if c.get("id") == self.selected_id
            ),
            None
        )

        if index is None:
            messagebox.showerror(
                "Error", "Contact नहीं मिला।"
            )
            return

        old = self.contacts[index]
        old_photo = old.get("photo", "")
        new_photo = old_photo

        if self.selected_photo != old_photo:
            if self.selected_photo:
                copied = self.copy_photo(self.selected_photo)

                if copied is None:
                    return

                new_photo = copied
            else:
                new_photo = ""

        self.contacts[index] = {
            "id": self.selected_id,
            "name": name,
            "phone": phone,
            "address": address,
            "photo": new_photo
        }

        if self.save_contacts():
            if old_photo and old_photo != new_photo:
                try:
                    if os.path.isfile(old_photo):
                        os.remove(old_photo)
                except OSError:
                    pass

            self.refresh_contacts()
            self.clear_form()
            self.status.config(text="Contact Updated")

    # ----------------------------------
    # DELETE CONTACT
    # ----------------------------------

    def delete_contact(self):
        if not self.selected_id:
            messagebox.showwarning(
                "Select Contact",
                "पहले Contact चुनें।"
            )
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "क्या आप यह Contact डिलीट करना चाहते हैं?"
        ):
            return

        index = next(
            (
                i for i, c in enumerate(self.contacts)
                if c.get("id") == self.selected_id
            ),
            None
        )

        if index is None:
            return

        contact = self.contacts.pop(index)

        if not self.save_contacts():
            self.contacts.insert(index, contact)
            return

        photo = contact.get("photo", "")

        if photo and os.path.isfile(photo):
            try:
                os.remove(photo)
            except OSError:
                pass

        self.refresh_contacts()
        self.clear_form()
        self.status.config(text="Contact Deleted")

    # ----------------------------------
    # CALL
    # ----------------------------------

    def call_contact(self):
        if not self.selected_id:
            messagebox.showwarning(
                "Select Contact",
                "पहले कोई Contact चुनें।"
            )
            return

        contact = next(
            (
                c for c in self.contacts
                if c.get("id") == self.selected_id
            ),
            None
        )

        if not contact:
            return

        phone = contact.get("phone", "")

        if not phone:
            messagebox.showwarning(
                "No Number",
                "इस Contact में नंबर नहीं है।"
            )
            return

        try:
            webbrowser.open(
                "tel:" + quote(phone, safe="+")
            )

            messagebox.showinfo(
                "Call",
                "कॉल लिंक खोलने का अनुरोध भेजा गया।\n"
                "Windows पर कॉल करने के लिए "
                "संगत कॉलिंग ऐप आवश्यक हो सकती है।"
            )

        except Exception as e:
            messagebox.showerror("Call Error", str(e))

    # ----------------------------------
    # CLEAR FORM
    # ----------------------------------

    def clear_form(self):
        self.name_var.set("")
        self.phone_var.set("")

        self.address_text.delete("1.0", "end")

        self.selected_id = None
        self.selected_photo = ""
        self.photo_image = None

        self.photo_label.configure(
            image="",
            text="No Photo Selected"
        )

        if hasattr(self, "tree"):
            for item in self.tree.selection():
                self.tree.selection_remove(item)

    # ----------------------------------
    # BACKUP
    # ----------------------------------

    def backup(self):
        path = filedialog.asksaveasfilename(
            title="Save Contact Backup",
            defaultextension=".zip",
            initialfile="contact_backup.zip",
            filetypes=[("ZIP Backup", "*.zip")]
        )

        if not path:
            return

        import zipfile

        try:
            with zipfile.ZipFile(
                path, "w", zipfile.ZIP_DEFLATED
            ) as backup_zip:

                backup_zip.write(
                    DATA_FILE,
                    arcname="contacts.json"
                ) if os.path.exists(DATA_FILE) else None

                for contact in self.contacts:
                    photo = contact.get("photo", "")

                    if photo and os.path.isfile(photo):
                        backup_zip.write(
                            photo,
                            arcname=os.path.join(
                                "photos",
                                os.path.basename(photo)
                            )
                        )

            messagebox.showinfo(
                "Backup",
                "Contact और उपलब्ध फोटो का बैकअप बन गया।"
            )

        except OSError as e:
            messagebox.showerror("Backup Error", str(e))

    # ----------------------------------
    # RESTORE
    # ----------------------------------

    def restore(self):
        import zipfile

        path = filedialog.askopenfilename(
            title="Select Contact Backup",
            filetypes=[("ZIP Backup", "*.zip")]
        )

        if not path:
            return

        if not messagebox.askyesno(
            "Confirm Restore",
            "Restore करने पर मौजूदा Contact सूची बदल जाएगी। "
            "पहले वर्तमान डेटा का बैकअप बना लें। जारी रखें?"
        ):
            return

        try:
            with zipfile.ZipFile(path, "r") as backup_zip:
                names = backup_zip.namelist()

                if "contacts.json" not in names:
                    raise ValueError(
                        "Backup में contacts.json नहीं मिली।"
                    )

                data = json.loads(
                    backup_zip.read("contacts.json").decode("utf-8")
                )

                if not isinstance(data, list):
                    raise ValueError("Backup format गलत है।")

                for contact in data:
                    if not isinstance(contact, dict):
                        raise ValueError("Contact format गलत है।")

                    for key in ("name", "phone", "address"):
                        if not isinstance(contact.get(key, ""), str):
                            raise ValueError("Contact जानकारी गलत है।")

                # फोटो को ऐप के photos फोल्डर में सुरक्षित तरीके से कॉपी करें
                photo_map = {}

                for name in names:
                    normalized = name.replace("\\", "/")

                    if not normalized.startswith("photos/"):
                        continue

                    basename = os.path.basename(normalized)

                    if not basename:
                        continue

                    destination = os.path.join(
                        PHOTO_DIR, basename
                    )

                    with open(destination, "wb") as f:
                        f.write(backup_zip.read(name))

                    photo_map[normalized] = destination

                for contact in data:
                    photo = contact.get("photo", "")

                    if photo:
                        archived_name = (
                            "photos/" + os.path.basename(photo)
                        )

                        contact["photo"] = photo_map.get(
                            archived_name, ""
                        )

                    if not contact.get("id"):
                        contact["id"] = str(uuid.uuid4())

                old_contacts = self.contacts
                self.contacts = data

                if not self.save_contacts():
                    self.contacts = old_contacts
                    return

                self.refresh_contacts()
                self.clear_form()

                messagebox.showinfo(
                    "Restore",
                    "Contact Backup सफलतापूर्वक Restore हो गया।"
                )

        except (
            OSError,
            ValueError,
            KeyError,
            json.JSONDecodeError,
            zipfile.BadZipFile
        ) as e:
            messagebox.showerror(
                "Restore Error",
                f"Backup पढ़ने में समस्या हुई:\n{e}"
            )


# ----------------------------------
# START APP
# ----------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactBook(root)
    root.mainloop()
