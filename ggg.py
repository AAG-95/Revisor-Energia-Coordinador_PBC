carpeta_recaudacion = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Revisiones\Revisión Recaudación\Revisión Histórica\\"

def identificar_filas_con_problemas(file_path, encoding="utf-8"):
    problematic_rows = []
    with open(file_path, "rb") as file:
        for i, line in enumerate(file):
            try:
                line.decode(encoding)
            except UnicodeDecodeError as e:
                problematic_byte = line[e.start:e.start+1]
                problematic_rows.append((i, line, e, problematic_byte))
    return problematic_rows

# Path to your CSV file
file_path = carpeta_recaudacion + "BDD Clientes Libres Históricos.csv"

# Identify problematic rows
problematic_rows = identificar_filas_con_problemas(file_path, encoding="utf-8")

# Print problematic rows
for row_num, line, error, problematic_byte in problematic_rows:
    print(f"Row {row_num} has an encoding issue: {error}")
    print(f"Problematic byte: {problematic_byte}")
    print(f"Row content: {line}")