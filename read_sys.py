with open("docs/SYSTEM_CONTEXT.md", "r", encoding="utf-8") as f:
    lines = f.readlines()
print("Total lines:", len(lines))
print("\n--- Last 50 lines ---")
print("".join(lines[-50:]))
