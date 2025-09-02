import pandas as pd

# Load your original Excel file
file_path = "Maps-Leads-Finder_1756813853156.xlsx"
df = pd.read_excel(file_path, sheet_name="sheet1")

# Select only required columns
cleaned_df = df[[
    "Name", "Phone", "Category", "Address", "Website"
]].copy()

# Extract city and locality
cleaned_df["City"] = cleaned_df["Address"].str.extract(r'([A-Za-z\s]+,\s*Bihar)')
cleaned_df["Locality"] = cleaned_df["Address"].str.split(",").str[0]

# Reorder columns
cleaned_df = cleaned_df[[
    "Name", "Phone", "Category", "Locality", "City", "Address", "Website"
]]

# Save to Excel and CSV
cleaned_df.to_excel("Cleaned_Builder_Data.xlsx", index=False)
cleaned_df.to_csv("Cleaned_Builder_Data.csv", index=False)

print("✅ Files saved as Cleaned_Builder_Data.xlsx and Cleaned_Builder_Data.csv")
