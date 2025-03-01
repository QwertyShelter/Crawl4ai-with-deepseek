import csv

from models.project import Project


def is_duplicate_project(project_name: str, seen_names: set) -> bool:
    return project_name in seen_names


def is_complete_project(project: dict, required_keys: list) -> bool:
    return all(key in project for key in required_keys)


def save_projects_to_csv(projects: list, filename: str):
    if not projects:
        print("No venues to save.")
        return

    # Use field names from the Venue model
    fieldnames = Project.model_fields.keys()

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(projects)
    print(f"Saved {len(projects)} venues to '{filename}'.")
