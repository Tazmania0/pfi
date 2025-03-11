def process_cutting_matrix(cutting_matrix):
    batches = []
    for entry in cutting_matrix:
        color = entry.get("color")
        for size_entry in entry.get("sizes", []):
            batch = {
                "color": color,
                "size": size_entry.get("size"),
                "quantity": size_entry.get("quantity"),
                "batch_size": size_entry.get("batch_size")
            }
            batches.append(batch)
    return batches
