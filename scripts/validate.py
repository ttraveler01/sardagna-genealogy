#!/usr/bin/env python3
"""
Validate sardagna.json against schema.json and custom rules.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from jsonschema import validate, ValidationError, Draft202012Validator

CURRENT_YEAR = datetime.now().year
LIVING_THRESHOLD = 1926  # Conservative cutoff: anyone born after this needs explicit death date

def load_json(path):
    """Load and parse a JSON file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {path}: {e}")
        sys.exit(1)

def validate_schema(data, schema):
    """Validate data against JSON schema."""
    errors = []
    try:
        validator = Draft202012Validator(schema)
        for error in validator.iter_errors(data):
            path = " → ".join(str(p) for p in error.absolute_path) or "root"
            errors.append(f"  - {path}: {error.message}")
    except Exception as e:
        errors.append(f"  Schema validation failed: {e}")
    return errors

def check_privacy(data):
    """Check privacy rules: no living persons without explicit death."""
    errors = []
    for person in data.get('individuals', []):
        birth_year = person.get('birthYear')
        death_year = person.get('deathYear')

        # If born after threshold and no death year, potential privacy violation
        if birth_year and birth_year > LIVING_THRESHOLD and death_year is None:
            errors.append(
                f"  - {person['id']} ({person['givenNames']} {person['surname']}, "
                f"b. {birth_year}): Born after {LIVING_THRESHOLD} without death date "
                f"(possibly living). Either add deathYear or exclude this person."
            )
    return errors

def check_sourcing(data):
    """Check that every relationship has at least one source."""
    errors = []
    for rel in data.get('relationships', []):
        sources = rel.get('sources', [])
        if not sources or not any(sources):
            rel_type = rel.get('type', '?')
            errors.append(
                f"  - Relationship {rel['from']} → {rel['to']} ({rel_type}): "
                f"No sources. Every relationship must cite at least one source document."
            )
    return errors

def check_referential_integrity(data):
    """Check that all IDs in relationships exist in individuals."""
    errors = []
    individual_ids = {ind['id'] for ind in data.get('individuals', [])}

    for rel in data.get('relationships', []):
        from_id = rel.get('from')
        to_id = rel.get('to')

        if from_id not in individual_ids:
            errors.append(f"  - Relationship from '{from_id}': ID not found in individuals")
        if to_id not in individual_ids:
            errors.append(f"  - Relationship to '{to_id}': ID not found in individuals")

    return errors

def check_duplicates(data):
    """Check for duplicate IDs."""
    errors = []
    seen_ids = {}

    for person in data.get('individuals', []):
        pid = person['id']
        if pid in seen_ids:
            errors.append(f"  - Duplicate individual ID: {pid}")
        seen_ids[pid] = person

    return errors

def check_logical_consistency(data):
    """Basic logical checks."""
    errors = []

    for person in data.get('individuals', []):
        birth = person.get('birthYear')
        death = person.get('deathYear')
        emig = person.get('emigration', {})
        emig_year = emig.get('year')

        # Death before birth?
        if birth and death and death < birth:
            errors.append(
                f"  - {person['id']}: Death year ({death}) before birth year ({birth})"
            )

        # Emigration before birth or after death?
        if emig_year:
            if birth and emig_year < birth:
                errors.append(
                    f"  - {person['id']}: Emigration ({emig_year}) before birth ({birth})"
                )
            if death and emig_year > death:
                errors.append(
                    f"  - {person['id']}: Emigration ({emig_year}) after death ({death})"
                )

    return errors

def main():
    """Run all validations."""
    repo_root = Path(__file__).parent.parent
    schema_path = repo_root / 'schema.json'
    data_paths = list((repo_root / 'data').glob('*.json'))

    if not data_paths:
        print("❌ No JSON files found in data/")
        sys.exit(1)

    all_errors = []
    all_warnings = []

    print("📋 Validating genealogy data...\n")

    for data_path in sorted(data_paths):
        print(f"Checking {data_path.name}...")

        schema = load_json(schema_path)
        data = load_json(data_path)

        # Schema validation
        errors = validate_schema(data, schema)
        if errors:
            all_errors.append((data_path.name, "Schema validation", errors))
            print(f"  ❌ Schema validation failed")
            continue
        print(f"  ✓ Schema valid")

        # Duplicate IDs
        errors = check_duplicates(data)
        if errors:
            all_errors.append((data_path.name, "Duplicate IDs", errors))
        else:
            print(f"  ✓ No duplicate IDs")

        # Referential integrity
        errors = check_referential_integrity(data)
        if errors:
            all_errors.append((data_path.name, "Referential integrity", errors))
        else:
            print(f"  ✓ All IDs are referenced correctly")

        # Sourcing
        errors = check_sourcing(data)
        if errors:
            all_errors.append((data_path.name, "Sourcing", errors))
            print(f"  ⚠️  Sourcing issues found")
        else:
            print(f"  ✓ All relationships have sources")

        # Privacy
        errors = check_privacy(data)
        if errors:
            all_warnings.append((data_path.name, "Privacy", errors))
            print(f"  ⚠️  Privacy concerns (review needed)")
        else:
            print(f"  ✓ Privacy rules OK")

        # Logical consistency
        errors = check_logical_consistency(data)
        if errors:
            all_errors.append((data_path.name, "Logical consistency", errors))
            print(f"  ❌ Logical inconsistencies found")
        else:
            print(f"  ✓ Logical consistency OK")

        print()

    # Generate report
    report = []
    report.append(f"# Validation Report — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    if all_errors or all_warnings:
        if all_errors:
            report.append("## ❌ Errors\n")
            for filename, category, errors in all_errors:
                report.append(f"### {filename} — {category}\n")
                for error in errors:
                    report.append(error + "\n")
                report.append("\n")

        if all_warnings:
            report.append("## ⚠️  Warnings (Review Required)\n")
            for filename, category, warnings in all_warnings:
                report.append(f"### {filename} — {category}\n")
                for warning in warnings:
                    report.append(warning + "\n")
                report.append("\n")
    else:
        report.append("✅ All checks passed.\n")

    report_text = "".join(report)

    # Write to file for GitHub Actions
    with open(repo_root / 'validation-report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(report_text)

    # Exit with error if there are errors (but not warnings)
    if all_errors:
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
