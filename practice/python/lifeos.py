import json
from datetime import datetime

DATA_FILE = "lifeos_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "moods": [],
            "habits": {},
            "expenses": [],
            "tasks": []
        }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- MOOD ----------------
def add_mood(data):
    mood = input("How do you feel today? ")
    data["moods"].append({
        "date": str(datetime.now().date()),
        "mood": mood
    })
    print("✅ Mood saved")

# ---------------- HABITS ----------------
def add_habit(data):
    habit = input("Enter habit name: ")
    data["habits"][habit] = []
    print("✅ Habit added")

def mark_habit(data):
    habit = input("Habit name: ")
    if habit in data["habits"]:
        data["habits"][habit].append(str(datetime.now().date()))
        print("✅ Habit marked done")
    else:
        print("❌ Habit not found")

# ---------------- EXPENSE ----------------
def add_expense(data):
    name = input("Expense name: ")
    amount = float(input("Amount: "))
    data["expenses"].append({
        "date": str(datetime.now().date()),
        "name": name,
        "amount": amount
    })
    print("✅ Expense saved")

# ---------------- TASKS ----------------
def add_task(data):
    task = input("Task description: ")
    deadline = input("Deadline (YYYY-MM-DD): ")
    data["tasks"].append({
        "task": task,
        "deadline": deadline,
        "done": False
    })
    print("✅ Task added")

# ---------------- INSIGHTS ----------------
def show_insights(data):
    print("\n📊 INSIGHTS")

    print(f"Moods logged: {len(data['moods'])}")
    print(f"Habits tracked: {len(data['habits'])}")
    print(f"Total expenses: ₹{sum(e['amount'] for e in data['expenses'])}")
    pending = sum(1 for t in data["tasks"] if not t["done"])
    print(f"Pending tasks: {pending}")

# ---------------- MENU ----------------
def menu():
    print("\n🧠 LifeOS Menu")
    print("1. Add Mood")
    print("2. Add Habit")
    print("3. Mark Habit Done")
    print("4. Add Expense")
    print("5. Add Task")
    print("6. Show Insights")
    print("7. Exit")

def main():
    data = load_data()

    while True:
        menu()
        choice = input("Choose: ")

        if choice == "1":
            add_mood(data)
        elif choice == "2":
            add_habit(data)
        elif choice == "3":
            mark_habit(data)
        elif choice == "4":
            add_expense(data)
        elif choice == "5":
            add_task(data)
        elif choice == "6":
            show_insights(data)
        elif choice == "7":
            save_data(data)
            print("👋 LifeOS saved. Goodbye!")
            break
        else:
            print("❌ Invalid option")

        save_data(data)

if __name__ == "__main__":
    main()
