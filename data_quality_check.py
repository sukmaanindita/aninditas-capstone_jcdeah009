import pandas as pd
from pathlib import Path

## Load Data Hasil Transformasi dari data/transformed
file_directory = Path(__file__).resolve().parent / 'data' / 'transformed'
file_name = 'yellow_tripdata_2026-01_transformed.csv'
full_file_path = file_directory / file_name

class DataCleaning:
    def __init__(self):
        self.data = None

    def load_data(self, full_file_path):
        try:
            self.data = pd.read_csv(full_file_path)
            print('Data berhasil dimuat.')
            return self.data
        except FileNotFoundError:
            print(f'Error: File tidak ditemukan: {full_file_path}')
        except Exception as e:
            print(f'Terjadi error saat memuat data: {e}')

    def catching_error(self) -> bool:
        if self.data is None:
            print("❌[ERROR] Data belum dimuat. Panggil load_data() dulu.")
            return False
        return True
    
    def adjust_data_types(self):
        if not self.catching_error():
            return None
        
        print("Cek tipe data :")
        print(self.data.dtypes)

        required_columns = [
            'tpep_pickup_datetime',
            'tpep_dropoff_datetime',
            'pickup_date',
        ]
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            print(f'❌[ERROR] Kolom tidak ditemukan: {missing_columns}')
            return None

        try:
            self.data['tpep_pickup_datetime'] = pd.to_datetime(
                self.data['tpep_pickup_datetime'], errors='coerce'
            )
            self.data['tpep_dropoff_datetime'] = pd.to_datetime(
                self.data['tpep_dropoff_datetime'], errors='coerce'
            )
            self.data['pickup_date'] = pd.to_datetime(
                self.data['pickup_date'], errors='coerce'
            )
            print('✅[OK] Kolom datetime telah diubah menjadi tipe datetime.')
        except Exception as e:
            print(f'❌[ERROR] Gagal mengubah tipe data datetime: {e}')
            return None

        return self.data

    def handling_null_data(self):
        # Handle string columns (object and string dtypes)
        string_cols = list(self.data.select_dtypes(include=['object', 'string']).columns)
        for string_column in string_cols:
            if self.data[string_column].isnull().any():
                print(f"⚠️[WARNING] Ditemukan nilai null pada kolom {string_column}. Mengganti dengan 'Unknown'.")
                # avoid chained assignment / inplace on a view
                self.data[string_column] = self.data[string_column].fillna('Unknown')
                print(f"✅[OK] Nilai null pada kolom {string_column} telah diganti dengan 'Unknown'.")

        # Handle numeric columns
        numeric_cols = list(self.data.select_dtypes(include=['number']).columns)
        for numeric_column in numeric_cols:
            if self.data[numeric_column].isnull().any():
                mean_value = self.data[numeric_column].mean()
                print(f"⚠️[WARNING] Ditemukan nilai null pada kolom {numeric_column}. Mengganti dengan mean: {mean_value:.2f}.")
                self.data[numeric_column] = self.data[numeric_column].fillna(mean_value)
                print(f"✅[OK] Nilai null pada kolom {numeric_column} telah diganti dengan mean: {mean_value:.2f}.")

        return self.data
        
    
    def duration_validation(self, trip_duration_col: str = 'trip_duration'):
        if not self.catching_error():
            return None

        invalid_durations = self.data[self.data[trip_duration_col] < 0]
        if not invalid_durations.empty:
            print(f"⚠️[WARNING] Ditemukan {len(invalid_durations)} baris dengan trip_duration negatif.")
            print(invalid_durations[[trip_duration_col]].head())

            self.data["error_type"] = self.data["trip_duration"].apply(lambda x: "Duration Invalid" if x < 0 else "Valid")
        else:
            print("✅[OK] Tidak ditemukan nilai trip_duration negatif.")

        return invalid_durations
    
    def distance_validation(self, distance_col: str = 'trip_distance'):
        if not self.catching_error():
            return None
        if distance_col not in self.data.columns:
            print(f"❌[ERROR] Kolom {distance_col} tidak ditemukan")
            return None

        invalid_distances = self.data[self.data[distance_col] < 0]
        if not invalid_distances.empty:
            print(f"⚠️[WARNING] Ditemukan {len(invalid_distances)} baris dengan trip_distance negatif.")
            print(invalid_distances[[distance_col]].head())

            self.data["error_type"] = self.data["trip_distance"].apply(lambda x: "Distance Invalid" if x < 0 else "Valid")
        else:
            print("✅[OK] Tidak ditemukan nilai trip_distance negatif.")

        return invalid_distances
    
class LoadCleanedData:
    def __init__(self, cleaned_data: pd.DataFrame):
        self.cleaned_data = cleaned_data

    def save_cleaned_data(self, output_file_path: Path):
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path = Path(__file__).resolve().parent / "data" / "mart"
        file_name = 'yellow_tripdata_2026-01_cleaned.csv'
        full_file_path = file_path / file_name

        try:
            self.cleaned_data.to_csv(full_file_path, index=False)
            print(f"✅[OK] Data yang sudah dibersihkan berhasil disimpan ke: {full_file_path}")
        except Exception as e:
            print(f"❌[ERROR] Gagal menyimpan data yang sudah dibersihkan: {e}")


def main():
    stats = DataCleaning()
    stats.load_data(full_file_path)
    stats.adjust_data_types()
    stats.handling_null_data()
    stats.duration_validation()
    stats.distance_validation()
    load_data = LoadCleanedData(stats.data)
    load_data.save_cleaned_data(full_file_path)

if __name__ == "__main__":
    raise SystemExit(main())
