from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import pandas as pd


class DataTransformation:
    def __init__(self) -> None:
        self.data: Optional[pd.DataFrame] = None

    def catching_error(self) -> bool:
        if self.data is None:
            print("❌[ERROR] Data belum dimuat. Panggil extract_data() dulu.")
            return False
        return True

    def extract_data(self, trip_path: Path) -> Optional[pd.DataFrame]:
        try:
            self.data = pd.read_parquet(trip_path)
            print(f"✅[OK] Data berhasil dimuat: {trip_path}")
            return self.data
        except FileNotFoundError:
            print(f"❌[ERROR] File tidak ditemukan: {trip_path}")
        except Exception as e:
            print(f"❌[ERROR] Gagal memuat parquet: {e}")
        return None

    def load_location_mapping(self, mapping_path: Path) -> Optional[pd.DataFrame]:
        try:
            # Pandas can read Path directly; keep simple for beginners
            mapping = pd.read_csv(mapping_path)
            mapping.columns = mapping.columns.str.lower()
            print(f"✅[OK] Data Mapping Location berhasil dimuat: {mapping_path}")
            return mapping
        except FileNotFoundError:
            print(f"❌[ERROR] File Mapping tidak ditemukan: {mapping_path}")
        except Exception as e:
            print(f"❌[ERROR] Gagal memuat mapping: {e}")
        return None

    def lower_columns(self) -> Optional[pd.DataFrame]:
        if not self.catching_error():
            return None
        self.data.columns = [c.lower() for c in self.data.columns]
        print(f"✅[OK] Nama kolom telah diubah menjadi huruf kecil.")
        return self.data

    def add_datetime_features(self, datetime_col: str = "tpep_pickup_datetime") -> Optional[pd.DataFrame]:
        if not self.catching_error():
            return None
        if datetime_col not in self.data.columns:
            print(f"❌[ERROR] Column {datetime_col} tidak ditemukan")
            return None

        dt = self.data[datetime_col]
        self.data["pickup_date"] = dt.dt.date
        self.data["pickup_hour"] = dt.dt.hour
        self.data["day_of_week"] = dt.dt.day_name()
        self.data["is_weekend"] = dt.dt.weekday >= 5
        self.data["trip_duration"] = (self.data["tpep_dropoff_datetime"] - self.data["tpep_pickup_datetime"]).dt.total_seconds()
        print(f"✅[OK] Kolom datetime telah ditambahkan: pickup_date, pickup_hour, day_of_week, is_weekend, trip_duration")
        return self.data
    
    def mapping_payment_type(self, payment_col: str = "payment_type") -> Optional[pd.DataFrame]:
        if not self.catching_error():
            return None
        if payment_col not in self.data.columns:
            print(f"❌[ERROR] Column {payment_col} tidak ditemukan")
            return None

        payment_mapping = {
            1: "Credit Card",
            2: "Cash",
            3: "No Charge",
            4: "Dispute",
            0: "Unknown",
        }
        self.data[payment_col] = self.data[payment_col].map(payment_mapping).fillna("Unknown")
        print(f"✅[OK] Kolom {payment_col} telah dimapping ke deskripsi pembayaran.")
        return self.data
    
    def mapping_store_and_fwd_flag(self, flag_col: str = "store_and_fwd_flag") -> Optional[pd.DataFrame]:
        if not self.catching_error():
            return None
        if flag_col not in self.data.columns:
            print(f"❌[ERROR] Column {flag_col} tidak ditemukan")
            return None

        flag_mapping = {
            "Y": "Store and Forward",
            "N": "Normal",
        }
        self.data[flag_col] = self.data[flag_col].map(flag_mapping).fillna("Unknown")
        print(f"✅[OK] Kolom {flag_col} telah dimapping ke deskripsi store_and_fwd_flag.")
        return self.data

    def add_time_period(self, hour_col: str = "pickup_hour") -> Optional[pd.DataFrame]:
        if not self.catching_error():
            return None
        if hour_col not in self.data.columns:
            print(f"❌[ERROR] Column {hour_col} tidak ditemukan")
            return None

        bins = [0, 6, 11, 16, 20, 24]
        labels = ["Late Night", "Morning", "Afternoon", "Evening Rush", "Night"]
        self.data["time_period"] = pd.cut(self.data[hour_col], bins=bins, labels=labels, right=False)
        print(f"✅[OK] Kolom time_period telah ditambahkan")
        return self.data

    def mapping_locationid_to_borough_columns(self, mapping: pd.DataFrame, pu_col: str = "pulocationid", do_col: str = "dolocationid") -> Optional[pd.DataFrame]:
        if not self.catching_error():
            return None
        if mapping is None:
            print(f"❌[ERROR] Mapping tidak tersedia. Pastikan load_location_mapping() berhasil dipanggil sebelum mapping.")
            return None

        mapping = mapping.copy()
        if "locationid" not in mapping.columns or "borough" not in mapping.columns:
            print(f"❌[ERROR] mapping harus berisi 'locationid' dan 'borough'")
            print(f"❌[ERROR] Kolom yang tersedia dimapping: {mapping.columns.tolist()}")
            return None

        # create dict int -> borough
        mapping_dict = mapping.set_index("locationid")["borough"].to_dict()

        # Map values in-place: replace ID values with borough names
        if pu_col in self.data.columns:
            self.data[pu_col] = self.data[pu_col].map(mapping_dict).fillna("Unknown")
        else:
            print(f"❌[WARN] {pu_col} tidak ditemukan; {pu_col} tidak dimapping")

        if do_col in self.data.columns:
            self.data[do_col] = self.data[do_col].map(mapping_dict).fillna("Unknown")
        else:
            print(f"❌[WARN] {do_col} tidak ditemukan; {do_col} tidak dimapping")

        print(f"✅[OK] Nilai pada kolom {pu_col} dan {do_col} telah dimapping menjadi borough")
        return self.data

    def transform_all(self, mapping: Optional[pd.DataFrame] = None) -> Optional[pd.DataFrame]:
        # convenience method to run all transforms in sensible order
        if not self.catching_error():
            return None
        self.lower_columns()
        # assume datetime column exists and is already datetime dtype; if not, user should ensure it
        self.add_datetime_features()
        self.add_time_period()
        self.mapping_payment_type()
        self.mapping_store_and_fwd_flag()
        if mapping is not None:
            self.mapping_locationid_to_borough_columns(mapping)
        return self.data

    def save(self, out_dir: str = "data/transformed", filename: str = "transformed.csv") -> Optional[Path]:
        if not self.catching_error():
            return None
        out_path = Path(__file__).resolve().parent / out_dir
        out_path.mkdir(parents=True, exist_ok=True)
        file_path = out_path / filename
        try:
            self.data.to_csv(file_path, index=False)
            print(f"✅[OK] === File berhasil disimpan: {file_path} ===")
            return file_path
        except Exception as e:
            print(f"❌[ERROR] === Gagal menyimpan file: {e} ===")
            return None


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Transform pipeline (v2) - beginner friendly")
    default_dir = Path(__file__).resolve().parent / "data"
    parser.add_argument("--trip", type=Path, default=default_dir / "yellow_tripdata_2026-01.parquet")
    parser.add_argument("--mapping", type=Path, default=default_dir / "taxi_zone_lookup_table.csv")
    parser.add_argument("--transformed", type=str, default="data/transformed")
    parser.add_argument("--mart", type=str, default="data/mart")
    parser.add_argument("--run", action="store_true", help="Actually run transformations and save files")

    args = parser.parse_args(argv)

    print("✅[INFO] Config:")
    print(f"  trip: {args.trip}")
    print(f"  mapping: {args.mapping}")
    print(f"  transformed: {args.transformed}")
    print(f"  mart: {args.mart}")

    transformer = DataTransformation()

    if not args.run:
        print("✅[INFO] Pipeline tidak dijalankan karena --run tidak diberikan. Gunakan --run untuk menjalankan transformasi dan menyimpan file.")
        return 0

    # Run pipeline
    if not args.trip.exists():
        print(f"❌[ERROR] File tidak ditemukan: {args.trip}")
        return 1
    transformer.extract_data(args.trip)

    mapping = None
    if args.mapping.exists():
        mapping = transformer.load_location_mapping(args.mapping)
    else:
        print(f"❌[WARNING] File tidak ditemukan: {args.mapping} (melanjutkan tanpa melakukan mapping LocationID)")

    transformer.transform_all(mapping)
    transformer.save(out_dir=args.transformed, filename="yellow_tripdata_2026-01_transformed.csv")
    transformer.save(out_dir=args.mart, filename="yellow_tripdata_2026-01.csv")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
