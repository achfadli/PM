import os

# Daftar folder dan file yang ingin dibuat
folders_and_files = [
    "accounts/templates/accounts/password_reset.html",
    "accounts/templates/accounts/password_reset_email.html",
    "accounts/templates/accounts/password_reset_done.html",
    "accounts/templates/accounts/password_reset_confirm.html",
    "accounts/templates/accounts/password_reset_complete.html",
    "accounts/templates/accounts/password_change.html",
    "accounts/templates/accounts/password_change_done.html",
    "accounts/templates/accounts/profile_detail.html",
]

# Membuat folder dan file
for path in folders_and_files:
    # Membuat folder jika belum ada
    folder = os.path.dirname(path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Membuat file jika belum ada
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(f"<!-- Template for {os.path.basename(path)} -->\n")
            f.write("\n")  # Menambahkan baris kosong

print("Folder dan file telah dibuat.")