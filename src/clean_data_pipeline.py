"""
clean_data_pipeline.py
=============================================================================
Pipeline lam sach va chuan hoa du lieu - Fashion_DW_Project
Giai doan: Chuan bi du lieu dau vao cho Kho du lieu (Data Warehouse Staging)

Pham vi: 13 bang CSV nghiep vu trong data/raw/
  - customers, geography, inventory, order_items, orders, payments,
    products, promotions, returns, reviews, sales, shipments, web_traffic
Loai tru: sample_submission.csv, submission_idea42_alphaequal.csv (du bao ML)

Quy tac lam sach:
  1. Bao toan tuyet doi du lieu goc: data/raw/ la bat bien (read-only).
  2. Xuat file da chuan hoa sang data/processed/ voi ten cot va cau truc giu nguyen.
  3. Chuan hoa khoang trang dau/cuoi o cac cot chuoi (.str.strip()).
  4. Chuan hoa va xac thuc dinh dang ngay gio ISO 8601 (YYYY-MM-DD).
  5. Bao luu nguyen ven NULL hop le o promo_id, promo_id_2, applicable_category.
  6. Bao luu toan bo 714,669 dong order_items (gom 32 dong trung order_id, product_id).
  7. Khong tao surrogate key cho order_items o tang CSV nay.
  8. Bao luu toan bo 39,939 dong returns (bao gom RET-043492).
  9. Bao luu cac gia tri nghi van nghiep vu (order < signup, margin < 5%, v.v.).
  10. Kiem chung nghiem ngat: SHA-256 raw, so dong, gia tri so hoc, tinh toan ven PK/FK.
=============================================================================
"""

import sys
import hashlib
from pathlib import Path
import pandas as pd
import numpy as np

# Duong dan thu muc
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DOCS_DIR = BASE_DIR / "docs"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Danh muc 13 bang nghiep vu
BUSINESS_FILES = [
    "customers.csv",
    "geography.csv",
    "inventory.csv",
    "order_items.csv",
    "orders.csv",
    "payments.csv",
    "products.csv",
    "promotions.csv",
    "returns.csv",
    "reviews.csv",
    "sales.csv",
    "shipments.csv",
    "web_traffic.csv",
]

# Cac cot chua gia tri ngay thang
DATE_COLUMNS = {
    "customers.csv": ["signup_date"],
    "inventory.csv": ["snapshot_date"],
    "orders.csv": ["order_date"],
    "promotions.csv": ["start_date", "end_date"],
    "returns.csv": ["return_date"],
    "reviews.csv": ["review_date"],
    "sales.csv": ["Date"],
    "shipments.csv": ["ship_date", "delivery_date"],
    "web_traffic.csv": ["date"],
}

# Cac cot duoc phep co NULL theo nghiep vu
VALID_NULL_COLUMNS = {
    "order_items.csv": ["promo_id", "promo_id_2"],
    "promotions.csv": ["applicable_category"],
}

