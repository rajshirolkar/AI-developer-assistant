import csv
import pandas as pd

def append_thumb(csv_path, value):
    with open(csv_path, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)  # Convert iterator to list to reuse it
        fieldnames = reader.fieldnames

        # Add 'thumb' column if it does not exist
        if 'thumb' not in fieldnames:
            fieldnames.append('thumb')
            for row in rows:
                row['thumb'] = None  # Initialize 'thumb' column with None for existing rows

    # Update the 'thumb' column in the last row with existing data in the first column
    if rows:
        rows[-1]['thumb'] = value  # Assuming the last row is where you want to update the 'thumb' value

    # Write the updated data back to the CSV file
    with open(csv_path, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    # Load the CSV file into a DataFrame
    # df = pd.read_csv(csv_path)
    #
    # # Check if 'thumb' column exists; if not, add it
    # if 'thumb' not in df.columns:
    #     df['thumb'] = pd.Series()
    #
    # # Create a new DataFrame with the value in the 'thumb' column
    # new_row = pd.DataFrame({'thumb': [value]}, index=[len(df)])
    #
    # # Other columns in the DataFrame will be NaN for this new row
    # # Concatenate the original DataFrame with the new row
    # df = pd.concat([df, new_row], ignore_index=True)
    #
    # # Save the DataFrame back to CSV
    # df.to_csv(csv_path, index=False)