from sentence_transformers import SentenceTransformer, util
import pandas as pd
import funciones as fc


def homologa_sistemas_RE244():
    # ruta de recaudación
    ruta_revision = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\Revisores RCUT.xlsm"
    # ruta de homologación RE244
    ruta_homologacion_RE244 = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Revisiones\Revisión Recaudación\Sistemas Transmisión\Clasificación Sistemas (RE244 2019).xlsx"

    # open excel with pandas
    df_revision = pd.read_excel(
        ruta_revision, sheet_name="Sistemas Zonales vigentes Clien"
    )
    df_revision = fc.ObtencionDatos().obtencion_tablas_clientes(df_revision, 4, 6, 10)
    #replace number and _ with ''
    df_revision['Barra_aux'] = df_revision['Barra'].str.replace("_","")
    
    df_revision['Barra_aux']  = df_revision['Barra_aux'].str[:-3]
    df_revision['Barra_aux'] = df_revision['Barra_aux'].apply(lambda x: x[0] + x[1:].lower())
    df_re244 = pd.read_excel(ruta_homologacion_RE244)

    return df_revision, df_re244


# Load a pre-trained Spanish model
model = SentenceTransformer("sentence-transformers/paraphrase-mpnet-base-v2")


# Function to find the best match for a string in a list using embeddings
def find_best_match(target, options):
    target_embedding = model.encode(target)
    options_embeddings = model.encode(options)

    # Calculate cosine similarity between target and each option
    similarities = util.pytorch_cos_sim(target_embedding, options_embeddings)[0]

    # Find the option with the highest similarity
    best_match_index = similarities.argmax().item()
    best_match = options[best_match_index]

    return best_match


df_revision, df_re244 = homologa_sistemas_RE244()

listado_re244 = df_re244["Tramo Subestación"].tolist()

lista_resultados = []

# Match records
for barra_aux, barra in zip(df_revision['Barra_aux'].tolist(), df_revision['Barra'].tolist()):
    mejor_resultado = find_best_match(barra_aux, listado_re244)
    # save match in list. append record1 and mejor_resltado and then convert into dataframe 
    lista_resultados.append((barra,barra_aux, mejor_resultado))
    print(f"{barra_aux} matched with {mejor_resultado}")


# Convert the list into a DataFrame
df_homologa = pd.DataFrame(lista_resultados, columns=['Barra', 'Barra_aux','mejor_resultado'])

ruta_salida =  r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Revisiones\Revisión Recaudación\Sistemas Transmisión\Homologación Barras RE244 2019.csv"

#csv 
df_homologa.to_csv(ruta_salida, sep=	";" , encoding= "UTF-8")
print(mejor_resultado)
