import os

def update_gitignore(predefined_rules):
    gitignore_path = '.gitignore'
    
    # Read existing .gitignore content
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as file:
            existing_rules = set(file.read().splitlines())
    else:
        existing_rules = set()

    # Split predefined rules into lines
    new_rules = set(predefined_rules.splitlines())

    # Find rules to append
    rules_to_append = new_rules - existing_rules

    # Append new rules if any
    if rules_to_append:
        with open(gitignore_path, 'a') as file:
            file.write('\n' + '\n'.join(rules_to_append) + '\n')
        print(f"Added {len(rules_to_append)} new rules to .gitignore")
    else:
        print("No new rules to add. .gitignore is up to date.")

if __name__ == "__main__":
    predefined_rules = """
**/__pycache__
**/*.swp
*.xml
.aider*

**/__pycache__/
**/*.db
log/
**/*Zone.Identifier
"""
    update_gitignore(predefined_rules)
