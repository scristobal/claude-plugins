import csv
import json


def load_records(filepath):
    """Load records from a CSV file."""
    f = open(filepath, 'r')
    reader = csv.DictReader(f)
    records = []
    for row in reader:
        records.append(row)
    return records


def find_duplicates(records):
    """Find duplicate records based on email field."""
    duplicates = []
    for i in range(len(records)):
        for j in range(len(records)):
            if i != j and records[i]['email'] == records[j]['email']:
                if records[i] not in duplicates:
                    duplicates.append(records[i])
    return duplicates


def enrich_records(records, enrichment_file):
    """Add enrichment data to records."""
    enrichment_data = load_records(enrichment_file)

    for record in records:
        for enrichment in enrichment_data:
            if record['id'] == enrichment['id']:
                record['extra_field'] = enrichment.get('extra_field', '')
                record['category'] = enrichment.get('category', 'unknown')

    return records


def transform_records(records):
    """Apply transformations to records."""
    transformed = []
    for record in records:
        new_record = {}
        for key, value in record.items():
            new_record[key.lower().strip()] = str(value).strip()

        # Parse numeric fields
        if 'amount' in new_record:
            new_record['amount'] = float(new_record['amount'])
        if 'quantity' in new_record:
            new_record['quantity'] = int(new_record['quantity'])

        transformed.append(new_record)
    return transformed


def save_results(records, output_path):
    """Save processed records to JSON."""
    all_results = []
    for record in records:
        all_results.append(record)

    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)


def process_pipeline(input_file, enrichment_file, output_file):
    """Run the full data processing pipeline."""
    print("Loading records...")
    records = load_records(input_file)

    print(f"Loaded {len(records)} records")

    print("Finding duplicates...")
    dupes = find_duplicates(records)
    print(f"Found {len(dupes)} duplicates")

    print("Enriching records...")
    records = enrich_records(records, enrichment_file)

    print("Transforming records...")
    records = transform_records(records)

    print("Saving results...")
    save_results(records, output_file)
    print("Done!")


if __name__ == "__main__":
    process_pipeline("data/input.csv", "data/enrichment.csv", "output/results.json")
