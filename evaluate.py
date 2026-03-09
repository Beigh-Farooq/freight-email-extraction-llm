import json


FIELDS = [
    "product_line",
    "origin_port_code",
    "origin_port_name",
    "destination_port_code",
    "destination_port_name",
    "incoterm",
    "cargo_weight_kg",
    "cargo_cbm",
    "is_dangerous",
]


def normalize(value):

    if isinstance(value, str):
        return value.strip().lower()

    return value


def load_json(path):

    with open(path) as f:
        return json.load(f)


def main():

    gt = load_json("data/ground_truth.json")
    pred = load_json("output.json")

    gt_map = {x["id"]: x for x in gt}
    pred_map = {x["id"]: x for x in pred}

    correct = {f: 0 for f in FIELDS}
    total = len(gt)

    for email_id in gt_map:

        for field in FIELDS:

            gt_val = normalize(gt_map[email_id].get(field))
            pr_val = normalize(pred_map[email_id].get(field))

            if gt_val == pr_val:
                correct[field] += 1

    print("\nAccuracy Report\n")

    total_correct = 0

    for f in FIELDS:

        acc = correct[f] / total
        total_correct += correct[f]

        print(f"{f}: {acc:.2f}")

    overall = total_correct / (total * len(FIELDS))

    print("\nOverall Accuracy:", round(overall, 2))


if __name__ == "__main__":
    main()