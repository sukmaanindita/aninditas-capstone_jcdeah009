# Capstone 01 - NYC Yellow Taxi ETL Pipeline

Project ini berisi pipeline sederhana untuk melakukan proses Extract, Transform, Load (ETL) dan data quality check pada dataset NYC Yellow Taxi bulan Januari 2026.

Pipeline membaca data mentah dalam format Parquet, melakukan transformasi kolom, mapping data referensi lokasi dan pembayaran, menyimpan hasil transformasi, lalu menjalankan pengecekan kualitas data sebelum menghasilkan dataset final yang sudah dibersihkan.

Pipeline juga sudah mencakup proses automasi menggunakan shell script untuk menjalankan seluruh pipeline dengan satu command, kemudian menyimpan log proses automasinya ke dalam folder `logs/`. Selain itu, project ini juga mendukung containerization menggunakan `DockerFile` dan `docker-compose.yaml`, sehingga pipeline dapat dijalankan di dalam container Docker dengan environment yang lebih konsisten.

## Tujuan Projects

- Membuat pipeline ETL menggunakan Python dan Pandas.
- Mengubah data mentah Yellow Taxi menjadi data yang lebih siap dianalisis.
- Menambahkan fitur turunan seperti tanggal pickup, jam pickup, hari, weekend flag, periode waktu, dan durasi perjalanan.
- Melakukan mapping kode pembayaran, store-and-forward flag, dan LocationID ke borough.
- Melakukan pengecekan kualitas data seperti tipe data, missing value, durasi negatif, dan jarak perjalanan negatif.
- Menyimpan output ke folder `data/transformed` dan `data/mart`.

## Struktur Project

```text
Capstone01/
├── data/
│   ├── yellow_tripdata_2026-01.parquet
│   ├── taxi_zone_lookup_table.csv
│   ├── transformed/
│   │   └── yellow_tripdata_2026-01_transformed.csv
│   └── mart/
│       ├── yellow_tripdata_2026-01.csv
│       └── yellow_tripdata_2026-01_cleaned.csv
├── logs/
│   └── pipeline.log
├── extract_transform_load_data.py
├── data_quality_check.py
├── auto_command_script.sh
├── docker-compose.yaml
├── DockerFile
├── requirements.txt
└── README.md
```

## Dataset

Dataset utama yang digunakan:

- `data/yellow_tripdata_2026-01.parquet`: data mentah perjalanan Yellow Taxi.
- `data/taxi_zone_lookup_table.csv`: data mapping lokasi taxi berdasarkan `LocationID`.

Karena ukuran dataset biasanya besar, folder `data/` dapat dimasukkan ke `.gitignore` agar file data tidak ikut terunggah ke GitHub.

## Alur Pipeline

### 1. Extract

Script `extract_transform_load_data.py` membaca file Parquet:

```python
pd.read_parquet("data/yellow_tripdata_2026-01.parquet")
```

Script juga membaca file mapping lokasi:

```python
pd.read_csv("data/taxi_zone_lookup_table.csv")
```

### 2. Transform

Transformasi yang dilakukan antara lain:

- Mengubah semua nama kolom menjadi huruf kecil.
- Menambahkan kolom:
  - `pickup_date`
  - `pickup_hour`
  - `day_of_week`
  - `is_weekend`
  - `trip_duration`
  - `time_period`
- Mapping `payment_type` menjadi deskripsi seperti `Credit Card`, `Cash`, `No Charge`, dan `Dispute`.
- Mapping `store_and_fwd_flag` menjadi `Store and Forward` atau `Normal`.
- Mapping `pulocationid` dan `dolocationid` menjadi nama borough.

### 3. Load

Hasil transformasi disimpan ke:

```text
data/transformed/yellow_tripdata_2026-01_transformed.csv
data/mart/yellow_tripdata_2026-01.csv
```

### 4. Data Quality Check

Script `data_quality_check.py` melakukan pengecekan dan cleaning:

- Memastikan data berhasil dimuat.
- Mengubah kolom tanggal menjadi tipe datetime.
- Mengisi missing value pada kolom string dengan `Unknown`.
- Mengisi missing value pada kolom numerik dengan nilai rata-rata.
- Mengecek nilai negatif pada `trip_duration`.
- Mengecek nilai negatif pada `trip_distance`.

Hasil akhir data yang sudah dibersihkan disimpan ke:

```text
data/mart/yellow_tripdata_2026-01_cleaned.csv
```

## Cara Menjalankan Project

### 1. Clone repository

```bash
git clone <repository-url>
cd Capstone01
```

### 2. Buat virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Untuk Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Pastikan file data tersedia

Simpan file berikut di folder `data/`:

```text
data/yellow_tripdata_2026-01.parquet
data/taxi_zone_lookup_table.csv
```

### 5. Jalankan proses transformasi

```bash
python3 extract_transform_load_data.py --run
```

Jika berhasil, file hasil transformasi akan muncul di:

```text
data/transformed/yellow_tripdata_2026-01_transformed.csv
data/mart/yellow_tripdata_2026-01.csv
```

### 6. Jalankan data quality check

```bash
python3 data_quality_check.py
```

Jika berhasil, file cleaned akan muncul di:

```text
data/mart/yellow_tripdata_2026-01_cleaned.csv
```

## Menjalankan dengan Shell Script

Project ini juga memiliki script automation:

```bash
bash auto_command_script.sh
```

Script ini akan menjalankan proses transformasi dan data quality check secara berurutan, lalu menyimpan log eksekusi ke `logs/pipeline.log`.

## Menjalankan dengan Docker

Build dan jalankan container:

```bash
docker compose up --build
```

Docker Compose akan menjalankan `auto_command_script.sh` di dalam container dan melakukan mount folder `data/` serta `logs/`.

## Output

| File | Keterangan |
| --- | --- |
| `data/transformed/yellow_tripdata_2026-01_transformed.csv` | Data hasil transformasi awal |
| `data/mart/yellow_tripdata_2026-01.csv` | Data mart hasil transformasi |
| `data/mart/yellow_tripdata_2026-01_cleaned.csv` | Data final setelah quality check |
| `logs/pipeline.log` | Log eksekusi pipeline automation |

## Dependencies

Dependency utama project:

```text
pandas
```

Dependency didefinisikan di `requirements.txt`.

## Author

Project ini dibuat sebagai bagian dari Capstone Project 1 JCDEAH-009.
