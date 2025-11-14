import os
import sys
import pandas as pd

def read_abstract_nos(filename, section):
    # Read the Excel file
    df = pd.read_excel(filename)

    # Strip whitespace from section number column and convert to string
    df['section number'] = df['section number'].astype(str).str.strip()
    # Filter rows where the 'section number' column matches the provided section
    filtered_df = df[df['section number'] == section.strip()]

    # Extract the 'abstract no.' column values from the filtered rows
    abstract_nos = filtered_df['abstract no.'].astype(str).str.strip().tolist()

    return abstract_nos

def concat_to(abstract_nos, folder, prefix, filename):
    with open(filename, "w", encoding="utf-8") as out_f:
        for base_name in abstract_nos:
            pathname = os.path.join(folder, f"{prefix}{base_name}.txt")
            if not os.path.isfile(pathname):
                print(f"{pathname} missing")
                continue
            with open(pathname, "r", encoding="utf-8") as in_f:
                print(f"{pathname} ...")
                out_f.write(f"<ABSTRACT:{base_name}>\n")
                out_f.write(in_f.read())
                out_f.write("\n")
                out_f.write(f"</ABSTRACT:{base_name}>\n")
                out_f.write("\n")

def main():
    if len(sys.argv) != 6:
        print("Usage: python concat.py <excel> <section> <source> <prefix> <output>")
        return

    excel = sys.argv[1]
    section = sys.argv[2]
    source = sys.argv[3]
    prefix = sys.argv[4]
    output = sys.argv[5]

    abstract_nos = read_abstract_nos(excel, section)
    for abstract_no in abstract_nos:
        print(abstract_no)

    concat_to(abstract_nos, source, prefix, output)

if __name__ == "__main__":
    main()
