import csv

input_file = 'raw_keno_data.txt'
output_file = 'keno_final_cleaned.csv'

# CSV header
header = ["Lottery Issue", "Date", "Time"] + [f"Ball {i}" for i in range(1, 21)]
output_lines = [header]

with open(input_file, 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    for row in reader:
        if len(row) >= 22:
            issue = row[0].strip().strip('"')
            datetime_raw = row[1].strip().strip('"')
            balls = [b.strip().strip('"') for b in row[2:22]]

            if len(balls) == 20:
                if ',' in datetime_raw:
                    date_part, time_part = [x.strip() for x in datetime_raw.split(',', 1)]
                else:
                    date_part, time_part = "", ""

                output_lines.append([issue, date_part, time_part] + balls)
            else:
                print(f"⚠️ Skipping row due to missing numbers: {row}")
        else:
            print(f"⚠️ Skipping malformed row: {row}")

# Write to output CSV
with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerows(output_lines)

print(f"✅ Done! Total draws processed: {len(output_lines) - 1}")
print(f"📄 Output saved to: {output_file}")
