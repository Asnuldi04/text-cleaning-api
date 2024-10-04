# -*- coding: utf-8 -*-
"""projek API Binar Academi.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/11rlaOBDdJ3HZnFC7gHK3KCk8ff66Tjme
"""

!pip install gdown

import gdown

#ID file dari link Google drive
abusive_csv_id = "1awLJj3q9xWhh2ZDZ8VxDeCX0Yu2N1f9e"
citation_bib_id = "1oX3HM-4JjYSQ2U3VjHyo2rPrrdADLPps"
data_csv_id = "1iXXr_PRihDS99tWKGieJDfieYcOj-wM2"
readme_md_id = "1PK3y9Dt5tmLZr6ZHdtK_eA-p9JgEvmBJ"

# link file google drive
abusive_csv_url = f"https://drive.google.com/uc?export=download&id={abusive_csv_id}"
citation_bib_url = f"https://drive.google.com/uc?export=download&id={citation_bib_id}"
data_csv_url = f"https://drive.google.com/uc?export=download&id={data_csv_id}"
readme_md_url = f"https://drive.google.com/uc?export=download&id={readme_md_id}"

# instal file dan simpan dengan nama yang sesuai
gdown.download(abusive_csv_url, 'abusive.csv', quiet=False)
gdown.download(citation_bib_url, 'citation.bib', quiet=False)
gdown.download(data_csv_url, 'data.csv', quiet=False)
gdown.download(readme_md_url, 'README.md', quiet=False)

print("Semua file berhasil diunduh.")

import pandas as pd

#baca file CSV
df_abusive = pd.read_csv('abusive.csv')
df_data = pd.read_csv('data.csv', encoding='latin-1')

#Tampilkan beberapa baris pertama dari kedua file CSV
print("Isi dari file abusive.csv:")
print(df_abusive.head())

print("Isi dari file data.csv:")
print(df_data.head())

#baca isi file README.md
with open('README.md', 'r') as file:
  readme_content = file.read()
  print("Isi dari file README.md:")
  print(readme_content[:500]) #Menampilkan 500 karakter pertama

!pip install bibtexparser

import bibtexparser

#membaca file .bib
with open('citation.bib') as bibtex_file:
  bib_database = bibtexparser.load(bibtex_file)
  print("Isi dari file citation.bib:")
  print(bib_database.entries)

import re

#gabungkan  data abusive.csv dan data.csv
combined_df = pd.concat([df_abusive, df_data], ignore_index=True)

# Proses pembersihan data
if 'Tweet' in combined_df.columns:
  combined_df.dropna(subset=['Tweet'], inplace=True) # menghapus barisan yang kosong dari kolom 'Tweet'
else:

    print("Kolom 'Tweet' tidak ditemukan di DataFrame.")

#nama kolom dari 'Tweet' ke kolom 'text_column'
combined_df.rename(columns={'Tweet' : 'text_column'}, inplace=True)

combined_df['clean_text'] = combined_df['text_column'].str.lower() \
                                  .apply(lambda x: re.sub(r'[^a-z\s]', '', x))

#tampilkan hasil pembersihan data
print("Hasil pembersihan data dari file CSV yang di gabungkan:")
print(combined_df[['text_column', 'clean_text']].head())

import sqlite3

# Buat database SQLite
conn = sqlite3.connect('cleaned_combined_data.db')

# Temukan kolom duplikat (memperhitungkan perbedaan huruf besar/kecil)
duplicate_cols = combined_df.columns[combined_df.columns.str.lower().duplicated(keep=False)]

# Set untuk menyimpan kolom yang sudah diubah (lowercase)
renamed_columns = set()

# Ubah nama kolom duplikat
for col in duplicate_cols:
    # Buat nama baru untuk kolom yang diubah
    new_col_name = col
    count = 1

    # Cek dan ubah nama kolom agar tetap unik (case-insensitive)
    while new_col_name.lower() in combined_df.columns.str.lower() or new_col_name.lower() in renamed_columns:
        new_col_name = f"{col}_{count}"
        count += 1

    # Ganti nama kolom dan simpan di set (lowercase)
    combined_df.rename(columns={col: new_col_name}, inplace=True)
    renamed_columns.add(new_col_name.lower())

# Simpan data yang sudah dibersihkan ke dalam database
combined_df.to_sql('cleaned_data_table', conn, if_exists='replace', index=False)
print("Data gabungan berhasil disimpan ke SQLite.")

# Tutup koneksi database setelah selesai
conn.close()

!pip install Flask pyngrok pandas

from flask import Flask, request, jsonify
from pyngrok import ngrok
import pandas as pd
import re

app = Flask(__name__)

@app.route('/clean_text', methods=['POST'])
def clean_text(): # Penghapusan indentasi ekstra sebelum 'def'
    input_text = request.form['text']
    clean_text = re.sub(r'[^a-z\s]', '', input_text.lower())
    return jsonify({'original_text': input_text, 'cleaned_text': clean_text})

@app.route('/upload_file', methods=['POST'])
def upload_file(): # Penghapusan indentasi ekstra sebelum 'def'
    file = request.files['file']
    new_df = pd.read_csv(file)
    new_df['clean_text'] = new_df['text_column'].apply(lambda x: re.sub(r'[^a-z\s]', '', x.lower()))
    return jsonify(new_df[['text_column', 'clean_text']].head().to_dict())

if __name__ == '__main__':
    ngrok.set_auth_token("2mvv6GFipdrzAyj6hUQMuwKQhk1_3qXjeAmqwpVxRDuceDn9v") # masukan kode Auth Token
    public_url = ngrok.connect(5000) # Baris ini dan berikutnya harus pada tingkat indentasi yang sama
    print(f"Ngrok URL: {public_url}") # Indentasi ekstra sebelum print dihapus

app.run(debug=True)