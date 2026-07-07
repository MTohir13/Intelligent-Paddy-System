# generate_hash.py
import bcrypt

print("🔐 PASSWORD HASH GENERATOR")
print("=" * 50)

# Enter your desired password
password = "Admin@1234"  # Change this if you want

# Generate the hash
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode(), salt)

print("\n✅ HASH GENERATED SUCCESSFULLY!")
print("=" * 50)
print(f"Original Password: {password}")
print(f"BCrypt Hash: {hashed.decode()}")
print("=" * 50)

print("\n📋 COPY THIS FOR SQL QUERY:")
print("-" * 50)
print(f"'{hashed.decode()}'")
print("-" * 50)

# Also generate for other users if needed
print("\n🔧 OTHER COMMON PASSWORDS:")
print("-" * 50)
for pwd, name in [("Officer@1234", "Officer"), ("Farmer@1234", "Farmer")]:
    hashed_pwd = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(rounds=12))
    print(f"{name}: {pwd}")
    print(f"Hash: {hashed_pwd.decode()}")
    print()