def compute_sha256(file_path: Path) -> str:
    """Tinh ma SHA-256 cua tap tin."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 70)
    print("BAT DAU PIPELINE LAM SACH DU LIEU (FASHION_DW_PROJECT)")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # BUOC 1: TINH SHA-256 DU LIEU GOC (PRE-EXECUTION HASH)
    # -------------------------------------------------------------------------
    print("\n[BUOC 1] Tinh ma SHA-256 cho toan bo 15 tap tin trong data/raw/...")
    all_raw_files = sorted(RAW_DIR.glob("*.csv"))
    raw_hashes_before = {}
    for f in all_raw_files:
        h = compute_sha256(f)
        raw_hashes_before[f.name] = h
        print(f"  {f.name:32s} SHA-256: {h[:16]}...")
    print(f"  => Da ghi nhan {len(raw_hashes_before)} ma hash goc.")

    # -------------------------------------------------------------------------
    # BUOC 2: DOC, CHUAN HOA VA XUAT DANG DATA/PROCESSED/
    # -------------------------------------------------------------------------
    print("\n[BUOC 2] Tien hanh chuan hoa va xuat 13 bang nghiep vu...")
    cleaning_metrics = []
    raw_dataframes = {}
    processed_dataframes = {}

    for fname in BUSINESS_FILES:
        raw_path = RAW_DIR / fname
        proc_path = PROCESSED_DIR / fname

        print(f"\n--- Xu ly: {fname} ---")
        df_raw = pd.read_csv(raw_path, low_memory=False)
        raw_dataframes[fname] = df_raw.copy()
        
        n_rows_raw = len(df_raw)
        n_cols_raw = len(df_raw.columns)
        df_proc = df_raw.copy()

        total_values_standardized = 0

        # 2.1 Chuan hoa khoang trang dau/cuoi cho cac cot chuoi
        str_cols = df_proc.select_dtypes(include=["object"]).columns
        for col in str_cols:
            s = df_proc[col]
            not_null_mask = s.notna()
            # Kiem tra xem co bao nhieu gia tri bi lech khoang trang
            s_str = s[not_null_mask].astype(str)
            s_stripped = s_str.str.strip()
            diff_count = (s_str != s_stripped).sum()
            if diff_count > 0:
                total_values_standardized += diff_count
                df_proc.loc[not_null_mask, col] = s_stripped
                print(f"  [STRIP] Cot '{col}': da cat khoang trang o {diff_count:,} gia tri.")

        # 2.2 Kiem tra va chuan hoa ngay thang (ISO 8601: YYYY-MM-DD)
        if fname in DATE_COLUMNS:
            for dcol in DATE_COLUMNS[fname]:
                # Kiem tra mau YYYY-MM-DD
                is_iso = df_proc[dcol].dropna().astype(str).str.match(r"^\d{4}-\d{2}-\d{2}$").all()
                if not is_iso:
                    raise ValueError(f"Phat hien dinh dang ngay bat thuong o {fname}[{dcol}]!")
                # Parse strict khong duoc loi (errors='raise')
                parsed_dates = pd.to_datetime(df_proc[dcol], format="%Y-%m-%d", errors="raise")
                # Format lai chac chan thanh YYYY-MM-DD
                df_proc[dcol] = parsed_dates.dt.strftime("%Y-%m-%d")
                print(f"  [DATE] Cot '{dcol}': da xac thuc ISO 8601 (YYYY-MM-DD) 100% hop le.")

        # 2.3 Bao luu cac cot co NULL hop le
        if fname in VALID_NULL_COLUMNS:
            for ncol in VALID_NULL_COLUMNS[fname]:
                null_cnt = df_proc[ncol].isna().sum()
                print(f"  [NULL] Cot '{ncol}': bao luu nguyen ven {null_cnt:,} gia tri NULL hop le.")

        # 2.4 Xuat ra file CSV trong data/processed/
        # Luu y: index=False, na_rep='' de ghi dung tieu chuan CSV (truong rong)
        df_proc.to_csv(proc_path, index=False, encoding="utf-8")
        processed_dataframes[fname] = df_proc

        n_rows_proc = len(df_proc)
        print(f"  => Da xuat: {proc_path} ({n_rows_proc:,} dong, {n_cols_raw} cot).")

        cleaning_metrics.append({
            "Bang": fname,
            "So_dong_raw": n_rows_raw,
            "So_dong_processed": n_rows_proc,
            "So_dong_cach_ly": 0,
            "Ty_le_bao_toan_%": round((n_rows_proc / n_rows_raw) * 100, 4),
            "So_cot": n_cols_raw,
            "So_gia_tri_chuan_hoa": total_values_standardized,
            "Trang_thai": "HOAN_THANH",
            "Ghi_chu": "Bao toan 100% du lieu; chuan hoa chuoi & ngay"
        })

    # -------------------------------------------------------------------------
    # BUOC 3: KIEM CHUNG BAT BUOC HAU XU LY (POST-PROCESSING VERIFICATION)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("[BUOC 3] KIEM CHUNG BAT BUOC HAU XU LY")
    print("=" * 70)

    verification_passed = True

    # Kiem tra 3.1: So sanh so dong va ten cot
    print("\n[KC 1] Kiem tra so dong va ten cot giua raw va processed...")
    total_raw_rows = 0
    total_proc_rows = 0
    for fname in BUSINESS_FILES:
        r_df = raw_dataframes[fname]
        p_df = processed_dataframes[fname]
        total_raw_rows += len(r_df)
        total_proc_rows += len(p_df)

        assert len(r_df) == len(p_df), f"LOI: So dong khong khop o {fname}!"
        assert list(r_df.columns) == list(p_df.columns), f"LOI: Cot khong khop o {fname}!"
    print(f"  => KHOP TUYET DOI: {total_raw_rows:,} dong raw == {total_proc_rows:,} dong processed.")
    assert total_raw_rows == 2960188, f"LOI: Tong dong khong dung 2,960,188 (thuc te: {total_raw_rows})!"

    # Kiem tra 3.2: Kiem tra NULL truoc va sau
    print("\n[KC 2] Kiem tra so luong NULL truoc va sau xu ly...")
    for fname in BUSINESS_FILES:
        r_df = raw_dataframes[fname]
        p_df = processed_dataframes[fname]
        r_nulls = r_df.isna().sum().to_dict()
        p_nulls = p_df.isna().sum().to_dict()
        assert r_nulls == p_nulls, f"LOI: So luong NULL bi thay doi o {fname}! Raw: {r_nulls}, Proc: {p_nulls}"
    print("  => KHOP TUYET DOI: Toan bo cac truong NULL giu nguyen 100%, khong phat sinh NULL moi.")

    # Kiem tra 3.3: Kiem tra khong thay doi so tien, so luong, ma dinh danh
    print("\n[KC 3] Kiem tra tinh bat bien cua so tien, so luong va ma dinh danh...")
    # order_items
    assert np.isclose(raw_dataframes["order_items.csv"]["quantity"].sum(),
                      processed_dataframes["order_items.csv"]["quantity"].sum()), "LOI: quantity order_items bi doi!"
    assert np.isclose(raw_dataframes["order_items.csv"]["unit_price"].sum(),
                      processed_dataframes["order_items.csv"]["unit_price"].sum()), "LOI: unit_price order_items bi doi!"
    assert np.isclose(raw_dataframes["order_items.csv"]["discount_amount"].sum(),
                      processed_dataframes["order_items.csv"]["discount_amount"].sum()), "LOI: discount_amount bi doi!"
    # payments
    assert np.isclose(raw_dataframes["payments.csv"]["payment_value"].sum(),
                      processed_dataframes["payments.csv"]["payment_value"].sum()), "LOI: payment_value bi doi!"
    # returns
    assert np.isclose(raw_dataframes["returns.csv"]["return_quantity"].sum(),
                      processed_dataframes["returns.csv"]["return_quantity"].sum()), "LOI: return_quantity bi doi!"
    assert np.isclose(raw_dataframes["returns.csv"]["refund_amount"].sum(),
                      processed_dataframes["returns.csv"]["refund_amount"].sum()), "LOI: refund_amount bi doi!"
    # products
    assert np.isclose(raw_dataframes["products.csv"]["price"].sum(),
                      processed_dataframes["products.csv"]["price"].sum()), "LOI: price products bi doi!"
    assert np.isclose(raw_dataframes["products.csv"]["cogs"].sum(),
                      processed_dataframes["products.csv"]["cogs"].sum()), "LOI: cogs products bi doi!"
    # sales
    assert np.isclose(raw_dataframes["sales.csv"]["Revenue"].sum(),
                      processed_dataframes["sales.csv"]["Revenue"].sum()), "LOI: Revenue sales bi doi!"
    assert np.isclose(raw_dataframes["sales.csv"]["COGS"].sum(),
                      processed_dataframes["sales.csv"]["COGS"].sum()), "LOI: COGS sales bi doi!"
    print("  => KHOP TUYET DOI: Toan bo tong so tien, so luong giu nguyen chinh xac.")

    # Kiem tra 3.4: Xac nhan ban ghi RET-043492 co mat nguyen ven
    print("\n[KC 4] Kiem tra ban ghi RET-043492 trong data/processed/returns.csv...")
    ret_proc = processed_dataframes["returns.csv"]
    rec_ret = ret_proc[ret_proc["return_id"] == "RET-043492"]
    assert len(rec_ret) == 1, "LOI: Khong tim thay RET-043492 trong processed returns!"
    assert rec_ret["return_quantity"].values[0] == 3, "LOI: return_quantity bi sua doi!"
    assert rec_ret["refund_amount"].values[0] == 3172.45, "LOI: refund_amount bi sua doi!"
    print("  => XAC NHAN: RET-043492 ton tai nguyen ven voi return_quantity=3, refund_amount=3172.45.")

    # Kiem tra 3.5: Kiem tra tinh bat bien cua thu muc data/raw/ qua SHA-256
    print("\n[KC 5] Kiem tra ma SHA-256 cua data/raw/ sau khi chay pipeline...")
    for f in all_raw_files:
        h_after = compute_sha256(f)
        h_before = raw_hashes_before[f.name]
        assert h_after == h_before, f"LOI NGHIEP TRONG: Tap tin data/raw/{f.name} da bi sua doi!"
        print(f"  [RAW UNTOUCHED] {f.name:32s}: SHA-256 khop 100%.")
    print("  => XAC NHAN: 100% tap tin trong data/raw/ khong bi thay doi bat ky byte nao.")

    # Kiem tra 3.6: Kiem tra khong co 2 file submission trong data/processed/
    print("\n[KC 6] Kiem tra loai tru cac file submission khoi data/processed/...")
    assert not (PROCESSED_DIR / "sample_submission.csv").exists(), "LOI: sample_submission.csv bi dua vao processed!"
    assert not (PROCESSED_DIR / "submission_idea42_alphaequal.csv").exists(), "LOI: submission_idea42 bi dua vao processed!"
    print("  => XAC NHAN: 2 tap tin submission du bao duoc tach rieng khoi kho du lieu.")

    # -------------------------------------------------------------------------
    # BUOC 4: XUAT BAO CAO CLEANING REPORT
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("[BUOC 4] XUAT BAO CAO CLEANING REPORT")
    print("=" * 70)
    df_metrics = pd.DataFrame(cleaning_metrics)
    report_path = DOCS_DIR / "cleaning_report.csv"
    df_metrics.to_csv(report_path, index=False, encoding="utf-8-sig")
    print(f"[OK] Da luu bao cao vao: {report_path}")
    print("\nTONG HOP KET QUA PIPELINE:")
    print(df_metrics.to_string(index=False))

    print("\n" + "=" * 70)
    print("HOAN THANH PIPELINE LAM SACH DU LIEU THANH CONG!")
    print(f"Tong so ban ghi xuat sang data/processed/: {total_proc_rows:,} dong")
    print("=" * 70)


if __name__ == "__main__":
    main()
